"""What the stop-selection endpoints accept and return."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.models import PickupStatus, SelectionType


class SelectionChoice(BaseModel):
    """The stop a student picks from the journey's list."""

    stop_id: uuid.UUID


class JourneyStop(BaseModel):
    """A stop of this journey, in the order the bus meets it, and whether the bus has passed it."""

    id: uuid.UUID
    name: str
    sequence: int
    passed: bool


class StopRequests(JourneyStop):
    """A stop with how many students the driver picks up and drops off there (#24)."""

    pickups: int
    dropoffs: int


class StopSummary(BaseModel):
    """The chosen stop, as the student's screen shows it."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str


# Where a pickup stands: bus not there yet, bus there (board now), boarded, or missed
WindowState = Literal["waiting", "open", "boarded", "missed"]


class SelectionOut(BaseModel):
    """A student's pickup or drop-off stop for one journey."""

    model_config = ConfigDict(from_attributes=True)

    type: SelectionType
    stop: StopSummary
    pickup_status: PickupStatus
    # Pickups only (None for a drop-off): the boarding window at that stop (#23)
    window_state: WindowState | None = None
    window_closes_at: datetime | None = None
