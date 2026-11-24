"""What the arrivals endpoint returns."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import ArrivalStatus


class ArrivalStop(BaseModel):
    """The stop an arrival belongs to."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    sequence: int


class ArrivalOut(BaseModel):
    """When the bus reached a stop, and whether it is still there."""

    model_config = ConfigDict(from_attributes=True)

    stop: ArrivalStop
    status: ArrivalStatus
    arrived_at: datetime
