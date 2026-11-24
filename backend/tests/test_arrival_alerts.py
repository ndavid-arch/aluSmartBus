"""Tests for the 'the bus is here' and 'you missed the bus' alerts (issue #26)."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.models import Notification, StopArrival
from app.seed_data import STOPS
from tests.conftest import auth_headers

REMERA, KIMIRONKO = STOPS[8], STOPS[9]


def at(stop) -> dict:
    """A precise reading exactly at a stop."""
    _, lat, lng = stop
    return {"latitude": lat, "longitude": lng, "accuracy": 5}


@pytest.fixture
def journey(client, route, driver, bus):
    """An active Rebero -> ALU journey, as the API returned it."""
    choice = {"bus_id": bus["id"], "direction": "rebero_to_alu"}
    return client.post("/journeys", json=choice, headers=auth_headers(driver)).json()


def choose(client, student, journey, kind, stop):
    """Choose a pickup or drop-off stop."""
    stops = {s["name"]: s["id"] for s in client.get(f"/journeys/{journey['id']}/stops").json()}
    client.put(
        f"/journeys/{journey['id']}/selections/{kind}",
        json={"stop_id": stops[stop[0]]},
        headers=auth_headers(student),
    )


def send(client, driver, journey, reading):
    """Send one reading from the driver's phone."""
    url = f"/journeys/{journey['id']}/locations"
    assert client.post(url, json=reading, headers=auth_headers(driver)).status_code == 201


def my_alerts(client, student, journey) -> list[dict]:
    """The alerts I have received for this journey, oldest first."""
    url = f"/journeys/{journey['id']}/notifications/mine"
    return client.get(url, headers=auth_headers(student)).json()


def backdate_arrival(db, minutes: float):
    """Pretend the bus reached the stop this many minutes ago."""
    arrival = db.scalar(select(StopArrival))
    arrival.arrived_at = datetime.now(UTC) - timedelta(minutes=minutes)
    db.commit()


def test_arrived_alert_when_the_bus_reaches_my_stop(client, driver, student, journey):
    """The bus at my pickup stop: 'the bus is here, board within 3 minutes' (FR-46)."""
    choose(client, student, journey, "pickup", REMERA)
    send(client, driver, journey, at(REMERA))
    [alert] = [a for a in my_alerts(client, student, journey) if a["type"] == "arrived"]
    assert alert["message"] == "The bus is at Remera Gare. Board within 3 minutes."


def test_the_arrived_alert_is_sent_once(client, driver, student, journey):
    """The bus staying at the stop does not repeat it."""
    choose(client, student, journey, "pickup", REMERA)
    for _ in range(3):
        send(client, driver, journey, at(REMERA))
    kinds = [a["type"] for a in my_alerts(client, student, journey)]
    assert kinds.count("arrived") == 1


def test_no_arrived_alert_for_another_stop(client, driver, student, journey):
    """The bus reaching Remera Gare says nothing to a student waiting at Kimironko Gare."""
    choose(client, student, journey, "pickup", KIMIRONKO)
    send(client, driver, journey, at(REMERA))
    assert "arrived" not in [a["type"] for a in my_alerts(client, student, journey)]


def test_missed_alert_when_the_window_closes(client, db, driver, student, journey):
    """3 minutes pass without boarding: 'you missed the bus' (FR-47)."""
    choose(client, student, journey, "pickup", REMERA)
    send(client, driver, journey, at(REMERA))
    backdate_arrival(db, minutes=4)
    send(client, driver, journey, at(KIMIRONKO))
    [alert] = [a for a in my_alerts(client, student, journey) if a["type"] == "missed_pickup"]
    assert alert["message"].startswith("You missed the bus at Remera Gare")


def test_the_missed_alert_is_sent_once(client, db, driver, student, journey):
    """Every later check (bus positions, my page) finds it already missed: no second alert."""
    choose(client, student, journey, "pickup", REMERA)
    send(client, driver, journey, at(REMERA))
    backdate_arrival(db, minutes=4)
    url = f"/journeys/{journey['id']}/selections/mine"
    client.get(url, headers=auth_headers(student))  # marks it missed
    send(client, driver, journey, at(KIMIRONKO))
    client.get(url, headers=auth_headers(student))
    kinds = [a["type"] for a in my_alerts(client, student, journey)]
    assert kinds.count("missed_pickup") == 1


def test_no_alert_when_a_bus_is_marked_unavailable(client, db, admin, student, bus, journey):
    """FR-48: an unavailable bus is shown only when a student selects it, never pushed."""
    choose(client, student, journey, "pickup", REMERA)
    change = {"availability": "unavailable", "reason": "Flat tyre"}
    url = f"/buses/{bus['id']}/availability"
    assert client.patch(url, json=change, headers=auth_headers(admin)).status_code == 200
    assert db.scalars(select(Notification)).all() == []
