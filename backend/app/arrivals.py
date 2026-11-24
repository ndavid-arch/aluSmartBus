"""Noticing when the bus reaches a stop and when it leaves it (FR-28 to FR-30)."""

from app.geo import distance_m
from app.models import ArrivalStatus, Journey, StopArrival


def record_arrivals(journey: Journey, lat: float, lng: float, radius_m: float) -> list[StopArrival]:
    """Save an arrival for each stop the bus has just come within radius_m of, and mark the ones it
    has moved away from as departed. Returns the new arrivals (for alerts and boarding later).
    """
    known = {arrival.stop_id: arrival for arrival in journey.stop_arrivals}
    new_arrivals = []
    for stop in journey.route.stops:
        at_stop = distance_m(lat, lng, stop.latitude, stop.longitude) <= radius_m
        arrival = known.get(stop.id)
        if at_stop and arrival is None:
            arrival = StopArrival(stop_id=stop.id)
            journey.stop_arrivals.append(arrival)
            new_arrivals.append(arrival)
        elif arrival is not None and not at_stop and arrival.status == ArrivalStatus.AT_STOP:
            arrival.status = ArrivalStatus.DEPARTED
    return new_arrivals
