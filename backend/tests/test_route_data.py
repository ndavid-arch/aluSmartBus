"""Checks on the real route data in seed_data.py, so a typo is caught before it is seeded."""

from itertools import pairwise

import pytest

from app.geo import distance_m
from app.seed import check_stops
from app.seed_data import STOPS

# Kigali lies roughly inside this box; a stop outside it is a typo (e.g. a lost minus sign)
KIGALI_LAT = (-2.1, -1.8)
KIGALI_LNG = (29.9, 30.3)

# Neighbouring stops on this route are never this far apart; more means a stop is misplaced
MAX_GAP_M = 3_000


def test_distance_between_two_known_points():
    """One degree of latitude is about 111 km anywhere on Earth."""
    assert distance_m(0, 30, 1, 30) == pytest.approx(111_195, rel=0.001)
    assert distance_m(-1.95, 30.1, -1.95, 30.1) == 0


def test_real_stops_pass_the_seed_checks():
    """Every stop has coordinates and a unique name, so the seed script will run."""
    check_stops(STOPS)


def test_every_stop_is_in_kigali():
    """A stop outside Kigali means a typo in its coordinates."""
    for name, lat, lng in STOPS:
        assert KIGALI_LAT[0] < lat < KIGALI_LAT[1], name
        assert KIGALI_LNG[0] < lng < KIGALI_LNG[1], name


def test_neighbouring_stops_are_close_together():
    """Consecutive stops are within 3 km of each other, so none is in the wrong place."""
    for (name1, lat1, lng1), (name2, lat2, lng2) in pairwise(STOPS):
        gap = distance_m(lat1, lng1, lat2, lng2)
        assert 100 < gap < MAX_GAP_M, f"{name1} -> {name2}: {gap:.0f} m"
