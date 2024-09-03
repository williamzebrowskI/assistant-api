#!/bin/bash
bin/elasticsearch -d

echo 'Checking for existing custom index...'
if curl -s -f -o /dev/null "http://localhost:9200/ai-index" -u "elastic:$ELASTIC_PASSWORD" -k; then
    echo 'Custom index already exists. Skipping index creation.'
else
    echo 'Custom index not found. Creating Elasticsearch index...'
    curl -X PUT 'http://localhost:9200/ai-index' -H 'Content-Type: application/json' -u "elastic:$ELASTIC_PASSWORD" -d '{
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }'
    echo 'Custom index created.'
fi

touch /tmp/assistant-start.marker

echo 'Elasticsearch setup complete. 🚀'
exec bin/elasticsearch