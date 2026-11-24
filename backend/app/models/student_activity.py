"""What students do around a journey: choose stops, board, and receive alerts."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, IdMixin, set_to_now
from app.models.enums import NotificationType, PickupStatus, SelectionType

if TYPE_CHECKING:
    from app.models.route import Stop


class StopSelection(IdMixin, Base):
    """A student's chosen pickup or drop-off stop for one journey."""

    __tablename__ = "stop_selections"
    # One pickup and one drop-off per student per journey
    __table_args__ = (
        UniqueConstraint("student_id", "journey_id", "type", name="one_selection_per_type"),
    )

    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    journey_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("journeys.id"))
    stop_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stops.id"))
    type: Mapped[SelectionType] = mapped_column(Enum(SelectionType, native_enum=False, length=20))
    pickup_status: Mapped[PickupStatus] = mapped_column(
        Enum(PickupStatus, native_enum=False, length=20), default=PickupStatus.PENDING
    )
    selected_at: Mapped[datetime] = set_to_now()
    stop: Mapped["Stop"] = relationship()


class BoardingRecord(IdMixin, Base):
    """Proof that a student scanned the bus QR code and got on."""

    __tablename__ = "boarding_records"
    # A student can only board the same journey once, so a second scan is not counted twice
    __table_args__ = (UniqueConstraint("student_id", "journey_id", name="one_boarding_per_trip"),)

    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    journey_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("journeys.id"))
    boarded_at: Mapped[datetime] = set_to_now()


class Notification(IdMixin, Base):
    """An alert sent to a student, kept so we never send the same one twice."""

    __tablename__ = "notifications"
    # Each kind of alert goes to a student at most once per journey (#25)
    __table_args__ = (
        UniqueConstraint(
            "student_id", "journey_id", "type", name="one_alert_of_each_kind_per_trip"
        ),
    )
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    journey_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("journeys.id"))
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, native_enum=False, length=20)
    )
    message: Mapped[str] = mapped_column(String(300))
    sent_at: Mapped[datetime] = set_to_now()
