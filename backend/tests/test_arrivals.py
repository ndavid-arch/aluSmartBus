"""Tests for noticing when the bus reaches a stop (issue #22)."""

import pytest
from sqlalchemy import select

from app.models import ArrivalStatus, StopArrival
from app.seed_data import STOPS
from tests.conftest import auth_headers

REMERA = STOPS[8]
METRES_PER_DEGREE = 111_195  # of latitude, anywhere on Earth


def near(stop, metres_north: float) -> dict:
    """A precise reading this many metres north of a stop."""
    _, lat, lng = stop
    return {"latitude": lat + metres_north / METRES_PER_DEGREE, "longitude": lng, "accuracy": 5}


@pytest.fixture
def journey(client, route, driver, bus):
    """An active Rebero -> ALU journey, as the API returned it."""
    choice = {"bus_id": bus["id"], "direction": "rebero_to_alu"}
    return client.post("/journeys", json=choice, headers=auth_headers(driver)).json()


def send(client, driver, journey, reading):
    """Send one reading from the driver's phone."""
    url = f"/journeys/{journey['id']}/locations"
    assert client.post(url, json=reading, headers=auth_headers(driver)).status_code == 201


def arrivals(client, journey) -> list[dict]:
    """The journey's arrivals as the API lists them."""
    return client.get(f"/journeys/{journey['id']}/arrivals").json()


def set_radius(client, admin, metres):
    """Change the arrival distance as the admin."""
    return client.patch(
        "/admin/settings", json={"arrival_radius_m": metres}, headers=auth_headers(admin)
    )


def test_arrival_is_saved_with_its_time_and_status(client, driver, journey):
    """20 m from Remera Gare is within the default 30 m, so the bus has arrived (FR-28, FR-30)."""
    send(client, driver, journey, near(REMERA, 20))
    [arrival] = arrivals(client, journey)
    assert arrival["stop"]["name"] == "Remera Gare"
    assert arrival["status"] == "at_stop"
    assert arrival["arrived_at"]


def test_outside_the_distance_is_not_an_arrival(client, driver, journey):
    """40 m away is not there yet."""
    send(client, driver, journey, near(REMERA, 40))
    assert arrivals(client, journey) == []


def test_leaving_the_stop_marks_it_departed(client, driver, journey):
    """Once the bus moves 100 m on, the stop is marked departed; its arrival time stays."""
    send(client, driver, journey, near(REMERA, 10))
    send(client, driver, journey, near(REMERA, 100))
    [arrival] = arrivals(client, journey)
    assert arrival["status"] == "departed"


def test_staying_at_a_stop_is_one_arrival(client, db, driver, journey):
    """Several readings at the same stop do not create several arrivals."""
    for metres in (15, 5, 0):
        send(client, driver, journey, near(REMERA, metres))
    assert len(db.scalars(select(StopArrival)).all()) == 1


def test_the_admin_can_change_the_distance(client, admin, driver, journey):
    """With 50 m, a reading 40 m away now counts as arrived (FR-29)."""
    assert client.get("/admin/settings", headers=auth_headers(admin)).json() == {
        "arrival_radius_m": 30.0
    }
    assert set_radius(client, admin, 50).status_code == 200
    send(client, driver, journey, near(REMERA, 40))
    assert [a["stop"]["name"] for a in arrivals(client, journey)] == ["Remera Gare"]


@pytest.mark.parametrize("metres", [2, 500])
def test_the_distance_must_be_sensible(client, admin, metres):
    """Below the GPS limit (5 m) or beyond a block (200 m) is refused."""
    assert set_radius(client, admin, metres).status_code == 422


def test_only_admins_change_settings(client, student, driver):
    """Drivers and students get 403; anyone not signed in gets 401."""
    for user in (student, driver):
        assert set_radius(client, user, 50).status_code == 403
    assert client.get("/admin/settings").status_code == 401


def test_arrivals_follow_the_bus_along_the_route(client, db, driver, journey):
    """Driving past three stops in order records three arrivals, in that order."""
    for stop in STOPS[8:11]:
        send(client, driver, journey, near(stop, 0))
    names = [a["stop"]["name"] for a in arrivals(client, journey)]
    assert names == [STOPS[8][0], STOPS[9][0], STOPS[10][0]]
    statuses = {a.stop.name: a.status for a in db.scalars(select(StopArrival))}
    assert statuses[STOPS[10][0]] == ArrivalStatus.AT_STOP  # still there
    assert statuses[STOPS[8][0]] == ArrivalStatus.DEPARTED
