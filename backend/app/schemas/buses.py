"""What the bus endpoints accept and return."""

import uuid
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import Availability

# A bus carries at least one student and no more than a large coach can hold
Capacity = Annotated[int, Field(gt=0, le=100)]


class BusCreate(BaseModel):
    """What an administrator types to register a bus."""

    plate_number: str
    capacity: Capacity

    @field_validator("plate_number")
    @classmethod
    def tidy_plate(cls, plate_number: str) -> str:
        """Store plates one way (" rab 123  a" becomes "RAB 123 A") so duplicates are caught."""
        plate_number = " ".join(plate_number.split()).upper()
        if not plate_number:
            raise ValueError("Enter the bus's plate number")
        if len(plate_number) > 20:
            raise ValueError("A plate number has at most 20 characters")
        return plate_number


class BusUpdate(BaseModel):
    """What an administrator can change about a bus after registering it."""

    capacity: Capacity


class AvailabilityUpdate(BaseModel):
    """A new status for a bus, with an optional reason when it is not running."""

    availability: Availability
    reason: str | None = Field(default=None, max_length=200)

    @field_validator("reason")
    @classmethod
    def tidy_reason(cls, reason: str | None) -> str | None:
        """Trim the reason, and treat an empty one as no reason at all."""
        if reason is None:
            return None
        return reason.strip() or None


class BusStatus(BaseModel):
    """What anyone may see about a bus: whether it is running and why not."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    plate_number: str
    capacity: int
    availability: Availability
    unavailable_reason: str | None
    # The journey it is on right now, so students can choose their stops (#21);
    # filled in by the public bus list, None when the bus is not on the road
    journey_id: uuid.UUID | None = None
    # Students who scanned on that journey (#28), and whether that reaches the capacity;
    # Full is only shown, never enforced: the driver decides (FR-54)
    boarded: int | None = None
    full: bool = False


class BusOut(BusStatus):
    """A bus as the admin screens show it, including its QR code value."""

    qr_code: str
