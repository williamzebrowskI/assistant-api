import os
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
from openai import OpenAI
from ws.flask_config import config
from managers.openai.thread_manager import ThreadManager
from managers.openai.assistant_manager import OpenAIAssistant
from managers.elastic.conversation_manager import ConversationManager
from dotenv import load_dotenv
load_dotenv()

# Set up OpenAI API client
client = OpenAI()
OpenAI.api_key = os.getenv('OPENAI_API_KEY')
ASSISTANT_ID = os.getenv('ASSISTANT_ID')

#Set up Managers
elastic_manager = ConversationManager()
thread_manager = ThreadManager(client=client)
assistant = OpenAIAssistant(assistant_id=ASSISTANT_ID)

# Set up assistant_id
assistant_id = assistant.assistant_id

# Set up Flask app
app_instance = config.app

from routes import chat_routes