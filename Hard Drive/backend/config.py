# File: /Users/rick/CaseProject/backend/config.py

import os
from dotenv import load_dotenv

load_dotenv()

# Auth0 Configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "dev-wmydj4rlx48n5trz.us.auth0.com")
API_AUDIENCE = os.getenv("API_AUDIENCE", "https://my-saas-app.local/api")
ALGORITHMS = ["RS256"]

# Database Configuration
# Use SQLite for testing to avoid PostgreSQL connection issues
# Database Configuration
DATABASE_URL = "sqlite:///./test.db"  # Hard-code SQLite for now
# Stripe Configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_...")
STRIPE_ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET", "whsec_...")

# Subscription Plans
SUBSCRIPTION_PLANS = {
    "basic": {
        "name": "Basic",
        "stripe_price_id": os.getenv("STRIPE_BASIC_PRICE_ID", "price_..."),
        "monthly_quota": 5
    },
    "professional": {
        "name": "Professional",
        "stripe_price_id": os.getenv("STRIPE_PRO_PRICE_ID", "price_..."),
        "monthly_quota": 25
    },
    "enterprise": {
        "name": "Enterprise",
        "stripe_price_id": os.getenv("STRIPE_ENTERPRISE_PRICE_ID", "price_..."),
        "monthly_quota": 999999  # Effectively unlimited
    }
}
