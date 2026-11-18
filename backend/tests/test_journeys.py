"""Tests for drivers starting journeys (issue #15)."""

import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Journey, Role
from tests.conftest import auth_headers

OTHER_BUS = {"plate_number": "RAC 456 B", "capacity": 25}


@pytest.fixture
def second_bus(client, admin):
    """Another registered bus, for tests that need two."""
    return client.post("/admin/buses", json=OTHER_BUS, headers=auth_headers(admin)).json()


@pytest.fixture
def second_driver(make_user):
    """Another driver account, for tests that need two."""
    return make_user(Role.DRIVER, "driver2@alueducation.com")


def start(client, user, bus_id, direction="rebero_to_alu"):
    """Ask to start a journey as the given user and return the response."""
    return client.post(
        "/journeys",
        json={"bus_id": str(bus_id), "direction": direction},
        headers=auth_headers(user),
    )


@pytest.mark.parametrize("direction", ["rebero_to_alu", "alu_to_rebero"])
def test_driver_starts_a_journey_in_either_direction(client, route, driver, bus, direction):
    """Starting records the bus, driver, direction, start time and status ACTIVE."""
    response = start(client, driver, bus["id"], direction)
    assert response.status_code == 201
    journey = response.json()
    assert journey["direction"] == direction
    assert journey["status"] == "active"
    assert journey["started_at"]
    assert journey["bus"]["plate_number"] == "RAB 123 A"
    assert journey["driver"]["full_name"] == driver.full_name


def test_journey_is_saved_on_the_route(client, db, route, driver, bus):
    """The journey row points to the Rebero - ALU route."""
    journey_id = start(client, driver, bus["id"]).json()["id"]
    assert db.get(Journey, uuid.UUID(journey_id)).route_id == route.id


def test_unknown_direction_is_refused(client, route, driver, bus):
    """Only the two real directions are accepted."""
    assert start(client, driver, bus["id"], "rebero_to_town").status_code == 422


def test_a_bus_cannot_have_two_active_journeys(client, route, driver, second_driver, bus):
    """A second driver cannot start a bus that is already on the road."""
    start(client, driver, bus["id"])
    response = start(client, second_driver, bus["id"])
    assert response.status_code == 409
    assert response.json()["detail"] == "This bus is already on a journey"


def test_a_driver_cannot_drive_two_buses(client, route, driver, bus, second_bus):
    """One driver has at most one active journey."""
    start(client, driver, bus["id"])
    assert start(client, driver, second_bus["id"]).status_code == 409


def test_an_unavailable_bus_cannot_start(client, route, admin, driver, bus):
    """A bus marked Unavailable (#14) stays off the road."""
    client.patch(
        f"/buses/{bus['id']}/availability",
        json={"availability": "unavailable", "reason": "Flat tyre"},
        headers=auth_headers(admin),
    )
    assert start(client, driver, bus["id"]).status_code == 409


def test_unknown_bus_is_not_found(client, route, driver):
    """A bus ID that does not exist gives 404."""
    assert start(client, driver, uuid.uuid4()).status_code == 404


def test_only_drivers_start_journeys(client, route, student, admin, bus):
    """Students and admins get 403; anyone not signed in gets 401."""
    assert start(client, student, bus["id"]).status_code == 403
    assert start(client, admin, bus["id"]).status_code == 403
    no_sign_in = client.post("/journeys", json={"bus_id": bus["id"], "direction": "rebero_to_alu"})
    assert no_sign_in.status_code == 401


def test_starting_without_the_route_explains_the_problem(client, driver, bus):
    """If the seed script has not been run, the driver gets a clear 503, not a crash."""
    response = start(client, driver, bus["id"])
    assert response.status_code == 503


def test_active_journeys_are_visible_to_drivers_and_admins(
    client, route, student, admin, driver, bus
):
    """Drivers and admins see who is on the road; students do not use this list."""
    start(client, driver, bus["id"])
    for user in (driver, admin):
        response = client.get("/journeys/active", headers=auth_headers(user))
        assert response.status_code == 200
        assert [j["bus"]["plate_number"] for j in response.json()] == ["RAB 123 A"]
    assert client.get("/journeys/active", headers=auth_headers(student)).status_code == 403


def test_database_refuses_two_active_journeys_for_one_bus(db, route, driver, second_driver, bus):
    """Even if the checks were skipped, the database index blocks a second active journey."""
    bus_id = uuid.UUID(bus["id"])
    db.add(
        Journey(bus_id=bus_id, driver_id=driver.id, route_id=route.id, direction="rebero_to_alu")
    )
    db.commit()
    db.add(
        Journey(
            bus_id=bus_id, driver_id=second_driver.id, route_id=route.id, direction="alu_to_rebero"
        )
    )
    with pytest.raises(IntegrityError):
        db.commit()
