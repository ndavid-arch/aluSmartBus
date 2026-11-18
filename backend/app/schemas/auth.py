"""What the sign-in and sign-up endpoints accept and return."""

import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.config import get_settings
from app.core.security import MIN_PASSWORD_LENGTH
from app.models.enums import Role
from app.schemas.common import EmailAddress, PersonName


class LoginRequest(BaseModel):
    """Email and password typed on the sign-in screen."""

    email: str
    password: str

    @field_validator("email")
    @classmethod
    def tidy_email(cls, email: str) -> str:
        """Ignore spaces and capital letters, so N.David@ALUstudent.com still matches."""
        return email.strip().lower()


class SignUpRequest(BaseModel):
    """What a student types to create their own account. There is no role field on purpose."""

    full_name: PersonName
    email: EmailAddress
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=128)

    @field_validator("email")
    @classmethod
    def must_be_student_email(cls, email: str) -> str:
        """Only ALU student emails may sign up; staff accounts are made by an administrator."""
        domain = get_settings().student_email_domain
        if not email.endswith(f"@{domain}"):
            raise ValueError(f"Use your @{domain} email address")
        return email


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
