"""Signing up, signing in and finding out who is signed in (FR-01, FR-04, FR-05, FR-67, FR-68)."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import CurrentUser, DbSession
from app.core.security import create_access_token, hash_password, verify_password
from app.models import Role, User
from app.schemas.auth import LoginRequest, SignUpRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def token_response(user: User) -> TokenResponse:
    """A sign-in token for this user, plus their role so the app opens the right page."""
    token = create_access_token(str(user.id), user.role.value)
    return TokenResponse(access_token=token, role=user.role)


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def sign_up(details: SignUpRequest, db: DbSession) -> TokenResponse:
    """Create a student account and sign the student in straight away (FR-67, FR-68)."""
    if db.scalar(select(User).where(User.email == details.email)) is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="This email already has an account. Sign in instead."
        )
    student = User(
        full_name=details.full_name,
        email=details.email,
        password_hash=hash_password(details.password),
        role=Role.STUDENT,
    )
    db.add(student)
    db.commit()
    return token_response(student)


@router.post("/login")
def login(details: LoginRequest, db: DbSession) -> TokenResponse:
    """Check the email and password and return a sign-in token."""
    user = db.scalar(select(User).where(User.email == details.email))
    # Same message for an unknown email and a wrong password: nobody can learn who has an account
    if user is None or not verify_password(details.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="This account has been disabled")
    return token_response(user)


@router.get("/me")
def read_me(user: CurrentUser) -> UserOut:
    """Return the signed-in user's details; the app uses this to check a saved token still works."""
    return UserOut.model_validate(user)
