# FAFSA Assistant API

This repository contains the code for `fafsa-chatgpt-assistant`, a tool designed to connect with our Assistant API for FAFSA-related queries.

## Getting Started

### Prerequisites

- Python 3.9
- pip

### Setting Up a Virtual Environment

1. **Clone this repository:**
    ```bash
    git clone https://github.com/BenefitsDataTrust/fafsa-chatgpt-assistant.git
    cd fafsa-chatgpt-assistant
    ```

2. **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```

3. **Activate the virtual environment:**
    - On Windows:
        ```bash
            .\venv\Scripts\activate
        ```
    - On MacOS/Linux:
        ```bash
            source venv/bin/activate
        ```

4. **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

Create a `.env` file in the root of your project and fill it with your OpenAI and Elasticsearch credentials:

    OPENAI_API_KEY=your_openai_api_key_here

    # Elasticsearch cloud authentication credentials
    es_url=your_elasticsearch_url_here
    es_port=your_elasticsearch_port_here
    es_index=your_elasticsearch_index_name_here
    es_api_key=your_elasticsearch_api_key_here

Ensure you replace the placeholder values with your actual credentials.

### Running the Application

1. **Start the FastAPI server:**
    Run the following command in your terminal where your virtual environment is activated:
    ```bash
    python app.py
    ```
    Wait for the FastAPI server to start up. You should see a message indicating the server is running, usually on `http://127.0.0.1:8000`.

2. **Accessing the Chat Interface:**
    Once the server is up and running, open the `HTML.index` file in a web browser to see the chat interface. This file should be located in your project directory. If you're using an IDE that supports live previews, you can also use that feature to open the file.

    Interact with the chat interface to send queries to our Wyatt ChatGPT Assistant and receive responses.


# FAFSA ChatGPT Assistant Overview

The FAFSA ChatGPT Assistant is designed to facilitate interactions with users seeking guidance on FAFSA processes via a ChatGPT-powered conversational interface. This assistant leverages the OpenAI API for generating responses and Elasticsearch for logging and retrieving conversation histories.

## Key Components

### FastAPI Setup

- **FastAPI Application**: Initiates a FastAPI server, enabling HTTP requests handling for the chat interface.
- **CORS Middleware**: Configures Cross-Origin Resource Sharing (CORS) settings to allow web requests from different origins, ensuring the frontend can communicate with the backend.

### OpenAI Integration

- **API Key Retrieval**: Fetches the OpenAI API key from environment variables, necessary for authenticating requests to OpenAI.
- **Assistant Management**: Handles the creation of threads and messages within the OpenAI environment, facilitating the conversation flow with the ChatGPT model.

### Elasticsearch Connector

- **Elasticsearch Configuration**: Establishes a connection to an Elasticsearch cluster using credentials from environment variables, allowing for asynchronous data operations.
- **Conversation Indexing**: Provides functionalities to index new conversation threads and update existing ones with user queries and assistant responses.

### Conversational Flow

1. **Thread Creation**: Generates a unique thread for new conversations or appends messages to existing threads based on the presence of a `thread_id`.
2. **Message Handling**: Manages sending user queries to the OpenAI Assistant and retrieving responses.
3. **Elasticsearch Logging**: Stores each conversation in Elasticsearch, including timestamps, thread IDs, and the exchange of messages, for historical reference and analysis.

### Running the Assistant

- Execute `python app.py` to start the FastAPI server.
- Access the chat interface through the provided HTML frontend to interact with the assistant.

## Environment Configuration

Includes a `.env` file setup for securely managing API keys and Elasticsearch connection details, crucial for operational integrity and data security.

## Logging and Debugging

Utilizes Python's logging module to track application events, aiding in monitoring and troubleshooting.

---

This assistant exemplifies a modern approach to building conversational AI applications, emphasizing modularity, scalability, and ease of integration with advanced NLP models and database technologies.
