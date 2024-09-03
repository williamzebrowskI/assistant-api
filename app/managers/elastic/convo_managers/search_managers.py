from app.managers.elastic.es_connector.elastic_connect import BaseElasticConnector
from app.managers.elastic.convo_managers.document_managers import DocumentManager
import logging
import os
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

document_manager = DocumentManager()

class SearchManager(BaseElasticConnector):
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

    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        with self.handle_errors(conversation_id, "Failed to fetch conversation"):
            response = self.es.get(index=self.es_index, id=conversation_id)
            if not response['found']:
                return []

            conversation_data = response['_source']
            turns = conversation_data.get('turns', []) or []
            history = [
                {'speaker': 'user', 'utterance': turn['user']['user_query']}
                for turn in turns
            ] + [
                {'speaker': 'agent', 'utterance': turn['assistant']['assistant_response']}
                for turn in turns
            ]

            logging.info(f"Conversation history for {conversation_id}: {history}")

            return history