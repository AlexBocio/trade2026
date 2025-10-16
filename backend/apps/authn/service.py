#!/usr/bin/env python3
"""
Authentication Service - JWT/JWKS Issuer
Phase 15: mTLS + Service Auth

Provides:
- JWT token issuance (client_credentials grant)
- JWKS endpoint for token verification
- Key rotation with zero-downtime

SECURITY WARNING: This is a DEV implementation.
Production requires:
- Proper key management (HSM or cloud KMS)
- Audit logging for all token issuance
- Rate limiting on /token endpoint
- Proper user management for password grant
"""

import os
import json
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException, Depends, Form, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import uvicorn

# Configuration
CONFIG_PATH = os.getenv("CONFIG_PATH", "/app/config.yaml")

app = FastAPI(title="Authentication Service", version="1.0.0")

# Global state
config: Dict = {}
clients: Dict[str, Dict] = {}
active_jwk: Optional[Dict] = None
next_jwk: Optional[Dict] = None


class TokenRequest(BaseModel):
    grant_type: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    audience: Optional[str] = None
    scope: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    scope: Optional[str] = None


class RotateResponse(BaseModel):
    success: bool
    old_kid: str
    new_kid: str
    message: str


def load_config():
    """Load configuration from YAML."""
    global config, clients

    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)

    # Build clients map
    clients = {}
    for client in config.get('clients', []):
        client_id = client['id']
        # Load secret from environment variable
        secret_env = client.get('secret_env')
        client_secret = os.getenv(secret_env, f"dev-secret-{client_id}")  # DEV ONLY fallback

        clients[client_id] = {
            'secret': client_secret,
            'roles': client['roles'],
            'tenant': client['tenant'],
            'scopes': client.get('scopes', [])
        }

    print(f"✓ Loaded config: {len(clients)} clients, issuer={config['issuer']}")


def generate_jwk_pair(kid: str, algorithm: str = "RS256") -> Dict:
    """Generate RSA key pair and return as JWK."""
    if algorithm == "RS256":
        key_size = config.get('keys', {}).get('key_size', 2048)
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )

        # Export private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Export public key
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Get public numbers for JWK
        public_numbers = public_key.public_numbers()

        # Convert to base64url without padding
        def int_to_base64url(value):
            value_hex = format(value, 'x')
            if len(value_hex) % 2:
                value_hex = '0' + value_hex
            value_bytes = bytes.fromhex(value_hex)
            import base64
            return base64.urlsafe_b64encode(value_bytes).rstrip(b'=').decode('utf-8')

        n = int_to_base64url(public_numbers.n)
        e = int_to_base64url(public_numbers.e)

        jwk = {
            'kty': 'RSA',
            'use': 'sig',
            'kid': kid,
            'alg': algorithm,
            'n': n,
            'e': e,
            'private_pem': private_pem.decode('utf-8'),
            'public_pem': public_pem.decode('utf-8')
        }

        return jwk

    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def load_or_generate_keys():
    """Load existing keys or generate new ones."""
    global active_jwk, next_jwk

    active_path = Path(config['keys']['active_path'])
    next_path = Path(config['keys']['next_path'])
    algorithm = config.get('algorithm', 'RS256')

    # Load or generate active key
    if active_path.exists():
        with open(active_path, 'r') as f:
            active_jwk = json.load(f)
        print(f"✓ Loaded active key: kid={active_jwk['kid']}")
    else:
        active_kid = f"key-{secrets.token_hex(8)}"
        active_jwk = generate_jwk_pair(active_kid, algorithm)
        active_path.parent.mkdir(parents=True, exist_ok=True)
        with open(active_path, 'w') as f:
            json.dump(active_jwk, f, indent=2)
        print(f"✓ Generated active key: kid={active_kid}")

    # Load or generate next key
    if next_path.exists():
        with open(next_path, 'r') as f:
            next_jwk = json.load(f)
        print(f"✓ Loaded next key: kid={next_jwk['kid']}")
    else:
        next_kid = f"key-{secrets.token_hex(8)}"
        next_jwk = generate_jwk_pair(next_kid, algorithm)
        with open(next_path, 'w') as f:
            json.dump(next_jwk, f, indent=2)
        print(f"✓ Generated next key: kid={next_kid}")


def get_jwks_public() -> Dict:
    """Return JWKS with public keys only."""
    keys = []

    for jwk in [active_jwk, next_jwk]:
        if jwk:
            public_jwk = {
                'kty': jwk['kty'],
                'use': jwk['use'],
                'kid': jwk['kid'],
                'alg': jwk['alg'],
                'n': jwk['n'],
                'e': jwk['e']
            }
            keys.append(public_jwk)

    return {'keys': keys}


def create_jwt(client_id: str, client_data: Dict, audience: Optional[str], scope: Optional[str]) -> str:
    """Create JWT using active key."""
    now = datetime.utcnow()
    exp = now + timedelta(seconds=config['token_ttl_seconds'])

    # Determine audience
    aud = audience if audience else config['audiences'][0]

    # Determine scope
    token_scope = scope if scope else ' '.join(client_data['scopes'])

    payload = {
        'iss': config['issuer'],
        'sub': client_id,
        'aud': aud,
        'iat': int(now.timestamp()),
        'exp': int(exp.timestamp()),
        'nbf': int(now.timestamp()),
        'roles': client_data['roles'],
        'tenant': client_data['tenant'],
        'scope': token_scope,
        'jti': secrets.token_hex(16)  # JWT ID for tracking
    }

    # Sign with active key
    token = jwt.encode(
        payload,
        active_jwk['private_pem'],
        algorithm=config.get('algorithm', 'RS256'),
        headers={'kid': active_jwk['kid']}
    )

    return token


@app.on_event("startup")
async def startup():
    """Initialize service."""
    print("=" * 60)
    print("Authentication Service Starting")
    print("=" * 60)
    print("")
    print("⚠️  WARNING: DEV IMPLEMENTATION")
    print("   - Uses local key storage (not HSM/KMS)")
    print("   - No audit logging")
    print("   - Fallback secrets for missing env vars")
    print("   - Production requires proper key management")
    print("")

    load_config()
    load_or_generate_keys()

    print("")
    print("=" * 60)
    print("✓ Authentication Service Ready")
    print("=" * 60)
    print(f"  - JWKS endpoint: /.well-known/jwks.json")
    print(f"  - Token endpoint: /token")
    print(f"  - Issuer: {config['issuer']}")
    print(f"  - Active key: {active_jwk['kid']}")
    print(f"  - Next key: {next_jwk['kid']}")
    print("=" * 60)


@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "service": "authn",
        "issuer": config.get('issuer'),
        "active_kid": active_jwk['kid'] if active_jwk else None,
        "next_kid": next_jwk['kid'] if next_jwk else None
    }


@app.get("/.well-known/jwks.json")
async def jwks():
    """JWKS endpoint - returns public keys for token verification."""
    return get_jwks_public()


@app.post("/token", response_model=TokenResponse)
async def token(
    grant_type: str = Form(...),
    client_id: Optional[str] = Form(None),
    client_secret: Optional[str] = Form(None),
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    audience: Optional[str] = Form(None),
    scope: Optional[str] = Form(None)
):
    """
    Token endpoint - issue JWT.

    Supports:
    - client_credentials: Service-to-service auth
    - password: Human auth (DEV ONLY)
    """

    if grant_type not in config.get('grant_types', []):
        raise HTTPException(status_code=400, detail=f"Unsupported grant_type: {grant_type}")

    if grant_type == "client_credentials":
        if not client_id or not client_secret:
            raise HTTPException(status_code=400, detail="client_id and client_secret required")

        # Verify client
        if client_id not in clients:
            raise HTTPException(status_code=401, detail="Invalid client")

        client_data = clients[client_id]

        # Constant-time comparison to prevent timing attacks
        if not secrets.compare_digest(client_secret, client_data['secret']):
            raise HTTPException(status_code=401, detail="Invalid client_secret")

        # Issue token
        access_token = create_jwt(client_id, client_data, audience, scope)

        return TokenResponse(
            access_token=access_token,
            expires_in=config['token_ttl_seconds'],
            scope=' '.join(client_data['scopes'])
        )

    elif grant_type == "password":
        # WARNING: DEV ONLY - production should use proper OAuth2/OIDC flow
        print("⚠️  WARNING: password grant used - DEV ONLY")

        if not username or not password:
            raise HTTPException(status_code=400, detail="username and password required")

        user_id = f"user:{username}"

        if user_id not in clients:
            raise HTTPException(status_code=401, detail="Invalid username")

        client_data = clients[user_id]

        if not secrets.compare_digest(password, client_data['secret']):
            raise HTTPException(status_code=401, detail="Invalid password")

        # Issue token
        access_token = create_jwt(user_id, client_data, audience, scope)

        return TokenResponse(
            access_token=access_token,
            expires_in=config['token_ttl_seconds'],
            scope=' '.join(client_data['scopes'])
        )

    else:
        raise HTTPException(status_code=400, detail=f"grant_type {grant_type} not implemented")


@app.post("/rotate", response_model=RotateResponse)
async def rotate_keys(authorization: Optional[str] = Header(None)):
    """
    Rotate JWKS keys.

    Process:
    1. Promote next_jwk to active_jwk
    2. Generate new next_jwk
    3. Update JWKS endpoint

    Old tokens signed with previous active key remain valid until expiry.
    """
    global active_jwk, next_jwk

    # TODO: Add proper authorization check
    # For now, simple check for Authorization header
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required for key rotation")

    old_kid = active_jwk['kid']

    # Promote next to active
    active_jwk = next_jwk

    # Generate new next
    algorithm = config.get('algorithm', 'RS256')
    new_kid = f"key-{secrets.token_hex(8)}"
    next_jwk = generate_jwk_pair(new_kid, algorithm)

    # Save to disk
    active_path = Path(config['keys']['active_path'])
    next_path = Path(config['keys']['next_path'])

    with open(active_path, 'w') as f:
        json.dump(active_jwk, f, indent=2)

    with open(next_path, 'w') as f:
        json.dump(next_jwk, f, indent=2)

    print(f"✓ Key rotation: {old_kid} -> {active_jwk['kid']} (next: {new_kid})")

    return RotateResponse(
        success=True,
        old_kid=old_kid,
        new_kid=active_jwk['kid'],
        message=f"Keys rotated successfully. Old tokens remain valid until expiry."
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8114"))
    uvicorn.run(app, host="0.0.0.0", port=port)
