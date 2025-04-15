# File: /Users/rick/CaseProject/backend/api/subscriptions.py

# File: /Users/rick/CaseProject/backend/api/subscriptions.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timezone

# Change relative imports to absolute imports
from services.subscription_service import SubscriptionService
from services.stripe_service import StripeService
from db.database import get_db
from config import SUBSCRIPTION_PLANS
from api.auth import get_current_user

router = APIRouter()

# Rest of the file remains the same...
# Request models
class SubscriptionRequest(BaseModel):
    plan_id: str
    return_url: Optional[str] = None

class CustomerPortalRequest(BaseModel):
    return_url: str

# Response models
class PlanInfo(BaseModel):
    id: str
    name: str
    monthly_quota: int
    price: float

class PlansResponse(BaseModel):
    plans: List[PlanInfo]

class SubscriptionDetails(BaseModel):
    plan_name: str
    status: str
    monthly_quota: int
    remaining_quota: int
    current_period_end: Optional[str] = None

class SubscriptionResponse(BaseModel):
    has_subscription: bool
    details: Optional[SubscriptionDetails] = None

@router.get("/plans", response_model=PlansResponse)
async def get_plans():
    """Get all available subscription plans"""
    plans = []
    for plan_id, plan_data in SUBSCRIPTION_PLANS.items():
        plans.append(PlanInfo(
            id=plan_id,
            name=plan_data["name"],
            monthly_quota=plan_data["monthly_quota"],
            price=float(plan_data.get("price", 0))
        ))
    return {"plans": plans}

@router.get("/my-subscription", response_model=SubscriptionResponse)
async def get_my_subscription(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the current user's subscription"""
    auth0_id = user.get("sub")
    if not auth0_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid user ID in token"
        )
    
    # Get user from database
    db_user = SubscriptionService.get_user_by_auth0_id(db, auth0_id)
    if not db_user:
        # Create user if not exists
        email = user.get("email", "")
        name = user.get("name", "")
        db_user = SubscriptionService.create_user(db, auth0_id, email, name)
    
    # Get subscription
    subscription = SubscriptionService.get_user_subscription(db, db_user.id)
    
    if not subscription:
        return {"has_subscription": False}
    
    # Format current_period_end as string if exists
    current_period_end = None
    if subscription.current_period_end:
        current_period_end = subscription.current_period_end.isoformat()
    
    return {
        "has_subscription": True,
        "details": {
            "plan_name": subscription.plan_name,
            "status": subscription.status,
            "monthly_quota": subscription.monthly_quota,
            "remaining_quota": subscription.remaining_quota,
            "current_period_end": current_period_end
        }
    }

@router.post("/create-subscription")
async def create_subscription(
    request: SubscriptionRequest, 
    user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Create a subscription for the current user"""
    auth0_id = user.get("sub")
    if not auth0_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid user ID in token"
        )
    
    # Validate plan ID
    if request.plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan ID: {request.plan_id}"
        )
    
    # Get or create user
    email = user.get("email", "")
    name = user.get("name", "")
    db_user = SubscriptionService.get_or_create_user(db, auth0_id, email, name)
    
    # Check if user already has a subscription
    existing_subscription = SubscriptionService.get_user_subscription(db, db_user.id)
    
    stripe_service = StripeService()
    
    if existing_subscription:
        # If user already has a subscription, update it
        # Get customer ID from existing subscription
        customer_id = existing_subscription.stripe_customer_id
        
        # Update subscription in Stripe
        stripe_subscription = stripe_service.update_subscription(
            existing_subscription.stripe_subscription_id,
            SUBSCRIPTION_PLANS[request.plan_id]["stripe_price_id"]
        )
        
        # Update subscription in database
        SubscriptionService.update_subscription(
            db,
            db_user.id,
            SUBSCRIPTION_PLANS[request.plan_id]["name"],
            request.plan_id,
            stripe_subscription["status"],
            datetime.fromtimestamp(stripe_subscription["current_period_end"], timezone.utc)
        )
        
        # Return success
        return {"success": True, "message": "Subscription updated successfully"}
    else:
        # Create customer in Stripe if not exists
        customer = stripe_service.create_customer(
            email=db_user.email,
            name=db_user.name,
            metadata={"auth0_id": auth0_id}
        )
        
        # Create checkout session
        checkout_session = stripe_service.create_checkout_session(
            customer_id=customer["id"],
            price_id=SUBSCRIPTION_PLANS[request.plan_id]["stripe_price_id"],
            success_url=request.return_url or "http://localhost:3000/subscription-success",
            cancel_url=request.return_url or "http://localhost:3000/subscription-cancel"
        )
        
        # Return checkout URL
        return {"client_secret": checkout_session["client_secret"]}

@router.post("/cancel-subscription")
async def cancel_subscription(
    user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Cancel the current user's subscription"""
    auth0_id = user.get("sub")
    if not auth0_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid user ID in token"
        )
    
    # Get user
    db_user = SubscriptionService.get_user_by_auth0_id(db, auth0_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get subscription
    subscription = SubscriptionService.get_user_subscription(db, db_user.id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )
    
    # Cancel subscription in Stripe
    stripe_service = StripeService()
    stripe_service.cancel_subscription(subscription.stripe_subscription_id)
    
    # Update subscription in database
    SubscriptionService.update_subscription(
        db,
        db_user.id,
        subscription.plan_name,
        subscription.plan_id,
        "canceled"
    )
    
    return {"success": True, "message": "Subscription canceled"}

@router.post("/customer-portal")
async def create_customer_portal(
    request: CustomerPortalRequest,
    user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Create a Stripe Customer Portal session for the current user"""
    auth0_id = user.get("sub")
    if not auth0_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid user ID in token"
        )
    
    # Get user
    db_user = SubscriptionService.get_user_by_auth0_id(db, auth0_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get subscription
    subscription = SubscriptionService.get_user_subscription(db, db_user.id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )
    
    # Create customer portal session
    stripe_service = StripeService()
    portal_session = stripe_service.create_portal_session(
        customer_id=subscription.stripe_customer_id,
        return_url=request.return_url
    )
    
    return {"url": portal_session["url"]}
