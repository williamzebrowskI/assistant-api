#!/bin/sh

# Set the PYTHONPATH
export PYTHONPATH=/usr/src/app
export PYTHONDONTWRITEBYTECODE=1

# Set Elasticsearch enabled/disabled
export ELASTICSEARCH_ENABLED=false # false to disable Elastic

# Set the port for the Node.js server
export FE_PORT=8001

# Start the Node.js server
echo "Starting Node.js server..."
cd frontend && PORT=$FE_PORT node server.js &

# Wait a moment for the Node.js server to start
sleep 2

# Print the clickable link
echo "\n\033[0;34mChat widget is available at: \033[4;34mhttp://localhost:$FE_PORT\033[0m"

# Start the Python server
echo "Starting Python server..."
exec poetry run gunicorn --config ws/gunicorn_config.py --worker-class eventlet -w 1 app.main:app_instance -b 0.0.0.0:8002