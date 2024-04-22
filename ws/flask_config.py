from flask import Flask
from flask_socketio import SocketIO
import os

class AppConfig:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins=[
                "http://127.0.0.1:5500", "http://localhost:8000", 
                "https://develop.getfafsahelp.org", "https://www.getfafsahelp.org", 
                "http://localhost:3000", "http://localhost:8002", 
                "https://benefitsdatatrust.github.io", "http://127.0.0.1:8002", 
                "https://deploy-preview-327--awesome-varahamihira-483edb.netlify.app"
            ],
            cors_credentials=True,
            cors_allowed_headers="*",
            manage_session=False,
            logger=False,
            engineio_logger=False
        )

config = AppConfig()