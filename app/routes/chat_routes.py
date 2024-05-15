import os
import logging
from datetime import datetime
from flask import session, request, jsonify
from flask_socketio import join_room
from ws.flask_config import config
from ws.message_data import MessageData
from managers.openai.managers.event_manager import EventHandler
from managers.elastic.logger.error_log import ErrorLogger
from managers.elastic.convo_managers.conversation_managers import ConversationManager
from models.models import User, AssistantResponse
from managers.google.sms_handler import SMSHandler
from app.main import app_instance
from utils.markdown_stripper import MarkdownStripper
from app.main import thread_manager, elastic_manager, client, assistant_id
from dotenv import load_dotenv
load_dotenv()

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

md_stripper = MarkdownStripper()
error_logger = ErrorLogger()
elastic_manager = ConversationManager()
FAFSA_SERVER_URL = os.getenv("BASE_URL")
sms_message_handler = SMSHandler(api_url=FAFSA_SERVER_URL)

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

        if not elastic_manager.document_exists(msg_data.conversation_uuid):
            elastic_manager.start_conversation(
                msg_data,
                "Wyatt Fafsa Conversation",
                msg_data.partner_id,
                assistant_type
            )
            
        thread_id = thread_manager.get_thread(msg_data.conversation_uuid)

        client.beta.threads.messages.create(thread_id=thread_id, role="user", content=msg_data.user_input)

        event_handler = EventHandler(userId=msg_data.user_id)
        
        start_response_timestamp = datetime.now().isoformat()

        with client.beta.threads.runs.stream(
            thread_id=thread_id,
            additional_instructions="Respond with information only related to FAFSA.",
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
        user = User(msg_data)
        assistant_response = AssistantResponse(
            assistant_id=assistant_id,
            assistant_type=assistant_type,
            thread_id=thread_id,
            assistant_response=strip_md_from_resp,
            start_response_timestamp=start_response_timestamp,
            end_respond_timestamp=response_end_time
        )

        elastic_manager.add_turn(msg_data, user, assistant_response)

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logging.error(error_message)
        error_logger.log_error(msg_data.conversation_uuid, error_message)
        config.socketio.emit('server_message', {'text': 'An error occurred, please try again later.'}, room=msg_data.user_id, namespace='/chat')


@app_instance.route('/sms', methods=['POST'])
def receive_sms():

    data = request.get_json()

    # Generate or Retrieve ConversationUUID
    conversation_uuid = sms_message_handler.generate_uuid_from_phone(data.get('From', ''), "some_salt_here")

    sms_data = {
        'text': data.get('Body', ''),
        'userId': data.get('From', ''),
        'conversationId': conversation_uuid,
        'currentPageUrl': None,
        'referralUrl': None,
        'partnerId': None,
        'sessionId': None
    }

    # Create MessageData object
    msg_data = MessageData(message=sms_data, request=request)
    assistant_type = "Google"

    # Create User object
    user = User(msg_data)

    try:
        if not sms_message_handler.conversation_manager.document_exists(conversation_uuid):
            logging.info(f"Document not found for UUID {conversation_uuid}, initializing...")
            sms_message_handler.conversation_manager.start_conversation(
                msg_data,
                "SMS Interaction",
                "None",
                assistant_type
            )
        else:
            logging.info(f"Existing UUID retrieved for the conversation: {conversation_uuid}")

        # Send message to API with conversation history
        api_response = sms_message_handler.send_message_to_api(msg_data.user_input, conversation_uuid)

        # Create AssistantResponse object
        assistant_response = AssistantResponse(
            assistant_id=None,
            thread_id=None,
            assistant_response=api_response,
            assistant_type=assistant_type,
            start_response_timestamp=datetime.now().isoformat(),
            end_respond_timestamp=None
        )

        sms_message_handler.conversation_manager.add_turn(
            msg_data,
            user,
            assistant_response,
        )
        return jsonify(
            {
            'user_id': data.get('From', ''),
            'message': api_response
            }
         )
    
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logging.error(error_message)
        error_logger.log_error(msg_data.conversation_uuid, error_message)
        return jsonify({
            'status': 'temporarily unavailable',
            'message': 'Service is temporarily unavailable, please try again later.'
        })