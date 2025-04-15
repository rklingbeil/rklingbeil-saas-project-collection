# File: /Users/rick/CaseProject/backend/middleware/logging.py

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from utils.logger import log_request, error_logger, app_logger

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all requests and responses"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate request duration
            duration_ms = round((time.time() - start_time) * 1000)
            
            # Log the request
            log_request(request, response.status_code, duration_ms)
            
            return response
            
        except Exception as e:
            # Log any unhandled exceptions
            duration_ms = round((time.time() - start_time) * 1000)
            error_logger.error(f"Unhandled exception in request: {str(e)}")
            log_request(request, 500, duration_ms)
            
            # Re-raise the exception
            raise
