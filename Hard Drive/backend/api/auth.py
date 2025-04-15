# File: /Users/rick/CaseProject/backend/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
from jose import jwt

# Auth0 configuration
AUTH0_DOMAIN = "dev-wmydj4rlx48n5trz.us.auth0.com"
API_AUDIENCE = "https://my-saas-app.local/api"
ALGORITHMS = ["RS256"]

# Set up HTTPBearer to extract the token from the Authorization header
auth_scheme = HTTPBearer()

# Create an APIRouter instance for endpoints
router = APIRouter()

def get_jwks():
    """
    Retrieves the JWKS from Auth0
    """
    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    response = requests.get(jwks_url)
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve JWKS from Auth0: {response.status_code}"
        )
    return response.json()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """
    TEMPORARY: Bypass Auth0 validation and return a dummy user
    """
    # Return a dummy user for testing purposes
    return {
        "sub": "auth0|123456789",
        "email": "rick@klingbeil-law.com",
        "name": "Rick Klingbeil",
        "picture": "https://example.com/profile.jpg",
        "email_verified": True
    }
    
    # ORIGINAL CODE (Commented out for now)
    """
    token = credentials.credentials
    
    try:
        # Decode the token header without verification to get the key ID
        unverified_header = jwt.get_unverified_header(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token header: {str(e)}"
        )
    
    # Get the key ID from the header
    kid = unverified_header.get("kid")
    if not kid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No key ID found in token header"
        )
    
    # Get the JWKS from Auth0
    jwks = get_jwks()
    
    # Find the matching key in JWKS
    rsa_key = None
    for key in jwks["keys"]:
        if key["kid"] == kid:
            rsa_key = key
            break
    
    if not rsa_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No matching key found for this token"
        )
    
    try:
        # Use Auth0 public key to verify token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTClaimsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid claims: {str(e)}"
        )
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}"
        )
    """

@router.get("/users/me")
def read_users_me(user: dict = Depends(get_current_user)):
    """
    Returns the current user's information (decoded token payload)
    """
    return user

# Enhanced user info endpoint to get full profile from Auth0
@router.get("/users/profile")
async def get_user_profile(user: dict = Depends(get_current_user)):
    """
    Get detailed user profile information from Auth0 Management API
    """
    # Extract user_id from the token
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID not found in token"
        )
        
    # For now, return the token information
    # In a future enhancement, we could use the Management API to get more user details
    return {
        "user_id": user_id,
        "email": user.get("email", ""),
        "name": user.get("name", ""),
        "picture": user.get("picture", ""),
        "email_verified": user.get("email_verified", False)
    }

@router.post("/client-token")
async def get_client_token():
    """
    Proxy endpoint to get a token using client credentials flow.
    This keeps the client secret secure on the server side.
    """
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    payload = {
        "client_id": "WvY1U2l9FY3xbHtnWLLSEyAWBeXi1Y6h",
        "client_secret": "oydmJakj1qEIBAcTmcP1kC-lUb_UFEa4HRc-Cd1XqozZfBkFbvHF9n4N-VXfeoAP",
        "audience": API_AUDIENCE,
        "grant_type": "client_credentials"
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(token_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get token: {str(e)}"
        )
