import os
from openai import OpenAI, AssistantEventHandler
from elastic_connector import ElasticConnector
from thread_manager import ThreadManager
from event_handler import EventHandler
from openai_assistant import OpenAIAssistant 
from flask import session
from flask_socketio import join_room
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import logging
from dotenv import load_dotenv
load_dotenv()

#Flask app and SocketIO setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
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

# Set up ThreadManager
thread_manager = ThreadManager(client=client)

# Set up OpenAI Assistant
ASSISTANT_ID = os.getenv('ASSISTANT_ID')
assistant = OpenAIAssistant(assistant_id=ASSISTANT_ID)
assistant_id = assistant.assistant_id


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect', namespace='/chat')
def handle_connect():
    user_id = request.args.get('userId')
    if user_id:
        join_room(user_id)
        session['userId'] = user_id 

@socketio.on('disconnect', namespace='/chat')
def handle_disconnect():
    logging.info(f"Client disconnected: {request.sid}")

@socketio.on('user_message', namespace='/chat')
def handle_user_message(message):
    user_input = message['text']
    user_id = message.get('userId')
    conversation_uuid = message.get('conversationId')
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(",")[0].strip()

    thread_id = thread_manager.get_thread(conversation_uuid)

    client.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_input)

    event_handler = EventHandler(userId=user_id)

    with client.beta.threads.runs.create_and_stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        event_handler=event_handler,
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