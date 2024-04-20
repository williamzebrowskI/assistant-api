from datetime import datetime
from ws.message_data import MessageData
import uuid

# Purpose: Defines data models (User, AssistantResponse, Conversation, Turn) used in Elasticsearch documents.
# Contents: Class definitions for each model type, used throughout the project to maintain data structure.

class User:
    def __init__(self, msg_data: MessageData, index=None):
        self.client_ip = msg_data.client_ip
        self.session_id = msg_data.session_id_ga
        self.user_id = msg_data.user_id
        self.url = msg_data.page_url
        self.user_query = msg_data.user_input
        self.index = index
        self.referral_url = msg_data.referral_url

    def to_dict(self):
        return {
            "index": self.index,
            "client_ip": self.client_ip,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "url": self.url,
            "referral_url": self.referral_url,
            "user_query": self.user_query,
        }

class AssistantResponse:
    def __init__(self, index=None, **kwargs):
        self.assistant_id = kwargs.get('assistant_id')
        self.thread_id = kwargs.get('thread_id')
        self.assistant_response = kwargs.get('assistant_response')
        self.assistant_type = kwargs.get('assistant_type', 'openAI')
        self.start_turn_timestamp = kwargs.get('start_turn_timestamp')
        self.start_response_timestamp = kwargs.get('start_response_timestamp')
        self.end_respond_timestamp = kwargs.get('end_respond_timestamp')
        self.index = index

    def to_dict(self):
        return {
            "start_turn_timestamp": self.start_turn_timestamp,
            "index": self.index,
            "assistant_id": self.assistant_id,
            "assistant_type": self.assistant_type,
            "thread_id": self.thread_id,
            "assistant_response": self.assistant_response,
            "start_respond_timestamp": self.start_response_timestamp,
            "end_respond_timestamp": self.end_respond_timestamp,
            "feedback": {
                "feedback_num": 0,
                "feedback_timestamp": datetime.now().isoformat()
            },
        }

class Conversation:
    def __init__(self, conversation_uuid, initial_session_id, initial_user_id, assistant_type, title, partner_id):
        self.conversation_id = conversation_uuid
        self.initial_session_id = initial_session_id
        self.initial_user_id = initial_user_id
        self.assistant_type = assistant_type
        self.partner_id = partner_id
        self.title = title
        self.start_timestamp = datetime.now().isoformat()
        self.last_updated_timestamp = self.start_timestamp
        self.debug_stack = []
        self.turns = []

    def to_dict(self):
        return {
            "conversation_id": self.conversation_id,
            "initial_session_id": self.initial_session_id,
            "initial_user_id": self.initial_user_id,
            "assistant_type": self.assistant_type,
            "partner_id": self.partner_id,
            "title": self.title,
            "start_timestamp": self.start_timestamp,
            "last_updated_timestamp": self.last_updated_timestamp,
            "debug_stack": self.debug_stack,
            "turns": self.turns
        }
    
class Turn:
    def __init__(self, user: User, assistant: AssistantResponse, conversation_uuid, index):
        self.turn_id = str(uuid.uuid4())
        self.conversation_uuid = conversation_uuid
        self.turn_timestamp = datetime.now()
        self.user = user.to_dict()
        self.assistant = assistant.to_dict()
        self.index = index

    def to_dict(self):
        return {
            "turn_id": self.turn_id,
            "conversation_id": self.conversation_uuid,
            "turn_timestamp": self.turn_timestamp,
            "user": self.user,
            "assistant": self.assistant,
            "index": self.index
        }

    def update_script(self):
        return {
            "source": """
                if (ctx._source.turns == null) {
                    ctx._source.turns = [];
                }
                ctx._source.turns.add(params.turn);
                ctx._source.last_updated_timestamp = params.last_updated_timestamp;
            """,
            "lang": "painless",
            "params": {
                "turn": self.to_dict(),
                "last_updated_timestamp": datetime.now()
            }
        }


