"""What the route and live-map endpoints return."""

import uuid
from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict

from app.clock import seconds_since
from app.eta import journey_progress, stops_ahead
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
    # The line to draw, as (latitude, longitude) points: along the roads once the road path is
    # saved (#79), otherwise straight from stop to stop
    path: list[tuple[float, float]] = []


class StopAhead(BaseModel):
    """A stop the bus has not reached yet, and roughly how many minutes away it is (#70)."""

    name: str
    minutes: int


class LiveBus(BaseModel):
    """Where one bus on the road is now: the same shape on page load and in live updates."""

    type: Literal["position"] = "position"  # live messages say what they are (see #20)
    journey_id: uuid.UUID
    bus_id: uuid.UUID
    plate_number: str
    direction: Direction
    latitude: float
    longitude: float
    accuracy: float
    recorded_at: datetime
    next_stop: str | None  # None when the bus is not on the route yet
    eta_minutes: int | None
    # Every stop still ahead, in travel order (empty off the route): the track screen's
    # minute tiles and timeline (#70)
    stops_ahead: list[StopAhead] = []
    # Worked out by the server, so a phone whose clock is wrong still knows how old this is
    age_seconds: float

    @classmethod
    def from_parts(cls, journey: Journey, location: LocationUpdate) -> Self:
        """Combine a journey and its latest reading into one map entry, with next stop and ETA."""
        progress = journey_progress(journey, location)

        return cls(
            journey_id=journey.id,
            bus_id=journey.bus_id,
            plate_number=journey.bus.plate_number,
            direction=journey.direction,
            latitude=location.latitude,
            longitude=location.longitude,
            accuracy=location.accuracy,
            recorded_at=location.recorded_at,
            next_stop=progress.next_stop,
            eta_minutes=progress.eta_minutes,
            stops_ahead=[
                StopAhead(name=stop.name, minutes=minutes)
                for stop, minutes in stops_ahead(journey, location)
            ],
            age_seconds=seconds_since(location.recorded_at),
        )
