from os import getenv
getenv('PYTHONDONTWRITEBYTECODE', '1')
from openai import OpenAI
from ws.flask_config import config
import logging
from managers.openai.managers.thread_manager import ThreadManager
from managers.openai.managers.assistant_manager import OpenAIAssistant
from managers.elastic.convo_managers.conversation_managers import ConversationManager
from dotenv import load_dotenv
load_dotenv()

# Set up OpenAI API client
client = OpenAI()
OpenAI.api_key = config.config.OPENAI_API_KEY
ASSISTANT_ID = config.config.ASSISTANT_ID

#Set up Managers
elastic_manager = ConversationManager()
thread_manager = ThreadManager(client=client)
assistant = OpenAIAssistant(assistant_id=ASSISTANT_ID)

# Set up assistant_id
assistant_id = assistant.assistant_id

# Set up Flask app
app_instance = config.app

from app.routes import chat_routes

