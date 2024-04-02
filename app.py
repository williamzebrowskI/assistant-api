import os
from openai import OpenAI, AssistantEventHandler
from elastic_connector import ElasticConnector
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import logging
from dotenv import load_dotenv
load_dotenv()

#Flask app and SocketIO setup
app = Flask(__name__)
socketio = SocketIO(
    app,
    cors_allowed_origins=["http://127.0.0.1:5500", "http://localhost:8002", "https://benefitsdatatrust.github.io", "http://127.0.0.1:8002"],
    cors_credentials=True,
    cors_allowed_headers="*",
    manage_session=False,
    logger=False,
    engineio_logger=False
)

# Set up OpenAI client
client = OpenAI()
OpenAI.api_key = os.getenv('OPENAI_API_KEY')

# Set up ElasticConnector
elastic_connector = ElasticConnector()

# Set up OpenAI Assistant
ASSISTANT_ID = os.getenv('ASSISTANT_ID')


class OpenAIAssistant:
    def __init__(self, assistant_id):
        """
        Initializes the OpenAIAssistant instance.

        Args:
            assistant_id (str): The unique identifier for the OpenAI Assistant.
        """
        self.assistant_id = assistant_id

class ThreadManager:
    """
    Manages conversation threads, ensuring each conversation has a unique thread.
    
    Attributes:
        threads (dict): A dictionary mapping conversation UUIDs to their respective thread IDs.
    
    Methods:
        get_thread(conversation_uuid): Retrieves or creates a unique thread ID for a given conversation.
    """
    def __init__(self):
        """
        Initializes the ThreadManager with an empty dictionary to store conversation thread mappings.
        """
        # Maps conversation_uuid to thread_id
        self.threads = {}

    def get_thread(self, conversation_uuid):
        """
        Retrieves the thread ID for a given conversation UUID. If the conversation does not have an associated
        thread ID, a new thread is created, stored, and then returned.
        
        Args:
            conversation_uuid (str): The unique identifier for a conversation.
        
        Returns:
            str: The thread ID associated with the given conversation UUID.
        """
        # If a thread_id exists for the conversation, return it
        if conversation_uuid in self.threads:
            return self.threads[conversation_uuid]
        else:
            # Otherwise, create a new thread_id, store it, and return it
            thread = client.beta.threads.create()
            self.threads[conversation_uuid] = thread.id
            return thread.id

class EventHandler(AssistantEventHandler):
    """
    Handles events triggered during the conversation with the OpenAI Assistant. This includes receiving text updates
    from the assistant and handling any errors that occur.

    Inherits from AssistantEventHandler to provide custom event handling logic for the Flask-SocketIO integration.
    """
    def on_text_delta(self, delta, snapshot):
        """
        Handles text updates from the assistant, emitting them to the client through SocketIO.

        Args:
            delta: Delta update containing the text changes.
            snapshot: The current state of the message after applying the delta update.
        """
        socketio.emit('assistant_message', {'text': delta.value}, namespace='/chat')

    def on_error(self, error):
        logging.warning(error)

thread_manager = ThreadManager()
assistant = OpenAIAssistant(assistant_id=ASSISTANT_ID)
assistant_id = assistant.assistant_id

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('user_message', namespace='/chat')
def handle_user_message(message):
    user_input = message['text']
    user_id = request.args.get('userId')
    conversation_uuid = request.args.get('conversationId')
    client_ip = request.remote_addr
    logging.info(f"User connected with ID: {user_id}; Conversation ID: {conversation_uuid}; Client IP: {request.remote_addr}")

    thread_id = thread_manager.get_thread(conversation_uuid)

    client.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_input)

    with client.beta.threads.runs.create_and_stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()
        response = stream.get_final_messages()
        for message in response:
            for content_block in message.content:
                if content_block.type == 'text':
                    text_value = content_block.text.value

     # Method to update the conversation in Elasticsearch.
    elastic_connector.push_or_update_conversation(
        conversation_uuid=conversation_uuid,
        user_id=user_id,
        client_ip=client_ip,
        thread_id=thread_id,
        assistant_id=assistant.assistant_id,
        user_query=user_input,
        assistant_response=text_value
    )

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8002)