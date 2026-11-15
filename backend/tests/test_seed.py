"""Tests for the seed script, using a throwaway in-memory database."""

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.db import Base
from app.models import Route, Stop
from app.seed import InvalidStopDataError, seed_route
from app.seed_data import STOPS

SAMPLE_STOPS = [("First", -1.98, 30.11), ("Middle", -1.96, 30.12), ("Last", -1.93, 30.14)]


@pytest.fixture
def session():
    """A fresh, empty database for each test, thrown away afterwards."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        yield db


def test_seed_creates_stops_in_order(session):
    """Stops are saved with sequence 1, 2, 3 in the order given."""
    route = seed_route(session, "Test route", SAMPLE_STOPS)
    assert [(s.name, s.sequence) for s in route.stops] == [("First", 1), ("Middle", 2), ("Last", 3)]


def test_seed_twice_does_not_duplicate(session):
    """Running the seed again leaves one route and the same stops."""
    seed_route(session, "Test route", SAMPLE_STOPS)
    seed_route(session, "Test route", SAMPLE_STOPS)
    assert session.scalar(select(func.count()).select_from(Route)) == 1
    assert session.scalar(select(func.count()).select_from(Stop)) == 3


def test_seed_refuses_missing_coordinates(session):
    """A stop without coordinates stops the seed and nothing is saved."""
    with pytest.raises(InvalidStopDataError, match="Missing coordinates for: Middle"):
        seed_route(session, "Test route", [("First", -1.98, 30.11), ("Middle", None, None)])
    assert session.scalar(select(func.count()).select_from(Route)) == 0


def test_seed_refuses_impossible_coordinates(session):
    """A latitude beyond 90 degrees is rejected."""
    with pytest.raises(InvalidStopDataError, match="Impossible coordinates"):
        seed_route(session, "Test route", [("Nowhere", 120.0, 30.0)])


def test_real_route_lists_twelve_unique_stops():
    """The SRS route has 12 designated stops, each named once."""
    names = [name for name, _, _ in STOPS]
    assert len(names) == 12
    assert len(set(names)) == 12
