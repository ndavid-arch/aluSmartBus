"""Fill the database with the route and its stops. Safe to run more than once.

Run from the backend folder:  python -m app.seed
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Route, Stop
from app.seed_data import ROUTE_NAME, STOPS

StopRow = tuple[str, float | None, float | None]


class InvalidStopDataError(ValueError):
    """Raised when stop data is missing or impossible, so nothing wrong is saved."""


def check_stops(stops: list[StopRow]) -> None:
    """Refuse missing coordinates, impossible coordinates and repeated stop names."""
    missing = [name for name, lat, lng in stops if lat is None or lng is None]
    if missing:
        raise InvalidStopDataError(f"Missing coordinates for: {', '.join(missing)}")
    out_of_range = [
        name for name, lat, lng in stops if not (-90 <= lat <= 90 and -180 <= lng <= 180)
    ]
    if out_of_range:
        raise InvalidStopDataError(f"Impossible coordinates for: {', '.join(out_of_range)}")
    names = [name for name, _, _ in stops]
    if len(names) != len(set(names)):
        raise InvalidStopDataError("Two stops have the same name")


def seed_route(session: Session, name: str, stops: list[StopRow]) -> Route:
    """Create the route with its stops in order, or return it unchanged if it already exists."""
    check_stops(stops)
    existing = session.scalar(select(Route).where(Route.name == name))
    if existing is not None:
        return existing
    route = Route(
        name=name,
        stops=[
            Stop(name=stop_name, latitude=lat, longitude=lng, sequence=position)
            for position, (stop_name, lat, lng) in enumerate(stops, start=1)
        ],
    )
    session.add(route)
    session.commit()
    return route


def main() -> None:
    """Seed the real route from seed_data.py into the database in .env."""
    with SessionLocal() as session:
        route = seed_route(session, ROUTE_NAME, STOPS)
        print(f"Route '{route.name}' has {len(route.stops)} stops.")


if __name__ == "__main__":
    main()
