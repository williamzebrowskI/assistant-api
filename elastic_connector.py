from elasticsearch import Elasticsearch
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
        Updates an existing conversation document by appending a new interaction 
        consisting of a user query and the assistant's response to the 'conversations' array.
        This method structures each interaction as a nested object under a unique index
        within the 'conversations' array, allowing for organized tracking of the conversation flow.

        Args:
            conversation_uuid (str): The unique identifier for the conversation document to be updated.
            user_query (str): The text of the user's query.
            assistant_response (str): The text of the assistant's response.

        Raises:
            Exception: Raises an exception if updating the document fails.
        """
        # Attempt to retrieve the current document to find the next index
        try:
            current_doc = self.es.get(index=self.es_index, id=conversation_uuid)
            current_conversations = current_doc['_source']['conversations']
            next_index = len(current_conversations)
        except Exception as e:
            print(f"Error retrieving document for updating: {e}")
            next_index = 0  # Default to 0 if unable to retrieve document
            
        conversation_entry = {
            "index": next_index,
            "details": {
                "user_query": user_query,
                "assistant_response": assistant_response,
                "conversation_timestamp": datetime.now().isoformat()
            }
        }

        script = {
                "script": {
                    "source": """
                        ctx._source.conversations.add(params.conversation);
                        ctx._source.updated_timestamp = params.updated_timestamp; 
                    """,
                    "lang": "painless",
                    "params": {
                        "conversation": conversation_entry,
                        "updated_timestamp": datetime.now().isoformat()
                    }
                }
            }
        
        try:
            response = self.es.update(index=self.es_index, id=conversation_uuid, body=script)
            logging.info(f"Document updated successfully: {response}")
        except Exception as e:
            logging.info(f"Error updating document in Elasticsearch: {e}")
    
    def push_or_update_conversation(self, conversation_uuid, user_id, client_ip, thread_id, assistant_id, user_query, assistant_response, url, referral_url, session_id):
        """
        Creates a new conversation document or updates an existing one in the Elasticsearch index.
        If the document exists, it appends a new interaction to the 'conversations' array. 
        If it does not exist, it creates a new document with the initial interaction.
        Each interaction within the 'conversations' array is indexed for easy reference,
        containing the user's query, assistant's response, and a timestamp.

        Args:
            conversation_uuid (str): The unique identifier for the conversation.
            user_id (str): The identifier for the user involved in the conversation.
            client_ip (str): The IP address of the user's client.
            thread_id (str): The thread identifier for the conversation within the assistant's context.
            assistant_id (str): The unique identifier of the assistant involved in the conversation.
            user_query (str): The text of the user's query.
            assistant_response (str): The text of the assistant's response.

        Raises:
            Exception: Raises an exception if pushing a new document or updating an existing one fails.
        """
        # Check if the document already exists
        exists = self.es.exists(index=self.es_index, id=conversation_uuid)
        
        if exists:
            # Document exists, so update it
            self.update_document(conversation_uuid, user_query, assistant_response)
        else:
            # Document does not exist, so create it
            initial_conversation_entry = {
                "index": 0,
                "details": {
                    "user_query": user_query,
                    "assistant_response": assistant_response,
                    "conversation_timestamp": datetime.now().isoformat()
                }
            }

            doc = {
                "user_id": user_id,
                "session_id": session_id,
                "url": url,
                "referral_url": referral_url,
                "client_ip": client_ip,
                "conversation_id": conversation_uuid,
                "assistant_id": assistant_id,
                "thread_id": thread_id,
                "updated_timestamp": datetime.now(),
                "conversations": [initial_conversation_entry]
            }

            try:
                response = self.es.index(index=self.es_index, id=conversation_uuid, document=doc)
                logging.info(f"Document indexed successfully: {response}")
            except Exception as e:
                logging.error(f"Error pushing document to Elasticsearch: {e}")