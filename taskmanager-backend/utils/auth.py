import os
import jwt
from jwt import PyJWKClient
from functools import wraps
from flask import request, jsonify
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL") or os.getenv("SUPABASE_PROJECT_URL", "")
jwks_url = f"{supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
jwk_client = PyJWKClient(jwks_url)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            print("[AUTH ERROR] Authorization header is missing")
            return jsonify({'error': 'Authorization header missing'}), 401
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            print("[AUTH ERROR] Invalid Authorization header format")
            return jsonify({'error': 'Invalid Authorization header format. Expected "Bearer <token>"'}), 401
        
        token = parts[1]

        try:
            signing_key = jwk_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256", "RS256"],
                audience="authenticated"
            )
            request.user_id = payload.get('sub')
            if not request.user_id:
                print("[AUTH ERROR] Token missing 'sub' claim")
                return jsonify({'error': 'Invalid token: missing sub claim'}), 401
        except Exception as e:
            print(f"[AUTH ERROR] JWT verification failed: {e}")
            return jsonify({'error': f'Invalid token: {str(e)}'}), 401

        return f(*args, **kwargs)
    
    return decorated
