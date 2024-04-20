import os
import logging
from datetime import datetime
from flask import session, request
from flask_socketio import join_room
from ws.flask_config import config
from managers.openai.event_manager import EventHandler
from managers.elastic.models import User, AssistantResponse
from utils.markdown_stripper import MarkdownStripper
from ws.message_data import MessageData
from app import thread_manager, elastic_manager, client, assistant_id
from dotenv import load_dotenv
load_dotenv()

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

md_stripper = MarkdownStripper()

# SocketIO event handlers
@config.socketio.on('connect', namespace='/chat')
def handle_connect():
    user_id = request.args.get('userId')
    if user_id:
        join_room(user_id)
        session['userId'] = user_id
        logging.info(f"User {user_id} connected with session {request.sid}.")

@config.socketio.on('disconnect', namespace='/chat')
def handle_disconnect():
    try:
        logging.info(f"Client {request.sid} disconnected")
    except Exception as e:
        logging.error(f"Disconnect error: {str(e)}")

@config.socketio.on('user_message', namespace='/chat')
def handle_user_message(message):

    msg_data = MessageData(message, request)

    start_turn_timestamp = datetime.now().isoformat()

    try:
        thread_id = thread_manager.get_thread(msg_data.conversation_uuid)

        client.beta.threads.messages.create(thread_id=thread_id, role="user", content=msg_data.user_input)

        event_handler = EventHandler(userId=msg_data.user_id)
        start_response_timestamp = datetime.now()

        with client.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=assistant_id,
            event_handler=event_handler,
        ) as stream:
            for text in stream.text_deltas:
                pass
            response = stream.get_final_messages()
            response_end_time = datetime.now()
            for message in response:
                for content_block in message.content:
                    if content_block.type == 'text':
                        text_value = content_block.text.value

        strip_md_from_resp = md_stripper.strip(text_value)

        # Initialize User and AssistantResponse objects
        user = User(msg_data)
        assistant_response = AssistantResponse(assistant_id, 'openAI', thread_id, strip_md_from_resp, start_turn_timestamp, start_response_timestamp=start_response_timestamp, end_respond_timestamp=response_end_time)

        # Document existence check and processing
        if not elastic_manager.document_exists(msg_data.conversation_uuid):
            elastic_manager.start_conversation(msg_data, "Conversation about FAFSA", msg_data.partner_id)
            # elastic_manager.start_conversation(msg_data)

        
        # Add turn to conversation
        elastic_manager.add_turn(msg_data, user, assistant_response)
        # elastic_manager.add_turn(msg_data.conversation_uuid, user, assistant_response)

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logging.error(error_message)
        elastic_manager.log_error(msg_data.conversation_uuid, error_message)
        config.socketio.emit('server_message', {'text': 'An error occurred, please try again later.'}, room=msg_data.user_id, namespace='/chat')
