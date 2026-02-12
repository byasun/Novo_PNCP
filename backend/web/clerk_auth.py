# Clerk JWT validation for Flask
# Place this file as clerk_auth.py in backend/web/
import requests
import jwt
from flask import request, jsonify
from functools import wraps


# Clerk settings from .env (via settings.py)
from backend.config.settings import _get_env
CLERK_ISSUER = _get_env("CLERK_ISSUER", "https://api.clerk.dev")
CLERK_JWKS_URL = _get_env("CLERK_JWKS_URL", f"{CLERK_ISSUER}/v1/jwks")
CLERK_AUDIENCE = _get_env("CLERK_AUDIENCE", None)

_jwks_cache = None

def get_clerk_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        resp = requests.get(CLERK_JWKS_URL, verify=False)
        resp.raise_for_status()
        _jwks_cache = resp.json()
    return _jwks_cache

def verify_clerk_jwt(token):
    jwks = get_clerk_jwks()
    unverified_header = jwt.get_unverified_header(token)
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
            break
    else:
        raise Exception("Public key not found in JWKS")
    payload = jwt.decode(
        token,
        public_key,
        algorithms=[unverified_header["alg"]],
        audience=CLERK_AUDIENCE,
        issuer=CLERK_ISSUER,
        options={"verify_aud": CLERK_AUDIENCE is not None}
    )
    return payload

def clerk_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        print(f"[ClerkAuth] Authorization header recebido: {auth_header}")
        if not auth_header.startswith("Bearer "):
            print("[ClerkAuth] Header ausente ou inválido.")
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            user_payload = verify_clerk_jwt(token)
            request.clerk_user = user_payload
        except Exception as e:
            print(f"[ClerkAuth] Erro ao validar JWT: {str(e)}")
            return jsonify({"error": f"Invalid token: {str(e)}"}), 401
        return f(*args, **kwargs)
    return decorated
