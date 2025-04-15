# File: /Users/rick/CaseProject/backend/scripts/db_manager.py

import sys
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the models
from models.subscription import Base, User, Subscription

# Define the database path explicitly
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"
print(f"Using database at: {DB_PATH}")

# Create the engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all database tables"""
    Base.metadata.create_all(engine)
    print("Database tables created successfully")
    
    # List all tables created
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables in database: {tables}")

def create_test_user():
    """Create a test user and subscription"""
    db = SessionLocal()
    try:
        # Clear existing data first
        db.query(Subscription).delete()
        db.query(User).delete()
        db.commit()
        
        # Create a new test user
        auth0_id = "WvY1U2l9FY3xbHtnWLLSEyAWBeXi1Y6h@clients"
        user = User(
            auth0_id=auth0_id,
            email="test@example.com",
            name="Test User"
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"Created test user with ID: {user.id}")
        
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
        
        # Verify the user exists
        verify_user = db.query(User).filter(User.auth0_id == auth0_id).first()
        if verify_user:
            print(f"User verified in database with ID: {verify_user.id}")
        else:
            print("ERROR: User not found after creation!")
            
    except Exception as e:
        db.rollback()
        print(f"Error creating test user: {e}")
    finally:
        db.close()

def list_users():
    """List all users in the database"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Total users in database: {len(users)}")
        for user in users:
            print(f"ID: {user.id}, Auth0 ID: {user.auth0_id}, Email: {user.email}")
            
        return users
    except Exception as e:
        print(f"Error listing users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python db_manager.py [init|create|list]")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "init":
        init_db()
    elif command == "create":
        create_test_user()
    elif command == "list":
        list_users()
    else:
        print(f"Unknown command: {command}")
