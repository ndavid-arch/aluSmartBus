"""Signing in and finding out who is signed in (FR-01, FR-04, FR-05)."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import CurrentUser, DbSession
from app.core.security import create_access_token, verify_password
from app.models import User
from app.schemas.auth import LoginRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(details: LoginRequest, db: DbSession) -> TokenResponse:
    """Check the email and password and return a sign-in token."""
    user = db.scalar(select(User).where(User.email == details.email))
    # Same message for an unknown email and a wrong password: nobody can learn who has an account
    if user is None or not verify_password(details.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="This account has been disabled")
    token = create_access_token(str(user.id), user.role.value)
    return TokenResponse(access_token=token, role=user.role)


@router.get("/me")
def read_me(user: CurrentUser) -> UserOut:
    """Return the signed-in user's details; the app uses this to check a saved token still works."""
    return UserOut.model_validate(user)
