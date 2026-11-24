"""What the stop-selection endpoints accept and return."""

import uuid

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


class StopSummary(BaseModel):
    """The chosen stop, as the student's screen shows it."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str


class SelectionOut(BaseModel):
    """A student's pickup or drop-off stop for one journey."""

    model_config = ConfigDict(from_attributes=True)

    type: SelectionType
    stop: StopSummary
    pickup_status: PickupStatus
