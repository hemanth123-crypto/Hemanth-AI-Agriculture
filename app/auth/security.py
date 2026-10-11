"""
app/auth/security.py
Security utilities: password hashing (PBKDF2-HMAC-SHA256 with per-user salt)
and standard RFC 7519 HMAC-SHA256 (HS256) JSON Web Token (JWT) generation & validation.
"""

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Optional, Dict, Any
from app.config.settings import settings

# Default secret key for token signing (can be configured in settings/.env)
JWT_SECRET_KEY = getattr(settings, "JWT_SECRET_KEY", "cropshield_agri_ai_secure_token_secret_key_2026_x99")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_SECONDS = 30 * 24 * 3600  # 30 days session validity


def generate_salt() -> str:
    """Generate a cryptographically secure 16-byte hex salt."""
    return secrets.token_hex(16)


def hash_password(password: str, salt: str) -> str:
    """
    Hash password using PBKDF2 with SHA-256 and 100,000 iterations.
    Returns hex digest string.
    """
    key = hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=password.encode("utf-8"),
        salt=salt.encode("utf-8"),
        iterations=100_000
    )
    return key.hex()


def verify_password(plain_password: str, stored_hash: str, salt: str) -> bool:
    """Verify plain password against stored PBKDF2 hash using constant-time compare."""
    calculated_hash = hash_password(plain_password, salt)
    return secrets.compare_digest(calculated_hash, stored_hash)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(s: str) -> bytes:
    padding = "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode((s + padding).encode("ascii"))


def create_access_token(data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
    """
    Generate an RFC 7519 compliant HS256 JWT token.
    Header: {"alg": "HS256", "typ": "JWT"}
    Payload: user claims with iat and exp
    """
    now = int(time.time())
    exp = now + (expires_delta if expires_delta is not None else JWT_EXPIRATION_SECONDS)

    payload = {
        **data,
        "iat": now,
        "exp": exp
    }

    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}

    header_bytes = json.dumps(header, separators=(",", ":")).encode("utf-8")
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")

    header_b64 = _b64url_encode(header_bytes)
    payload_b64 = _b64url_encode(payload_bytes)

    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    signature = hmac.new(
        JWT_SECRET_KEY.encode("utf-8"),
        signing_input,
        hashlib.sha256
    ).digest()
    sig_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode HS256 JWT token.
    Returns payload dict if signature and expiration are valid, None otherwise.
    """
    try:
        parts = token.strip().split(".")
        if len(parts) != 3:
            return None

        header_b64, payload_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")

        expected_sig = hmac.new(
            JWT_SECRET_KEY.encode("utf-8"),
            signing_input,
            hashlib.sha256
        ).digest()
        actual_sig = _b64url_decode(sig_b64)

        if not secrets.compare_digest(expected_sig, actual_sig):
            return None

        payload_bytes = _b64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Verify expiration
        exp = payload.get("exp")
        if exp and int(time.time()) > exp:
            return None

        return payload
    except Exception:
        return None
