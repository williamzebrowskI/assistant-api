#!/bin/sh

# Set the PYTHONPATH
export PYTHONPATH=/usr/src/app

# Set Elasticsearch enabled/disabled
export ELASTICSEARCH_ENABLED=false  # or false to disable

# Train the model
# echo "Training model..."
# poetry run python /usr/src/app/managers/google/nlp/nn_trainer.py

# Start the server
echo "Starting server..."
exec poetry run gunicorn --config ws/gunicorn_config.py --worker-class eventlet -w 1 app.main:app_instance -b 0.0.0.0:8002