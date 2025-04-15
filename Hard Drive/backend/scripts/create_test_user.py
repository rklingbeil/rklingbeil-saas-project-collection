# File: /Users/rick/CaseProject/backend/scripts/create_test_user.py

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import json

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv(dotenv_path='../.env')

# Import the database models
from models.subscription import User, Subscription, Base

# Get the database URL from environment variables
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///../test.db')

# Create a database connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def create_test_user():
    # Check if user already exists
    auth0_id = "WvY1U2l9FY3xbHtnWLLSEyAWBeXi1Y6h@clients"
    existing_user = db.query(User).filter(User.auth0_id == auth0_id).first()
    
    if existing_user:
        print(f"User already exists with ID: {existing_user.id}")
        return existing_user
    
    # Create a new test user
    user = User(
        auth0_id=auth0_id,
        email="test@example.com",
        name="Test User"
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"Created new user with ID: {user.id}")
    
    # Create a subscription for the user
    subscription = Subscription(
        user_id=user.id,
        stripe_customer_id="cus_test",
        stripe_subscription_id="sub_test",
        plan_name="Test Plan",
        plan_id="test",
        status="active",
        monthly_quota=100,
        remaining_quota=100
    )
    
    db.add(subscription)
    db.commit()
    
    print(f"Created subscription for user")
    return user

if __name__ == "__main__":
    try:
        user = create_test_user()
        print(f"Test user created successfully: {user.auth0_id}")
    except Exception as e:
        print(f"Error creating test user: {e}")
    finally:
        db.close()
