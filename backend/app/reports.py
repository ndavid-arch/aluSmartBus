"""Building the admin report from completed journeys in a period (#30, FR-57, FR-58).

Only counts leave this module: the report never names a student (FR-59).
"""

from collections import Counter
from datetime import UTC, date, datetime, time, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import (
    BoardingRecord,
    Journey,
    JourneyStatus,
    PickupStatus,
    Route,
    SelectionType,
    StopSelection,
)
from app.schemas.reports import JourneyRow, Report, StopDemand


def period_bounds(start: date, end: date) -> tuple[datetime, datetime]:
    """The UTC moments where the local days start..end begin and end (end day included)."""
    local = timezone(timedelta(hours=get_settings().local_utc_offset_hours))
    first = datetime.combine(start, time.min, tzinfo=local)
    after_last = datetime.combine(end + timedelta(days=1), time.min, tzinfo=local)
    return first.astimezone(UTC), after_last.astimezone(UTC)


def completed_journeys(db: Session, start: date, end: date) -> list[Journey]:
    """Journeys that started in the period and have finished, oldest first."""
    since, until = period_bounds(start, end)
    return list(
        db.scalars(
            select(Journey)
            .where(
                Journey.status == JourneyStatus.COMPLETED,
                Journey.started_at >= since,
                Journey.started_at < until,
            )
            .order_by(Journey.started_at)
        )
    )


def boardings_per_journey(db: Session, journeys: list[Journey]) -> Counter:
    """How many students boarded each journey, by journey ID."""
    rows = db.execute(
        select(BoardingRecord.journey_id, func.count())
        .where(BoardingRecord.journey_id.in_([journey.id for journey in journeys]))
        .group_by(BoardingRecord.journey_id)
    )
    return Counter(dict(rows.all()))


def demand_by_stop(db: Session, route: Route, journeys: list[Journey]) -> list[StopDemand]:
    """For every stop in route order: pickups, boardings, misses and drop-offs chosen there."""
    selections = db.scalars(
        select(StopSelection).where(
            StopSelection.journey_id.in_([journey.id for journey in journeys])
        )
    )
    counts: Counter = Counter()
    for selection in selections:
        if selection.type == SelectionType.DROPOFF:
            counts[selection.stop_id, "dropoffs"] += 1
            continue
        counts[selection.stop_id, "pickups"] += 1
        if selection.pickup_status == PickupStatus.BOARDED:
            counts[selection.stop_id, "boarded"] += 1
        elif selection.pickup_status == PickupStatus.MISSED:
            counts[selection.stop_id, "missed"] += 1
    return [
        StopDemand(
            stop_id=stop.id,
            name=stop.name,
            sequence=stop.sequence,
            pickups=counts[stop.id, "pickups"],
            boarded=counts[stop.id, "boarded"],
            missed=counts[stop.id, "missed"],
            dropoffs=counts[stop.id, "dropoffs"],
        )
        for stop in sorted(route.stops, key=lambda stop: stop.sequence)
    ]


def average_occupancy(journeys: list[Journey], boarded: Counter) -> float | None:
    """Boardings divided by the seats the buses offered on these journeys."""
    seats = sum(journey.bus.capacity for journey in journeys)
    if seats == 0:
        return None
    return round(sum(boarded[journey.id] for journey in journeys) / seats, 3)


def build_report(db: Session, route: Route, start: date, end: date) -> Report:
    """Everything the admin's report page shows for one period."""
    journeys = completed_journeys(db, start, end)
    boarded = boardings_per_journey(db, journeys)
    stops = demand_by_stop(db, route, journeys)
    return Report(
        start=start,
        end=end,
        completed_journeys=len(journeys),
        boardings=sum(boarded.values()),
        average_occupancy=average_occupancy(journeys, boarded),
        missed_pickups=sum(stop.missed for stop in stops),
        journeys=[
            JourneyRow(
                id=journey.id,
                plate_number=journey.bus.plate_number,
                driver_name=journey.driver.full_name,
                direction=journey.direction,
                started_at=journey.started_at,
                ended_at=journey.ended_at,
                boarded=boarded[journey.id],
            )
            for journey in journeys
        ],
        stops=stops,
    )
