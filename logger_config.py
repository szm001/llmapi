import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging(log_level: str = "INFO"):
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    if not root_logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log"),
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, f"error_{datetime.now().strftime('%Y%m%d')}.log"),
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
    
    return root_logger
