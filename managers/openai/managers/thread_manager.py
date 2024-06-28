from openai import OpenAI
from managers.elastic.logger.error_log import ErrorLogger
from managers.elastic.convo_managers.document_managers import DocumentManager 
import logging
from typing import Optional
from contextlib import contextmanager

class ThreadManager(DocumentManager):
    def __init__(self, client: OpenAI, error_logger: Optional[ErrorLogger] = None):
        super().__init__()
        self.client = client
        self.threads = {}
        self.error_logger = error_logger or ErrorLogger()

    @contextmanager
    def handle_errors(self, conversation_id: str, action: str):
        try:
            yield
        except Exception as e:
            error_msg = f"{action} for UUID '{conversation_id}': {e}"
            logging.error(error_msg, exc_info=True)
            self.error_logger.log_error(conversation_id, error_msg)
            raise RuntimeError(error_msg) from e

    def get_thread(self, conversation_id: str) -> str:
        """Retrieve an existing thread ID or create a new one if it doesn't exist."""
        with self.handle_errors(conversation_id, "Failed to retrieve or create thread"):
            if conversation_id in self.threads:
                return self.threads[conversation_id]
            else:
                return self.create_thread(conversation_id)

    def create_thread(self, conversation_id: str) -> str:
        """Create a new thread and store its ID."""
        with self.handle_errors(conversation_id, "Failed to create thread"):
            thread = self.client.beta.threads.create()
            self.threads[conversation_id] = thread.id
            logging.info(f"New thread created with ID: {thread.id} for conversation UUID: {conversation_id}")
            return thread.id