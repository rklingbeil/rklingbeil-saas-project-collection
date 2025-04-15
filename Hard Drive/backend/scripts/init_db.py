# File: /Users/rick/CaseProject/backend/scripts/init_db.py

import sys
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv(dotenv_path='../.env')

# Import the Base and all models to ensure they're registered with the metadata
from models.subscription import Base, User, Subscription, CaseAnalysis

# Get the database URL from environment variables
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///../test.db')

def init_db():
    # Create a database connection
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    print("Database tables created successfully")

if __name__ == "__main__":
    try:
        init_db()
    except Exception as e:
        print(f"Error initializing database: {e}")
