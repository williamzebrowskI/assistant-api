# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    python3 -m venv /opt/poetry && \
    /opt/poetry/bin/pip install poetry && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Copy the current directory contents
COPY . ./

# Install dependencies
RUN poetry install

# Ensure the virtual environment's bin directory is in the PATH
ENV PATH="/usr/src/app/.venv/bin:$PATH"

# Make port 8000 available to the world outside this container
EXPOSE 8002

# Run app.py when the container launches
CMD ["gunicorn", "--config", "/usr/src/app/ws/gunicorn_config.py", "--worker-class", "eventlet", "-w", "1", "app.main:app_instance", "-b", "0.0.0.0:8002"]