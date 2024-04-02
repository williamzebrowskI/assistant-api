from flask import session
from openai import AssistantEventHandler
import logging

class EventHandler(AssistantEventHandler):
    """
    Handles events triggered during the conversation with the OpenAI Assistant.
    This includes receiving text updates from the assistant and handling any errors that occur.
    Inherits from a base event handler to provide custom event handling logic for Flask-SocketIO integration.
    """
    def on_text_delta(self, delta, snapshot):
        """
        Handles text updates from the assistant, emitting them to the client through SocketIO.
        """
        # Perform a late import for socketio here
        from app import socketio

        user_id = session.get('userId')
        socketio.emit('assistant_message', {'text': delta.value}, room=user_id, namespace='/chat')
    
    def on_error(self, error):
        """
        Handles any errors that occur during the conversation with the OpenAI Assistant.
        """
        logging.warning(f"Error: {error}")
