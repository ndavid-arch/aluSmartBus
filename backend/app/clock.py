"""Times in one zone (UTC), so the server's clock is the only one that matters."""

from datetime import UTC, datetime


def as_utc(moment: datetime) -> datetime:
    """The same moment with its zone stated (SQLite gives times without a zone: they are UTC)."""
    return moment.replace(tzinfo=UTC) if moment.tzinfo is None else moment


def seconds_since(moment: datetime) -> float:
    """How long ago a moment was, by the server's clock; never negative."""
    return max((datetime.now(UTC) - as_utc(moment)).total_seconds(), 0.0)
