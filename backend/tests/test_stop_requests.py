"""Tests for the driver seeing how many students wait at each stop (issue #24)."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.models import Role, StopArrival
from app.seed_data import STOPS
from tests.conftest import auth_headers

REMERA = STOPS[8]


@pytest.fixture
def journey(client, route, driver, bus):
    """An active Rebero -> ALU journey, as the API returned it."""
    choice = {"bus_id": bus["id"], "direction": "rebero_to_alu"}
    return client.post("/journeys", json=choice, headers=auth_headers(driver)).json()


@pytest.fixture
def classmate(make_user):
    """A second student, so counts can go above one."""
    return make_user(Role.STUDENT, "classmate@alustudent.com")


def choose(client, student, journey, kind, stop_name):
    """Choose a pickup or drop-off stop by its name."""
    stops = {s["name"]: s["id"] for s in client.get(f"/journeys/{journey['id']}/stops").json()}
    client.put(
        f"/journeys/{journey['id']}/selections/{kind}",
        json={"stop_id": stops[stop_name]},
        headers=auth_headers(student),
    )


def requests_by_stop(client, user, journey) -> dict[str, tuple[int, int]]:
    """What the driver's list shows, as {stop name: (pickups, drop-offs)}."""
    response = client.get(f"/journeys/{journey['id']}/requests", headers=auth_headers(user))
    assert response.status_code == 200
    return {s["name"]: (s["pickups"], s["dropoffs"]) for s in response.json()}


def test_every_stop_is_listed_in_travel_order_with_no_requests_yet(client, driver, journey):
    """A new journey: all stops, first to last, nobody waiting."""
    listed = client.get(f"/journeys/{journey['id']}/requests", headers=auth_headers(driver)).json()
    assert [stop["name"] for stop in listed] == [name for name, _, _ in STOPS]
    assert all(stop["pickups"] == 0 and stop["dropoffs"] == 0 for stop in listed)


def test_counts_show_how_many_wait_and_get_off_at_each_stop(
    client, driver, student, classmate, journey
):
    """Two students wait at Remera Gare; one gets off at Zindiro (FR-35)."""
    choose(client, student, journey, "pickup", "Remera Gare")
    choose(client, classmate, journey, "pickup", "Remera Gare")
    choose(client, classmate, journey, "dropoff", "Zindiro")
    shown = requests_by_stop(client, driver, journey)
    assert shown["Remera Gare"] == (2, 0)
    assert shown["Zindiro"] == (0, 1)
    assert shown["Kimironko Gare"] == (0, 0)


def test_the_list_follows_a_student_changing_their_stop(client, driver, student, journey):
    """Changing a pickup moves the count from the old stop to the new one."""
    choose(client, student, journey, "pickup", "Remera Gare")
    choose(client, student, journey, "pickup", "Kimironko Gare")
    shown = requests_by_stop(client, driver, journey)
    assert shown["Remera Gare"] == (0, 0)
    assert shown["Kimironko Gare"] == (1, 0)


def test_a_student_who_missed_the_bus_is_not_counted(client, db, driver, student, journey):
    """After the boarding window closes (#23), they are neither waiting nor getting off."""
    choose(client, student, journey, "pickup", "Remera Gare")
    choose(client, student, journey, "dropoff", "Zindiro")
    _, lat, lng = REMERA
    reading = {"latitude": lat, "longitude": lng, "accuracy": 5}
    client.post(f"/journeys/{journey['id']}/locations", json=reading, headers=auth_headers(driver))
    arrival = db.scalar(select(StopArrival))
    arrival.arrived_at = datetime.now(UTC) - timedelta(minutes=4)
    db.commit()
    shown = requests_by_stop(client, driver, journey)
    assert shown["Remera Gare"] == (0, 0)
    assert shown["Zindiro"] == (0, 0)


def test_an_admin_can_see_the_requests_too(client, admin, student, journey):
    """Admins oversee every journey."""
    choose(client, student, journey, "pickup", "Remera Gare")
    assert requests_by_stop(client, admin, journey)["Remera Gare"] == (1, 0)


def test_another_driver_cannot_see_this_journeys_requests(client, make_user, journey):
    """Only the journey's own driver (or an admin) sees who waits where."""
    other = make_user(Role.DRIVER, "other.driver@alueducation.com")
    url = f"/journeys/{journey['id']}/requests"
    assert client.get(url, headers=auth_headers(other)).status_code == 403


@pytest.mark.parametrize("who", ["student", "guest"])
def test_students_and_guests_cannot_see_the_requests(client, student, journey, who):
    """Who waits where is for the driver: a student gets 403, a guest 401."""
    headers = auth_headers(student) if who == "student" else {}
    response = client.get(f"/journeys/{journey['id']}/requests", headers=headers)
    assert response.status_code == (403 if who == "student" else 401)
