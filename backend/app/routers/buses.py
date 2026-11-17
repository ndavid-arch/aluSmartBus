"""Administrators register buses and set their capacity (FR-36, FR-37, FR-52, FR-56)."""

import secrets
import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import AdminUser, DbSession
from app.models import Bus
from app.schemas.buses import BusCreate, BusOut, BusUpdate

router = APIRouter(prefix="/admin/buses", tags=["buses"])


def make_qr_code() -> str:
    """A random value for the bus's QR code; it is set once and never changes."""
    return secrets.token_urlsafe(24)


def get_bus_or_404(db: Session, bus_id: uuid.UUID) -> Bus:
    """Find a bus by its ID, or answer 404 if there is no such bus."""
    bus = db.get(Bus, bus_id)
    if bus is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Bus not found")
    return bus


@router.post("", status_code=status.HTTP_201_CREATED)
def register_bus(details: BusCreate, db: DbSession, _admin: AdminUser) -> BusOut:
    """Register a bus with its plate number and capacity, and give it a QR code."""
    if db.scalar(select(Bus).where(Bus.plate_number == details.plate_number)) is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="This plate number is already registered"
        )
    bus = Bus(plate_number=details.plate_number, capacity=details.capacity, qr_code=make_qr_code())
    db.add(bus)
    db.commit()
    return BusOut.model_validate(bus)


@router.get("")
def list_buses(db: DbSession, _admin: AdminUser) -> list[BusOut]:
    """All buses, sorted by plate number."""
    buses = db.scalars(select(Bus).order_by(Bus.plate_number))
    return [BusOut.model_validate(bus) for bus in buses]


@router.patch("/{bus_id}")
def change_capacity(
    bus_id: uuid.UUID, changes: BusUpdate, db: DbSession, _admin: AdminUser
) -> BusOut:
    """Change a bus's capacity; its ID, plate and QR code stay the same."""
    bus = get_bus_or_404(db, bus_id)
    bus.capacity = changes.capacity
    db.commit()
    return BusOut.model_validate(bus)
