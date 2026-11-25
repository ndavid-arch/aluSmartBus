"""Bus status: anyone can see which buses are running and how full they are (#14, #28);
admins and drivers change whether a bus runs."""

import uuid
from typing import NamedTuple

from fastapi import APIRouter
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import DbSession, StaffUser
from app.models import Availability, BoardingRecord, Bus, Journey, JourneyStatus
from app.routers.buses import get_bus_or_404
from app.schemas.buses import AvailabilityUpdate, BusStatus

router = APIRouter(prefix="/buses", tags=["bus status"])


class Trip(NamedTuple):
    """The journey a bus is on right now and how many students have boarded it."""

    journey_id: uuid.UUID
    boarded: int


def journeys_on_the_road(db: Session) -> dict[uuid.UUID, Trip]:
    """Each bus that is on a journey right now, with that journey and its boarding count."""
    rows = db.execute(
        select(Journey.bus_id, Journey.id, func.count(BoardingRecord.id))
        .outerjoin(BoardingRecord, BoardingRecord.journey_id == Journey.id)
        .where(Journey.status == JourneyStatus.ACTIVE)
        .group_by(Journey.bus_id, Journey.id)
    )
    return {bus_id: Trip(journey_id, boarded) for bus_id, journey_id, boarded in rows}


def public_status(bus: Bus, on_the_road: dict[uuid.UUID, Trip]) -> BusStatus:
    """A bus's public status, with its current journey and seat count (if it is on the road)."""
    shown = BusStatus.model_validate(bus)
    trip = on_the_road.get(bus.id)
    if trip is None:
        return shown
    return shown.model_copy(
        update={
            "journey_id": trip.journey_id,
            "boarded": trip.boarded,
            "full": trip.boarded >= bus.capacity,
        }
    )


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
    return public_status(bus, journeys_on_the_road(db))
