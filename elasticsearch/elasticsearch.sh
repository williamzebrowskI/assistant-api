#!/bin/bash
echo 'Starting Elasticsearch...'
bin/elasticsearch -d


# echo 'Checking for password...'
if [ ! -f /tmp/es_output.txt ]; then
    echo 'Running password reset'
    echo y | bin/elasticsearch-reset-password -u elastic | tee /tmp/es_output.txt
fi
PASSWORD=$(grep -oP '(?<=New value: ).*' /tmp/es_output.txt)
if [ -z "$PASSWORD" ]; then
    echo 'Error: Password not extracted correctly. Exiting.'
    exit 1
fi

# Create a service account token for Kibana
echo 'Creating service account token for Kibana...'
SERVICE_TOKEN=$(bin/elasticsearch-service-tokens create elastic/kibana kibana-token | grep -oP '(?<=SERVICE_TOKEN elastic/kibana/kibana-token = ).*')
if [ -z "$SERVICE_TOKEN" ]; then
    echo 'Error: Service account token not created correctly. Exiting.'
    exit 1
fi

# Save the service token to a file
echo "$SERVICE_TOKEN" > /tmp/kibana_service_token.txt

# Clean up everything except the current Elasticsearch directory and the es_output.txt file
ES_CONFIG_DIR="/tmp"
CURRENT_BUILD_ID=$(basename "$(ls -d ${ES_CONFIG_DIR}/elasticsearch-* | head -n 1)")

for DIR in ${ES_CONFIG_DIR}/elasticsearch-*; do
    if [ "$(basename "$DIR")" != "$CURRENT_BUILD_ID" ]; then
        echo "Deleting old build directory: $DIR"
        rm -rf "$DIR"
    fi
done

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

touch /tmp/kibana-start.marker

echo 'Elasticsearch setup complete. 🚀'
exec bin/elasticsearch