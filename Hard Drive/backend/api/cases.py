# File: /Users/rick/CaseProject/backend/api/cases.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

# Change both imports to use functions instead of classes
from services.openai_service import analyze_case
from services.pinecone_service import get_similar_cases
from services.subscription_service import SubscriptionService
from db.database import get_db
from api.auth import get_current_user
from utils.logger import app_logger, error_logger

router = APIRouter()

# Request models
class SubjectCase(BaseModel):
    court: Optional[str] = None
    date: Optional[str] = None
    plaintiff_medical_expert: Optional[str] = None
    defense_medical_expert: Optional[str] = None
    plaintiff_expert: Optional[str] = None
    defense_expert: Optional[str] = None
    judge_arbitrator_mediator: Optional[str] = None
    insurance_company: Optional[str] = None
    claim_type: Optional[str] = None
    injury_type: Optional[str] = None
    facts: str
    injuries: str
    economic_damages: str

class CaseSearchRequest(BaseModel):
    subject_case: SubjectCase
    session_id: Optional[str] = None

# Response models
class CaseAnalysisResponse(BaseModel):
    prediction: str
    similar_cases: List[Dict[str, Any]]
    quota_remaining: Optional[int] = None

@router.post("/search", response_model=CaseAnalysisResponse)
async def search_similar_cases(
    request: CaseSearchRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search for similar cases and analyze the subject case.
    This endpoint requires an active subscription with available quota.
    """
    # Extract user info from Auth0 token
    auth0_id = user.get("sub")
    if not auth0_id:
        error_logger.error(f"Invalid user ID in token: {user}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID in token"
        )

    # Get or create user
    try:
        email = user.get("email", "")
        name = user.get("name", "")
        app_logger.info(f"Processing request for user: {auth0_id}, email: {email}")
        db_user = SubscriptionService.get_or_create_user(db, auth0_id, email, name)
    except Exception as e:
        error_logger.error(f"Error getting or creating user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing user information: {str(e)}"
        )
    
    # Check subscription quota
    try:
        app_logger.info(f"Checking subscription quota for user: {auth0_id}")
        remaining_quota = SubscriptionService.check_and_decrement_quota(db, db_user.id)
        app_logger.info(f"Remaining quota for user {auth0_id}: {remaining_quota}")
    except HTTPException as e:
        # If subscription check fails, return appropriate error
        error_logger.warning(f"Subscription check failed for user {auth0_id}: {str(e.detail)}")
        raise e
    except Exception as e:
        # Handle any other errors
        error_logger.error(f"Subscription error for user {auth0_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Subscription error: {str(e)}"
        )
    
    try:
        # Prepare subject case dict for processing
        subject_case_dict = request.subject_case.dict()
        
        # Call the get_similar_cases function directly
        app_logger.info(f"Retrieving similar cases for user {auth0_id}")
        similar_cases = get_similar_cases(subject_case_dict)
        
        # Call the analyze_case function directly
        app_logger.info(f"Analyzing case for user {auth0_id}")
        prediction = analyze_case(subject_case_dict, similar_cases)
        
        # Record the case analysis in the database
        app_logger.info(f"Recording case analysis for user {auth0_id}")
        SubscriptionService.record_case_analysis(
            db, 
            db_user.id, 
            subject_case_dict, 
            prediction, 
            similar_cases
        )
        
        # Return the results along with remaining quota
        app_logger.info(f"Case analysis completed successfully for user {auth0_id}")
        return {
            "prediction": prediction,
            "similar_cases": similar_cases,
            "quota_remaining": remaining_quota
        }
    
    except Exception as e:
        # Handle any errors in the analysis process
        error_logger.error(f"Error analyzing case for user {auth0_id}: {str(e)}", exc_info=True)
        
        # Determine the type of error for better user feedback
        if "pinecone" in str(e).lower():
            error_detail = "Error retrieving similar cases from database"
        elif "openai" in str(e).lower() or "api key" in str(e).lower():
            error_detail = "Error generating case analysis"
        else:
            error_detail = f"Error analyzing case: {str(e)}"
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )

@router.get("/history")
async def get_case_history(
    skip: int = 0, 
    limit: int = 10,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's case analysis history"""
    auth0_id = user.get("sub")
    if not auth0_id:
        error_logger.error(f"Invalid user ID in token for history request: {user}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID in token"
        )
    
    try:
        app_logger.info(f"Retrieving case history for user: {auth0_id}")
        # Get case analyses for the user
        analyses = SubscriptionService.get_case_analyses_from_auth0_id(db, auth0_id, skip, limit)
        
        # Format the response
        result = []
        for analysis in analyses:
            result.append({
                "id": analysis.id,
                "created_at": analysis.created_at.isoformat(),
                "subject_case": analysis.subject_case,
                "prediction": analysis.prediction
            })
        
        app_logger.info(f"Retrieved {len(result)} case analyses for user {auth0_id}")
        return result
    
    except HTTPException as e:
        error_logger.warning(f"HTTP exception in case history for user {auth0_id}: {str(e.detail)}")
        raise e
    except Exception as e:
        error_logger.error(f"Error retrieving case history for user {auth0_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving case history: {str(e)}"
        )
