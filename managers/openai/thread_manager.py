from openai import OpenAI
import logging

client = OpenAI()  # This should ideally not be a global variable

class ThreadManager:
    def __init__(self, client):
        self.client = client
        self.threads = {}
        self.logger = logging.getLogger(__name__)

    def get_thread(self, conversation_uuid):
        if conversation_uuid in self.threads:
            return self.threads[conversation_uuid]
        try:
            thread = self.client.beta.threads.create()
            self.threads[conversation_uuid] = thread.id
            return thread.id
        except Exception as e:
            self.logger.error("Error creating or retrieving thread for UUID '%s': %s", conversation_uuid, e, exc_info=True)
            raise  # It's generally a good practice to re-raise exceptions after logging unless specifically handling them
