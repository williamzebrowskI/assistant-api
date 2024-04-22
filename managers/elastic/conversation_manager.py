# Purpose: Contains specific business logic for managing conversations, such as starting a conversation and adding turns.
# Contents: Uses models and DocumentManager methods to implement conversation-specific logic.

import logging
from managers.elastic.models import Conversation, Turn, User, AssistantResponse
from ws.message_data import MessageData
from managers.elastic.document_manager import DocumentManager
from dotenv import load_dotenv
load_dotenv()

class ConversationManager(DocumentManager):
    def __init__(self):
        super().__init__()
    
    def start_conversation(self, msg_data: MessageData, title: str, partner_id: str):
        """Starts a new conversation using the data provided in MessageData instance."""
        conversation_uuid = msg_data.conversation_uuid
        initial_session_id = msg_data.session_id_ga
        initial_user_id = msg_data.user_id
        assistant_type = "openAI"

        try:
            conversation = Conversation(conversation_uuid, initial_session_id, initial_user_id, assistant_type, title, partner_id)
            self.create_document(conversation_uuid, conversation.to_dict())
        except Exception as e:
            error_msg = f"Failed to start conversation {conversation_uuid}: {e}"
            logging.error(error_msg)
            self.log_error(conversation_uuid, error_msg)
            raise RuntimeError(error_msg) from e


    def add_turn(self, msg_data: MessageData, user: User, assistant: AssistantResponse):
        """Adds a turn to an existing conversation."""
        conversation_uuid = msg_data.conversation_uuid
        try:
            if not self.document_exists(conversation_uuid):
                self.start_conversation(msg_data, "Conversation about FAFSA", msg_data.partner_id)

            current_index = self.get_current_index(conversation_uuid)
            user.index = user.index if user.index is not None else current_index
            assistant.index = assistant.index if assistant.index is not None else current_index

            turn = Turn(user, assistant, conversation_uuid, current_index)
            script = turn.update_script()
            
            self.update_document(conversation_uuid, script)
            logging.info(f"Turn added to conversation {conversation_uuid}")
        except Exception as e:
            error_msg = f"Error adding turn to conversation {conversation_uuid}: {str(e)}"
            logging.error(error_msg)
            self.log_error(conversation_uuid, error_msg)
            raise


    def get_current_index(self, conversation_uuid):
        """Returns the current index of the conversation."""
        try:
            doc = self.es.get(index=self.es_index, id=conversation_uuid)
            turns = doc['_source'].get('turns', [])
            return len(turns)
        
        except Exception as e:
            error_msg = f"Failed to fetch current index for conversation {conversation_uuid}: {str(e)}"
            logging.error(error_msg)
            self.log_error(conversation_uuid, error_msg)
            raise
