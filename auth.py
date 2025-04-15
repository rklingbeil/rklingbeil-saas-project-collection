# File: /Users/rick/CaseProject/backend/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
from jose import jwt, JWTError

# Auth0 configuration – update these values with your actual Auth0 settings.
AUTH0_DOMAIN = "dev-wmydj4rlx48n5trz.us.auth0.com"
API_AUDIENCE = "https://my-saas-app.local/api"  # Ensure this exactly matches your token’s aud claim.
ALGORITHMS = ["RS256"]

# Set up HTTPBearer to extract the token from the Authorization header.
auth_scheme = HTTPBearer()

def get_auth0_public_keys():
    """
    Retrieves Auth0's JSON Web Key Set (JWKS) from the well-known URL.
    """
    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    response = requests.get(jwks_url)
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve JWKS from Auth0"
        )
    return response.json()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """
    Validates the JWT token issued by Auth0 using Auth0's public keys.
    If valid, returns the decoded token payload.
    Otherwise, raises an HTTP 401 error with debugging information.
    """
    token = credentials.credentials
    jwks = get_auth0_public_keys()
    unverified_header = jwt.get_unverified_header(token)
    print("Unverified token header:", unverified_header)  # Debug output

    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header.get("kid"):
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
            break

    print("RSA key used for verification:", rsa_key)  # Debug output

    if not rsa_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not find an appropriate key"
        )
    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        return payload
    except JWTError as e:
        # Print the detailed error for debugging.
        print("JWTError during token decoding:", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: " + str(e)
        )

# Create an APIRouter instance for endpoints.
router = APIRouter()

@router.get("/users/me")
def read_users_me(user: dict = Depends(get_current_user)):
    """
    A simple endpoint that returns the current user's information (decoded token payload).
    """
    return user

