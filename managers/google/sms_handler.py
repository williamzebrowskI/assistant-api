import os
import hashlib
import uuid
import requests
import logging
from typing import Optional
from managers.elastic.convo_managers.conversation_managers import ConversationManager
from managers.elastic.convo_managers.search_managers import SearchManager
from managers.elastic.es_connector.elastic_connect import BaseElasticConnector
from managers.elastic.logger.error_log import ErrorLogger
from utils.url_utility import UrlUtility
from contextlib import contextmanager

class SMSHandler:
    def __init__(self, api_url: str, 
                 conversation_manager: Optional[ConversationManager] = None,
                 elastic_connector: Optional[BaseElasticConnector] = None,
                 elastic_manager: Optional[SearchManager] = None,
                 error_logger: Optional[ErrorLogger] = None):
        self.conversation_manager = conversation_manager or ConversationManager()
        self.elastic_connector = elastic_connector or BaseElasticConnector()
        self.elastic_manager = elastic_manager or SearchManager()
        self.error_logger = error_logger or ErrorLogger()
        self.api_url = api_url
        self.conversation_histories = {}

    @contextmanager
    def handle_errors(self, conversation_uuid: str, action: str):
        try:
            yield
        except Exception as e:
            error_message = f"{action} for conversation {conversation_uuid}: {e}"
            logging.error(error_message)
            self.error_logger.log_error(conversation_uuid, error_message)
            raise RuntimeError(error_message) from e

    def send_message_to_api(self, message_body: str, conversation_uuid: str) -> str:
        """Send message to an external API including the conversation history."""
        with self.handle_errors(conversation_uuid, "Error sending message to API"):
            conversation_history = self.elastic_manager.get_conversation_history(conversation_uuid) or []
            FAFSA_SERVER_URL = os.getenv("BASE_URL")
            headers = {'Content-Type': 'application/json'}
            payload = {
                "conversation_history": {"messages": conversation_history},
                "query": message_body
            }
            response = requests.post(UrlUtility.create_url(f"{FAFSA_SERVER_URL}/answer_faq"), headers=headers, json=payload)
            response_data = response.json().get("response", "")
            logging.info(f"Message sent to API for conversation {conversation_uuid}. Response: {response_data}")
            return response_data

    def generate_uuid_from_phone(self, phone_number: str, salt: str = "") -> str:
        """Generate a consistent UUID based on the phone number and optional salt."""
        hash_object = hashlib.sha256((phone_number + salt).encode())
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, hash_object.hexdigest()))