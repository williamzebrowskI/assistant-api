from os import getenv
getenv('PYTHONDONTWRITEBYTECODE', '1')
from openai import OpenAI
from app.ws.flask_config import config
from app.managers.openai.managers.thread_manager import ThreadManager
from app.managers.openai.managers.assistant_manager import OpenAIAssistant
from app.managers.elastic.convo_managers.conversation_managers import ConversationManager
from app.managers.elastic.es_connector.elastic_connect import BaseElasticConnector  
from dotenv import load_dotenv
load_dotenv()

# Set up OpenAI API client
client = OpenAI()
OpenAI.api_key = config.config.OPENAI_API_KEY
ASSISTANT_ID = config.config.ASSISTANT_ID

#Set up Managers
elastic_connector = BaseElasticConnector()
elastic_manager = ConversationManager()
thread_manager = ThreadManager(client=client)
assistant = OpenAIAssistant(assistant_id=ASSISTANT_ID)

# Set up assistant_id
assistant_id = assistant.assistant_id

# Set up Flask app
app_instance = config.app

from app.routes import chat_routes

