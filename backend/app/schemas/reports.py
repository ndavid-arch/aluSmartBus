"""What the admin report contains (#30): totals and demand only, never students' names."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models import Direction


class JourneyRow(BaseModel):
    """One completed journey in the period and how many students boarded it."""

    id: uuid.UUID
    plate_number: str
    driver_name: str
    direction: Direction
    started_at: datetime
    ended_at: datetime | None
    boarded: int


class StopDemand(BaseModel):
    """How much one stop was used in the period (FR-58)."""

    stop_id: uuid.UUID
    name: str
    sequence: int
    pickups: int  # pickups chosen here
    boarded: int  # of those, the students who scanned on in time
    missed: int  # of those, the students who missed the bus
    dropoffs: int  # drop-offs chosen here


class Report(BaseModel):
    """Completed journeys, boarding totals and demand by stop for a chosen period (FR-57)."""

    start: date
    end: date
    completed_journeys: int
    boardings: int
    # Boardings divided by seats offered across the journeys (0.5 = half full); None without trips
    average_occupancy: float | None
    missed_pickups: int
    journeys: list[JourneyRow]
    stops: list[StopDemand]
