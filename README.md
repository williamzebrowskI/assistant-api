# Assistant-api

The `fafsa-chatgpt-assistant` repository hosts the cutting-edge Assistants API designed to streamline FAFSA-related inquiries through a ChatGPT-powered conversational interface. It combines the prowess of OpenAI's GPT model with Elasticsearch's data indexing for an intuitive and efficient user experience.

## Table of Contents
- [Diagram Depiction](#diagram-depiction)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Setting Up a Virtual Environment](#setting-up-a-virtual-environment)
  - [Configuration](#configuration)
  - [Running the Application](#running-the-application)
- [FAFSA ChatGPT Assistant Overview](#fafsa-chatgpt-assistant-overview)
- [Key Components](#key-components)
  - [FastAPI Setup](#fastapi-setup)
  - [OpenAI Integration](#openai-integration)
  - [Elasticsearch Connector](#elasticsearch-connector)
  - [Conversational Flow](#conversational-flow)
- [Running the Assistant](#running-the-assistant)
- [Environment Configuration](#environment-configuration)
- [Logging and Debugging](#logging-and-debugging)

The following Diagram depicts the flow of a user's message from end to end.
![FAFSA Assistant API Diagram](images/flow.png)

## Getting Started

### Prerequisites

- Python 3.9
- pip

### Setting Up a Virtual Environment

1. **Clone this repository:**
    ```bash
    git clone https://github.com/williamzebrowskI/assistant-api.git
    cd assistant-api
    ```

2. **Create a `.env` File**:
    Create a `.env` file in the root of your project and fill it with your OpenAI and Elasticsearch credentials:

    ```
    OPENAI_API_KEY=your_openai_api_key_here
    ASSISTANT_ID=your_assistants_id_here
    # Elasticsearch cloud authentication credentials
    ES_URL=your_elasticsearch_url_here
    ES_PORT=your_elasticsearch_port_here
    ES_INDEX=your_elasticsearch_index_name_here
    ES_API_KEY=your_elasticsearch_api_key_here
    CORS_ALLOWED_ORIGINS="http://127.0.0.1:8002"
    ```

    Ensure you replace the placeholder values with your actual credentials.

### Running the Application

1. **Build the Docker Image**:
    Use the `--no-cache` option to ensure a fresh build:

    ```bash
    docker build --no-cache -t open-assistant .
    ```

2. **Run the Docker Container**:

    ```bash
    docker run -p 8002:8002 openai-assistant
    ```

3. **Accessing the Chat Interface:**
    Once the server is up and running, open the `index.html` file in a web browser to see the chat interface. This file should be located in your project directory. If you're using an IDE that supports live previews, you can also use that feature to open the file.

    Interact with the chat interface to send queries to our Wyatt ChatGPT Assistant and receive responses.

## FAFSA ChatGPT Assistant Overview

The FAFSA ChatGPT Assistant is designed to facilitate interactions with users seeking guidance on FAFSA processes via a ChatGPT-powered conversational interface. This assistant leverages the OpenAI API for generating responses and Elasticsearch for logging and retrieving conversation histories.

## Key Components

### FastAPI Setup

- **FastAPI Application**: Initiates a FastAPI server, enabling HTTP requests handling for the chat interface.
- **CORS Middleware**: Configures Cross-Origin Resource Sharing (CORS) settings to allow web requests from different origins, ensuring the frontend can communicate with the backend.

### OpenAI Assistant Integration

#### OpenAIAssistant Class Overview

The `OpenAIAssistant` class is designed to seamlessly integrate OpenAI's GPT models into our application, enabling the generation of dynamic, intelligent responses to user queries. This integration is pivotal for facilitating an engaging conversational experience in the FAFSA ChatGPT Assistant application.

##### Purpose

The primary purpose of the `OpenAIAssistant` class is to abstract the complexities involved in communicating with the OpenAI API. It manages the lifecycle of conversations, including initiating new threads, managing ongoing conversations, and generating responses based on user input.

##### Setup

To utilize the `OpenAIAssistant`, ensure you have the following configured:

- **API Key**: Securely store the OpenAI API key in your environment variables or `.env` file. This key is required to authenticate your requests to the OpenAI API.
- **Assistant Configuration**: Define the specific GPT model (e.g., `gpt-3.5-turbo`) and settings appropriate for your application's conversational needs.

##### Key Functionalities

###### `initialize_conversation()`

- Initializes a new conversation thread with OpenAI, setting up the context and parameters for the conversation.
- Stores conversation state to facilitate seamless continuation of the conversation.

###### `generate_response(user_query)`

- Sends the user's query to OpenAI and retrieves a response based on the current conversation context.
- Utilizes advanced natural language processing and generation techniques to ensure the response is relevant, accurate, and coherent.

###### `manage_conversation_state()`

- Dynamically manages the conversation's state, including tracking the conversation history and context changes.
- Ensures that each response is contextually appropriate, maintaining a natural and logical flow to the conversation.

#### Integration Benefits

Integrating the `OpenAIAssistant` class into our application brings several key benefits:

- **Enhanced User Experience**: By leveraging OpenAI's advanced NLP capabilities, the assistant can provide users with highly relevant, informative, and engaging responses.
- **Scalability**: The modular design of the `OpenAIAssistant` allows for easy updates and modifications, such as changing the GPT model or adjusting conversation parameters, without extensive code overhauls.
- **Simplicity**: The abstraction provided by the class simplifies the process of integrating complex AI functionalities into the application, making the development process more efficient and less error-prone.

##### Conclusion

The `OpenAIAssistant` class represents a core component of our FAFSA ChatGPT Assistant application, bridging the gap between user queries and the sophisticated language understanding and generation capabilities of OpenAI's GPT models. Through this integration, we aim to deliver an exceptional conversational experience that aids users in navigating the complexities of the FAFSA process.


# Elasticsearch Connector

## Elastic Data Model Integration

This documentation outlines the setup and usage of the Elastic Data Model within our AssistantAPI application. Our model leverages Elasticsearch for operations such as document creation, updates, and management within an Elasticsearch index. The integration is facilitated through the `ElasticConnector` class, which establishes a connection to Elasticsearch using environmental variables and provides asynchronous methods for interacting with the data.

## Setup

### Environment Variables

Before utilizing the `ElasticConnector`, ensure the following environmental variables are set in your environment or within a `.env` file:

- `ES_URL`: The URL of your Elasticsearch instance.
- `ES_INDEX`: The Elasticsearch index to which documents will be pushed and from which they will be retrieved.
- `ES_PORT`: The port on which your Elasticsearch instance is running.
- `ES_API_KEY`: The API key for authenticating with your Elasticsearch instance.

These variables are critical for establishing a connection to Elasticsearch. The connector will log warnings if any of these are unset.

## ElasticConnector Class

### Initialization

Upon instantiation, the `ElasticConnector` class initializes a connection to an Elasticsearch instance using the aforementioned environmental variables. This connection is essential for performing asynchronous operations against the Elasticsearch index.

### Methods

#### async push_to_index(conversation_uuid, user_id, client_ip, thread_id, assistant_id)

This asynchronous method creates a new conversation document in Elasticsearch. The document includes metadata such as the user's ID, the client's IP address, the thread's ID, the assistant's ID, and a timestamp marking the creation time. This setup initializes an empty list for conversations to hold future interactions.

**Parameters:**

- `conversation_uuid` (str): Unique identifier for the conversation document.
- `user_id` (str): ID of the user initiating the conversation.
- `client_ip` (str): IP address of the client.
- `thread_id` (str): Unique identifier of the thread associated with the conversation.
- `assistant_id` (str): ID of the assistant involved in the conversation.

#### async update_document(conversation_uuid, user_query, assistant_response)

This method appends a new interaction to the conversations array of an existing document. Each interaction consists of a user query and the corresponding assistant response, allowing for the historical tracking of interactions within a conversation.

**Parameters:**

- `conversation_uuid` (str): Unique identifier for the conversation document.
- `user_query` (str): The query submitted by the user.
- `assistant_response` (str): The response generated by the assistant.

Both methods handle exceptions gracefully by logging errors, ensuring the application's stability in the face of Elasticsearch operation failures.

## Conclusion

The `ElasticConnector` class provides a streamlined approach to integrating Elasticsearch into your application for handling conversation data. By following the setup instructions and utilizing the provided methods, you can efficiently manage conversation documents within your chosen Elasticsearch index.



### Conversational Flow

1. **Client-Side Identification**: When the user starts a conversation, a `conversation_uuid` and `user_id` are generated to uniquely identify the session and user across interactions.
   
2. **Thread Creation**: Initiates a new conversation thread for first-time queries or appends messages to existing threads using the `thread_id`.
   
3. **Message Handling**: Manages the exchange of messages between the user and the OpenAI Assistant, maintaining the context and continuity of the conversation.
   
4. **Elasticsearch Logging**: Archives each conversation in Elasticsearch, tagging them with `conversation_uuid` and `user_id` to construct a detailed history for analysis and continued dialogue.

### Running the Assistant

- Execute `python app.py` to start the FastAPI server.
- Access the chat interface through the provided HTML frontend to interact with the assistant.

## Environment Configuration

Includes a `.env` file setup for securely managing API keys and Elasticsearch connection details, crucial for operational integrity and data security.

## Logging and Debugging

Utilizes Python's logging module to track application events, aiding in monitoring and troubleshooting.

---

This assistant exemplifies a modern approach to building conversational AI applications, emphasizing modularity, scalability, and ease of integration with advanced NLP models and database technologies.
