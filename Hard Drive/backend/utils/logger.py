# File: /Users/rick/CaseProject/backend/utils/logger.py

import os
import logging
from logging.handlers import RotatingFileHandler
import datetime
import json

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(logs_dir, exist_ok=True)

# Configure log file paths
log_file = os.path.join(logs_dir, "application.log")
error_log_file = os.path.join(logs_dir, "error.log")
request_log_file = os.path.join(logs_dir, "requests.log")

# Configure the logger
def get_logger(name, log_file=log_file):
    """Get a configured logger instance"""
    logger = logging.getLogger(name)
    
    # Only configure handlers if they haven't been configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create file handler with rotation (10MB max size, keep 10 backup files)
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

# Get logger instances
app_logger = get_logger("app")
error_logger = get_logger("error", error_log_file)

# Configure request logger
request_logger = logging.getLogger("request")
request_logger.setLevel(logging.INFO)
request_handler = RotatingFileHandler(
    request_log_file,
    maxBytes=10*1024*1024,
    backupCount=10
)
request_formatter = logging.Formatter('%(asctime)s - %(message)s')
request_handler.setFormatter(request_formatter)
request_logger.addHandler(request_handler)

def log_request(request, response_status, duration_ms):
    """Log API request and response information"""
    try:
        log_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else "unknown",
            "status_code": response_status,
            "duration_ms": duration_ms,
            "user_agent": request.headers.get("user-agent", "unknown")
        }
        
        # Add auth info if available
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            log_data["authenticated"] = True
        else:
            log_data["authenticated"] = False
            
        request_logger.info(json.dumps(log_data))
    except Exception as e:
        error_logger.error(f"Failed to log request: {str(e)}")
