from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import User

# Create the standard router instance
router = APIRouter()

# Dummy endpoint to check the user profile functionality
@router.get("/profile")
async def get_profile():
    """
    A simple endpoint to verify that the user profile functionality is working.
    """
    return {"message": "User profile endpoint is working!"}

# Additional dummy endpoint for testing
@router.get("/test")
async def test_user():
    """
    Another simple endpoint to verify that the Users router is working.
    """
    return {"message": "User endpoint is working!"}

# Pydantic model for user registration
class UserCreate(BaseModel):
    username: str
    password: str

# Endpoint for user registration
@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user.
    
    Checks if the username already exists. If not, it creates a new user with a
    dummy hashed password (for demonstration purposes only). In production, use a
    secure hashing algorithm like bcrypt.
    """
    # Check if the username already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Create a dummy hashed password; replace with a secure hash in production
    hashed_password = "hashed_" + user.password

    # Create a new user instance
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.id}

