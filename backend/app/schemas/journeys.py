"""What the journey endpoints accept and return."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import Direction, JourneyStatus


class JourneyStart(BaseModel):
    """What a driver chooses before tapping Start."""

    bus_id: uuid.UUID
    direction: Direction


class JourneyBus(BaseModel):
    """The bus on a journey, as journey lists show it."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    plate_number: str


class JourneyDriver(BaseModel):
    """The driver of a journey; only the name is shown, never contact details."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str


class JourneyOut(BaseModel):
    """A journey with its bus and driver."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    direction: Direction
    status: JourneyStatus
    started_at: datetime
    bus: JourneyBus
    driver: JourneyDriver
