from openai import OpenAI
import logging

client = OpenAI()

class ThreadManager:
    """
    Manages conversation threads for interactions with the OpenAI Assistant. 
    Ensures that each conversation is linked to a unique thread for maintaining 
    the context of the conversation.

    Attributes:
        client (OpenAI): An instance of the OpenAI client, used to interact with OpenAI's API.
        threads (dict): A dictionary mapping conversation UUIDs to their respective OpenAI thread IDs.

    Methods:
        get_thread(conversation_uuid): Retrieves the thread ID associated with a given conversation UUID.
                                       If no thread exists for the UUID, a new thread is created using the OpenAI API.

    Args:
        client (OpenAI): An instance of the OpenAI client.
    """
    def __init__(self, client):
        """
        Initializes the ThreadManager with a client instance and an empty dictionary for storing thread IDs.

        Args:
            client (OpenAI): An instance of the OpenAI client.
        """
        self.client = client
        self.threads = {}
        self.logger = logging.getLogger(__name__)

    def get_thread(self, conversation_uuid):
        """
        Retrieves the thread ID for a given conversation UUID. If the conversation UUID does not have an
        associated thread ID, a new thread is created using the OpenAI API, and its ID is stored and returned.

        Args:
            conversation_uuid (str): The unique identifier for the conversation.

        Returns:
            str: The thread ID associated with the conversation UUID.
        """
        try:
            if conversation_uuid in self.threads:
                return self.threads[conversation_uuid]
            else:
                thread = self.client.beta.threads.create()
                self.threads[conversation_uuid] = thread.id
                return thread.id
        except Exception as e:
            # Log the error condition
            self.logger.error(f"Error creating or retrieving thread for conversation UUID {conversation_uuid}: {e}", exc_info=True)
            # You might want to handle the error, e.g., by returning None or re-raising the exception
            return None

