from managers.elastic.elastic_connector import BaseElasticConnector
from managers.elastic.document_manager import DocumentManager
import logging

document_manager = DocumentManager()

class SearchManager(BaseElasticConnector):
    def __init__(self):
        super().__init__()
        self.document_manager = document_manager

    def get_conversation_history(self, conversation_uuid):
            """Retrieve the entire conversation document by UUID."""
            try:
                response = self.es.get(index=self.es_index, id=conversation_uuid)
                if response['found']:
                    # Extract the necessary parts from the conversation
                    conversation_data = response['_source']
                    history = []
                    for turn in conversation_data['turns']:
                        user_message = turn['user']['user_query']
                        assistant_message = turn['assistant']['assistant_response']
                        history.append({'speaker': 'user', 'utterance': user_message})
                        history.append({'speaker': 'agent', 'utterance': assistant_message})
                    return history
                else:
                    return []
            except Exception as e:
                error_message = f"Failed to fetch conversation by UUID {conversation_uuid}: {str(e)}"
                logging.error(error_message)
                self.document_manager.log_error(conversation_uuid, error_message)
                raise Exception(f"Error retrieving conversation history: {error_message}") from e