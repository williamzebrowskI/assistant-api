# Purpose: Contains specific business logic for managing conversations, such as starting a conversation and adding turns.
# Contents: Uses models and DocumentManager methods to implement conversation-specific logic.

import logging
from dataclasses import asdict
from typing import Optional, Dict, Any
from contextlib import contextmanager
from models.models import Conversation, Turn, User, AssistantResponse
from ws.message_data import MessageData
from managers.elastic.logger.error_log import ErrorLogger
from managers.elastic.convo_managers.document_managers import DocumentManager

class ConversationManager(DocumentManager):
    def __init__(self, error_logger: Optional[ErrorLogger] = None):
        super().__init__()
        self.error_logger = error_logger or ErrorLogger()

    @contextmanager
    def handle_errors(self, conversation_uuid: str, action: str):
        try:
            yield
        except Exception as e:
            error_msg = f"{action} for conversation {conversation_uuid}: {e}"
            logging.error(error_msg)
            self.error_logger.log_error(conversation_uuid, error_msg)
            raise RuntimeError(error_msg) from e

    def start_conversation(self, msg_data: MessageData, title: str, partner_id: str, assistant_type: str) -> None:
        """
        Starts a new conversation and creates a document in the database.

        :param msg_data: MessageData object containing conversation metadata.
        :param title: Title of the conversation.
        :param partner_id: ID of the partner.
        :param assistant_type: Type of the assistant.
        """
        conversation_uuid = msg_data.conversation_uuid
        initial_session_id = msg_data.session_id_ga
        initial_user_id = msg_data.user_id

        with self.handle_errors(conversation_uuid, "Failed to start conversation"):
            conversation = Conversation(
                conversation_uuid, initial_session_id, initial_user_id, assistant_type, title, partner_id, turns=[]
            )
            self.create_document(conversation_uuid, asdict(conversation))
            logging.info(f"Conversation {conversation_uuid} started successfully.")

    def add_turn(self, msg_data: MessageData, user: User, assistant: AssistantResponse, upsert_body: Optional[Dict[str, Any]] = None) -> None:
        """
        Adds a turn to an existing conversation.

        :param msg_data: MessageData object containing conversation metadata.
        :param user: User object representing the user.
        :param assistant: AssistantResponse object representing the assistant's response.
        :param upsert_body: Optional dictionary for upsert body.
        """
        conversation_uuid = msg_data.conversation_uuid

        with self.handle_errors(conversation_uuid, "Error adding turn to conversation"):
            current_index = self.get_current_index(conversation_uuid)
            user.index = current_index
            assistant.index = current_index

            turn = Turn.from_user_and_assistant(user, assistant, conversation_uuid, current_index)

            script = turn.update_script()
            upsert_body = {"turns": [asdict(turn)]}

            self.update_document(conversation_uuid, script, upsert_body)
            logging.info(f"Turn added to conversation {conversation_uuid} at index {current_index}.")

    def get_current_index(self, conversation_uuid: str) -> int:
        """
        Retrieves the current index of turns in a conversation.

        :param conversation_uuid: UUID of the conversation.
        :return: Current index of turns.
        """
        with self.handle_errors(conversation_uuid, "Failed to fetch current index"):
            doc = self.es.get(index=self.es_index, id=conversation_uuid)
            turns = doc['_source'].get('turns', [])
            current_index = len(turns) if turns is not None else 0
            logging.info(f"Current index for conversation {conversation_uuid} is {current_index}.")
            return current_index