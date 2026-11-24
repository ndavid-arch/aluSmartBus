"""Tests for the 3-minute boarding window and missed pickups (issue #23)."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.boarding import expire_missed_pickups, within_window
from app.models import Journey, PickupStatus, StopArrival, StopSelection
from app.seed_data import STOPS
from tests.conftest import auth_headers

ARRIVED = datetime(2026, 11, 24, 8, 0, 0, tzinfo=UTC)
REMERA = STOPS[8]


def at(stop) -> dict:
    """A precise reading exactly at a stop."""
    _, lat, lng = stop
    return {"latitude": lat, "longitude": lng, "accuracy": 5}


# --- The rule itself (FR-34 boundary tests) ---------------------------------------------


@pytest.mark.parametrize(
    ("after", "counts"),
    [
        (timedelta(minutes=2, seconds=59), True),
        (timedelta(minutes=3), True),
        (timedelta(minutes=3, seconds=1), False),
        (timedelta(seconds=-1), False),
    ],
)
def test_a_scan_counts_only_inside_the_three_minutes(after, counts):
    """2:59 and 3:00 count; 3:01 is too late; before the bus arrives does not count either."""
    assert within_window(ARRIVED, ARRIVED + after) is counts


# --- Through the API ---------------------------------------------------------------------


@pytest.fixture
def journey(client, route, driver, bus):
    """An active Rebero -> ALU journey, as the API returned it."""
    choice = {"bus_id": bus["id"], "direction": "rebero_to_alu"}
    return client.post("/journeys", json=choice, headers=auth_headers(driver)).json()


@pytest.fixture
def pickup_at_remera(client, student, journey):
    """The student's pickup is Remera Gare."""
    stops = {s["name"]: s["id"] for s in client.get(f"/journeys/{journey['id']}/stops").json()}
    client.put(
        f"/journeys/{journey['id']}/selections/pickup",
        json={"stop_id": stops["Remera Gare"]},
        headers=auth_headers(student),
    )


def my_pickup(client, student, journey) -> dict:
    """My pickup as the API shows it."""
    url = f"/journeys/{journey['id']}/selections/mine"
    [pickup] = client.get(url, headers=auth_headers(student)).json()
    return pickup


def send(client, driver, journey, reading):
    """Send one reading from the driver's phone."""
    url = f"/journeys/{journey['id']}/locations"
    assert client.post(url, json=reading, headers=auth_headers(driver)).status_code == 201


def backdate_arrival(db, minutes: float):
    """Pretend the bus reached the stop this many minutes ago."""
    arrival = db.scalar(select(StopArrival))
    arrival.arrived_at = datetime.now(UTC) - timedelta(minutes=minutes)
    db.commit()


def test_before_the_bus_arrives_the_pickup_is_waiting(client, student, journey, pickup_at_remera):
    """No arrival yet: the window has not opened."""
    pickup = my_pickup(client, student, journey)
    assert pickup["window_state"] == "waiting"
    assert pickup["window_closes_at"] is None


def test_the_window_opens_when_the_bus_reaches_my_stop(
    client, driver, student, journey, pickup_at_remera
):
    """Arrival at my pickup stop opens a 3-minute window (FR-31)."""
    send(client, driver, journey, at(REMERA))
    pickup = my_pickup(client, student, journey)
    assert pickup["window_state"] == "open"
    assert pickup["window_closes_at"] is not None


def test_after_three_minutes_without_boarding_the_pickup_is_missed(
    client, db, driver, student, journey, pickup_at_remera
):
    """Not boarded within 3 minutes: MISSED, and shown as missed, not as waiting (FR-32, FR-33)."""
    send(client, driver, journey, at(REMERA))
    backdate_arrival(db, minutes=4)
    pickup = my_pickup(client, student, journey)
    assert pickup["pickup_status"] == "missed"
    assert pickup["window_state"] == "missed"


def test_the_next_bus_position_also_marks_missed_pickups(
    client, db, driver, student, journey, pickup_at_remera
):
    """Even if the student is not looking, the next reading updates the pickup."""
    send(client, driver, journey, at(REMERA))
    backdate_arrival(db, minutes=4)
    send(client, driver, journey, at(STOPS[9]))
    selection = db.scalar(select(StopSelection))
    db.refresh(selection)
    assert selection.pickup_status == PickupStatus.MISSED


def test_expiry_follows_the_same_boundaries(client, db, driver, journey, pickup_at_remera):
    """Checked at 2:59 the pickup stays pending; at 3:01 it is missed."""
    send(client, driver, journey, at(REMERA))
    saved = db.get(Journey, uuid.UUID(journey["id"]))
    arrived_at = db.scalar(select(StopArrival)).arrived_at
    assert expire_missed_pickups(db, saved, arrived_at + timedelta(minutes=2, seconds=59)) == []
    [missed] = expire_missed_pickups(db, saved, arrived_at + timedelta(minutes=3, seconds=1))
    assert missed.pickup_status == PickupStatus.MISSED


def test_a_missed_pickup_cannot_be_changed(client, db, driver, student, journey, pickup_at_remera):
    """Once missed, the record stays as it is (for reports)."""
    send(client, driver, journey, at(REMERA))
    backdate_arrival(db, minutes=4)
    my_pickup(client, student, journey)
    stops = {s["name"]: s["id"] for s in client.get(f"/journeys/{journey['id']}/stops").json()}
    response = client.put(
        f"/journeys/{journey['id']}/selections/pickup",
        json={"stop_id": stops["Zindiro"]},
        headers=auth_headers(student),
    )
    assert response.status_code == 409


def test_a_drop_off_has_no_boarding_window(client, student, journey):
    """The window is only about getting on."""
    stops = {s["name"]: s["id"] for s in client.get(f"/journeys/{journey['id']}/stops").json()}
    url = f"/journeys/{journey['id']}/selections/dropoff"
    response = client.put(url, json={"stop_id": stops["Zindiro"]}, headers=auth_headers(student))
    assert response.json()["window_state"] is None
