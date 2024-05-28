from openai import AssistantEventHandler
import logging
import re
from contextlib import contextmanager

class EventHandler(AssistantEventHandler):
    """
    Handles events triggered during the interaction with the OpenAI Assistant, specifically tailored for Flask-SocketIO integration. 
    This class inherits from AssistantEventHandler and extends its functionality to support real-time communication in a web application context. 
    It manages sending text updates received from the OpenAI Assistant back to the client through SocketIO, ensuring messages are delivered 
    to the correct user session based on a provided user identifier.
    """
    def __init__(self, userId: str):
        """
        Initializes the EventHandler instance with a specific user identifier and optional configuration.
        """
        super().__init__()
        self.userId = userId

    @contextmanager
    def handle_errors(self, action: str):
        try:
            yield
        except Exception as e:
            error_msg = f"{action}: {e}"
            logging.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e

    def on_text_delta(self, delta, snapshot) -> None:
        """
        Emits text updates received from the OpenAI Assistant to the appropriate client through SocketIO, 
        using the user's unique identifier to target the correct room. 
        """
        with self.handle_errors("Error processing text delta"):
            from ws.flask_config import config
            annotation_pattern = re.compile(r"【\d+:\d+†[^】]*】")

            config.socketio.emit(
                'assistant_message', 
                {'text': re.sub(annotation_pattern, '', delta.value)},
                room=self.userId, 
                namespace='/chat'
            )