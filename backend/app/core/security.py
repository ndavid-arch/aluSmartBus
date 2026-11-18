"""Password hashing and sign-in tokens."""

from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

ALGORITHM = "HS256"
MIN_PASSWORD_LENGTH = 8  # the same rule for sign-up and for accounts made in the terminal
_password_hasher = PasswordHash.recommended()  # argon2, as planned in the SRS


def hash_password(password: str) -> str:
    """Turn a password into a one-way hash that is safe to store."""
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Check a typed password against the stored hash."""
    return _password_hasher.verify(password, password_hash)


def create_access_token(user_id: str, role: str, expires_minutes: int | None = None) -> str:
    """Make a signed token saying who the user is and their role, valid for a limited time."""
    settings = get_settings()
    minutes = settings.access_token_minutes if expires_minutes is None else expires_minutes
    expires_at = datetime.now(UTC) + timedelta(minutes=minutes)
    claims = {"sub": user_id, "role": role, "exp": expires_at}
    return jwt.encode(claims, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Read a token's claims; raises jwt.InvalidTokenError if it is fake, changed or expired."""
    return jwt.decode(token, get_settings().secret_key, algorithms=[ALGORITHM])
