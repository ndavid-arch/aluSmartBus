"""What the driver-account endpoints accept and return."""

from pydantic import BaseModel, field_validator

from app.schemas.auth import UserOut


class DriverCreate(BaseModel):
    """Details an administrator types to create a driver account."""

    full_name: str
    email: str
    phone: str | None = None

    @field_validator("full_name")
    @classmethod
    def name_not_blank(cls, full_name: str) -> str:
        """Refuse an empty name and trim stray spaces."""
        full_name = full_name.strip()
        if not full_name:
            raise ValueError("Enter the driver's name")
        return full_name

    @field_validator("email")
    @classmethod
    def looks_like_email(cls, email: str) -> str:
        """Tidy the email and refuse anything that is clearly not an address."""
        email = email.strip().lower()
        local, _, domain = email.partition("@")
        if not local or "." not in domain:
            raise ValueError("Enter a valid email address")
        return email


class DriverOut(UserOut):
    """A driver as the admin screens show them."""

    phone: str | None
    is_active: bool


class DriverCreated(DriverOut):
    """A new driver plus their temporary password, shown to the admin only once."""

    temporary_password: str
