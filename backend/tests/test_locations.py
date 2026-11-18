"""Tests for the driver's phone sharing the bus location (issue #16)."""

import uuid

import pytest
from sqlalchemy import func, select

from app.models import Journey, JourneyStatus, LocationUpdate, Role
from tests.conftest import auth_headers

# Remera Gare, read with a typical phone accuracy
READING = {"latitude": -1.9587323, "longitude": 30.1194352, "accuracy": 7}


@pytest.fixture
def journey(client, route, driver, bus):
    """An active journey driven by the test driver, as the API returned it."""
    choice = {"bus_id": bus["id"], "direction": "rebero_to_alu"}
    return client.post("/journeys", json=choice, headers=auth_headers(driver)).json()


def send(client, user, journey_id, reading=READING):
    """Send one reading as the given user and return the response."""
    return client.post(
        f"/journeys/{journey_id}/locations", json=reading, headers=auth_headers(user)
    )


def saved_readings(db) -> int:
    """How many readings are stored."""
    return db.scalar(select(func.count()).select_from(LocationUpdate))


def test_driver_shares_the_bus_location(client, db, driver, journey):
    """A reading from the driver of an active journey is saved with the server's time."""
    response = send(client, driver, journey["id"])
    assert response.status_code == 201
    saved = response.json()
    assert saved["latitude"] == READING["latitude"]
    assert saved["longitude"] == READING["longitude"]
    assert saved["recorded_at"]
    assert saved_readings(db) == 1


def test_every_reading_is_kept(client, db, driver, journey):
    """Readings sent every few seconds are all stored, so the route can be replayed later."""
    for step in range(3):
        moved = {**READING, "latitude": READING["latitude"] + step * 0.0005}
        assert send(client, driver, journey["id"], moved).status_code == 201
    assert saved_readings(db) == 3


def test_an_ended_journey_refuses_readings(client, db, driver, journey):
    """Updates are only accepted for an active journey."""
    db.get(Journey, uuid.UUID(journey["id"])).status = JourneyStatus.COMPLETED
    db.commit()
    assert send(client, driver, journey["id"]).status_code == 409
    assert saved_readings(db) == 0


def test_another_driver_cannot_send_for_this_journey(client, make_user, journey):
    """Only the journey's own driver can move its bus on the map."""
    other_driver = make_user(Role.DRIVER, "driver2@alueducation.com")
    assert send(client, other_driver, journey["id"]).status_code == 403


def test_students_and_guests_cannot_send(client, student, journey):
    """A student gets 403 and someone not signed in gets 401."""
    assert send(client, student, journey["id"]).status_code == 403
    no_sign_in = client.post(f"/journeys/{journey['id']}/locations", json=READING)
    assert no_sign_in.status_code == 401


def test_unknown_journey_is_not_found(client, route, driver):
    """A journey ID that does not exist gives 404."""
    assert send(client, driver, uuid.uuid4()).status_code == 404


@pytest.mark.parametrize(
    "bad",
    [
        {**READING, "latitude": 91},
        {**READING, "longitude": -181},
        {**READING, "accuracy": -1},
    ],
)
def test_impossible_values_are_refused(client, driver, journey, bad):
    """Coordinates outside the Earth or a negative accuracy are rejected."""
    assert send(client, driver, journey["id"], bad).status_code == 422


def test_inaccurate_readings_are_not_saved(client, db, driver, journey):
    """Readings worse than ±30 m (the spike's limit) would make the bus jump about."""
    response = send(client, driver, journey["id"], {**READING, "accuracy": 52})
    assert response.status_code == 422
    assert saved_readings(db) == 0
