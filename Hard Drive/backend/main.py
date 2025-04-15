# File: /Users/rick/CaseProject/backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

# Change relative imports to absolute imports
from api import auth, cases, subscriptions, webhooks, health
from db.database import engine, Base
from config import AUTH0_DOMAIN, API_AUDIENCE
from middleware.logging import RequestLoggingMiddleware
from utils.logger import app_logger, error_logger

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    app_logger.info("Database tables created successfully")
except SQLAlchemyError as e:
    error_logger.error(f"Error creating database tables: {e}")

app = FastAPI(title="Legal Case Analysis API")

# Add logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add application description
@app.get("/")
async def root():
    return {
        "service": "Legal Case Analysis API",
        "version": "1.0.0",
        "auth": {
            "domain": AUTH0_DOMAIN,
            "audience": API_AUDIENCE
        }
    }

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(cases.router, prefix="/cases", tags=["Case Analysis"])
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(health.router, prefix="/health", tags=["Health"])

# Startup event
@app.on_event("startup")
async def startup_event():
    app_logger.info("Application starting up...")
    app_logger.info(f"Auth0 Domain: {AUTH0_DOMAIN}")
    app_logger.info(f"API Audience: {API_AUDIENCE}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    app_logger.info("Application shutting down...")
