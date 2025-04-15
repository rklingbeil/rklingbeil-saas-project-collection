# File: /Users/rick/CaseProject/backend/scripts/debug_token.py

import jwt
import json
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path so we can import modules
sys.path.append("..")

# Import models
from models.subscription import User

# Create a database connection
engine = create_engine("sqlite:///../test.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def debug_token():
    # Read the token from file
    with open("auth0_token.txt", "r") as f:
        token = f.read().strip()
    
    # Decode the token without verification (we just want to see the claims)
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        print("Decoded token:")
        print(json.dumps(decoded, indent=2))
        
        # Get the 'sub' claim which is the Auth0 ID
        auth0_id = decoded.get('sub')
        print(f"\nAuth0 ID from token: {auth0_id}")
        
        # Check if this user exists in the database
        user = db.query(User).filter(User.auth0_id == auth0_id).first()
        if user:
            print(f"User found in database with ID: {user.id}")
            print(f"Database auth0_id: {user.auth0_id}")
            print(f"Email: {user.email}")
        else:
            print("User NOT found in database")
            
            # Check for any users in the database
            users = db.query(User).all()
            print(f"\nTotal users in database: {len(users)}")
            for user in users:
                print(f"ID: {user.id}, Auth0 ID: {user.auth0_id}")
                
    except Exception as e:
        print(f"Error decoding token: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_token()
