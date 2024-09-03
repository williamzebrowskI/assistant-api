from datetime import datetime
from dataclasses import dataclass, asdict, field

@dataclass
class User:
    user_id: str
    user_query: str
    index: int = None

    @classmethod
    def from_message_data(cls, msg_data, index=None):
        return cls(
            user_id=msg_data.user_id,
            user_query=msg_data.user_input,
            index=index,
        )

@dataclass
class AssistantResponse:
    assistant_id: str = None
    thread_id: str = None
    assistant_response: str = None
    index: int = None
    feedback: dict = field(default_factory=lambda: {
        "feedback_num": 0,
        "feedback_timestamp": datetime.now().isoformat()
    })

@dataclass
class Conversation:
    conversation_id: str
    user_id: str
    turns: list = None

@dataclass
class Turn:
    conversation_id: str
    user: dict
    assistant: dict
    index: int

    @classmethod
    def from_user_and_assistant(cls, user, assistant, conversation_id, index):
        return cls(
            conversation_id=conversation_id,
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
            """,
            "lang": "painless",
            "params": {
                "turn": asdict(self),
            }
        }