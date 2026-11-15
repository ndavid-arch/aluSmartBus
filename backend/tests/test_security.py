"""Tests for password hashing and sign-in tokens."""

import jwt
import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_is_not_stored_as_typed():
    """The hash never contains the password itself."""
    hashed = hash_password("bus-to-campus")
    assert "bus-to-campus" not in hashed
    assert hashed.startswith("$argon2")


def test_correct_password_matches_and_wrong_one_does_not():
    """Only the original password verifies against its hash."""
    hashed = hash_password("bus-to-campus")
    assert verify_password("bus-to-campus", hashed)
    assert not verify_password("wrong-password", hashed)


def test_token_carries_user_and_role():
    """A new token can be read back with the same user id and role."""
    claims = decode_access_token(create_access_token("user-123", "student"))
    assert claims["sub"] == "user-123"
    assert claims["role"] == "student"


def test_expired_token_is_rejected():
    """A token past its expiry time cannot be used."""
    token = create_access_token("user-123", "student", expires_minutes=-1)
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_changed_token_is_rejected():
    """Editing a token (for example to change the role) breaks its signature."""
    token = create_access_token("user-123", "student")
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token[:-2] + "xx")
