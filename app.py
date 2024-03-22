import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from elastic_connector import ElasticConnector
from pydantic import BaseModel, UUID4
from typing import Optional
from functools import partial
import openai
from dotenv import load_dotenv
import os
from datetime import datetime
import logging
import sys
load_dotenv()

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

api_key = os.environ.get('OPENAI_API_KEY', 'unassigned_openai_api_key')

openai.api_key = api_key

if api_key == 'unassigned_openai_api_key':
    logging.warning('OPENAI_API_KEY is not set.')


app = FastAPI(title="OpenAI Assistant API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://benefitsdatatrust.github.io",
    "http://localhost",
    "http://0.0.0.0:8002"],
    #allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "HEAD", "OPTIONS"],
    allow_headers=["Access-Control-Allow-Headers", 'Content-Type', 'Authorization', 'Access-Control-Allow-Origin'],
)

ASSISTANT_ID = os.environ.get('ASSISTANT_ID', 'unassigned_assistant_id')
if ASSISTANT_ID == 'unassigned_assistant_id':
    logging.warning('ASSISTANT_ID is not set.')

class Query(BaseModel):
    question: str
    thread_id: Optional[str] = None
    conversation_uuid: Optional[str] = None
    user_id: Optional[str] = None

class OpenAIAssistant:
    def __init__(self, assistant_id):
        """
        Initializes the OpenAIAssistant instance.

        Args:
            assistant_id (str): The unique identifier for the OpenAI Assistant.
        """
        self.assistant_id = assistant_id
        self.client = openai
        self.elastic_connector = ElasticConnector()

    async def create_thread(self, query):
        """
        Asynchronously creates a new thread in the OpenAI Assistant.
        Args:
            query (str): The user's query to initialize the thread with.
        
        Returns:
            str: The ID of the created thread.
        """
        loop = asyncio.get_event_loop()
        thread_create = partial(self.client.beta.threads.create, messages=[{"role": "user", "content": query}])
        thread = await loop.run_in_executor(None, thread_create)
        return thread.id

    async def add_message_to_thread(self, query, thread_id):
        """
        Asynchronously adds a message from the user to an existing thread.

        Args:
            query (str): The user's query to add to the thread.
            thread_id (str): The ID of the thread to add the message to.
        
        Returns:
            str: The ID of the created message.
        """
        loop = asyncio.get_event_loop()
        message_create = partial(self.client.beta.threads.messages.create, thread_id=thread_id, role="user", content=query)
        message = await loop.run_in_executor(None, message_create)
        return message.id

    async def run_thread(self, thread_id):
        """
        Asynchronously runs the assistant on the specified thread, generating a response.

        Args:
            assistant_id (str): The ID of the assistant to run on the thread.
            thread_id (str): The ID of the thread to run the assistant on.
        
        Returns:
            object: The run object created by executing the assistant on the thread.
        """
        loop = asyncio.get_event_loop()
        run_create = partial(self.client.beta.threads.runs.create, thread_id=thread_id, assistant_id=self.assistant_id)
        run = await loop.run_in_executor(None, run_create)
        return run

    async def check_run_status(self, thread_id, run_id):
        """
        Asynchronously checks the status of a run on a thread.
        Args:
            thread_id (str): The ID of the thread.
            run_id (str): The ID of the run to check the status of.
        
        Returns:
            object: The status of the run.
        """
       
        loop = asyncio.get_event_loop()
        run_retrieve = partial(self.client.beta.threads.runs.retrieve, thread_id=thread_id, run_id=run_id)
        run_status = await loop.run_in_executor(None, run_retrieve)
        return run_status

    async def query_assistant(self, query, thread_id=None, conversation_uuid=None, user_id=None, client_ip=None):
        """
        Asynchronously queries the assistant, managing thread creation, message addition, and response generation.

        Args:
            conversation_uuid (str): The unique identifier for the conversation.
            query (str): The user's query to process.
            thread_id (Optional[str]): The ID of an existing thread to add the query to, if any.
        
        Returns:
            tuple: A tuple containing the assistant's response, the thread ID, and the message ID.
        """

        loop = asyncio.get_event_loop()
        message_id = None

        # If no thread exists, create a new one and log it to Elasticsearch
        if thread_id is None:
            thread_id = await self.create_thread(query)
            doc = {"user_id": f"{user_id}", "client_ip": client_ip, "thread_id": f"{thread_id}", "timestamp": datetime.now(), "conversations": {}}
            await self.elastic_connector.push_to_index(conversation_uuid, doc)
        else:
            # If a thread exists, add the user's message to it
            message_id = await self.add_message_to_thread(query, thread_id)

         # Run the assistant on the thread to generate a response
        run = await self.run_thread(thread_id)
        
        # Keep checking the status of the run until it is completed 
        run_status = await self.check_run_status(thread_id, run.id)
        while run_status.status != "completed":
            run_status = await self.check_run_status(thread_id, run.id)

        # Retrieve the latest message from the assistant
        messages_response = await loop.run_in_executor(None, partial(self.client.beta.threads.messages.list, thread_id=thread_id))
        messages = messages_response.data
        latest_message = messages[0]

        # Log the query and response pair to the Elasticsearch record
        doc = {"conversations": {f'User: {query}': f'Wyatt: {latest_message.content[0].text.value}'}}
        await self.elastic_connector.update_document(conversation_uuid, doc)

        return latest_message.content[0].text.value, thread_id, message_id, conversation_uuid

assistant = OpenAIAssistant(assistant_id=ASSISTANT_ID)

# API
@app.post("/query/", response_model=dict)
async def query_openai(request: Request, query: Query):
    client_ip = request.client.host
    try:
        response, thread_id, message_id, conversation_uuid = await assistant.query_assistant(query.question, query.thread_id, query.conversation_uuid, query.user_id, client_ip=client_ip)
        return {
            "response": response, 
            "thread_id": thread_id,
            "message_id": message_id,
            "conversation_uuid": conversation_uuid,
            "user_id": query.user_id, 
            "question": query.question,
            "client_ip": client_ip
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8002, reload=True)
