# Purpose: Establishes connection to Elasticsearch and contains the BaseElasticConnector class which includes basic connection setup and error logging specific to Elasticsearch operations.
# Contents: Initialization of the Elasticsearch client, log_error method.  

import os
import logging
from elasticsearch import Elasticsearch
from ws.flask_config import config

class BaseElasticConnector:
    def __init__(self):
        self.es_host = os.environ.get('ES_HOST', 'elasticsearch')
        self.es_port = os.environ.get('ES_PORT', '9200')
        self.es_username = os.environ.get('ES_USERNAME', 'elastic')
        self.es_index = os.environ.get('ES_INDEX', 'ai-index')
        self.es_password = os.environ.get('ES_PASSWORD')

        if not self.es_password:
            raise ValueError("Elasticsearch password not found in environment variables")

        try:
            self.es = Elasticsearch(
                f"http://{self.es_host}:{self.es_port}",
                basic_auth=(self.es_username, self.es_password),
                verify_certs=False,
            )

        except Exception as e:
            logging.error(f"Failed to connect to Elasticsearch: {e}")
            raise SystemExit(f"Connection to Elasticsearch failed: {e}")