from flask import session
from openai import AssistantEventHandler
import logging

class EventHandler(AssistantEventHandler):
    """
    Handles events triggered during the interaction with the OpenAI Assistant, specifically tailored for Flask-SocketIO integration. 
    This class inherits from AssistantEventHandler and extends its functionality to support real-time communication in a web application context. 
    It manages sending text updates received from the OpenAI Assistant back to the client through SocketIO, ensuring messages are delivered 
    to the correct user session based on a provided user identifier.

    Attributes:
        userId (str): A unique identifier for the user, used to direct messages to the correct SocketIO room.

    Methods:
        __init__(self, userId): Initializes a new instance of the EventHandler with the user's unique identifier.
        on_text_delta(self, delta, snapshot): Emits text updates received from the OpenAI Assistant to the client's SocketIO session.
        on_error(self, error): Logs any errors encountered during the interaction with the OpenAI Assistant.
    """
    def __init__(self, userId):
        """
        Initializes the EventHandler instance with a specific user identifier.

        Args:
            userId (str): The unique identifier for the user's session, used for routing messages.
        """
        super().__init__()
        self.userId = userId

    def on_text_delta(self, delta, snapshot):
        """
        Emits text updates received from the OpenAI Assistant to the appropriate client through SocketIO, 
        using the user's unique identifier to target the correct room.

        Args:
            delta: The text delta update from the OpenAI Assistant.
            snapshot: The current snapshot of the message, including the delta.
        """
        # Perform a late import for socketio here
        from app import socketio

        socketio.emit('assistant_message', {'text': delta.value}, room=self.userId, namespace='/chat')
    
    def on_error(self, error):
        """
        Logs any errors that occur during the interaction with the OpenAI Assistant to help with debugging and error tracking.

        Args:
            error: The error message or object encountered during the interaction.
        """
        logging.warning(f"Error: {error}")
