"""Tests for ending a journey, by hand or at the terminal stop (issue #20)."""

import uuid

import pytest
from sqlalchemy import func, select

from app.models import Journey, JourneyStatus, LocationUpdate, Role
from app.seed_data import STOPS
from tests.conftest import auth_headers

REBERO, REMERA, ZINDIRO, ALU_CAMPUS = STOPS[0], STOPS[8], STOPS[11], STOPS[-1]


def reading_at(stop) -> dict:
    """A precise reading exactly at a stop."""
    _, lat, lng = stop
    return {"latitude": lat, "longitude": lng, "accuracy": 5}


def start(client, driver, bus, direction="rebero_to_alu") -> dict:
    """Start a journey and return it."""
    choice = {"bus_id": bus["id"], "direction": direction}
    return client.post("/journeys", json=choice, headers=auth_headers(driver)).json()


def send(client, driver, journey, stop) -> dict:
    """Send a reading at a stop and return the reply."""
    url = f"/journeys/{journey['id']}/locations"
    return client.post(url, json=reading_at(stop), headers=auth_headers(driver)).json()


def end(client, user, journey):
    """Ask to end the journey as the given user."""
    return client.post(f"/journeys/{journey['id']}/end", headers=auth_headers(user))


def status_of(db, journey) -> JourneyStatus:
    """The journey's status as stored in the database."""
    return db.get(Journey, uuid.UUID(journey["id"])).status


# --- Ending by hand ---------------------------------------------------------------------


def test_driver_ends_their_journey(client, route, driver, bus):
    """The driver can end the journey manually; it leaves the 'on the road' list."""
    journey = start(client, driver, bus)
    response = end(client, driver, journey)
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert client.get("/journeys/active", headers=auth_headers(driver)).json() == []


def test_completed_journeys_are_kept_for_reports(client, db, route, driver, bus):
    """Ending changes the status and end time; nothing is deleted (FR-19)."""
    journey = start(client, driver, bus)
    send(client, driver, journey, REMERA)
    end(client, driver, journey)
    saved = db.get(Journey, uuid.UUID(journey["id"]))
    assert saved.status == JourneyStatus.COMPLETED
    assert saved.ended_at is not None
    assert db.scalar(select(func.count()).select_from(LocationUpdate)) == 1


def test_a_journey_cannot_be_ended_twice(client, route, driver, bus):
    """The second attempt is refused."""
    journey = start(client, driver, bus)
    end(client, driver, journey)
    assert end(client, driver, journey).status_code == 409


def test_only_the_journeys_driver_can_end_it(client, route, make_user, student, driver, bus):
    """Another driver or a student gets 403, and someone not signed in gets 401."""
    journey = start(client, driver, bus)
    other_driver = make_user(Role.DRIVER, "driver2@alueducation.com")
    assert end(client, other_driver, journey).status_code == 403
    assert end(client, student, journey).status_code == 403
    assert client.post(f"/journeys/{journey['id']}/end").status_code == 401


def test_ending_an_unknown_journey_is_not_found(client, route, driver):
    """A journey ID that does not exist gives 404."""
    assert end(client, driver, {"id": str(uuid.uuid4())}).status_code == 404


def test_the_bus_can_start_again_after_ending(client, route, driver, bus):
    """Once ended, the same bus is free for its next journey."""
    end(client, driver, start(client, driver, bus))
    again = client.post(
        "/journeys",
        json={"bus_id": bus["id"], "direction": "alu_to_rebero"},
        headers=auth_headers(driver),
    )
    assert again.status_code == 201


# --- Ending automatically at the terminal -----------------------------------------------


def test_reaching_alu_campus_completes_the_journey(client, db, route, driver, bus):
    """Going Rebero -> ALU, the first reading at ALU Campus marks the journey COMPLETED."""
    journey = start(client, driver, bus)
    assert send(client, driver, journey, ZINDIRO)["journey_status"] == "active"
    assert send(client, driver, journey, ALU_CAMPUS)["journey_status"] == "completed"
    assert status_of(db, journey) == JourneyStatus.COMPLETED


def test_going_the_other_way_the_terminal_is_rebero(client, db, route, driver, bus):
    """Going ALU -> Rebero, reaching Rebero ends it; ALU Campus does not."""
    journey = start(client, driver, bus, direction="alu_to_rebero")
    send(client, driver, journey, REMERA)
    send(client, driver, journey, REBERO)
    assert status_of(db, journey) == JourneyStatus.COMPLETED


def test_a_middle_stop_does_not_end_the_journey(client, db, route, driver, bus):
    """Passing Remera Gare is just a stop on the way."""
    journey = start(client, driver, bus)
    send(client, driver, journey, ZINDIRO)
    send(client, driver, journey, REMERA)
    assert status_of(db, journey) == JourneyStatus.ACTIVE


def test_starting_at_the_terminal_does_not_end_it_straight_away(client, db, route, driver, bus):
    """A bus parked at ALU when the driver taps Start (the wrong way, say) is not ended at once."""
    journey = start(client, driver, bus)
    send(client, driver, journey, ALU_CAMPUS)
    send(client, driver, journey, ALU_CAMPUS)
    assert status_of(db, journey) == JourneyStatus.ACTIVE


@pytest.mark.parametrize("by_hand", [True, False])
def test_open_maps_are_told_to_remove_the_bus(client, route, driver, bus, by_hand):
    """Whether ended by hand or at the terminal, maps get a 'journey_ended' message."""
    journey = start(client, driver, bus)
    send(client, driver, journey, ZINDIRO)
    with client.websocket_connect("/live/ws") as live_map:
        if by_hand:
            end(client, driver, journey)
        else:
            send(client, driver, journey, ALU_CAMPUS)
        message = live_map.receive_json()
    assert message == {"type": "journey_ended", "journey_id": journey["id"]}
