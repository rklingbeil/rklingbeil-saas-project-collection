from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import CORS
import os
import requests
import json
from jose import jwt
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # This is for handling Cross-Origin Resource Sharing (CORS)

# Auth0 configuration
AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN', 'dev-wmydj4rlx48n5trz.us.auth0.com')
API_AUDIENCE = os.environ.get('AUTH0_API_AUDIENCE', 'https://my-saas-app.local/api')
ALGORITHMS = ["RS256"]

# Helper function to get Auth0's public keys
def get_auth0_public_keys():
    """
    Retrieves Auth0's JSON Web Key Set (JWKS) from the well-known URL.
    """
    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    response = requests.get(jwks_url)
    if response.status_code != 200:
        return jsonify({"error": "Failed to retrieve JWKS from Auth0"}), 500
    return response.json()

# Authentication decorator
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            return jsonify({"error": "Authorization header is missing"}), 401
        
        try:
            # Extract token from header
            token_parts = auth_header.split()
            if token_parts[0].lower() != 'bearer' or len(token_parts) != 2:
                return jsonify({"error": "Invalid Authorization header format"}), 401
            token = token_parts[1]
            
            # Get the key id from the token
            unverified_header = jwt.get_unverified_header(token)
            jwks = get_auth0_public_keys()
            
            # Find the matching key
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
            
            if not rsa_key:
                return jsonify({"error": "Could not find an appropriate key"}), 401
            
            # Verify the token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f"https://{AUTH0_DOMAIN}/"
            )
            
            # Add the payload to the request context
            request.auth_payload = payload
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.JWTClaimsError:
            return jsonify({"error": "Invalid claims, please check audience and issuer"}), 401
        except Exception as e:
            return jsonify({"error": f"Could not validate credentials: {str(e)}"}), 401
            
    return decorated

# Simple health check endpoint
@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "message": "SaaS Case Analysis API is running"}), 200

# Auth endpoint to get user profile
@app.route("/api/auth/users/profile", methods=["GET"])
@requires_auth
def get_user_profile():
    # Extract user info from the token
    user_info = {
        "user_id": request.auth_payload.get("sub", ""),
        "email": request.auth_payload.get("email", ""),
        "name": request.auth_payload.get("name", "")
    }
    return jsonify(user_info), 200

# Cases search endpoint (placeholder)
@app.route("/api/cases/search", methods=["POST"])
@requires_auth
def search_cases():
    # This would normally process the case data and return analysis
    # For now, just return a placeholder response
    return jsonify({
        "prediction": "Sample prediction",
        "confidence": 0.85,
        "similar_cases": [
            {"id": 1, "title": "Sample Case 1", "similarity": 0.9},
            {"id": 2, "title": "Sample Case 2", "similarity": 0.8}
        ]
    }), 200

# Run the app on all interfaces (0.0.0.0) so it's accessible from any device in the network
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
