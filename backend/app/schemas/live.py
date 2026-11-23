"""What the route and live-map endpoints return."""

import uuid
from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict

from app.models import Direction, Journey, LocationUpdate


class StopOut(BaseModel):
    """A designated stop, in the order the bus visits it going Rebero -> ALU."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    latitude: float
    longitude: float
    sequence: int


class RouteOut(BaseModel):
    """The route line and its stops, for drawing the map."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    stops: list[StopOut]


class LiveBus(BaseModel):
    """Where one bus on the road is now: the same shape on page load and in live updates."""

    journey_id: uuid.UUID
    bus_id: uuid.UUID
    plate_number: str
    direction: Direction
    latitude: float
    longitude: float
    accuracy: float
    recorded_at: datetime

    @classmethod
    def from_parts(cls, journey: Journey, location: LocationUpdate) -> Self:
        """Combine a journey and its latest reading into one map entry."""
        return cls(
            journey_id=journey.id,
            bus_id=journey.bus_id,
            plate_number=journey.bus.plate_number,
            direction=journey.direction,
            latitude=location.latitude,
            longitude=location.longitude,
            accuracy=location.accuracy,
            recorded_at=location.recorded_at,
        )
