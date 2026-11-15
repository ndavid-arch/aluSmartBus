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