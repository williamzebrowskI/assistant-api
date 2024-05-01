import os
import hashlib
import uuid
import requests
import logging
from managers.elastic.conversation_manager import ConversationManager
from managers.elastic.document_manager import DocumentManager
from managers.elastic.search_manager import SearchManager
from managers.elastic.elastic_connector import BaseElasticConnector
from dotenv import load_dotenv
load_dotenv()

fafsa_server_url = os.getenv("BASE_URL")

class SMSHandler:
    def __init__(self, api_url):
        self.conversation_manager = ConversationManager()
        self.elastic_connector = BaseElasticConnector()
        self.document_manager = DocumentManager()
        self.elastic_manager = SearchManager()
        self.api_url = api_url
        self.conversation_histories = {}

    def send_message_to_api(self, message_body, conversation_uuid):
        """Send message to an external API including the conversation history."""
        conversation_history = self.elastic_manager.get_conversation_history(conversation_uuid)
        conversation_history = conversation_history or []

        try:
            headers = {'Content-Type': 'application/json'}
            payload = {
                "conversation_history": {"messages": conversation_history},
                "query": message_body
            }
            
            response = requests.post(f"{fafsa_server_url}/answer_faq", headers=headers, json=payload)
            response_data = response.json()["response"]
            return response_data
        except Exception as e:
            error_message = f"Error sending message to API: {str(e)}"
            logging.error(error_message)
            self.document_manager.log_error(conversation_uuid, error_message)
            raise Exception("Failed to send message due to internal server error")


    def generate_uuid_from_phone(self, phone_number, salt=""):
        """Generate a consistent UUID based on the phone number and optional salt."""
        hash_object = hashlib.sha256((phone_number + salt).encode())
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, hash_object.hexdigest()))
    
