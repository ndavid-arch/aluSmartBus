"""Database connection: the engine, sessions and the base class for all models."""

import uuid
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from app.core.config import get_settings

engine = create_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Parent class for every model; it keeps the list of all tables."""

class IdMixin:
    """Gives a model a random UUID primary key, as in the class diagram."""

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

def get_db() -> Iterator[Session]:
    """Give each request its own database session and close it when the request ends."""
    with SessionLocal() as session:
        yield session