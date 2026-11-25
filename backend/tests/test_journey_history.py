"""Tests for the admin's list of active and completed journeys (issue #29)."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.models import Journey
from tests.conftest import auth_headers


def start(client, driver, bus, direction="rebero_to_alu") -> dict:
    """The driver starts a journey on the bus."""
    choice = {"bus_id": bus["id"], "direction": direction}
    return client.post("/journeys", json=choice, headers=auth_headers(driver)).json()


def end(client, driver, journey):
    """The driver ends the journey."""
    client.post(f"/journeys/{journey['id']}/end", headers=auth_headers(driver))


@pytest.fixture
def finished_then_running(client, db, route, driver, bus):
    """A completed morning trip, then the bus back on the road an hour later."""
    finished = start(client, driver, bus)
    end(client, driver, finished)
    running = start(client, driver, bus, direction="alu_to_rebero")
    # Readings in a test share the same second, so set clear start times
    db.get(Journey, uuid.UUID(finished["id"])).started_at = datetime.now(UTC) - timedelta(hours=1)
    db.commit()
    return finished, running


def listed(client, admin, query="") -> list[dict]:
    """What the admin's journey list shows."""
    response = client.get(f"/journeys{query}", headers=auth_headers(admin))
    assert response.status_code == 200
    return response.json()


def test_active_and_completed_journeys_are_listed_newest_first(
    client, admin, finished_then_running
):
    """Both kinds, with the latest started on top (FR-55)."""
    finished, running = finished_then_running
    assert [j["id"] for j in listed(client, admin)] == [running["id"], finished["id"]]


def test_each_journey_has_bus_driver_direction_and_times(
    client, admin, driver, bus, finished_then_running
):
    """Box 1: everything the admin needs to follow a trip."""
    running, finished = listed(client, admin)
    assert finished["bus"]["plate_number"] == bus["plate_number"]
    assert finished["driver"]["full_name"] == driver.full_name
    assert finished["direction"] == "rebero_to_alu"
    assert finished["status"] == "completed"
    assert finished["started_at"] and finished["ended_at"]
    assert running["status"] == "active"
    assert running["ended_at"] is None


@pytest.mark.parametrize("status", ["active", "completed"])
def test_the_list_can_show_one_kind_only(client, admin, finished_then_running, status):
    """?status=active or ?status=completed."""
    shown = listed(client, admin, f"?status={status}")
    assert [j["status"] for j in shown] == [status]


def test_the_list_is_limited(client, admin, finished_then_running):
    """The admin can ask for fewer rows."""
    assert len(listed(client, admin, "?limit=1")) == 1


@pytest.mark.parametrize("query", ["?limit=0", "?limit=201", "?status=parked"])
def test_bad_filters_are_refused(client, admin, query):
    """Limits outside 1 to 200, or a status that does not exist."""
    assert client.get(f"/journeys{query}", headers=auth_headers(admin)).status_code == 422


def test_only_admins_see_every_journey(client, driver, student):
    """Drivers and students use their own screens; guests must sign in."""
    assert client.get("/journeys", headers=auth_headers(driver)).status_code == 403
    assert client.get("/journeys", headers=auth_headers(student)).status_code == 403
    assert client.get("/journeys").status_code == 401
