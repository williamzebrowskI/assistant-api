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
        self.es_username = config.config.ES_USERNAME
        self.es_index = config.config.ES_INDEX
        self.es_password = config.config.ES_PASSWORD

        try: 
            self.es = Elasticsearch(
               "https://elasticsearch:9200",
                basic_auth=(self.es_username, self.es_password),
                verify_certs=False,
                ssl_show_warn=False
            )
                        # Check if the connection is successful
            if self.es.ping():
                print("Successfully connected to Elasticsearch!")
                logging.info("Successfully connected to Elasticsearch!")
            else:
                print("Connected to Elasticsearch, but ping failed.")
                logging.warning("Connected to Elasticsearch, but ping failed.")
            
            # Optionally, you can print more information about the cluster
            info = self.es.info()
            print(f"Elasticsearch cluster name: {info['cluster_name']}")
            print(f"Elasticsearch version: {info['version']['number']}")

        except Exception as e:
            logging.error("Failed to connect to Elasticsearch: %s", e)
            raise SystemExit("Connection to Elasticsearch failed: %s" % e)
