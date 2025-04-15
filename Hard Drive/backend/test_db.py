# test_db.py
from sqlalchemy import create_engine, text
from config import DATABASE_URL

def main():
    # Create the SQLAlchemy engine using the DATABASE_URL from config.py
    engine = create_engine(DATABASE_URL)
    
    # Connect to the database and execute a simple query (SELECT 1)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        for row in result:
            print(row)  # Expected output: (1,)

    print("Database connection successful!")

if __name__ == "__main__":
    main()

