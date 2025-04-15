# File: /Users/rick/CaseProject/backend/services/subscription_service.py

# File: /Users/rick/CaseProject/backend/services/subscription_service.py

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

# Change relative imports to absolute imports
from models.subscription import User, Subscription, CaseAnalysis
from config import SUBSCRIPTION_PLANS

class SubscriptionService:
    @staticmethod
    def get_user_by_auth0_id(db: Session, auth0_id: str):
        """Get a user by Auth0 ID"""
        return db.query(User).filter(User.auth0_id == auth0_id).first()
    
    @staticmethod
    def create_user(db: Session, auth0_id: str, email: str, name: str = None):
        """Create a new user"""
        # Ensure we're getting proper data from Auth0
        if not auth0_id or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Auth0 ID and email are required"
            )
            
        user = User(auth0_id=auth0_id, email=email, name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    # Rest of the file remains the same...    
    @staticmethod
    def get_or_create_user(db: Session, auth0_id: str, email: str, name: str = None):
        """Get existing user or create a new one"""
        # Handle the case where auth0_id is not properly formatted
        if not auth0_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Auth0 user ID"
            )
            
        user = SubscriptionService.get_user_by_auth0_id(db, auth0_id)
        if not user:
            user = SubscriptionService.create_user(db, auth0_id, email, name)
        return user
    
    @staticmethod
    def create_subscription(db: Session, user_id: int, stripe_customer_id: str, stripe_subscription_id: str, 
                           plan_name: str, plan_id: str, status: str, trial_end=None, current_period_end=None):
        """Create a subscription for a user"""
        # Get monthly quota based on plan name
        monthly_quota = SUBSCRIPTION_PLANS.get(plan_id.lower(), {}).get('monthly_quota', 5)
        
        subscription = Subscription(
            user_id=user_id,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            plan_name=plan_name,
            plan_id=plan_id,
            status=status,
            trial_end=trial_end,
            current_period_end=current_period_end,
            monthly_quota=monthly_quota,
            remaining_quota=monthly_quota
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription
    
    @staticmethod
    def update_subscription(db: Session, user_id: int, plan_name: str, plan_id: str, status: str, current_period_end=None):
        """Update a user's subscription"""
        subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        # Get monthly quota based on plan name
        monthly_quota = SUBSCRIPTION_PLANS.get(plan_id.lower(), {}).get('monthly_quota', 5)
        
        subscription.plan_name = plan_name
        subscription.plan_id = plan_id
        subscription.status = status
        subscription.monthly_quota = monthly_quota
        
        # Reset quota if upgrading
        if subscription.remaining_quota < monthly_quota:
            subscription.remaining_quota = monthly_quota
            
        if current_period_end:
            subscription.current_period_end = current_period_end
        
        db.commit()
        db.refresh(subscription)
        return subscription
    
    @staticmethod
    def get_user_subscription(db: Session, user_id: int):
        """Get a user's subscription"""
        return db.query(Subscription).filter(Subscription.user_id == user_id).first()
    
    @staticmethod
    def get_subscription_from_auth0_id(db: Session, auth0_id: str):
        """Get a user's subscription by Auth0 ID"""
        user = SubscriptionService.get_user_by_auth0_id(db, auth0_id)
        if not user:
            return None
            
        return SubscriptionService.get_user_subscription(db, user.id)
    
    @staticmethod
    def check_and_decrement_quota(db: Session, user_id: int):
        """
        TEMPORARY: Bypass subscription check and always return a positive quota
        """
        # Return a fixed number (20) as the remaining quota
        return 20
        
        # ORIGINAL CODE (Commented out for testing)
        """
        subscription = SubscriptionService.get_user_subscription(db, user_id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        if subscription.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Subscription is not active"
            )
        
        if subscription.remaining_quota <= 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Monthly quota exceeded"
            )
        
        subscription.remaining_quota -= 1
        db.commit()
        
        return subscription.remaining_quota
        """
    
    @staticmethod
    def record_case_analysis(db: Session, user_id: int, subject_case, prediction, similar_cases):
        """Record a case analysis in the database"""
        case_analysis = CaseAnalysis(
            user_id=user_id,
            subject_case=subject_case,
            prediction=prediction,
            similar_cases=similar_cases
        )
        
        db.add(case_analysis)
        db.commit()
        db.refresh(case_analysis)
        return case_analysis
    
    @staticmethod
    def get_user_case_analyses(db: Session, user_id: int, skip: int = 0, limit: int = 10):
        """Get a user's case analyses"""
        return db.query(CaseAnalysis).filter(
            CaseAnalysis.user_id == user_id
        ).order_by(CaseAnalysis.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_case_analyses_from_auth0_id(db: Session, auth0_id: str, skip: int = 0, limit: int = 10):
        """Get a user's case analyses by Auth0 ID"""
        user = SubscriptionService.get_user_by_auth0_id(db, auth0_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return SubscriptionService.get_user_case_analyses(db, user.id, skip, limit)
