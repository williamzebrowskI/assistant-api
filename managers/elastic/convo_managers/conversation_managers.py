# Purpose: Contains specific business logic for managing conversations, such as starting a conversation and adding turns.
# Contents: Uses models and DocumentManager methods to implement conversation-specific logic.

import logging
from dataclasses import asdict
from models.models import Conversation, Turn, User, AssistantResponse
from ws.message_data import MessageData
from managers.elastic.logger.error_log import ErrorLogger
from managers.elastic.convo_managers.document_managers import DocumentManager

class ConversationManager(DocumentManager):
    def __init__(self):
        super().__init__()
        self.error_logger = ErrorLogger()
    
    def start_conversation(self, msg_data: MessageData, title: str, partner_id: str, assistant_type: str):
        conversation_uuid = msg_data.conversation_uuid
        initial_session_id = msg_data.session_id_ga
        initial_user_id = msg_data.user_id

        try:
            conversation = Conversation(conversation_uuid, initial_session_id, initial_user_id, assistant_type, title, partner_id)
            self.create_document(conversation_uuid, asdict(conversation))
        except Exception as e:
            error_msg = f"Failed to start conversation {conversation_uuid}: {e}"
            logging.error(error_msg)
            self.error_logger.log_error(conversation_uuid, error_msg)
            raise RuntimeError(error_msg) from e

    def add_turn(self, msg_data: MessageData, user: User, assistant: AssistantResponse, upsert_body=None):
        conversation_uuid = msg_data.conversation_uuid
        try:
            current_index = self.get_current_index(conversation_uuid)
            user.index = current_index
            assistant.index = current_index

            turn = Turn.from_user_and_assistant(user, assistant, conversation_uuid, current_index)

            script = turn.update_script()
            upsert_body = {"turns": [asdict(turn)]}

            self.update_document(conversation_uuid, script, upsert_body)
        except Exception as e:
            error_msg = f"Error adding turn to conversation {conversation_uuid}: {str(e)}"
            logging.error(error_msg)
            self.error_logger.log_error(conversation_uuid, error_msg)
            raise

    def get_current_index(self, conversation_uuid):
        try:
            doc = self.es.get(index=self.es_index, id=conversation_uuid)
            turns = doc['_source'].get('turns', [])
            return len(turns) if turns is not None else 0
        except Exception as e:
            error_msg = f"Failed to fetch current index for conversation {conversation_uuid}: {str(e)}"
            logging.error(error_msg)
            self.error_logger.log_error(conversation_uuid, error_msg)
            raise