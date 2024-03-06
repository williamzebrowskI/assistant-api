import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from functools import partial
import openai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise Exception("OPENAI_API_KEY not found in environment variables")

openai.api_key = api_key

app = FastAPI(title="OpenAI Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ASSISTANT_ID = 'asst_YZD96qZjXi3mFBahDoQgDN1I'

class Query(BaseModel):
    question: str
    thread_id: Optional[str] = None

class OpenAIAssistant:
    def __init__(self, assistant_id):
        self.assistant_id = assistant_id
        self.client = openai

    async def query_assistant(self, query, thread_id=None):
        loop = asyncio.get_event_loop()
        message_id = None

        if thread_id is None:
            thread_create = partial(self.client.beta.threads.create, messages=[{"role": "user", "content": query}])
            thread = await loop.run_in_executor(None, thread_create)
            thread_id = thread.id

        else:
            message_create = partial(self.client.beta.threads.messages.create, thread_id=thread_id, role="user", content=query)
            message = await loop.run_in_executor(None, message_create)
            message_id = message.id

        run_create = partial(self.client.beta.threads.runs.create, thread_id=thread_id, assistant_id=self.assistant_id)
        run = await loop.run_in_executor(None, run_create)

        run_retrieve = partial(self.client.beta.threads.runs.retrieve, thread_id=thread_id, run_id=run.id)
        run_status = await loop.run_in_executor(None, run_retrieve)

        while run_status.status != "completed":
            await asyncio.sleep(1)
            run_status = await loop.run_in_executor(None, run_retrieve)

        messages_response = await loop.run_in_executor(None, partial(self.client.beta.threads.messages.list, thread_id=thread_id))
        messages = messages_response.data

        latest_message = messages[0]
        return latest_message.content[0].text.value, thread_id, message_id
    

assistant = OpenAIAssistant(assistant_id=ASSISTANT_ID)

@app.post("/query/", response_model=dict)
async def query_openai(query: Query):
    try:
        response, thread_id, message_id = await assistant.query_assistant(query.question, query.thread_id)
        return {
            "response": response, 
            "thread_id": thread_id,
            "message_id": message_id  # Include message_id in the response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
