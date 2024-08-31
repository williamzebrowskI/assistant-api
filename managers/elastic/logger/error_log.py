import logging
from datetime import datetime
import os
from managers.elastic.es_connector.elastic_connect import BaseElasticConnector

class ErrorLogger(BaseElasticConnector):
    def __init__(self):
        super().__init__()
        self.elasticsearch_enabled = os.getenv('ELASTICSEARCH_ENABLED', 'false').lower() == 'true'

    def log_error(self, conversation_uuid, error_message):
        if not self.elasticsearch_enabled:
            logging.info(f"Elasticsearch is disabled. Skipping error logging for {conversation_uuid}.")
            return
        if not conversation_uuid:
            logging.error("Conversation UUID not provided for logging error.")
            return
        
        script = {
            "source": """
                if (ctx._source.debug_stack == null) {
                    ctx._source.debug_stack = [];
                }
                ctx._source.debug_stack.add(params.error);
            """,
            "lang": "painless",
            "params": {
                "error": {
                    "timestamp": datetime.now().isoformat(),
                    "message": error_message
                }
            }
        }
        upsert_body = {
            "debug_stack": [script['params']['error']]
        }
        try:
            self.es.update(
                index=self.es_index,
                id=conversation_uuid,
                body={
                    "script": script,
                    "upsert": upsert_body
                }
            )
            logging.info(f"Error logged to Elasticsearch for conversation UUID {conversation_uuid}")
        except Exception as ex:
            logging.error(f"Failed to log error to Elasticsearch for conversation UUID {conversation_uuid}: {ex}")
            raise