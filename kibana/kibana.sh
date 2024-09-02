#!/bin/sh

# Path to the shared volume where the marker file is stored
ES_CONFIG_DIR="/app/es_config"
MARKER_FILE="$ES_CONFIG_DIR/kibana-start.marker"
PASSWORD_FILE="$ES_CONFIG_DIR/es_output.txt"
SERVICE_TOKEN_FILE="$ES_CONFIG_DIR/kibana_service_token.txt"

# Wait until the marker file is detected
while [ ! -f "$MARKER_FILE" ]; do
    sleep 1
done

rm -f "$MARKER_FILE"

# Read the service token from the file
if [ -f "$SERVICE_TOKEN_FILE" ]; then
    export ELASTICSEARCH_SERVICE_TOKEN=$(cat "$SERVICE_TOKEN_FILE")
    echo "Elasticsearch service token extracted and exported."
else
    echo "Error: Service token file not found. Ensure the token creation process completed successfully."
    exit 1
fi

# Extract the password from the file
if [ -f "$PASSWORD_FILE" ]; then
    export ELASTIC_PASSWORD=$(grep -oP '(?<=New value: ).*' "$PASSWORD_FILE")
else
    echo "Error: Password file not found. Ensure the password reset process completed successfully."
    exit 1
fi


# Start Kibana
/usr/local/bin/kibana-docker &

# Wait until Kibana is available
until curl -s http://localhost:5601 >/dev/null; do
    sleep 1
done

echo "\n\033[0;34mKibana is available at: \033[4;34mhttp://localhost:5601\033[0m"
echo "username: elastic"
echo "password: $ELASTIC_PASSWORD"

touch $ES_CONFIG_DIR/assistant-start.marker

rm -f "$MARKER_FILE"

# Keep the container running
tail -f /dev/null