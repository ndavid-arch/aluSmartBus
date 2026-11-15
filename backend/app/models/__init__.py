"""All database models. Importing this package registers every table with Base."""

from app.models.bus import Bus
from app.models.enums import (
    ArrivalStatus,
    Availability,
    Direction,
    JourneyStatus,
    NotificationType,
    PickupStatus,
    Role,
    SelectionType,
)
from app.models.journey import Journey, LocationUpdate, StopArrival
from app.models.route import Route, Stop
from app.models.student_activity import BoardingRecord, Notification, StopSelection
from app.models.user import User

__all__ = [
    "ArrivalStatus",
    "Availability",
    "BoardingRecord",
    "Bus",
    "Direction",
    "Journey",
    "JourneyStatus",
    "LocationUpdate",
    "Notification",
    "NotificationType",
    "PickupStatus",
    "Role",
    "Route",
    "SelectionType",
    "Stop",
    "StopArrival",
    "StopSelection",
    "User",
]
