from elasticsearch import AsyncElasticsearch
import os
from dotenv import load_dotenv
load_dotenv()

class ElasticConnector():
    """
    This class serves as a connector for Elasticsearch operations.
    It handles the creation and updating of documents within an Elasticsearch index.
    """
    def __init__(self):
        # Initialization with environmental variables
        self.es_url = os.getenv('es_url')
        self.es_index = os.getenv('es_index')
        self.es_port = os.getenv('es_port')
        self.es_api_key = os.getenv('es_api_key')
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
            response = await self.es.index(index=f"{self.es_index}", id=f"{conversation_uuid}", document=doc)
            print("Document indexed successfully:", response)
        except Exception as e:
            print(f"Error pushing document to Elasticsearch: {e}")


    async def update_document(self, conversation_uuid, doc):
        """
        Asynchronously updates an existing document within the Elasticsearch index.
        
        Args:
            index (str): The name of the index to push the document to.
            conversation_uuid (str): The unique identifier for the conversation.
            doc (dict): The partial document with updated data.
        """
        try:
            print(conversation_uuid)
            response = await self.es.update(index=f"{self.es_index}", id=f"{conversation_uuid}", doc=doc)
            print("Document updated successfully:", response)
        except Exception as e:
            print(f"Error updating document in Elasticsearch: {e}")