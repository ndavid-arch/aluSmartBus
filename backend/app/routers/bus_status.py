"""Bus status: anyone can see which buses are running; admins and drivers change it (#14)."""

import uuid

from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import DbSession, StaffUser
from app.models import Availability, Bus, Journey, JourneyStatus
from app.routers.buses import get_bus_or_404
from app.schemas.buses import AvailabilityUpdate, BusStatus

router = APIRouter(prefix="/buses", tags=["bus status"])


def journeys_on_the_road(db: Session) -> dict[uuid.UUID, uuid.UUID]:
    """Each bus that is on a journey right now, mapped to that journey's ID."""
    rows = db.execute(
        select(Journey.bus_id, Journey.id).where(Journey.status == JourneyStatus.ACTIVE)
    )
    return {bus_id: journey_id for bus_id, journey_id in rows}


def public_status(bus: Bus, on_the_road: dict[uuid.UUID, uuid.UUID]) -> BusStatus:
    """A bus's public status, with the journey it is on right now (if any)."""
    return BusStatus.model_validate(bus).model_copy(update={"journey_id": on_the_road.get(bus.id)})


@router.get("")
def list_bus_status(db: DbSession) -> list[BusStatus]:
    """Every bus and whether it is running, for students and guests; no sign-in needed."""
    on_the_road = journeys_on_the_road(db)
    buses = db.scalars(select(Bus).order_by(Bus.plate_number))
    return [public_status(bus, on_the_road) for bus in buses]


@router.get("/{bus_id}")
def get_bus_status(bus_id: uuid.UUID, db: DbSession) -> BusStatus:
    """The latest status of one bus, checked when a student selects it."""
    return public_status(get_bus_or_404(db, bus_id), journeys_on_the_road(db))


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
