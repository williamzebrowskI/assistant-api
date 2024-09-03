# Purpose: Contains specific business logic for managing conversations, such as starting a conversation and adding turns.
# Contents: Uses models and DocumentManager methods to implement conversation-specific logic.

import os
import logging
from dataclasses import asdict
from typing import Optional, Dict, Any
from contextlib import contextmanager
from app.models.models import Conversation, Turn, User, AssistantResponse
from app.ws.message_data import MessageData
from app.managers.elastic.convo_managers.document_managers import DocumentManager

class ConversationManager(DocumentManager):
    def __init__(self):
        super().__init__()

    @contextmanager
    def handle_errors(self, conversation_id: str, action: str):
        try:
            yield
        except Exception as e:
            error_msg = f"{action} for conversation {conversation_id}: {e}"
            logging.error(error_msg)
            raise RuntimeError(error_msg) from e

    def start_conversation(self, msg_data: MessageData) -> None:
        """
        Starts a new conversation and creates a document in the database.

        :param msg_data: MessageData object containing conversation metadata.
        """
        conversation_id = msg_data.conversation_id
        user_id = msg_data.user_id

        with self.handle_errors(conversation_id, "Failed to start conversation"):
            conversation = Conversation(
                conversation_id, user_id, turns=[]
            )
            self.create_document(conversation_id, asdict(conversation))
            logging.info(f"Conversation {conversation_id} started successfully.")

    def add_turn(self, msg_data: MessageData, user: User, assistant: AssistantResponse, upsert_body: Optional[Dict[str, Any]] = None, intent: Optional[str] = None, confidence: Optional[float] = None) -> None:
        """
        Adds a turn to an existing conversation.

        :param msg_data: MessageData object containing conversation metadata.
        :param user: User object representing the user.
        :param assistant: AssistantResponse object representing the assistant's response.
        :param upsert_body: Optional dictionary for upsert body.
        """
        conversation_id = msg_data.conversation_id

        with self.handle_errors(conversation_id, "Error adding turn to conversation"):
            current_index = self.get_current_index(conversation_id)
            user.index = current_index
            assistant.index = current_index

            turn = Turn.from_user_and_assistant(user, assistant, conversation_id, current_index)

            # Detailed logging of the turn object before sending to Elasticsearch
            logging.info(f"Turn object to be upserted: {turn}")

            script = turn.update_script()
            upsert_body = {"turns": [asdict(turn)]}

            # Detailed logging of upsert_body
            logging.info(f"Upsert body: {upsert_body}")

            self.update_document(conversation_id, script, upsert_body)
            logging.info(f"Turn added to conversation {conversation_id} at index {current_index}.")

    def get_current_index(self, conversation_id: str) -> int:
        """
        Retrieves the current index of turns in a conversation.

        :param conversation_id: UUID of the conversation.
        :return: Current index of turns.
        """
        with self.handle_errors(conversation_id, "Failed to fetch current index"):
            doc = self.es.get(index=self.es_index, id=conversation_id)
            turns = doc['_source'].get('turns', [])
            current_index = len(turns) if turns is not None else 0
            logging.info(f"Current index for conversation {conversation_id} is {current_index}.")
            return current_index