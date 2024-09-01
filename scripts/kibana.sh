#!/bin/sh

# Start Kibana
/usr/local/bin/kibana-docker &

# Wait until Kibana is available
until curl -s http://localhost:5601 >/dev/null; do
    sleep 1
done

echo "\n\033[0;34mKibana is available at: \033[4;34mhttp://localhost:5601\033[0m"

# Keep the container running
tail -f /dev/null