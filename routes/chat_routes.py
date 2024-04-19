import os
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
from datetime import datetime
from ws.flask_config import config
from managers.openai.event_manager import EventHandler
from app import thread_manager, elastic_manager, client, assistant_id
from managers.elastic.models import User, AssistantResponse
from flask import session, request
from flask_socketio import join_room
import logging

from utils.markdown_stripper import MarkdownStripper

md_stripper = MarkdownStripper()

from dotenv import load_dotenv
load_dotenv()


@config.socketio.on('connect', namespace='/chat')
def handle_connect():
    user_id = request.args.get('userId')
    if user_id:
        join_room(user_id)
        session['userId'] = user_id 

@config.socketio.on('disconnect', namespace='/chat')
def handle_disconnect():
    try:
        # Properly handle the disconnect logic
        logging.info(f"Client {request.sid} disconnected")
    except Exception as e:
        logging.error(f"Disconnect error: {str(e)}")

@config.socketio.on('user_message', namespace='/chat')
def handle_user_message(message):
    user_input = message.get('text', 'Unknown')
    user_id = message.get('userId', 'Unknown')
    conversation_uuid = message.get('conversationId', 'Unknown')
    page_url = message.get('currentPageUrl', 'Unknown')
    referral_url = message.get('referralUrl', 'Unknown')
    session_id_ga = message.get('sessionId', 'Unknown')
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(",")[0].strip()

    start_turn_timestamp = datetime.now().isoformat()

    try:
        thread_id = thread_manager.get_thread(conversation_uuid)

        client.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_input)

        event_handler = EventHandler(userId=user_id)
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
        user = User(client_ip, session_id_ga, user_id, page_url, referral_url, user_input)
        assistant_response = AssistantResponse(assistant_id, 'openAI', thread_id, strip_md_from_resp, start_turn_timestamp, start_response_timestamp=start_response_timestamp, end_respond_timestamp=response_end_time)

        # Document existence check and processing
        if not elastic_manager.document_exists(conversation_uuid):
            elastic_manager.start_conversation(conversation_uuid, session_id_ga, user_id, "openAI", "Conversation about FAFSA")
        
        elastic_manager.add_turn(conversation_uuid, user, assistant_response)

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logging.error(error_message)
        elastic_manager.log_error(conversation_uuid, error_message)
        config.socketio.emit('server_message', {'text': 'An error occurred, please try again later.'}, room=user_id, namespace='/chat')
