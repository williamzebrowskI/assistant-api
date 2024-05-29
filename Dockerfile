# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install curl and other dependencies
RUN apt-get update && apt-get install -y curl

# Install Poetry
ENV POETRY_HOME=/opt/poetry
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.create false

# Copy the current directory contents
COPY . ./

# Install dependencies using Poetry
RUN poetry install --only main

RUN poetry run pip list

RUN poetry run which gunicorn

# Debug: Check if gunicorn is in the PATH after installation
RUN which gunicorn || echo "Gunicorn not found in PATH"

# Make port 8002 available to the world outside this container
EXPOSE 8002

CMD ["poetry", "run", "gunicorn", "--config", "ws/gunicorn_config.py", "--worker-class", "eventlet", "-w", "1", "app.main:app_instance", "-b", "0.0.0.0:8002"]

# Run app.py when the container launches
# CMD ["gunicorn", "--config", "ws/gunicorn_config.py", "--worker-class", "eventlet", "-w", "1", "app.main:app_instance", "-b", "0.0.0.0:8002"]