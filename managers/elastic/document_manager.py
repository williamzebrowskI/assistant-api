# Purpose: Manages document CRUD operations in Elasticsearch that are generic and not specifically tied to conversations alone.
# Contents: Methods for creating, updating, and checking documents.

from .elastic_connector import BaseElasticConnector
import logging
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

class DocumentManager(BaseElasticConnector):
    def __init__(self):
        super().__init__()
 
    def create_document(self, conversation_uuid, body):

        try:
            response = self.es.index(index=self.es_index, id=conversation_uuid, body=body)
            logging.info(f"Document {conversation_uuid} created successfully. Response: {response}")

        except Exception as e:
            error_msg = f"Failed to create document {conversation_uuid}: {str(e)}"
            logging.error(error_msg)
            if conversation_uuid:
                self.log_error(conversation_uuid, error_msg)
            raise

    def update_document(self, conversation_uuid, script, upsert_body=None):
        try:
            response = self.es.update(
                index=self.es_index, 
                id=conversation_uuid, 
                body={
                    "script": script,
                    "upsert": upsert_body
                }
            )
            logging.info(f"Document {conversation_uuid} updated successfully. Response: {response}")
        except Exception as e:
            error_msg = f"Failed to update document {conversation_uuid}: {str(e)}"
            logging.error(error_msg)
            self.log_error(conversation_uuid, error_msg)
            raise

    def document_exists(self, conversation_uuid):

        try:
            return self.es.exists(index=self.es_index, id=conversation_uuid)
            
        except Exception as e:
            error_msg = f"Failed to check if document {conversation_uuid} exists: {str(e)}"
            logging.error(error_msg)
            self.log_error(conversation_uuid, error_msg)
            raise

    def log_error(self, conversation_uuid, error_message):
        if not conversation_uuid:
            logging.error("Conversation UUID not provided for logging error.")
            return
        
        script = {
            "source": "if (ctx._source.debug_stack == null) { ctx._source.debug_stack = []; } ctx._source.debug_stack.add(params.error);",
            "lang": "painless",
            "params": {
                "error": {
                    "timestamp": datetime.now().isoformat(),
                    "message": error_message
                }
            }
        }
        try:
            self.es.update(index=self.es_index, id=conversation_uuid, body={"script": script})
            logging.info("Error logged to Elasticsearch for conversation UUID %s", conversation_uuid)
        except Exception as ex:
            error_msg = logging.error("Failed to log error to Elasticsearch for conversation UUID %s: %s", conversation_uuid, ex)
            self.log_error(conversation_uuid, error_msg)
            raise RuntimeError("Failed to log error to Elasticsearch: %s" % ex) from ex
