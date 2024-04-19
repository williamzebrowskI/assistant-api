from datetime import datetime
import uuid

# Purpose: Defines data models (User, AssistantResponse, Conversation, Turn) used in Elasticsearch documents.
# Contents: Class definitions for each model type, used throughout the project to maintain data structure.

class User:
    def __init__(self, client_ip, session_id, user_id, url, referral_url, user_query, index=None):
        self.client_ip = client_ip
        self.session_id = session_id
        self.user_id = user_id
        self.url = url
        self.user_query = user_query
        self.index = index
        self.referral_url = referral_url
       

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
    def __init__(self, assistant_id, assistant_type, thread_id, assistant_response, start_turn_timestamp=None, start_response_timestamp = None,end_respond_timestamp=None, index=None):
        self.assistant_id = assistant_id
        self.assistant_type = assistant_type
        self.thread_id = thread_id
        self.assistant_response = assistant_response
        self.start_response_timestamp = start_response_timestamp
        self.start_turn_timestamp = start_turn_timestamp
        self.end_respond_timestamp = end_respond_timestamp
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
    def __init__(self, conversation_uuid, initial_session_id, initial_user_id, assistant_type, title):
        self.conversation_id = conversation_uuid
        self.initial_session_id = initial_session_id
        self.initial_user_id = initial_user_id
        self.assistant_type = assistant_type
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
        self.turn_timestamp = datetime.now().isoformat()
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
                "last_updated_timestamp": datetime.now().isoformat()
            }
        }


