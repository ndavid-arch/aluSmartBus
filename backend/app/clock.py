"""Times in one zone (UTC), so the server's clock is the only one that matters; Kigali's local
days and months are only used to group things for people (reports, monthly points)."""

from datetime import UTC, date, datetime, time, timedelta, timezone

from app.core.config import get_settings


def as_utc(moment: datetime) -> datetime:
    """The same moment with its zone stated (SQLite gives times without a zone: they are UTC)."""
    return moment.replace(tzinfo=UTC) if moment.tzinfo is None else moment


def seconds_since(moment: datetime) -> float:
    """How long ago a moment was, by the server's clock; never negative."""
    return max((datetime.now(UTC) - as_utc(moment)).total_seconds(), 0.0)


def local_zone() -> timezone:
    """Kigali's time zone (a fixed offset: Rwanda has no daylight saving)."""
    return timezone(timedelta(hours=get_settings().local_utc_offset_hours))


def start_of_local_day(day: date) -> datetime:
    """The UTC moment a Kigali day begins."""
    return datetime.combine(day, time.min, tzinfo=local_zone()).astimezone(UTC)


def start_of_this_month() -> datetime:
    """The UTC moment the current Kigali month began."""
    return start_of_local_day(datetime.now(local_zone()).date().replace(day=1))
