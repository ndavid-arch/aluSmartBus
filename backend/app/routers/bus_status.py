"""Bus status: anyone can see which buses are running; admins and drivers change it (#14)."""

import uuid

from fastapi import APIRouter
from sqlalchemy import select

from app.core.deps import DbSession, StaffUser
from app.models import Availability, Bus
from app.routers.buses import get_bus_or_404
from app.schemas.buses import AvailabilityUpdate, BusStatus

router = APIRouter(prefix="/buses", tags=["bus status"])


@router.get("")
def list_bus_status(db: DbSession) -> list[BusStatus]:
    """Every bus and whether it is running, for students and guests; no sign-in needed."""
    buses = db.scalars(select(Bus).order_by(Bus.plate_number))
    return [BusStatus.model_validate(bus) for bus in buses]


@router.get("/{bus_id}")
def get_bus_status(bus_id: uuid.UUID, db: DbSession) -> BusStatus:
    """The latest status of one bus, checked when a student selects it."""
    return BusStatus.model_validate(get_bus_or_404(db, bus_id))


@router.patch("/{bus_id}/availability")
def change_availability(
    bus_id: uuid.UUID, changes: AvailabilityUpdate, db: DbSession, _staff: StaffUser
) -> BusStatus:
    """Mark a bus Available or Unavailable; a reason is kept only while it is Unavailable."""
    bus = get_bus_or_404(db, bus_id)
    bus.availability = changes.availability
    running = changes.availability == Availability.AVAILABLE
    bus.unavailable_reason = None if running else changes.reason
    db.commit()
    return BusStatus.model_validate(bus)
