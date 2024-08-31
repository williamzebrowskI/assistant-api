# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app
    
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get install -y net-tools && \
    apt-get clean

# Verify installation of Node.js and npm
RUN node -v && npm -v

# Copy frontend package.json and package-lock.json
COPY frontend/package*.json ./frontend/

# Install Node.js dependencies
WORKDIR /usr/src/app/frontend
RUN npm install --no-optional && npm cache clean --force

# Switch back to the main directory
WORKDIR /usr/src/app

# Install Poetry
ENV POETRY_HOME=/opt/poetry
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.create false

# Copy the rest of the application
COPY . .

# Install Python dependencies using Poetry
RUN poetry install --only main

# Explicitly copy and set permissions for the startup script
COPY scripts/start.sh ./scripts/
RUN chmod +x ./scripts/start.sh

COPY scripts/init-elasticsearch.sh ./scripts/
RUN chmod +x ./scripts/init-elasticsearch.sh

# Expose ports for both Node.js and Python servers
EXPOSE 8001 8002