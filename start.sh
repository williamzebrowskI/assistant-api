#!/bin/sh

# Set the PYTHONPATH
export PYTHONPATH=/usr/src/app

export PYTHONDONTWRITEBYTECODE=1

# Set Elasticsearch enabled/disabled
export ELASTICSEARCH_ENABLED=false  # false to disable Elastic

# Start the server
echo "Starting server..."
exec poetry run gunicorn --config ws/gunicorn_config.py --worker-class eventlet -w 1 app.main:app_instance -b 0.0.0.0:8002