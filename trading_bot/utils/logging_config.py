import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logging(log_level=logging.DEBUG):
    # Get the directory where this script is located
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs_dir = os.path.join(base_dir, 'logs')
    
    # Create logs directory if it doesn't exist
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configureer root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Formatter voor alle handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler met DEBUG level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    
    # File handler voor alle logs
    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'trading_bot.log'),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'error.log'),
        maxBytes=5*1024*1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Verwijder bestaande handlers
    logger.handlers = []
    
    # Voeg nieuwe handlers toe
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    # Log startup info
    logger.info("Logging setup complete")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Logs directory: {logs_dir}")
    
    return logger 