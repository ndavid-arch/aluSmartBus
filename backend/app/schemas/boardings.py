"""What the boarding endpoint accepts and returns (#27)."""

import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.models import Direction

# The text inside the bus's QR code (made by make_qr_code: 32 characters, at most 64 stored)
QrText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]


class BoardingScan(BaseModel):
    """What the student's phone read from the QR code by the bus door."""

    qr_code: QrText


class BoardingOut(BaseModel):
    """The boarding that was recorded, or the one that already existed for this journey."""

    journey_id: uuid.UUID
    plate_number: str
    direction: Direction
    boarded_at: datetime
    already_boarded: bool
