from flask import Flask
from flask_socketio import SocketIO
from os import getenv
from dotenv import load_dotenv
load_dotenv()


class CorsUtility:
    @staticmethod
    def get_cors(origin):
        cors_allowed_origins = getenv('CORS_ALLOWED_ORIGINS')
        if cors_allowed_origins is not None:
            cors_allowed_origins = [origin.strip() for origin in cors_allowed_origins.split(',')]
        return cors_allowed_origins


class AppConfig:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = getenv('FLASK_SECRET_KEY')
        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins=CorsUtility.get_cors,
            cors_credentials=True,
            cors_allowed_headers="*",
            manage_session=False,
            logger=False,
            engineio_logger=False
        )

config = AppConfig()