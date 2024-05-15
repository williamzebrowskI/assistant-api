# Purpose: Establishes connection to Elasticsearch and contains the BaseElasticConnector class which includes basic connection setup and error logging specific to Elasticsearch operations.
# Contents: Initialization of the Elasticsearch client, log_error method.  

import os
import logging
from elasticsearch import Elasticsearch
from utils.url_utility import UrlUtility

class BaseElasticConnector:
    def __init__(self):
        self.es_url = os.getenv('ES_URL', 'localhost')
        self.es_port = os.getenv('ES_PORT', 9200)
        self.es_api_key = os.getenv('ES_API_KEY')
        self.es_index = os.getenv('ES_INDEX', 'conversations')

        try: 
            self.es = Elasticsearch(
                hosts=[UrlUtility.create_url(f"{self.es_url}:{self.es_port}")],
                api_key=self.es_api_key
            )
        except Exception as e:
            logging.error("Failed to connect to Elasticsearch: %s", e)
            raise SystemExit("Connection to Elasticsearch failed: %s" % e)
