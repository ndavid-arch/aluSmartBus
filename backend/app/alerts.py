"""Alerts for students waiting for a pickup (the server decides; the student's page shows them).

- 'The bus is coming', about 10 and 5 minutes before the stop (#25, FR-44, FR-45)
- 'The bus is here', when it reaches the stop (#26, FR-46)
- 'You missed the bus' is sent where pickups are marked missed, in app/boarding.py (FR-47)

Each is saved in the notifications table, so a student gets each kind once per journey.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.boarding import pickup_arrivals, waiting_pickups
from app.eta import minutes_to_stops_ahead
from app.models import (
    Journey,
    LocationUpdate,
    Notification,
    NotificationType,
    StopArrival,
)

# Closest first: a bus 4 minutes away gets the 5-minute alert, not the 10-minute one
COMING_ALERTS = [
    (5, NotificationType.FIVE_MINUTES),
    (10, NotificationType.TEN_MINUTES),
]


def coming_alert_due(minutes: int) -> NotificationType | None:
    """Which 'bus is coming' alert fits this many minutes away, if any."""
    return next((kind for limit, kind in COMING_ALERTS if minutes <= limit), None)


def coming_message(kind: NotificationType, stop_name: str) -> str:
    """The words of the alert, e.g. 'The bus is about 5 minutes from Remera Gare.'"""
    minutes = 5 if kind == NotificationType.FIVE_MINUTES else 10
    return f"The bus is about {minutes} minutes from {stop_name}. Start walking to the stop."


def send_coming_alerts(
    db: Session, journey: Journey, location: LocationUpdate
) -> list[Notification]:
    """Record the 10- and 5-minute alerts now due for this journey's waiting students."""
    minutes_away = minutes_to_stops_ahead(journey, location)
    arrived = pickup_arrivals(journey)  # the bus is already there: the 'arrived' alert (#26)
    sent = {
        (alert.student_id, alert.type)
        for alert in db.scalars(select(Notification).where(Notification.journey_id == journey.id))
    }
    new_alerts = []
    for pickup in waiting_pickups(db, journey):
        minutes = minutes_away.get(pickup.stop_id)  # None: passed, or the bus is off the route
        if minutes is None or pickup.stop_id in arrived:
            continue
        kind = coming_alert_due(minutes)
        if kind is None:
            continue
        # Never go back to "10 minutes" after "5 minutes" (traffic can make the ETA jump)
        already = {(pickup.student_id, kind), (pickup.student_id, NotificationType.FIVE_MINUTES)}
        if already & sent:
            continue
        alert = Notification(
            student_id=pickup.student_id,
            journey_id=journey.id,
            type=kind,
            message=coming_message(kind, pickup.stop.name),
        )
        db.add(alert)
        new_alerts.append(alert)
    return new_alerts


def send_arrival_alerts(
    db: Session, journey: Journey, new_arrivals: list[StopArrival]
) -> list[Notification]:
    """Tell each student waiting at a stop the bus has just reached that it is there (FR-46)."""
    reached = {arrival.stop_id for arrival in new_arrivals}
    new_alerts = []
    for pickup in waiting_pickups(db, journey):
        if pickup.stop_id not in reached:
            continue
        alert = Notification(
            student_id=pickup.student_id,
            journey_id=journey.id,
            type=NotificationType.ARRIVED,
            message=f"The bus is at {pickup.stop.name}. Board within 3 minutes.",
        )
        db.add(alert)
        new_alerts.append(alert)
    return new_alerts
