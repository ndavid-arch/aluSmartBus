"""The boarding window: how long a student has to get on after the bus reaches their stop (#23).

FR-31 to FR-34: the window opens when the bus arrives at the pickup stop and lasts 3 minutes.
A scan at 2:59 counts; one at 3:01 is too late and the pickup is MISSED.
"""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clock import as_utc
from app.models import Journey, PickupStatus, SelectionType, StopSelection

BOARDING_WINDOW = timedelta(minutes=3)


def window_closes_at(arrived_at: datetime) -> datetime:
    """When the boarding window at a stop closes."""
    return as_utc(arrived_at) + BOARDING_WINDOW


def within_window(arrived_at: datetime, moment: datetime) -> bool:
    """Whether a moment (a QR scan, say) falls inside the window; exactly 3:00 still counts."""
    return as_utc(arrived_at) <= as_utc(moment) <= window_closes_at(arrived_at)


def pickup_arrivals(journey: Journey) -> dict:
    """When the bus reached each stop on this journey, by stop ID."""
    return {arrival.stop_id: arrival.arrived_at for arrival in journey.stop_arrivals}


def expire_missed_pickups(db: Session, journey: Journey, now: datetime) -> list[StopSelection]:
    """Mark as MISSED every pending pickup whose stop the bus reached more than 3 minutes ago."""
    arrived = pickup_arrivals(journey)
    pending = db.scalars(
        select(StopSelection).where(
            StopSelection.journey_id == journey.id,
            StopSelection.type == SelectionType.PICKUP,
            StopSelection.pickup_status == PickupStatus.PENDING,
        )
    )
    missed = []
    for selection in pending:
        arrived_at = arrived.get(selection.stop_id)
        if arrived_at is not None and not within_window(arrived_at, now):
            selection.pickup_status = PickupStatus.MISSED
            missed.append(selection)
    return missed
