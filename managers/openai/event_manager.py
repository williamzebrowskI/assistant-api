# from flask_config import config
from openai import AssistantEventHandler
import logging

class EventHandler(AssistantEventHandler):
    """
    Handles events triggered during the interaction with the OpenAI Assistant, specifically tailored for Flask-SocketIO integration. 
    This class inherits from AssistantEventHandler and extends its functionality to support real-time communication in a web application context. 
    It manages sending text updates received from the OpenAI Assistant back to the client through SocketIO, ensuring messages are delivered 
    to the correct user session based on a provided user identifier.
    """
    def __init__(self, userId):
        """
        Initializes the EventHandler instance with a specific user identifier.
        """
        super().__init__()
        self.userId = userId

    def on_text_delta(self, delta, snapshot):
        """
        Emits text updates received from the OpenAI Assistant to the appropriate client through SocketIO, 
        using the user's unique identifier to target the correct room. 
        """
        # Perform a late import for socketio here
        from ws.flask_config import config

        # Check if the delta contains any annotations and remove them
        delta.annotations = ""

        config.socketio.emit('assistant_message', {'text': delta.value}, room=self.userId, namespace='/chat')
    

    def on_error(self, error):
        logging.error("An error occurred: %s", error)
