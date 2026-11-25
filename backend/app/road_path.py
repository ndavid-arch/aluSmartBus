"""The route along the real roads (#79).

A routing engine is asked once for the road path through the stops, and the answer is saved in
app/data/road_path.json, so the app never calls it again. Run it from the backend folder:

    python -m app.road_path

Without the file, the map joins the stops with straight lines, as before.
"""

import json
import sys
from functools import cache
from pathlib import Path
from urllib.request import urlopen

from app.geo import distance_m
from app.seed_data import STOPS

PATH_FILE = Path(__file__).parent / "data" / "road_path.json"
# The free OSRM demo server: no key needed, fine for one request (it uses OpenStreetMap roads)
ROUTING_URL = "https://router.project-osrm.org/route/v1/driving/"
# A stop further than this from the road path means the engine chose another road there
MAX_STOP_GAP_M = 60

# Extra points the bus passes through, when the engine picks a different road than the bus.
# Key: the stop they come after (0 = Rebero); value: (latitude, longitude) points, in order.
# Example: {6: [(-1.9681, 30.0942)]} makes the path go through that point after Rwandex.
VIA_POINTS: dict[int, list[tuple[float, float]]] = {}

Point = tuple[float, float]  # (latitude, longitude)


def waypoints(stops=STOPS, via=VIA_POINTS) -> list[Point]:
    """The stops in order with any via points after the stop they belong to."""
    points: list[Point] = []
    for index, (_, lat, lng) in enumerate(stops):
        points.append((lat, lng))
        points.extend(via.get(index, []))
    return points


def routing_url(points: list[Point]) -> str:
    """The request for one route through all points; OSRM wants longitude first."""
    coordinates = ";".join(f"{lng},{lat}" for lat, lng in points)
    return f"{ROUTING_URL}{coordinates}?overview=full&geometries=geojson"


def path_from_answer(answer: dict) -> list[Point]:
    """The road path as (latitude, longitude) points, from the engine's GeoJSON answer."""
    if answer.get("code") != "Ok" or not answer.get("routes"):
        raise ValueError(f"The routing engine found no route: {answer.get('message', answer)}")
    return [(lat, lng) for lng, lat in answer["routes"][0]["geometry"]["coordinates"]]


def stops_off_the_path(path: list[Point], stops=STOPS) -> list[tuple[str, float]]:
    """Stops further than MAX_STOP_GAP_M from every point of the path, with their distance."""
    far = []
    for name, lat, lng in stops:
        gap = min(distance_m(lat, lng, p_lat, p_lng) for p_lat, p_lng in path)
        if gap > MAX_STOP_GAP_M:
            far.append((name, round(gap)))
    return far


def path_length_km(path: list[Point]) -> float:
    """How long the path is along the road, in kilometres."""
    metres = sum(distance_m(*a, *b) for a, b in zip(path, path[1:], strict=False))
    return round(metres / 1000, 1)


@cache
def load_road_path() -> list[Point] | None:
    """The saved road path, or None when it has not been fetched yet (read once per process)."""
    if not PATH_FILE.exists():
        return None
    return [(lat, lng) for lat, lng in json.loads(PATH_FILE.read_text())["points"]]


def main() -> int:
    """Fetch the road path once, check it against the stops, and save it."""
    with urlopen(routing_url(waypoints()), timeout=30) as response:  # noqa: S310 (fixed https URL)
        path = path_from_answer(json.load(response))
    PATH_FILE.parent.mkdir(parents=True, exist_ok=True)  # git does not keep an empty folder
    PATH_FILE.write_text(
        json.dumps(
            {"source": "OSRM, OpenStreetMap contributors", "points": [list(p) for p in path]},
        )
    )
    print(f"Saved {len(path)} points, {path_length_km(path)} km, to {PATH_FILE}")
    for name, gap in stops_off_the_path(path):
        print(
            f"  Check {name}: {gap} m from the path; add a via point near it if the road is wrong"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
