# File: /Users/rick/CaseProject/backend/api/health.py

from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional
import time
import os
from openai import OpenAI
from datetime import datetime

from db.database import get_db
from utils.logger import app_logger, error_logger
from services.pinecone_service import pc as pinecone_client, INDEX_NAME

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    components: Dict[str, Any]
    version: str = "1.0.0"

@router.get("/", response_model=HealthResponse)
async def health_check(request: Request, detailed: bool = False, db: Session = Depends(get_db)):
    """
    Check the health of all system components.
    Set detailed=true for more comprehensive checks (slower but more thorough).
    """
    start_time = time.time()
    app_logger.info("Health check initiated")
    
    health_status = {
        "database": check_database(db),
        "openai": check_openai_api(detailed),
        "pinecone": check_pinecone(detailed),
        "environment": check_environment()
    }
    
    # Determine overall status
    overall_status = "healthy"
    for component, status in health_status.items():
        if status["status"] == "unhealthy":
            overall_status = "unhealthy"
            break
        elif status["status"] == "degraded" and overall_status != "unhealthy":
            overall_status = "degraded"
    
    duration_ms = round((time.time() - start_time) * 1000)
    app_logger.info(f"Health check completed in {duration_ms}ms with status: {overall_status}")
    
    # Add additional metadata
    health_status["uptime"] = {
        "status": "info",
        "server_time": datetime.now().isoformat(),
        "response_time_ms": duration_ms
    }
    
    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "components": health_status,
        "version": "1.0.0"
    }

def check_database(db: Session) -> Dict[str, Any]:
    """Check database connectivity by executing a simple query"""
    try:
        # Execute a simple query
        start_time = time.time()
        db.execute("SELECT 1")
        duration_ms = round((time.time() - start_time) * 1000)
        
        return {
            "status": "healthy",
            "response_time_ms": duration_ms
        }
    except Exception as e:
        error_logger.error(f"Database health check failed: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e)
        }

def check_openai_api(detailed: bool) -> Dict[str, Any]:
    """Check OpenAI API connectivity"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        return {
            "status": "unhealthy",
            "error": "OpenAI API key not configured"
        }
    
    try:
        # For a simple check we just initialize the client
        start_time = time.time()
        client = OpenAI(api_key=api_key)
        
        # For detailed check, we make a minimal API call
        if detailed:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use a smaller model for health checks
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
        duration_ms = round((time.time() - start_time) * 1000)
        
        return {
            "status": "healthy",
            "response_time_ms": duration_ms
        }
    except Exception as e:
        error_logger.error(f"OpenAI health check failed: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e)
        }

def check_pinecone(detailed: bool) -> Dict[str, Any]:
    """Check Pinecone connectivity"""
    if not pinecone_client:
        return {
            "status": "unhealthy",
            "error": "Pinecone client not initialized"
        }
    
    try:
        start_time = time.time()
        
        # For a simple check, we just verify the client exists
        # For detailed check, we query the index stats
        if detailed:
            try:
                index = pinecone_client.Index(INDEX_NAME)
                stats = index.describe_index_stats()
                vector_count = stats.get('total_vector_count', 0)
                
                # If index is empty, mark as degraded but not unhealthy
                if vector_count == 0:
                    return {
                        "status": "degraded",
                        "message": "Pinecone index exists but contains no vectors",
                        "response_time_ms": round((time.time() - start_time) * 1000)
                    }
            except Exception as e:
                return {
                    "status": "degraded",
                    "error": f"Pinecone index error: {str(e)}",
                    "response_time_ms": round((time.time() - start_time) * 1000)
                }
                
        duration_ms = round((time.time() - start_time) * 1000)
        
        return {
            "status": "healthy",
            "response_time_ms": duration_ms
        }
    except Exception as e:
        error_logger.error(f"Pinecone health check failed: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e)
        }

def check_environment() -> Dict[str, Any]:
    """Check if all required environment variables are set"""
    required_vars = [
        "OPENAI_API_KEY",
        "PINECONE_API_KEY",
        "DATABASE_URL",
        "AUTH0_DOMAIN",
        "API_AUDIENCE"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        return {
            "status": "degraded" if "OPENAI_API_KEY" not in missing_vars else "unhealthy",
            "missing_variables": missing_vars
        }
    
    return {
        "status": "healthy",
        "config_count": len(required_vars)
    }

@router.get("/ping")
async def ping():
    """
    Simple ping endpoint for basic liveness checks.
    This is a lightweight endpoint that doesn't check any components.
    """
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
