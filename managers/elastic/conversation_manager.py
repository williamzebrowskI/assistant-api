# Purpose: Contains specific business logic for managing conversations, such as starting a conversation and adding turns.
# Contents: Uses models and DocumentManager methods to implement conversation-specific logic.

import logging
from managers.elastic.models import Conversation, Turn
from managers.elastic.document_manager import DocumentManager
from dotenv import load_dotenv
load_dotenv()

class ConversationManager(DocumentManager):
    def __init__(self, index_name='conversations'):
        super().__init__(index_name)

    def start_conversation(self, conversation_uuid, initial_session_id, initial_user_id, assistant_type, title):
        
        try:
            conversation = Conversation(conversation_uuid, initial_session_id, initial_user_id, assistant_type, title)
            self.create_document(conversation_uuid, conversation.to_dict())
        except Exception as es_exc:
            error_msg = f"Failed to start conversation {conversation_uuid}: {es_exc}"
            logging.error(error_msg)
            self.log_error(conversation_uuid, error_msg)
            raise RuntimeError(error_msg) from es_exc


    def add_turn(self, conversation_uuid, user, assistant):

        try:
            if not self.document_exists(conversation_uuid):
                self.start_conversation(conversation_uuid, user.session_id, user.user_id, assistant.assistant_type, "Conversation about FAFSA")

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

        try:
            doc = self.es.get(index=self.es_index, id=conversation_uuid)
            turns = doc['_source'].get('turns', [])
            return len(turns)
        
        except Exception as e:
            error_msg = f"Failed to fetch current index for conversation {conversation_uuid}: {str(e)}"
            logging.error(error_msg)
            self.log_error(conversation_uuid, error_msg)
            raise
