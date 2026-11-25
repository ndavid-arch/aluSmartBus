"""Contribution points (#34, FR-62 to FR-65), worked out from records the server already keeps.

- +10 for each trip boarded (a QR scan, #27): one per journey, so it cannot be repeated
- +5 for boarding on time: the student chose a pickup and scanned within its window (#23)

Nothing is stored as "points", so they can never drift from what really happened, and no
button exists that a student could tap to farm them.
"""

from collections import Counter
from datetime import datetime

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models import (
    BoardingRecord,
    Journey,
    PickupStatus,
    SelectionType,
    Stop,
    StopSelection,
    User,
)

POINTS_PER_TRIP = 10
POINTS_PER_ON_TIME_BOARDING = 5


def since_start(query: Select, since: datetime | None) -> Select:
    """Keep only journeys that started at or after `since` (no limit when None)."""
    return query if since is None else query.where(Journey.started_at >= since)


def trips_by_student(db: Session, since: datetime | None = None) -> Counter:
    """How many journeys each student boarded, by student ID."""
    query = (
        select(BoardingRecord.student_id, func.count())
        .join(Journey, BoardingRecord.journey_id == Journey.id)
        .group_by(BoardingRecord.student_id)
    )
    return Counter(dict(db.execute(since_start(query, since)).all()))


def on_time_boardings_by_student(db: Session, since: datetime | None = None) -> Counter:
    """How many chosen pickups each student boarded within the window, by student ID."""
    query = (
        select(StopSelection.student_id, func.count())
        .join(Journey, StopSelection.journey_id == Journey.id)
        .where(
            StopSelection.type == SelectionType.PICKUP,
            StopSelection.pickup_status == PickupStatus.BOARDED,
        )
        .group_by(StopSelection.student_id)
    )
    return Counter(dict(db.execute(since_start(query, since)).all()))


def points_by_student(db: Session, since: datetime | None = None) -> Counter:
    """Every student's points, for all time or since a moment; students with none are left out."""
    points: Counter = Counter()
    for student_id, trips in trips_by_student(db, since).items():
        points[student_id] += trips * POINTS_PER_TRIP
    for student_id, on_time in on_time_boardings_by_student(db, since).items():
        points[student_id] += on_time * POINTS_PER_ON_TIME_BOARDING
    return points


def leaderboard_name(user: User) -> str:
    """'Aline U.' (first name, last initial), or 'A. U.' when the student hides their name."""
    parts = user.full_name.split()
    if not parts:
        return "Rider"
    first, last = parts[0], parts[-1] if len(parts) > 1 else ""
    if user.hide_name_on_leaderboard:
        return " ".join(f"{part[0].upper()}." for part in (first, last) if part)
    return f"{first} {last[0].upper()}." if last else first


def usual_stop(db: Session, student: User) -> str | None:
    """The pickup stop this student has chosen most often, if any (ties: alphabetical)."""
    return db.scalar(
        select(Stop.name)
        .join(StopSelection, StopSelection.stop_id == Stop.id)
        .where(
            StopSelection.student_id == student.id,
            StopSelection.type == SelectionType.PICKUP,
        )
        .group_by(Stop.name)
        .order_by(func.count().desc(), Stop.name)
        .limit(1)
    )
