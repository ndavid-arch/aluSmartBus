"""What the driver-account endpoints accept and return."""

from pydantic import BaseModel

from app.schemas.auth import UserOut
from app.schemas.common import EmailAddress, PersonName


class DriverCreate(BaseModel):
    """Details an administrator types to create a driver account."""

    full_name: PersonName
    email: EmailAddress
    phone: str | None = None


class DriverOut(UserOut):
    """A driver as the admin screens show them."""

    phone: str | None
    is_active: bool


class DriverCreated(DriverOut):
    """A new driver plus their temporary password, shown to the admin only once."""

    temporary_password: str
