from datetime import datetime
from dataclasses import dataclass, asdict, field
import uuid

@dataclass
class User:
    client_ip: str
    session_id: str
    user_id: str
    url: str
    user_query: str
    index: int = None
    referral_url: str = None
    intent_data: dict = field(default_factory=dict) 

    @classmethod
    def from_message_data(cls, msg_data, index=None, intent=None, confidence=None):
        intent_data = {
            "intent": intent,
            "confidence": confidence
        }
        return cls(
            client_ip=msg_data.client_ip,
            session_id=msg_data.session_id_ga,
            user_id=msg_data.user_id,
            url=msg_data.page_url,
            user_query=msg_data.user_input,
            index=index,
            referral_url=msg_data.referral_url,
            intent_data=intent_data
        )

@dataclass
class AssistantResponse:
    assistant_id: str = None
    thread_id: str = None
    assistant_response: str = None
    assistant_type: str = 'openAI'
    start_respond_timestamp: str = None
    end_respond_timestamp: str = None
    index: int = None
    feedback: dict = field(default_factory=lambda: {
        "feedback_num": 0,
        "feedback_timestamp": datetime.now().isoformat()
    })

@dataclass
class Conversation:
    conversation_id: str
    initial_session_id: str
    initial_user_id: str
    assistant_type: str
    partner_id: str
    title: str
    start_timestamp: str = datetime.now().isoformat()
    last_updated_timestamp: str = start_timestamp
    debug_stack: list = None
    turns: list = None

@dataclass
class Turn:
    turn_id: str
    conversation_id: str
    turn_timestamp: str
    user: dict
    assistant: dict
    index: int

    @classmethod
    def from_user_and_assistant(cls, user, assistant, conversation_id, index):
        return cls(
            turn_id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            turn_timestamp=datetime.now().isoformat(),
            user=asdict(user),
            assistant=asdict(assistant),
            index=index
        )

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
                "turn": asdict(self),
                "last_updated_timestamp": datetime.now().isoformat()
            }
        }