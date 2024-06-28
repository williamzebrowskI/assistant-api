# Purpose: Manages document CRUD operations in Elasticsearch that are generic and not specifically tied to conversations alone.
# Contents: Methods for creating, updating, and checking documents.

import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager
from managers.elastic.es_connector.elastic_connect import BaseElasticConnector
from managers.elastic.logger.error_log import ErrorLogger

class DocumentManager(BaseElasticConnector):
    def __init__(self, error_logger: Optional[ErrorLogger] = None):
        super().__init__()
        self.error_logger = error_logger or ErrorLogger()

    @contextmanager
    def handle_errors(self, conversation_id: str, action: str):
        try:
            yield
        except Exception as e:
            error_msg = f"{action} for document {conversation_id}: {e}"
            logging.error(error_msg)
            self.error_logger.log_error(conversation_id, error_msg)
            raise RuntimeError(error_msg) from e

    def create_document(self, conversation_id: str, body: Dict[str, Any]) -> None:
        """
        Creates a document in Elasticsearch.

        :param conversation_id: UUID of the conversation.
        :param body: Body of the document.
        """
        with self.handle_errors(conversation_id, "Failed to create document"):
            response = self.es.index(index=self.es_index, id=conversation_id, body=body)
            logging.info(f"Document {conversation_id} created successfully. Response: {response}")

    def update_document(self, conversation_id: str, script: Dict[str, Any], upsert_body: Optional[Dict[str, Any]] = None) -> None:
        """
        Updates a document in Elasticsearch.

        :param conversation_id: UUID of the conversation.
        :param script: Script to update the document.
        :param upsert_body: Optional upsert body.
        """
        with self.handle_errors(conversation_id, "Failed to update document"):
            response = self.es.update(
                index=self.es_index, 
                id=conversation_id, 
                body={
                    "script": script,
                    "upsert": upsert_body
                }
            )
            logging.info(f"Document {conversation_id} updated successfully. Response: {response}")

    def document_exists(self, conversation_id: str) -> bool:
        """
        Checks if a document exists in Elasticsearch.

        :param conversation_id: UUID of the conversation.
        :return: True if the document exists, False otherwise.
        """
        with self.handle_errors(conversation_id, "Failed to check if document exists"):
            exists = self.es.exists(index=self.es_index, id=conversation_id)
            logging.info(f"Document {conversation_id} exists: {exists}")
            return exists