from managers.elastic.es_connector.elastic_connect import BaseElasticConnector
from managers.elastic.convo_managers.document_managers import DocumentManager
from managers.elastic.logger.error_log import ErrorLogger
import logging

document_manager = DocumentManager()

class SearchManager(BaseElasticConnector):
    def __init__(self):
        super().__init__()
        self.error_logger = ErrorLogger()

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
                error_msg = f"Failed to fetch conversation by UUID {conversation_uuid}: {str(e)}"
                logging.error(error_msg)
                self.error_logger.log_error(conversation_uuid, error_msg)
                raise Exception(f"Error retrieving conversation history: {error_msg}") from e