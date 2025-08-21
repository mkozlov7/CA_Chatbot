
import logging
import logging.handlers
import os
import sys
from pythonjsonlogger import jsonlogger

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs"))
os.makedirs(LOGS_DIR, exist_ok=True)

# --- Detailed JSON Logger --- #

def setup_detailed_logger():
    """Sets up the detailed logger for audit and debugging."""
    logger = logging.getLogger('detailed_logger')
    logger.setLevel(logging.INFO)
    logger.propagate = False # Prevent duplicate logs in root logger

    # Avoid adding handlers if they already exist
    if not logger.handlers:
        log_path = os.path.join(LOGS_DIR, "detailed_activity.log")
        
        # Use a rotating file handler to prevent log files from growing indefinitely
        handler = logging.handlers.RotatingFileHandler(
            log_path, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
        )
        
        # Use a custom JSON formatter
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s %(session_id)s',
            json_ensure_ascii=False
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

# --- Aggregated Request Logger --- #

def setup_request_logger():
    """Sets up a simple logger to count requests over time."""
    logger = logging.getLogger('request_logger')
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        log_path = os.path.join(LOGS_DIR, "requests.log")
        
        handler = logging.handlers.RotatingFileHandler(
            log_path, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
        )
        
        # Simple formatter, just the timestamp is needed for counting
        formatter = logging.Formatter('%(asctime)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

# --- Get Loggers --- #
# These will be imported by other modules
detailed_logger = setup_detailed_logger()
request_logger = setup_request_logger()

