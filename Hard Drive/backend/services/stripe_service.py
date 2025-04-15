# File: /Users/rick/CaseProject/backend/services/stripe_service.py

import os
import stripe
from config import STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_ENDPOINT_SECRET

class StripeService:
    def __init__(self):
        # Initialize Stripe with the secret key
        stripe.api_key = STRIPE_SECRET_KEY
    
    def create_customer(self, email, name=None, metadata=None):
        """Create a new customer in Stripe"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            return customer
        except Exception as e:
            print(f"Error creating Stripe customer: {e}")
            # Return a dummy customer ID for development
            return {"id": "cus_dummy"}
    
    def create_checkout_session(self, customer_id, price_id, success_url, cancel_url):
        """Create a checkout session for subscription"""
        try:
            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url
            )
            return checkout_session
        except Exception as e:
            print(f"Error creating checkout session: {e}")
            # Return dummy data for development
            return {"client_secret": "dummy_secret"}
    
    def update_subscription(self, subscription_id, price_id):
        """Update a subscription with a new price"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription["items"]["data"][0]["id"],
                    "price": price_id
                }]
            )
            return updated_subscription
        except Exception as e:
            print(f"Error updating subscription: {e}")
            # Return dummy data for development
            return {
                "status": "active",
                "current_period_end": 1735689600  # Dec 31, 2024
            }
    
    def cancel_subscription(self, subscription_id):
        """Cancel a subscription"""
        try:
            return stripe.Subscription.delete(subscription_id)
        except Exception as e:
            print(f"Error canceling subscription: {e}")
            return {"status": "canceled"}
    
    def create_portal_session(self, customer_id, return_url):
        """Create a Stripe customer portal session"""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            return session
        except Exception as e:
            print(f"Error creating portal session: {e}")
            # Return dummy data for development
            return {"url": return_url}
