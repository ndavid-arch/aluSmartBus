"""Where a bus is along its route: the next stop and roughly when it gets there (FR-24, FR-25),
and how long until each stop after it (#25).

The route is treated as straight lines between consecutive stops. Over a few kilometres of
Kigali that is close enough, and it needs no outside map service.
"""

from dataclasses import dataclass
from itertools import pairwise
from math import ceil, cos, hypot, radians

from app.core.config import get_settings
from app.geo import EARTH_RADIUS_M
from app.models import Direction, Journey, LocationUpdate, Stop

SECONDS_PER_MINUTE = 60

Point = tuple[float, float]  # metres east and north on a flat grid


@dataclass(frozen=True)
class Progress:
    """The answer for one bus: its next stop and ETA, or None for both when off the route."""

    next_stop: str | None
    eta_minutes: int | None
    # The next stop's place in travel order; the stops before it have been passed
    next_index: int | None = None


def to_xy(lat: float, lng: float, ref_lat: float) -> Point:
    """Turn a position into metres on a flat grid; accurate enough across one city."""
    x = radians(lng) * EARTH_RADIUS_M * cos(radians(ref_lat))
    y = radians(lat) * EARTH_RADIUS_M
    return x, y


def closest_point_on_segment(p: Point, a: Point, b: Point) -> tuple[float, float]:
    """Where along a-b the point nearest to p is (0 = at a, 1 = at b), and how far p is from it."""
    ab_x, ab_y = b[0] - a[0], b[1] - a[1]
    length_squared = ab_x**2 + ab_y**2
    if length_squared == 0:
        along = 0.0
    else:
        along = ((p[0] - a[0]) * ab_x + (p[1] - a[1]) * ab_y) / length_squared
        along = min(max(along, 0.0), 1.0)
    nearest = (a[0] + along * ab_x, a[1] + along * ab_y)
    return along, hypot(p[0] - nearest[0], p[1] - nearest[1])


def stops_in_travel_order(stops: list[Stop], direction: Direction) -> list[Stop]:
    """Stops are stored Rebero -> ALU; going the other way, the bus meets them in reverse."""
    ordered = sorted(stops, key=lambda stop: stop.sequence)
    return ordered if direction == Direction.REBERO_TO_ALU else ordered[::-1]


def minutes_for(metres: float, speed_kmh: float) -> int:
    """Whole minutes to drive this far at the average speed, rounded up."""
    metres_per_second = speed_kmh * 1000 / 3600
    return max(ceil(metres / metres_per_second / SECONDS_PER_MINUTE), 0)


def locate_on_route(
    route: list[Stop], lat: float, lng: float, off_route_m: float
) -> tuple[int, list[float]] | None:
    """The bus's next stop (its place in travel order) and the metres from the bus to it and to
    every later stop; None when the bus is not on the route."""
    if len(route) < 2:
        return None
    ref_lat = route[0].latitude
    bus = to_xy(lat, lng, ref_lat)
    points = [to_xy(stop.latitude, stop.longitude, ref_lat) for stop in route]

    # The leg of the route the bus is closest to tells us which stop comes next
    legs = [closest_point_on_segment(bus, a, b) for a, b in pairwise(points)]
    leg, (along, distance_from_route) = min(enumerate(legs), key=lambda item: item[1][1])
    if distance_from_route > off_route_m:
        return None

    if leg == 0 and along == 0:
        next_index, metres_left = 0, hypot(bus[0] - points[0][0], bus[1] - points[0][1])
    else:
        a, b = points[leg], points[leg + 1]
        next_index = leg + 1
        metres_left = (1 - along) * hypot(b[0] - a[0], b[1] - a[1])

    # Then add each leg after the next stop, one by one
    metres = [metres_left]
    for a, b in pairwise(points[next_index:]):
        metres.append(metres[-1] + hypot(b[0] - a[0], b[1] - a[1]))
    return next_index, metres


def bus_progress(
    stops: list[Stop],
    direction: Direction,
    lat: float,
    lng: float,
    speed_kmh: float,
    off_route_m: float,
) -> Progress:
    """Find the bus's next stop and ETA from its position, or say it is not on the route."""
    route = stops_in_travel_order(stops, direction)
    located = locate_on_route(route, lat, lng, off_route_m)
    if located is None:
        return Progress(next_stop=None, eta_minutes=None)
    next_index, metres = located
    return Progress(
        next_stop=route[next_index].name,
        eta_minutes=minutes_for(metres[0], speed_kmh),
        next_index=next_index,
    )


def stops_ahead(journey: Journey, location: LocationUpdate) -> list[tuple[Stop, int]]:
    """Each stop still ahead of the bus, in travel order, with the minutes until it gets there
    (#25, #70). Empty when the bus is off the route, so nothing is shown or sent on a guess."""
    settings = get_settings()
    route = stops_in_travel_order(journey.route.stops, journey.direction)
    located = locate_on_route(
        route, location.latitude, location.longitude, settings.off_route_distance_m
    )
    if located is None:
        return []
    next_index, metres = located
    return [
        (stop, minutes_for(distance, settings.average_bus_speed_kmh))
        for stop, distance in zip(route[next_index:], metres, strict=True)
    ]


def minutes_to_stops_ahead(journey: Journey, location: LocationUpdate) -> dict:
    """Minutes until the bus reaches each stop still ahead of it, by stop ID (for the alerts)."""
    return {stop.id: minutes for stop, minutes in stops_ahead(journey, location)}


def journey_progress(journey: Journey, location: LocationUpdate) -> Progress:
    """bus_progress for a journey at one of its readings, using the app's settings."""
    settings = get_settings()
    return bus_progress(
        journey.route.stops,
        journey.direction,
        location.latitude,
        location.longitude,
        settings.average_bus_speed_kmh,
        settings.off_route_distance_m,
    )
