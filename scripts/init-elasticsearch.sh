#!/bin/bash
echo 'Starting Elasticsearch...'
bin/elasticsearch -d


echo 'Checking for password...'
if [ ! -f /tmp/es_output.txt ]; then
    echo 'Running password reset'
    echo y | bin/elasticsearch-reset-password -u elastic | tee /tmp/es_output.txt
fi
PASSWORD=$(grep -oP '(?<=New value: ).*' /tmp/es_output.txt)
if [ -z "$PASSWORD" ]; then
    echo 'Error: Password not extracted correctly. Exiting.'
    exit 1
fi
echo "Extracted Elasticsearch password: '$PASSWORD'"

echo 'Checking for existing custom index...'
# Check if our custom index exists
if curl -s -f -o /dev/null "http://localhost:9200/ai-index" -u "elastic:$PASSWORD" -k; then
    echo 'Custom index already exists. Skipping index creation.'
else
    echo 'Custom index not found. Creating Elasticsearch index...'
    curl -X PUT 'http://localhost:9200/ai-index' -H 'Content-Type: application/json' -u "elastic:$PASSWORD" -d '{
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }'
    echo 'Custom index created.'
fi

echo 'Elasticsearch setup complete. Switching to foreground mode...'
exec bin/elasticsearch