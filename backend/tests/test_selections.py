"""Tests for students choosing their pickup and drop-off stops (issue #21)."""

import uuid

import pytest

from app.models import Role
from app.seed_data import STOPS
from tests.conftest import auth_headers

# Between Remera Gare (stop 9) and Kimironko Gare (stop 10), going Rebero -> ALU
PAST_REMERA = {"latitude": -1.9540, "longitude": 30.1225, "accuracy": 6}


@pytest.fixture
def journey(client, route, driver, bus):
    """An active Rebero -> ALU journey, as the API returned it."""
    choice = {"bus_id": bus["id"], "direction": "rebero_to_alu"}
    return client.post("/journeys", json=choice, headers=auth_headers(driver)).json()


def stops_of(client, journey) -> dict[str, dict]:
    """The journey's stops by name."""
    listed = client.get(f"/journeys/{journey['id']}/stops").json()
    return {stop["name"]: stop for stop in listed}


def choose(client, student, journey, kind, stop_name):
    """Choose a pickup or drop-off stop by its name."""
    stop_id = stops_of(client, journey)[stop_name]["id"]
    return client.put(
        f"/journeys/{journey['id']}/selections/{kind}",
        json={"stop_id": stop_id},
        headers=auth_headers(student),
    )


def mine(client, student, journey) -> dict[str, str]:
    """My selections as {type: stop name}."""
    url = f"/journeys/{journey['id']}/selections/mine"
    return {
        s["type"]: s["stop"]["name"] for s in client.get(url, headers=auth_headers(student)).json()
    }


def test_student_chooses_a_pickup_stop_and_sees_it(client, student, journey):
    """The chosen stop is saved and shown back to me (FR-12)."""
    response = choose(client, student, journey, "pickup", "Remera Gare")
    assert response.status_code == 200
    assert response.json()["stop"]["name"] == "Remera Gare"
    assert response.json()["pickup_status"] == "pending"
    assert mine(client, student, journey) == {"pickup": "Remera Gare"}


def test_choosing_again_changes_the_stop(client, student, journey):
    """Picking another stop replaces the first choice; there is still one pickup."""
    choose(client, student, journey, "pickup", "Remera Gare")
    choose(client, student, journey, "pickup", "Kimironko Gare")
    assert mine(client, student, journey) == {"pickup": "Kimironko Gare"}


def test_stops_are_listed_in_the_journeys_direction(client, route, driver, bus, journey):
    """Rebero -> ALU starts at Rebero; the way back starts at ALU Campus."""
    assert next(iter(stops_of(client, journey))) == "Rebero"
    client.post(f"/journeys/{journey['id']}/end", headers=auth_headers(driver))
    choice = {"bus_id": bus["id"], "direction": "alu_to_rebero"}
    back = client.post("/journeys", json=choice, headers=auth_headers(driver)).json()
    assert next(iter(stops_of(client, back))) == "ALU Campus"


def test_a_stop_not_on_the_route_is_refused(client, student, journey):
    """Only this journey's stops can be chosen."""
    response = client.put(
        f"/journeys/{journey['id']}/selections/pickup",
        json={"stop_id": str(uuid.uuid4())},
        headers=auth_headers(student),
    )
    assert response.status_code == 422


def test_stops_the_bus_has_passed_cannot_be_chosen(client, driver, student, journey):
    """Once the bus is past Remera Gare, Rebero to Remera are marked passed and refused."""
    client.post(
        f"/journeys/{journey['id']}/locations", json=PAST_REMERA, headers=auth_headers(driver)
    )
    stops = stops_of(client, journey)
    assert stops["Remera Gare"]["passed"] is True
    assert stops["Kimironko Gare"]["passed"] is False
    assert choose(client, student, journey, "pickup", "Rebero").status_code == 409
    assert choose(client, student, journey, "pickup", "Kimironko Gare").status_code == 200


def test_pickup_must_come_before_drop_off(client, student, journey):
    """A drop-off at Remera and a pickup at Zindiro (after it) makes no sense."""
    choose(client, student, journey, "dropoff", "Remera Gare")
    assert choose(client, student, journey, "pickup", "Zindiro").status_code == 422
    assert choose(client, student, journey, "pickup", "Sonatube").status_code == 200


@pytest.mark.parametrize(
    ("kind", "stop_name"), [("pickup", STOPS[-1][0]), ("dropoff", STOPS[0][0])]
)
def test_no_pickup_at_the_last_stop_or_drop_off_at_the_first(
    client, student, journey, kind, stop_name
):
    """Going Rebero -> ALU, nobody boards at ALU Campus or gets off at Rebero."""
    assert choose(client, student, journey, kind, stop_name).status_code == 422


def test_an_ended_journey_refuses_choices(client, driver, student, journey):
    """Stops can only be chosen while the journey is active."""
    client.post(f"/journeys/{journey['id']}/end", headers=auth_headers(driver))
    assert choose(client, student, journey, "pickup", "Remera Gare").status_code == 409


def test_only_students_choose_stops(client, driver, journey):
    """A driver gets 403 and someone not signed in gets 401."""
    assert choose(client, driver, journey, "pickup", "Remera Gare").status_code == 403
    stop_id = stops_of(client, journey)["Remera Gare"]["id"]
    url = f"/journeys/{journey['id']}/selections/pickup"
    assert client.put(url, json={"stop_id": stop_id}).status_code == 401


def test_students_only_see_their_own_choices(client, make_user, student, journey):
    """Another student's pickup does not appear in my list."""
    classmate = make_user(Role.STUDENT, "classmate@alustudent.com")
    choose(client, classmate, journey, "pickup", "Sonatube")
    assert mine(client, student, journey) == {}


def test_the_bus_list_says_which_journey_a_bus_is_on(client, bus, journey):
    """Students find the journey to choose stops for from the public bus list."""
    [listed] = client.get("/buses").json()
    assert listed["journey_id"] == journey["id"]
    assert client.get(f"/buses/{bus['id']}").json()["journey_id"] == journey["id"]
