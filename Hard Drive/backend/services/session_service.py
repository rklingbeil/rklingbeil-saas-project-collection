# File: /Users/rick/CaseProject/backend/services/session_service.py

import uuid
import json
import time
from typing import Dict

class SessionService:
    """
    In-memory implementation of SessionService for development and testing.
    This implementation doesn't require Redis and stores sessions in memory.
    """
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """
        Initialize an in-memory session store.
        
        Parameters are kept for API compatibility but not used.
        """
        # Initialize in-memory store as a dictionary
        self.sessions = {}

    def create_session(self, ttl_seconds: int = 3600) -> str:
        """
        Create a new session with a specified time-to-live (TTL).
        
        Parameters:
            ttl_seconds (int): Time in seconds until the session expires.
        
        Returns:
            session_id (str): A unique session identifier.
        """
        session_id = str(uuid.uuid4())
        key = f"session:{session_id}"
        # Store an empty dictionary with expiration timestamp
        expiry = time.time() + ttl_seconds
        self.sessions[key] = {
            "data": {},
            "expiry": expiry
        }
        return session_id

    def get_session_data(self, session_id: str) -> dict:
        """
        Retrieve session data using the session ID.
        
        Parameters:
            session_id (str): The session identifier.
        
        Returns:
            A dictionary containing the session data.
        """
        key = f"session:{session_id}"
        session = self.sessions.get(key)
        
        if not session:
            return {}
            
        # Check if session has expired
        if session["expiry"] < time.time():
            del self.sessions[key]
            return {}
            
        return session["data"]

    def update_session_data(self, session_id: str, data: dict) -> None:
        """
        Update the session data by merging the new data with existing data.
        
        Parameters:
            session_id (str): The session identifier.
            data (dict): A dictionary containing data to update for the session.
        """
        key = f"session:{session_id}"
        session = self.sessions.get(key)
        
        if not session:
            # Create new session if it doesn't exist
            expiry = time.time() + 3600  # 1 hour default
            self.sessions[key] = {
                "data": data,
                "expiry": expiry
            }
            return
            
        # Check if session has expired
        if session["expiry"] < time.time():
            # Renew the session with new data
            expiry = time.time() + 3600  # 1 hour default
            self.sessions[key] = {
                "data": data,
                "expiry": expiry
            }
        else:
            # Update existing session
            session["data"].update(data)

    def clear_session(self, session_id: str) -> None:
        """
        Delete the session data.
        
        Parameters:
            session_id (str): The session identifier.
        """
        key = f"session:{session_id}"
        if key in self.sessions:
            del self.sessions[key]
    
    def clear_all_sessions(self) -> None:
        """
        Clear all sessions from memory.
        """
        self.sessions.clear()
