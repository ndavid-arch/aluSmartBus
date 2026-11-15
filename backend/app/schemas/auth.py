"""What the sign-in endpoints accept and return."""

import uuid

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import Role


class LoginRequest(BaseModel):
    """Email and password typed on the sign-in screen."""

    email: str
    password: str

    @field_validator("email")
    @classmethod
    def tidy_email(cls, email: str) -> str:
        """Ignore spaces and capital letters, so N.David@ALUstudent.com still matches."""
        return email.strip().lower()


class TokenResponse(BaseModel):
    """A successful sign-in: the token, and the role so the app opens the right view."""

    access_token: str
    token_type: str = "bearer"
    role: Role


class UserOut(BaseModel):
    """A user's public details. Never includes the password hash."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: str
    role: Role
