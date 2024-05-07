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
    
    def start_conversation(self, msg_data: MessageData, title: str, partner_id: str, assistant_type: str):
        """Starts a new conversation using the data provided in MessageData instance."""
        conversation_uuid = msg_data.conversation_uuid
        initial_session_id = msg_data.session_id_ga
        initial_user_id = msg_data.user_id

        try:
            conversation = Conversation(conversation_uuid, initial_session_id, initial_user_id, assistant_type, title, partner_id)
            self.create_document(conversation_uuid, conversation.to_dict())
        except Exception as e:
            error_msg = f"Failed to start conversation {conversation_uuid}: {e}"
            logging.error(error_msg)
            self.log_error(conversation_uuid, error_msg)
            raise RuntimeError(error_msg) from e

    def add_turn(self, msg_data: MessageData, user: User, assistant: AssistantResponse, upsert_body=None):
        """Adds a turn to an existing conversation or starts a new one if it doesn't exist."""
        conversation_uuid = msg_data.conversation_uuid
        try:
            # Fetch the current index if the conversation exists, otherwise start at 0
            current_index = self.get_current_index(conversation_uuid) if self.document_exists(conversation_uuid) else 0
            user.index = current_index
            assistant.index = current_index

            # Create the turn
            turn = Turn(user, assistant, conversation_uuid, current_index)
            script = turn.update_script()

            # Prepare an upsert body that includes the conversation and the current turn
            if not self.document_exists(conversation_uuid):
                # Create a new conversation object with the first turn
                conversation = Conversation(
                    conversation_uuid, 
                    msg_data.session_id_ga, 
                    msg_data.user_id, 
                    assistant.assistant_type, 
                    "Conversation about FAFSA", 
                    msg_data.partner_id
                )
                conversation.turns = [turn.to_dict()]  # Include the first turn
                upsert_body = conversation.to_dict()
            else:
                # If the conversation already exists, prepare only the current turn as part of the upsert
                upsert_body = {
                    "turns": [turn.to_dict()]
                }

            # Perform the upsert operation
            self.update_document(conversation_uuid, script, upsert_body)

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
