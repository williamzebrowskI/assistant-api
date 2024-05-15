# Purpose: Manages document CRUD operations in Elasticsearch that are generic and not specifically tied to conversations alone.
# Contents: Methods for creating, updating, and checking documents.

from managers.elastic.es_connector.elastic_connect import BaseElasticConnector
from managers.elastic.logger.error_log import ErrorLogger
import logging

class DocumentManager(BaseElasticConnector):
    def __init__(self):
        super().__init__()
        self.error_logger = ErrorLogger()
 
    def create_document(self, conversation_uuid, body):

        try:
            response = self.es.index(index=self.es_index, id=conversation_uuid, body=body)
            logging.info(f"Document {conversation_uuid} created successfully. Response: {response}")

        except Exception as e:
            error_msg = f"Failed to create document {conversation_uuid}: {str(e)}"
            logging.error(error_msg)
            if conversation_uuid:
                self.error_logger.log_error(conversation_uuid, error_msg)
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
            self.error_logger.log_error(conversation_uuid, error_msg)
            raise

    def document_exists(self, conversation_uuid):
        try:
            return self.es.exists(index=self.es_index, id=conversation_uuid)
        except Exception as e:
            error_msg = f"Failed to check if document {conversation_uuid} exists: {str(e)}"
            logging.error(error_msg)
            self.error_logger.log_error(conversation_uuid, error_msg)
            raise
