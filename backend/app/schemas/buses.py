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


class BusOut(BaseModel):
    """A bus as the admin screens show it, including its QR code value."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    plate_number: str
    capacity: int
    qr_code: str
    availability: Availability
