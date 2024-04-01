from elasticsearch import AsyncElasticsearch, Elasticsearch
import os
import logging
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()


class ElasticConnector():
    """
    This class serves as a connector for Elasticsearch operations.
    It handles the creation and updating of documents within an Elasticsearch index.
    """
    def __init__(self):
        # Initialization with environmental variables
        self.es_url = os.environ.get('ES_URL', 'unassigned_elastic_url')
        if self.es_url == 'unassigned_elastic_url':
            logging.warning('Elastic URL is not set.')
    
        self.es_index = os.environ.get('ES_INDEX', 'unassigned_elastic_index')
        if self.es_index == 'unassigned_elastic_index':
            logging.warning('Elastic Index is not set.')

        self.es_port = os.environ.get('ES_PORT', 'unassigned_elastic_port')
        if self.es_port == 'unassigned_elastic_port':
            logging.warning('Elastic Port is not set.')

        self.es_api_key = os.environ.get('ES_API_KEY', 'unassigned_elastic_api_key')
        if self.es_api_key == 'unassigned_elastic_api_key':
            logging.warning('Elastic Port is not set.')

         # Establish connection to Elasticsearch
        self.es = Elasticsearch(hosts=[f"{self.es_url }:{self.es_port}"], api_key=f"{self.es_api_key }")


    def update_document(self, conversation_uuid, user_query, assistant_response):
        """
        Asynchronously appends a new interaction (a user query and the corresponding assistant response) to the `conversations` array of an existing document in the Elasticsearch index.

        This method updates an existing conversation document by appending a new entry to the `conversations` list. Each entry includes the user's query and the assistant's response, maintaining a record of the interaction within the conversation.

        Args:
            conversation_uuid (str): The unique identifier for the existing conversation document to be updated.
            user_query (str): The query submitted by the user.
            assistant_response (str): The response generated by the assistant in reply to the user's query.

        Raises:
            Exception: If there is an error appending the new interaction to the conversation document, it prints an error message with details.
        """
        conversation_entry = {
                "assistant_response": assistant_response,
                "user_query": user_query
            }

        script = {
                "script": {
                    "source": """
                        ctx._source.conversations.add(params.conversation);
                        ctx._source.timestamp = params.timestamp; 
                    """,
                    "lang": "painless",
                    "params": {
                        "conversation": conversation_entry,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            }
        
        try:
            response = self.es.update(index=self.es_index, id=conversation_uuid, body=script)
            logging.info(f"Document updated successfully: {response}")
        except Exception as e:
            logging.info(f"Error updating document in Elasticsearch: {e}")
    
    def push_or_update_conversation(self, conversation_uuid, user_id, client_ip, thread_id, assistant_id, user_query, assistant_response):
        # Check if the document already exists
        exists = self.es.exists(index=self.es_index, id=conversation_uuid)
        
        if exists:
            # Document exists, so update it
            self.update_document(conversation_uuid, user_query, assistant_response)
        else:
            # Document doesn't exist, create it
            doc = {
                "user_id": user_id,
                "client_ip": client_ip,
                "assistant_id": assistant_id,
                "thread_id": thread_id,
                "timestamp": datetime.now(),
                "conversations": [{"user_query": user_query, "assistant_response": assistant_response}]
            }
            try:
                response = self.es.index(index=self.es_index, id=conversation_uuid, document=doc)
                logging.info(f"Document indexed successfully: {response}")
            except Exception as e:
                logging.error(f"Error pushing document to Elasticsearch: {e}")
