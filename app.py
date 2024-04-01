import os
from openai import OpenAI, AssistantEventHandler
from elastic_connector import ElasticConnector
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from dotenv import load_dotenv
load_dotenv()

#Flask app and SocketIO setup
app = Flask(__name__)
socketio = SocketIO(
    app,
    cors_allowed_origins=["http://localhost:8003", "https://benefitsdatatrust.github.io", "http://127.0.0.1:8003"],
    cors_credentials=True,
    cors_allowed_headers="*",
    manage_session=False,
    logger=True,
    engineio_logger=True
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
    Manages conversation threads for the OpenAI Assistant. Responsible for creating new threads and maintaining the
    state of an ongoing conversation.

    Attributes:
        thread_id (str): ID of the current conversation thread. None if no thread is active.
        is_new_thread (bool): Flag indicating whether the current thread is a new thread.
    """
    def __init__(self):
        """
        Initializes the ThreadManager with no active thread.
        """
        self.thread_id = None
        self.is_new_thread = False

    def get_thread(self):
        """
        Retrieves the current thread ID, creating a new thread if none exists.

        Returns:
            str: The thread ID of the current or new conversation thread.
        """
        if not self.thread_id:
            thread = client.beta.threads.create()
            self.thread_id = thread.id
            self.is_new_thread = True
        return self.thread_id

    def reset_thread(self):
        """
        Resets the current conversation thread, marking no active thread.
        """
        self.thread_id = None
        self.is_new_thread = False

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
        print(error)

thread_manager = ThreadManager()
assistant = OpenAIAssistant(assistant_id=ASSISTANT_ID)
assistant_id = assistant.assistant_id

@app.route('/')
def index():
    return render_template('index_2.html')

@socketio.on('user_message', namespace='/chat')
def handle_user_message(message):
    user_input = message['text']
    user_id = request.args.get('userId')
    conversation_uuid = request.args.get('conversationId')
    client_ip = request.remote_addr
    print(f"User connected with ID: {user_id}; Conversation ID: {conversation_uuid}; Client IP: {request.remote_addr}")


    thread_id = thread_manager.get_thread()

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

    if thread_manager.is_new_thread:
        elastic_connector.push_to_index(conversation_uuid, user_id, client_ip, thread_id, assistant_id)
        thread_manager.is_new_thread = False 


    elastic_connector.update_document(conversation_uuid=conversation_uuid, user_query=user_input, assistant_response=text_value)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8002)