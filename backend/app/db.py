"""Database connection: the engine, sessions and the base class for all models."""

import uuid
from collections.abc import Iterator
from datetime import datetime

from sqlalchemy import DateTime, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.core.config import get_settings

engine = create_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Parent class for every model; it keeps the list of all tables."""


class IdMixin:
    """Gives a model a random UUID primary key, as in the class diagram."""

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)


def set_to_now() -> Mapped[datetime]:
    """A date-and-time column the database fills in with the current time."""
    return mapped_column(DateTime(timezone=True), server_default=func.now())


def get_db() -> Iterator[Session]:
    """Give each request its own database session and close it when the request ends."""
    with SessionLocal() as session:
        yield session
