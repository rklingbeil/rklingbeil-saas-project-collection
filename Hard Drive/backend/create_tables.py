# create_tables.py

from sqlalchemy import create_engine
from config import DATABASE_URL
from models import Base

# Create an SQLAlchemy engine using your DATABASE_URL from config.py
engine = create_engine(DATABASE_URL)

# Create all tables defined in models.py
Base.metadata.create_all(engine)
print("Tables created successfully!")

