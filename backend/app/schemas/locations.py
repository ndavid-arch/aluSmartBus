"""What the location endpoint accepts and returns."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.config import get_settings
from app.models import JourneyStatus


class LocationIn(BaseModel):
    """One GPS reading from the driver's phone; impossible values are refused."""

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy: float = Field(ge=0)  # metres, as reported by the phone

    @field_validator("accuracy")
    @classmethod
    def accurate_enough(cls, accuracy: float) -> float:
        """Refuse vague readings (the GPS spike, #9): they would make the bus jump about."""
        limit = get_settings().location_accuracy_limit_m
        if accuracy > limit:
            raise ValueError(
                f"This reading is only accurate to ±{accuracy:.0f} m (limit ±{limit:.0f} m)"
            )
        return accuracy


class LocationOut(BaseModel):
    """A saved reading; recorded_at comes from the server's clock, not the phone's."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    latitude: float
    longitude: float
    accuracy: float
    recorded_at: datetime


class LocationSaved(LocationOut):
    """The saved reading, plus the journey's status: COMPLETED once the bus reaches the terminal."""

    journey_status: JourneyStatus
