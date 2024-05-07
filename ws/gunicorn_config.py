import logging

# Custom formatter with color coding
class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    green = "\x1b[32;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s [%(process)d] [%(levelname)s] %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "[%Y-%m-%d %H:%M:%S %z]")
        return formatter.format(record)

def setup_logging():
    try:
        # Console handler with custom formatter
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(CustomFormatter())

        # Get the root logger and configure it
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(console_handler)
    except Exception as e:
        # Logging setup failure
        logging.error(f"Failed to set up logging: {e}")

def on_starting(server):
    try:
        setup_logging()
        logging.info("Server is starting 🚀")
    except Exception as e:
        logging.error(f"Failed during server start: {e}")

def when_ready(server):
    try:
        logging.info("Successful! Server is ready to receive traffic. 🤗")
    except Exception as e:
        logging.error(f"Failed when server was ready: {e}")

def on_exit(server):
    try:
        logging.info("Server is shutting down.")
    except Exception as e:
        logging.error(f"Failed during server shutdown: {e}")
