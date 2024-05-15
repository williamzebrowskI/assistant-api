from openai import OpenAI
from managers.elastic.logger.error_log import ErrorLogger
from managers.elastic.convo_managers.document_managers import DocumentManager 
import logging


class ThreadManager(DocumentManager):
    def __init__(self, client: OpenAI):
        self.client = client
        self.threads = {}
        self.error_logger = ErrorLogger() 

    def get_thread(self, conversation_uuid: str) -> str:
        """Retrieve an existing thread ID or create a new one if it doesn't exist."""
        try:
            if conversation_uuid in self.threads:
                return self.threads[conversation_uuid]
            else:
                return self.create_thread(conversation_uuid)
        except Exception as e:
            error_msg = f"Failed to retrieve or create thread for UUID '{conversation_uuid}': {e}"
            logging.error(error_msg, exc_info=True)
            self.error_logger.log_error(conversation_uuid, error_msg)
            raise

    def create_thread(self, conversation_uuid: str) -> str:
        """Create a new thread and store its ID."""
        try:
            thread = self.client.beta.threads.create()
            self.threads[conversation_uuid] = thread.id
            logging.info(f"New thread created with ID: {thread.id} for conversation UUID: {conversation_uuid}")
            return thread.id
        
        except Exception as e:
            error_msg = f"Failed to create thread for UUID '{conversation_uuid}': {e}"
            logging.error(error_msg, exc_info=True)
            self.error_logger.log_error(conversation_uuid, error_msg)
            raise