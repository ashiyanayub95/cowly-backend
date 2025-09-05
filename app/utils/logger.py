import os
import logging
from logging.handlers import RotatingFileHandler
from logging import StreamHandler

def setup_logger():
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, 'app.log')

    # Clear existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

    file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=5)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
