from elasticsearch import Elasticsearch, AsyncElasticsearch
import os
from dotenv import load_dotenv
load_dotenv()

class ElasticConnector():
    def __init__(self):
        self.es_url = os.getenv('es_url')
        self.es_index = os.getenv('es_index')
        self.es_port = os.getenv('es_port')
        self.es_api_key = os.getenv('es_api_key')
        self.es = AsyncElasticsearch(hosts=[f"{self.es_url }:{self.es_port}"], api_key=f"{self.es_api_key }")

    async def push_to_index(self, conversation_uuid, doc):
        try:
            response = await self.es.index(index=f"{self.es_index}", id=f"{conversation_uuid}", document=doc)
            print("Document indexed successfully:", response)
        except Exception as e:
            print(f"Error pushing document to Elasticsearch: {e}")

    async def update_document(self, conversation_uuid, doc):
        try:
            response = await self.es.update(index=f"{self.es_index}", id=f"{conversation_uuid}", doc=doc)
            print("Document updated successfully:", response)
        except Exception as e:
            print(f"Error updating document in Elasticsearch: {e}")