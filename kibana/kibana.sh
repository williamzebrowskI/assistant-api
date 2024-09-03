#!/bin/sh

# Start Kibana
/usr/local/bin/kibana-docker &

# Display link to Kibana
echo "\n\033[0;34mKibana is available at: \033[4;34mhttp://localhost:5601\033[0m"

# Keep the container running
tail -f /dev/null