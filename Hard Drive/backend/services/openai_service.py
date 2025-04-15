# File: /Users/rick/CaseProject/backend/services/openai_service.py

import os
import time
import json
from openai import OpenAI
from openai import APIError, RateLimitError, APIConnectionError, AuthenticationError
from utils.logger import app_logger, error_logger

# Maximum number of retries for transient errors
MAX_RETRIES = 3
# Base delay for exponential backoff (in seconds)
BASE_DELAY = 1

# Retrieve the API key from the environment variable.
API_KEY = os.getenv("OPENAI_API_KEY")
if API_KEY is None:
    error_msg = "OPENAI_API_KEY environment variable not set"
    error_logger.error(error_msg)
    raise EnvironmentError(error_msg)

# Create an OpenAI client using the new interface.
try:
    client = OpenAI(api_key=API_KEY)
    app_logger.info("OpenAI client initialized successfully")
except Exception as e:
    error_logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    raise

def format_case_details(case: dict) -> str:
    """
    Formats the case details from a dictionary into a readable string.
    Handles various formats of economic damages data.
    """
    # Get economic damages - check multiple possible field names
    economic_damages = None
    
    # Check for direct economic_damages field
    if 'economic_damages' in case and case['economic_damages']:
        economic_damages = case['economic_damages']
    # Check for specials field which may contain economic damages info
    elif 'specials' in case and case['specials']:
        economic_damages = case['specials']
    # Check for specials_values field
    elif 'specials_values' in case and case['specials_values']:
        economic_damages = case['specials_values']
    # Check for result field which might contain settlement info
    elif 'result' in case and case['result']:
        economic_damages = f"Settlement/Verdict: {case['result']}"
    
    return (
        f"Court: {case.get('court', 'N/A')}\n"
        f"Date: {case.get('date', 'N/A')}\n"
        f"Plaintiff Medical Expert: {case.get('plaintiff_medical_expert', 'N/A')}\n"
        f"Defense Medical Expert: {case.get('defense_medical_expert', 'N/A')}\n"
        f"Plaintiff Expert: {case.get('plaintiff_expert', 'N/A')}\n"
        f"Defense Expert: {case.get('defense_expert', 'N/A')}\n"
        f"Judge/Arbitrator/Mediator: {case.get('judge_arbitrator_mediator', 'N/A')}\n"
        f"Insurance Company: {case.get('insurance_company', 'N/A')}\n"
        f"Claim Type: {case.get('claim_type', 'N/A')}\n"
        f"Injury Type: {case.get('injury_type', 'N/A')}\n"
        f"Facts: {case.get('facts', 'N/A')}\n"
        f"Injuries: {case.get('injuries', 'N/A')}\n"
        f"Economic Damages: {economic_damages if economic_damages else 'N/A'}\n"
    )

def analyze_case(subject_case: dict, similar_cases: list) -> str:
    """
    Analyzes the provided Subject Case by constructing a detailed prompt that includes:
      - The subject case details.
      - Summaries of multiple similar cases.
    The prompt instructs GPT-4 to compare the Subject Case with the Similar Cases and predict a settlement or verdict value.
    
    Parameters:
      subject_case: A dictionary with details of the Subject Case.
      similar_cases: A list of dictionaries, each containing details of a Similar Case.
    
    Returns:
      A prediction string from GPT-4.
    """
    # Format the Subject Case details
    subject_text = format_case_details(subject_case)

    # Format each Similar Case
    similar_cases_text = ""
    for idx, case in enumerate(similar_cases, start=1):
        similar_cases_text += f"Similar Case {idx}:\n{format_case_details(case)}\n"

    # Construct the full prompt
    prompt = (
        "You are a legal expert tasked with analyzing a provided civil legal case (the 'Subject Case') "
        "and comparing it with historical cases (the 'Similar Cases') to predict a settlement or verdict value.\n\n"
        "Step 1: Understand the Subject Case.\n"
        f"{subject_text}\n"
        "Step 2: Analyze the Similar Cases.\n"
        f"{similar_cases_text}\n"
        "Based on your analysis of the Subject Case and the Similar Cases, predict a settlement or verdict value. "
        "Provide a single predicted value (e.g., '$75,000'), state the confidence level (High, Moderate, or Low), and summarize the key factors that influenced your prediction."
    )

    app_logger.info("Sending case analysis request to OpenAI")
    
    # Implement retry logic with exponential backoff
    retry_count = 0
    while True:
        try:
            # Call the ChatGPT API with the constructed prompt.
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=300
            )
            
            prediction = response.choices[0].message.content.strip()
            app_logger.info("Successfully received case analysis from OpenAI")
            return prediction
            
        except RateLimitError as e:
            # Handle rate limit errors with proper retries
            retry_count += 1
            if retry_count > MAX_RETRIES:
                error_logger.error(f"OpenAI rate limit exceeded after {MAX_RETRIES} retries: {str(e)}")
                raise Exception(f"OpenAI service unavailable due to rate limiting. Please try again later.")
            
            # Calculate exponential backoff delay
            delay = BASE_DELAY * (2 ** (retry_count - 1))
            error_logger.warning(f"OpenAI rate limit hit, retrying in {delay} seconds (attempt {retry_count}/{MAX_RETRIES})")
            time.sleep(delay)
            
        except APIConnectionError as e:
            # Handle connection errors with retries
            retry_count += 1
            if retry_count > MAX_RETRIES:
                error_logger.error(f"OpenAI connection error after {MAX_RETRIES} retries: {str(e)}")
                raise Exception(f"Could not connect to OpenAI service. Please check your network connection and try again.")
            
            delay = BASE_DELAY * (2 ** (retry_count - 1))
            error_logger.warning(f"OpenAI connection error, retrying in {delay} seconds (attempt {retry_count}/{MAX_RETRIES})")
            time.sleep(delay)
            
        except AuthenticationError as e:
            # Authentication errors should not be retried
            error_logger.error(f"OpenAI authentication error: {str(e)}")
            raise Exception(f"Authentication error with OpenAI. Please check your API key configuration.")
            
        except APIError as e:
            # Other API errors with potential retries
            retry_count += 1
            if retry_count > MAX_RETRIES:
                error_logger.error(f"OpenAI API error after {MAX_RETRIES} retries: {str(e)}")
                raise Exception(f"Error in OpenAI service: {str(e)}")
            
            # Only retry 5xx errors, don't retry 4xx errors
            if hasattr(e, 'http_status') and 500 <= e.http_status < 600:
                delay = BASE_DELAY * (2 ** (retry_count - 1))
                error_logger.warning(f"OpenAI server error, retrying in {delay} seconds (attempt {retry_count}/{MAX_RETRIES})")
                time.sleep(delay)
            else:
                error_logger.error(f"OpenAI client error: {str(e)}")
                raise Exception(f"Error with OpenAI request: {str(e)}")
                
        except Exception as e:
            # Log and re-raise any other unexpected errors
            error_logger.error(f"Unexpected error in OpenAI service: {str(e)}", exc_info=True)
            raise Exception(f"Unexpected error in case analysis: {str(e)}")

if __name__ == "__main__":
    # Sample Subject Case details for testing.
    sample_subject_case = {
        "court": "Superior Court",
        "date": "2025-01-15",
        "plaintiff_medical_expert": "Dr. Smith",
        "defense_medical_expert": "Dr. Johnson",
        "plaintiff_expert": "Expert A",
        "defense_expert": "Expert B",
        "judge_arbitrator_mediator": "Judge Williams",
        "insurance_company": "ABC Insurance",
        "claim_type": "Personal Injury",
        "injury_type": "Back Injury",
        "facts": "The plaintiff suffered a back injury in a car accident.",
        "injuries": "Severe back pain, limited mobility",
        "specials": "$50,000 in economic damages",
        "specials_values": "$50,000"
    }
    
    # Sample Similar Cases details for testing.
    sample_similar_cases = [
        {
            "court": "Arbitration - Multnomah County",
            "date": "9/15/11",
            "plaintiff_medical_expert": "Dr. A",
            "defense_medical_expert": "Dr. B",
            "plaintiff_expert": "Expert X",
            "defense_expert": "Expert Y",
            "judge_arbitrator_mediator": "Judge Z",
            "insurance_company": "XYZ Insurance",
            "claim_type": "Personal Injury",
            "injury_type": "Back Injury",
            "facts": "The plaintiff suffered a back injury in a similar accident.",
            "injuries": "Moderate back pain",
            "specials": "$40,000 in economic damages",
            "specials_values": "$40,000"
        },
        {
            "court": "Arbitration - Clackamas County",
            "date": "10/20/10",
            "plaintiff_medical_expert": "Dr. C",
            "defense_medical_expert": "Dr. D",
            "plaintiff_expert": "Expert M",
            "defense_expert": "Expert N",
            "judge_arbitrator_mediator": "Judge Q",
            "insurance_company": "LMN Insurance",
            "claim_type": "Personal Injury",
            "injury_type": "Back Injury",
            "facts": "A similar incident with severe back injury.",
            "injuries": "Severe back injury",
            "specials": "$60,000 in economic damages",
            "specials_values": "$60,000"
        }
    ]
    
    try:
        result = analyze_case(sample_subject_case, sample_similar_cases)
        print("Prediction:", result)
    except Exception as e:
        print(f"Error testing OpenAI service: {str(e)}")
