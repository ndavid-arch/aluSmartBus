"""Tests for counting boardings and showing Full at capacity (issue #28)."""

import pytest

from app.models import Role
from tests.conftest import auth_headers

SEATS = 2  # a small bus, so it fills up in a test


@pytest.fixture
def small_bus(client, admin, bus):
    """The test bus with only 2 seats."""
    url = f"/admin/buses/{bus['id']}"
    return client.patch(url, json={"capacity": SEATS}, headers=auth_headers(admin)).json()


@pytest.fixture
def journey(client, route, driver, small_bus):
    """An active journey on the small bus."""
    choice = {"bus_id": small_bus["id"], "direction": "rebero_to_alu"}
    return client.post("/journeys", json=choice, headers=auth_headers(driver)).json()


@pytest.fixture
def students(make_user):
    """Three students who want to get on."""
    return [make_user(Role.STUDENT, f"student{n}@alustudent.com") for n in range(3)]


def scan(client, student, qr_code):
    """A student scans the code by the bus door (#27)."""
    return client.post("/boardings", json={"qr_code": qr_code}, headers=auth_headers(student))


def status_of(client, bus) -> dict:
    """The bus as everyone sees it."""
    return client.get(f"/buses/{bus['id']}").json()


def test_a_bus_not_on_the_road_has_no_count(client, small_bus):
    """No journey, nothing to count."""
    shown = status_of(client, small_bus)
    assert shown["boarded"] is None
    assert shown["full"] is False


def test_a_new_journey_starts_empty(client, small_bus, journey):
    """On the road, nobody has boarded yet."""
    shown = status_of(client, small_bus)
    assert shown["boarded"] == 0
    assert shown["full"] is False


def test_the_count_comes_from_successful_scans(client, small_bus, journey, students):
    """Repeat scans and invalid codes are not counted (FR-53)."""
    scan(client, students[0], small_bus["qr_code"])
    scan(client, students[0], small_bus["qr_code"])  # already boarded
    scan(client, students[1], "not-a-smartbus-code")  # invalid QR code
    assert status_of(client, small_bus)["boarded"] == 1


def test_full_shows_when_the_count_reaches_capacity(client, small_bus, journey, students):
    """One below capacity is not full; at capacity it is."""
    scan(client, students[0], small_bus["qr_code"])
    assert status_of(client, small_bus)["full"] is False
    scan(client, students[1], small_bus["qr_code"])
    shown = status_of(client, small_bus)
    assert shown["boarded"] == SEATS
    assert shown["full"] is True


def test_a_full_bus_can_still_be_boarded(client, small_bus, journey, students):
    """The system does not block boarding; the driver decides (FR-54)."""
    for student in students[:SEATS]:
        scan(client, student, small_bus["qr_code"])
    assert scan(client, students[2], small_bus["qr_code"]).status_code == 201
    shown = status_of(client, small_bus)
    assert shown["boarded"] == SEATS + 1
    assert shown["full"] is True


def test_the_bus_list_shows_the_count_too(client, small_bus, journey, students):
    """Students see Full in the list of buses, without signing in."""
    scan(client, students[0], small_bus["qr_code"])
    [listed] = client.get("/buses").json()
    assert listed["boarded"] == 1


def test_the_next_journey_counts_from_zero(client, driver, small_bus, journey, students):
    """Boardings belong to one journey; a new trip starts empty."""
    for student in students[:SEATS]:
        scan(client, student, small_bus["qr_code"])
    client.post(f"/journeys/{journey['id']}/end", headers=auth_headers(driver))
    choice = {"bus_id": small_bus["id"], "direction": "alu_to_rebero"}
    client.post("/journeys", json=choice, headers=auth_headers(driver))
    shown = status_of(client, small_bus)
    assert shown["boarded"] == 0
    assert shown["full"] is False
