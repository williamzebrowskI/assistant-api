import os
import hashlib
import uuid
import requests
import logging
from managers.elastic.convo_managers.conversation_managers import ConversationManager
from managers.elastic.convo_managers.search_managers import SearchManager
from managers.elastic.es_connector.elastic_connect import BaseElasticConnector
from managers.elastic.logger.error_log import ErrorLogger
from utils.url_utility import UrlUtility

class SMSHandler:
    def __init__(self, api_url):
        self.conversation_manager = ConversationManager()
        self.elastic_connector = BaseElasticConnector()
        self.elastic_manager = SearchManager()
        self.error_logger = ErrorLogger()
        self.api_url = api_url
        self.conversation_histories = {}

    def send_message_to_api(self, message_body, conversation_uuid):
        """Send message to an external API including the conversation history."""
        conversation_history = self.elastic_manager.get_conversation_history(conversation_uuid)
        conversation_history = conversation_history or []

        try:
            FAFSA_SERVER_URL = os.getenv("BASE_URL")
            headers = {'Content-Type': 'application/json'}
            payload = {
                "conversation_history": {"messages": conversation_history},
                "query": message_body
            }
            response = requests.post(UrlUtility.create_url(f"{FAFSA_SERVER_URL}/answer_faq"), headers=headers, json=payload)
            response_data = response.json()["response"]
            return response_data
        except Exception as e:
            error_message = f"Error sending message to API: {str(e)}"
            logging.error(error_message)
            self.error_logger.log_error(conversation_uuid, error_message)
            raise Exception("Failed to send message due to internal server error")


    def generate_uuid_from_phone(self, phone_number, salt=""):
        """Generate a consistent UUID based on the phone number and optional salt."""
        hash_object = hashlib.sha256((phone_number + salt).encode())
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, hash_object.hexdigest()))
    
