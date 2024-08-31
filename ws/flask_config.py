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
    
class VarConfig:
    SECRET_KEY = getenv('FLASK_SECRET_KEY', 'default_secret_key')
    OPENAI_API_KEY = getenv('OPENAI_API_KEY')
    ES_USERNAME = getenv('ES_USERNAME')
    ES_PASSWORD = getenv('ES_PASSWORD')
    ASSISTANT_ID = getenv('ASSISTANT_ID')
    BASE_URL = getenv('BASE_URL')
    ES_URL = getenv('ES_URL')
    ES_PORT = getenv('ES_PORT')
    ES_INDEX = getenv('ES_INDEX')
    ES_API_KEY = getenv('ES_API_KEY')
    CORS_ALLOWED_ORIGINS = getenv('CORS_ALLOWED_ORIGINS').split(',')

class ConfigAccessor:
    def __init__(self, flask_config):
        self._config = flask_config

    def __getattr__(self, item):
        try:
            return self._config[item]
        except KeyError:
            raise AttributeError(f"Configuration key '{item}' not found.")

class AppConfig:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config.from_object(VarConfig)
        self.config = ConfigAccessor(self.app.config)
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