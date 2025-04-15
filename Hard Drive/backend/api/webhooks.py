# File: /Users/rick/CaseProject/backend/api/webhooks.py

from fastapi import APIRouter, Request, HTTPException, Depends, status
from sqlalchemy.orm import Session
import stripe
from datetime import datetime, timezone

from config import STRIPE_ENDPOINT_SECRET
from db.database import get_db
from services.subscription_service import SubscriptionService

router = APIRouter()

@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events"""
    # Get the raw request body
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    # If we don't have a proper signature header, return error
    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature"
        )
    
    try:
        # Verify the event using the signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_ENDPOINT_SECRET
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload"
        )
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    
    # Handle the event
    if event["type"] == "checkout.session.completed":
        # Process checkout session completed event
        session = event["data"]["object"]
        
        # Extract customer ID from session
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")
        
        # Get customer details from Stripe
        customer = stripe.Customer.retrieve(customer_id)
        auth0_id = customer.get("metadata", {}).get("auth0_id")
        
        if not auth0_id:
            print("Error: No Auth0 ID found in customer metadata")
            return {"status": "error", "message": "No Auth0 ID found"}
        
        # Get subscription details
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Get plan details
        plan_id = subscription["items"]["data"][0]["plan"]["id"]
        plan_name = subscription["items"]["data"][0]["plan"]["nickname"] or "Default Plan"
        
        # Get period details
        current_period_end = datetime.fromtimestamp(subscription["current_period_end"], timezone.utc)
        trial_end = None
        if subscription.get("trial_end"):
            trial_end = datetime.fromtimestamp(subscription["trial_end"], timezone.utc)
        
        # Get user from database
        user = SubscriptionService.get_user_by_auth0_id(db, auth0_id)
        
        if not user:
            print(f"Error: User with Auth0 ID {auth0_id} not found")
            return {"status": "error", "message": "User not found"}
        
        # Create subscription in database
        SubscriptionService.create_subscription(
            db=db,
            user_id=user.id,
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id,
            plan_name=plan_name,
            plan_id=plan_id,
            status=subscription["status"],
            trial_end=trial_end,
            current_period_end=current_period_end
        )
    
    elif event["type"] == "customer.subscription.updated":
        # Process subscription updated event
        subscription = event["data"]["object"]
        
        # Extract customer ID from subscription
        customer_id = subscription.get("customer")
        
        # Get customer details from Stripe
        customer = stripe.Customer.retrieve(customer_id)
        auth0_id = customer.get("metadata", {}).get("auth0_id")
        
        if not auth0_id:
            print("Error: No Auth0 ID found in customer metadata")
            return {"status": "error", "message": "No Auth0 ID found"}
        
        # Get plan details
        plan_id = subscription["items"]["data"][0]["plan"]["id"]
        plan_name = subscription["items"]["data"][0]["plan"]["nickname"] or "Default Plan"
        
        # Get period details
        current_period_end = datetime.fromtimestamp(subscription["current_period_end"], timezone.utc)
        
        # Get user from database
        user = SubscriptionService.get_user_by_auth0_id(db, auth0_id)
        
        if not user:
            print(f"Error: User with Auth0 ID {auth0_id} not found")
            return {"status": "error", "message": "User not found"}
        
        # Update subscription in database
        SubscriptionService.update_subscription(
            db=db,
            user_id=user.id,
            plan_name=plan_name,
            plan_id=plan_id,
            status=subscription["status"],
            current_period_end=current_period_end
        )
    
    elif event["type"] == "customer.subscription.deleted":
        # Process subscription deleted event
        subscription = event["data"]["object"]
        
        # Extract customer ID from subscription
        customer_id = subscription.get("customer")
        
        # Get customer details from Stripe
        customer = stripe.Customer.retrieve(customer_id)
        auth0_id = customer.get("metadata", {}).get("auth0_id")
        
        if not auth0_id:
            print("Error: No Auth0 ID found in customer metadata")
            return {"status": "error", "message": "No Auth0 ID found"}
        
        # Get user from database
        user = SubscriptionService.get_user_by_auth0_id(db, auth0_id)
        
        if not user:
            print(f"Error: User with Auth0 ID {auth0_id} not found")
            return {"status": "error", "message": "User not found"}
        
        # Update subscription status in database
        subscription_db = SubscriptionService.get_user_subscription(db, user.id)
        
        if subscription_db:
            subscription_db.status = "canceled"
            db.commit()
    
    return {"status": "success"}
