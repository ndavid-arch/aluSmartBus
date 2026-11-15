"""Shared request helpers ("dependencies") that routes can ask FastAPI for."""

import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db import get_db
from app.models import User

_bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User:
    """Return the signed-in user from the request's token, or answer 401 if there is none."""
    not_signed_in = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not signed in",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise not_signed_in
    try:
        claims = decode_access_token(credentials.credentials)
        user = db.get(User, uuid.UUID(claims["sub"]))
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise not_signed_in from None
    if user is None or not user.is_active:
        raise not_signed_in
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
