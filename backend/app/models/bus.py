"""Buses registered by the administrator."""

from sqlalchemy import CheckConstraint, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base, IdMixin
from app.models.enums import Availability


class Bus(IdMixin, Base):
    """One bus, with its own QR code for boarding and a seat capacity."""

    __tablename__ = "buses"
    __table_args__ = (CheckConstraint("capacity > 0", name="capacity_positive"),)

    plate_number: Mapped[str] = mapped_column(String(20), unique=True)
    capacity: Mapped[int]
    qr_code: Mapped[str] = mapped_column(String(64), unique=True)
    availability: Mapped[Availability] = mapped_column(
        Enum(Availability, native_enum=False, length=20), default=Availability.AVAILABLE
    )
    unavailable_reason: Mapped[str | None] = mapped_column(String(200))
