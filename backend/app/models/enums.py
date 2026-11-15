"""Fixed lists of allowed values, taken from the class diagram."""

import enum


class Role(enum.StrEnum):
    """What a signed-in user is allowed to do. Guests have no account, so no role."""

    STUDENT = "student"
    DRIVER = "driver"
    ADMIN = "admin"


class Availability(enum.StrEnum):
    """Whether a bus can be used today."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class Direction(enum.StrEnum):
    """Which way a journey goes along the route."""

    REBERO_TO_ALU = "rebero_to_alu"
    ALU_TO_REBERO = "alu_to_rebero"


class JourneyStatus(enum.StrEnum):
    """A journey is active from Start until it reaches the last stop or the driver ends it."""

    ACTIVE = "active"
    COMPLETED = "completed"


class ArrivalStatus(enum.StrEnum):
    """Whether the bus is still at a stop (boarding window open) or has left it."""

    AT_STOP = "at_stop"
    DEPARTED = "departed"


class SelectionType(enum.StrEnum):
    """Whether a student chose a stop to get on or to get off."""

    PICKUP = "pickup"
    DROPOFF = "dropoff"


class PickupStatus(enum.StrEnum):
    """What happened to a student's pickup request."""

    PENDING = "pending"
    BOARDED = "boarded"
    MISSED = "missed"


class NotificationType(enum.StrEnum):
    """The alerts a student can receive (FR-44 to FR-47)."""

    TEN_MINUTES = "ten_minutes"
    FIVE_MINUTES = "five_minutes"
    ARRIVED = "arrived"
    MISSED_PICKUP = "missed_pickup"
