# Purpose: Establishes connection to Elasticsearch and contains the BaseElasticConnector class which includes basic connection setup and error logging specific to Elasticsearch operations.
# Contents: Initialization of the Elasticsearch client, log_error method.  

import os
import logging
from elasticsearch import Elasticsearch
from utils.url_utility import UrlUtility
from ws.flask_config import config

class BaseElasticConnector:
    def __init__(self):
        self.es_url = config.config.ES_URL
        self.es_port = config.config.ES_PORT
        self.es_api_key = config.config.ES_API_KEY
        self.es_index = config.config.ES_INDEX

        try: 
            self.es = Elasticsearch(
                hosts=[UrlUtility.create_url(f"{self.es_url}:{self.es_port}")],
                api_key=self.es_api_key
            )
        except Exception as e:
            logging.error("Failed to connect to Elasticsearch: %s", e)
            raise SystemExit("Connection to Elasticsearch failed: %s" % e)
