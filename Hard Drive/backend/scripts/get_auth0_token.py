# File: /Users/rick/CaseProject/backend/scripts/get_auth0_token.py

import requests
import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path='../.env')

# Get Auth0 configuration from environment variables
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
API_AUDIENCE = os.getenv('API_AUDIENCE')

def get_token():
    """
    Gets a test token from Auth0 using the client credentials flow.
    This is for testing API endpoints that require authentication.
    """
    # Get client credentials from command line arguments or prompt user
    if len(sys.argv) >= 3:
        client_id = sys.argv[1]
        client_secret = sys.argv[2]
    else:
        client_id = input("Enter your Auth0 client ID: ")
        client_secret = input("Enter your Auth0 client secret: ")
    
    # Auth0 token endpoint
    url = f"https://{AUTH0_DOMAIN}/oauth/token"
    
    # Prepare request payload
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": API_AUDIENCE,
        "grant_type": "client_credentials"
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        # Make the request to Auth0
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        # Parse the response
        token_data = response.json()
        
        # Print the token and useful information
        print("\nAuth0 Token:")
        print(token_data["access_token"])
        print("\nToken Type:", token_data["token_type"])
        print("Expires In:", token_data["expires_in"], "seconds")
        
        # Save the token to a file for convenience
        with open("auth0_token.txt", "w") as f:
            f.write(token_data["access_token"])
        print("\nToken saved to auth0_token.txt")
        
        # Print a curl example for testing
        print("\nExample curl command for testing:")
        print(f'curl -X GET http://localhost:8000/auth/users/me -H "Authorization: Bearer {token_data["access_token"]}"')
        
    except requests.exceptions.RequestException as e:
        print(f"Error getting token: {e}")
        if hasattr(e, 'response') and e.response:
            print("Response:", e.response.text)
        sys.exit(1)

if __name__ == "__main__":
    get_token()
