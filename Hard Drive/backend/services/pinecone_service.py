import os
import json
import random
from typing import Dict, List, Any

# Mock Pinecone client and constants
pc = object()  # Mock Pinecone client
INDEX_NAME = "legal-case-index"  # This was in the original code

# Mock similar cases function that returns dummy data
def get_similar_cases(case_dict: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    A temporary mock function that returns dummy similar cases.
    This is used to bypass the Pinecone and SentenceTransformer issues.
    
    Args:
        case_dict: Dictionary containing case details
        top_k: Number of similar cases to return
        
    Returns:
        List of dictionaries with similar case data
    """
    print(f"Mock get_similar_cases called with case: {case_dict}")
    
    # Create dummy similar cases
    similar_cases = [
        {
            "court": "Superior Court",
            "date": "2022-05-15",
            "claim_type": "Personal Injury",
            "injury_type": "Back Injury",
            "facts": "Plaintiff slipped on wet floor in grocery store",
            "injuries": "Lower back sprain requiring 8 weeks of physical therapy",
            "economic_damages": "$8,500",
            "result": "$23,000"
        },
        {
            "court": "District Court",
            "date": "2023-02-10",
            "claim_type": "Personal Injury",
            "injury_type": "Neck Injury",
            "facts": "Rear-end collision at low speed",
            "injuries": "Whiplash requiring 4 weeks of treatment",
            "economic_damages": "$4,200",
            "result": "$12,500"
        },
        {
            "court": "Circuit Court",
            "date": "2021-11-22",
            "claim_type": "Personal Injury",
            "injury_type": "Shoulder Injury",
            "facts": "Fall due to unmarked wet floor",
            "injuries": "Rotator cuff strain",
            "economic_damages": "$6,300",
            "result": "$18,750"
        }
    ]
    
    # Return the number of cases requested
    return similar_cases[:min(top_k, len(similar_cases))]

# Additional functions that might be needed by the application
def initialize_pinecone():
    """Mock initialization function"""
    print("Mock Pinecone initialization")
    return True
