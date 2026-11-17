"""Administrators create and list driver accounts; drivers cannot sign themselves up (FR-03)."""

import secrets

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import AdminUser, DbSession
from app.core.security import hash_password
from app.models import Role, User
from app.schemas.drivers import DriverCreate, DriverCreated, DriverOut

router = APIRouter(prefix="/admin/drivers", tags=["drivers"])


def make_temporary_password() -> str:
    """A random 12-character password the admin passes on to the driver."""
    return secrets.token_urlsafe(9)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_driver(details: DriverCreate, db: DbSession, _admin: AdminUser) -> DriverCreated:
    """Create a driver account with a temporary password."""
    if db.scalar(select(User).where(User.email == details.email)) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="This email already has an account")
    password = make_temporary_password()
    driver = User(
        full_name=details.full_name,
        email=details.email,
        phone=details.phone,
        password_hash=hash_password(password),
        role=Role.DRIVER,
    )
    db.add(driver)
    db.commit()
    details_out = DriverOut.model_validate(driver).model_dump()
    return DriverCreated(**details_out, temporary_password=password)


@router.get("")
def list_drivers(db: DbSession, _admin: AdminUser) -> list[DriverOut]:
    """All driver accounts, sorted by name."""
    drivers = db.scalars(select(User).where(User.role == Role.DRIVER).order_by(User.full_name))
    return [DriverOut.model_validate(driver) for driver in drivers]
