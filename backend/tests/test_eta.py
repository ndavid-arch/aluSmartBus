"""Tests for working out a bus's next stop and ETA (issue #18)."""

import pytest

from app.eta import bus_progress
from app.models import Direction, Stop
from app.seed_data import STOPS

SPEED_KMH = 20
OFF_ROUTE_M = 400
REBERO, RUJUGIRO = STOPS[0], STOPS[1]


@pytest.fixture
def stops() -> list[Stop]:
    """The real 13 stops, as unsaved Stop objects; no database needed."""
    return [
        Stop(name=name, latitude=lat, longitude=lng, sequence=number)
        for number, (name, lat, lng) in enumerate(STOPS, start=1)
    ]


def progress(stops, lat, lng, direction=Direction.REBERO_TO_ALU):
    """The next stop and ETA for a bus at this position."""
    return bus_progress(stops, direction, lat, lng, SPEED_KMH, OFF_ROUTE_M)


def halfway(stop_a, stop_b) -> tuple[float, float]:
    """The point midway between two stops."""
    return (stop_a[1] + stop_b[1]) / 2, (stop_a[2] + stop_b[2]) / 2


def test_between_two_stops_the_next_one_is_ahead(stops):
    """Halfway from Rebero to Rujugiro (about 1.7 km), Rujugiro is next, about 3 min away."""
    result = progress(stops, *halfway(REBERO, RUJUGIRO))
    assert result.next_stop == "Rujugiro"
    assert result.eta_minutes == 3  # 850 m at 20 km/h is about 2.5 min, rounded up


def test_the_other_direction_meets_the_stops_in_reverse(stops):
    """Going ALU -> Rebero from the same spot, Rebero is next instead."""
    result = progress(stops, *halfway(REBERO, RUJUGIRO), direction=Direction.ALU_TO_REBERO)
    assert result.next_stop == "Rebero"


def test_eta_gets_smaller_as_the_bus_moves_on(stops):
    """Each new position gives a new, closer ETA (FR-25)."""
    lat_a, lng_a = REBERO[1], REBERO[2]
    lat_b, lng_b = RUJUGIRO[1], RUJUGIRO[2]
    etas = [
        progress(stops, lat_a + (lat_b - lat_a) * f, lng_a + (lng_b - lng_a) * f).eta_minutes
        for f in (0.2, 0.5, 0.9)
    ]
    assert etas == sorted(etas, reverse=True)
    assert etas[0] > etas[-1]


def test_at_a_stop_the_eta_is_zero_not_negative(stops):
    """Standing at the last stop, the ETA is 0, never below."""
    _, lat, lng = STOPS[-1]
    result = progress(stops, lat, lng)
    assert result.next_stop == "ALU Campus"
    assert result.eta_minutes == 0


def test_just_before_the_first_stop_it_is_next(stops):
    """A bus about 150 m before Rebero (at the depot, say) is heading to Rebero first."""
    result = progress(stops, REBERO[1] - 0.0013, REBERO[2] - 0.0003)
    assert result.next_stop == "Rebero"
    assert result.eta_minutes >= 0


def test_far_from_the_route_there_is_no_next_stop(stops):
    """At the parking station a few km away: 'Not on the route yet', no ETA."""
    result = progress(stops, -1.9500, 30.0600)
    assert result.next_stop is None
    assert result.eta_minutes is None


def test_a_route_with_fewer_than_two_stops_gives_no_eta(stops):
    """There is no line to follow with one stop, so nothing is guessed."""
    assert progress(stops[:1], REBERO[1], REBERO[2]).next_stop is None
