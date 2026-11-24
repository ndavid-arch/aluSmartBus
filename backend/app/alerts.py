"""'The bus is coming' alerts: about 10 and 5 minutes before the bus reaches a pickup stop (#25).

FR-44, FR-45. The server decides when an alert is due and records it in the notifications
table, so each one is sent only once per journey; the student's page then shows it.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.boarding import pickup_arrivals
from app.eta import minutes_to_stops_ahead
from app.models import (
    Journey,
    LocationUpdate,
    Notification,
    NotificationType,
    PickupStatus,
    SelectionType,
    StopSelection,
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
    waiting = db.scalars(
        select(StopSelection).where(
            StopSelection.journey_id == journey.id,
            StopSelection.type == SelectionType.PICKUP,
            StopSelection.pickup_status == PickupStatus.PENDING,
        )
    )
    new_alerts = []
    for pickup in waiting:
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
