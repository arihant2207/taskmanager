import os
import jwt
import traceback
from jwt import PyJWKClient
from functools import wraps
from flask import request, jsonify
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL") or os.getenv("SUPABASE_PROJECT_URL", "")
jwks_url = f"{supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
jwk_client = PyJWKClient(jwks_url, cache_keys=True, timeout=10)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print(f"[AUTH START] Verifying auth for path: {request.path}", flush=True)
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                print("[AUTH ERROR] Authorization header is missing", flush=True)
                return jsonify({'error': 'Authorization header missing'}), 401
            
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                print("[AUTH ERROR] Invalid Authorization header format", flush=True)
                return jsonify({'error': 'Invalid Authorization header format. Expected "Bearer <token>"'}), 401
            
            token = parts[1]

            print("[AUTH TRACE] Fetching signing key from JWKS...", flush=True)
            signing_key = jwk_client.get_signing_key_from_jwt(token)
            print("[AUTH TRACE] Decoding JWT token...", flush=True)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256", "RS256"],
                audience="authenticated"
            )
            request.user_id = payload.get('sub')
            if not request.user_id:
                print("[AUTH ERROR] Token missing 'sub' claim", flush=True)
                return jsonify({'error': 'Invalid token: missing sub claim'}), 401
            
            print(f"[AUTH SUCCESS] Authenticated user_id: {request.user_id}", flush=True)
            return f(*args, **kwargs)
        except Exception as e:
            print(f"[AUTH EXCEPTION] Authentication failed: {e}", flush=True)
            traceback.print_exc()
            return jsonify({'error': f'Invalid token: {str(e)}'}), 401
    
    return decorated
