# app/utils/logger.py
import logging
import os
from logging.handlers import RotatingFileHandler
from .config import config

def setup_logger():
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = config.get('logging.file', 'logs/franchise_monitor.log')
    log_level = getattr(logging, config.get('logging.level', 'INFO').upper())
    
    logger = logging.getLogger('FranchiseMonitor')
    logger.setLevel(log_level)
    
    # File Handler
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()