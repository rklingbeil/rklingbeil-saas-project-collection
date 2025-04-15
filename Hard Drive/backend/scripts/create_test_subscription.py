# File: /Users/rick/CaseProject/backend/scripts/create_test_subscription.py

from sqlalchemy.orm import Session
from db.database import get_db
from models.subscription import User, Subscription
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def create_test_subscription():
    db = next(get_db())
    try:
        # Get or create user (using Auth0 ID from the auth bypass)
        auth0_id = "auth0|123456789"  # Use the actual Auth0 ID from your application
        user = db.query(User).filter(User.auth0_id == auth0_id).first()
        
        if not user:
            print("User not found, creating test user")
            user = User(auth0_id=auth0_id, email="rick@klingbeil-law.com", name="Rick Klingbeil")
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            print(f"Found existing user: {user.email}")
        
        # Check for existing subscription
        subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
        
        if not subscription:
            print("Creating test subscription")
            subscription = Subscription(
                user_id=user.id,
                stripe_customer_id="cus_test",
                stripe_subscription_id="sub_test",
                plan_name="Professional",
                plan_id="price_pro",
                status="active",
                monthly_quota=20,
                remaining_quota=20
            )
            db.add(subscription)
            db.commit()
            print("Test subscription created successfully")
        else:
            print(f"Found existing subscription: {subscription.plan_name}, {subscription.status}")
            print(f"Quota: {subscription.remaining_quota}/{subscription.monthly_quota}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_subscription()
