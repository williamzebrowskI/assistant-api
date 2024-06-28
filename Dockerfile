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

# Copy and set permissions for the startup script
RUN chmod +x ./start.sh

EXPOSE 8002

CMD ["./start.sh"]