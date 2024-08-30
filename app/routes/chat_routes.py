import os
import logging
from datetime import datetime
from flask import session, request, jsonify
from flask_socketio import join_room
from ws.flask_config import config
from ws.message_data import MessageData
from managers.openai.managers.event_manager import EventHandler
from managers.elastic.logger.error_log import ErrorLogger
from managers.elastic.convo_managers.conversation_managers import ConversationManager, DocumentManager
from models.models import User, AssistantResponse
from app.main import app_instance
from utils.markdown_stripper import MarkdownStripper
from app.main import thread_manager, elastic_manager, client, assistant_id
# from managers.google.nlp.intent_classifier import IntentClassifier
from dotenv import load_dotenv
load_dotenv()

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
elasticsearch_enabled = os.getenv('ELASTICSEARCH_ENABLED', 'false').lower() == 'true'

# classifier = IntentClassifier()
md_stripper = MarkdownStripper()
error_logger = ErrorLogger()
elastic_manager = ConversationManager() if elasticsearch_enabled else None
document_manager = DocumentManager() if elasticsearch_enabled else None

# SocketIO event handlers
@config.socketio.on('connect', namespace='/chat')
def handle_connect():
    user_id = request.args.get('userId')
    if user_id:
        join_room(user_id)
        session['userId'] = user_id
        logging.info(f"User {user_id} connected with session {request.sid}.")

@config.socketio.on('heartbeat', namespace='/chat')
def handle_heartbeat(message):
    # logging.info(f"Heartbeat received: {message}")
    pass

@config.socketio.on('disconnect', namespace='/chat')
def handle_disconnect():
    try:
        pass
        logging.info(f"Client {request.sid} disconnected")
    except Exception as e:
        logging.error(f"Disconnect error: {str(e)}")

@config.socketio.on('user_message', namespace='/chat')
def handle_user_message(message):
    assistant_type = "OpenAI"
    msg_data = MessageData(message, request)

    try:
        if elasticsearch_enabled and not elastic_manager.document_exists(msg_data.conversation_id):
            elastic_manager.start_conversation(
                msg_data,
                msg_data.partner_id,
                "Conversation",
                assistant_type
            )

        thread_id = thread_manager.get_thread(msg_data.conversation_id)
        client.beta.threads.messages.create(thread_id=thread_id, role="user", content=msg_data.user_input)

        event_handler = EventHandler(userId=msg_data.user_id)
        start_respond_timestamp = datetime.now().isoformat()

        with client.beta.threads.runs.stream(
            thread_id=thread_id,
            additional_instructions="You are a helpful assistant.",
            assistant_id=assistant_id,
            event_handler=event_handler,
            tool_choice={"type": "file_search"}
        ) as stream:
            for text in stream.text_deltas:
                pass
            response = stream.get_final_messages()
            response_end_time = datetime.now().isoformat()
            for message in response:
                for content_block in message.content:
                    if content_block.type == 'text':
                        text_value = content_block.text.value
                        strip_md_from_resp = md_stripper.strip(text_value)

                        # Initialize User and AssistantResponse objects
                        user = User.from_message_data(msg_data)
                        assistant_response = AssistantResponse(
                            assistant_id=assistant_id,
                            assistant_type=assistant_type,
                            thread_id=thread_id,
                            assistant_response=strip_md_from_resp,
                            start_respond_timestamp=start_respond_timestamp,
                            end_respond_timestamp=response_end_time
                        )

                        if elasticsearch_enabled:
                            elastic_manager.add_turn(
                                msg_data,
                                user,
                                assistant_response
                            )

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logging.error(error_message)
        if elasticsearch_enabled:
            error_logger.log_error(msg_data.conversation_id, error_message)
        config.socketio.emit('server_message', {'text': 'An error occurred, please try again later.'}, room=msg_data.user_id, namespace='/chat')