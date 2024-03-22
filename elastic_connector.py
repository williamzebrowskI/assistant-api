from elasticsearch import AsyncElasticsearch
import os
import logging
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        self.es = AsyncElasticsearch(hosts=[f"{self.es_url }:{self.es_port}"], api_key=f"{self.es_api_key }")

    async def push_to_index(self, conversation_uuid, doc):
        """
        Asynchronously pushes a new document to the Elasticsearch index.
        
        Args:
            index (str): The name of the index to push the document to
            conversation_uuid (str): The unique identifier for the conversation.
            doc (dict): The document to be indexed, containing conversation data.
        """
        try:
            response = await self.es.index(index=self.es_index, id=conversation_uuid, document=doc)
            logging.info(f"Document indexed successfully: {response}")
        except Exception as e:
            logging.error(f"Error pushing document to Elasticsearch: {e}")


    async def update_document(self, conversation_uuid, doc):
        """
        Asynchronously updates an existing document within the Elasticsearch index.
        
        Args:
            index (str): The name of the index to push the document to.
            conversation_uuid (str): The unique identifier for the conversation.
            doc (dict): The partial document with updated data.
        """
        try:
            response = await self.es.update(index=self.es_index, id=conversation_uuid, doc=doc)
            logging.info(f"Document updated successfully: {response}")
        except Exception as e:
            logging.error(f"Error updating document in Elasticsearch: {e}")