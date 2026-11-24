"""Journeys and what the system records while a bus is driving."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Index, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, IdMixin, set_to_now
from app.models.enums import ArrivalStatus, Direction, JourneyStatus

if TYPE_CHECKING:
    from app.models.bus import Bus
    from app.models.route import Route, Stop
    from app.models.user import User

# Enum columns store the member's NAME, so an active journey has status 'ACTIVE' in the table
ONLY_ACTIVE = text("status = 'ACTIVE'")


class Journey(IdMixin, Base):
    """One trip of one bus, driven by one driver, along one route in one direction."""

    __tablename__ = "journeys"

    # The database itself refuses a second active journey for one bus (FR-16),
    # even if two drivers press Start at the same moment
    __table_args__ = (
        Index(
            "one_active_journey_per_bus",
            "bus_id",
            unique=True,
            postgresql_where=ONLY_ACTIVE,
            sqlite_where=ONLY_ACTIVE,
        ),
    )

    bus_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("buses.id"))
    driver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    route_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("routes.id"))
    direction: Mapped[Direction] = mapped_column(Enum(Direction, native_enum=False, length=20))
    status: Mapped[JourneyStatus] = mapped_column(
        Enum(JourneyStatus, native_enum=False, length=20), default=JourneyStatus.ACTIVE
    )
    started_at: Mapped[datetime] = set_to_now()
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    bus: Mapped["Bus"] = relationship()
    driver: Mapped["User"] = relationship()
    route: Mapped["Route"] = relationship()

    location_updates: Mapped[list["LocationUpdate"]] = relationship(
        back_populates="journey", cascade="all, delete-orphan"
    )
    stop_arrivals: Mapped[list["StopArrival"]] = relationship(
        back_populates="journey", cascade="all, delete-orphan"
    )


class LocationUpdate(IdMixin, Base):
    """One position sent by the driver's phone during a journey."""

    __tablename__ = "location_updates"
    # Finding "the latest position of this journey" is the most common question, so index it
    __table_args__ = (Index("ix_location_journey_time", "journey_id", "recorded_at"),)

    journey_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("journeys.id"))
    latitude: Mapped[float]
    longitude: Mapped[float]
    accuracy: Mapped[float]  # metres, as reported by the phone
    recorded_at: Mapped[datetime] = set_to_now()

    journey: Mapped[Journey] = relationship(back_populates="location_updates")


class StopArrival(IdMixin, Base):
    """The moment a journey reached a stop; opens the boarding window there."""

    __tablename__ = "stop_arrivals"
    __table_args__ = (UniqueConstraint("journey_id", "stop_id", name="one_arrival_per_stop"),)

    journey_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("journeys.id"))
    stop_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stops.id"))
    arrived_at: Mapped[datetime] = set_to_now()
    status: Mapped[ArrivalStatus] = mapped_column(
        Enum(ArrivalStatus, native_enum=False, length=20), default=ArrivalStatus.AT_STOP
    )

    journey: Mapped[Journey] = relationship(back_populates="stop_arrivals")
    stop: Mapped["Stop"] = relationship()
