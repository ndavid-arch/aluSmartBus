"""Routes and their stops, in the order the bus visits them."""

import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, IdMixin


class Route(IdMixin, Base):
    """A route such as Rebero - ALU. Its stops are kept in visiting order."""

    __tablename__ = "routes"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    stops: Mapped[list["Stop"]] = relationship(
        back_populates="route", order_by="Stop.sequence", cascade="all, delete-orphan"
    )


class Stop(IdMixin, Base):
    """A designated stop. sequence 1 is the first stop going Rebero -> ALU."""

    __tablename__ = "stops"
    __table_args__ = (UniqueConstraint("route_id", "sequence", name="one_stop_per_position"),)

    route_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("routes.id"))
    name: Mapped[str] = mapped_column(String(100))
    latitude: Mapped[float]
    longitude: Mapped[float]
    sequence: Mapped[int]
    route: Mapped[Route] = relationship(back_populates="stops")