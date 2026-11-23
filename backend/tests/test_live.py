"""Tests for the route and the live bus positions on the map (issue #17)."""

import pytest

from tests.conftest import auth_headers

# Two readings near the start of the route: Rebero, then on the way to Rujugiro
AT_REBERO = {"latitude": -1.9903207, "longitude": 30.0612489, "accuracy": 8}
MOVED_ON = {"latitude": -1.9880, "longitude": 30.0680, "accuracy": 6}


@pytest.fixture
def journey(client, route, driver, bus):
    """An active journey driven by the test driver, as the API returned it."""
    choice = {"bus_id": bus["id"], "direction": "rebero_to_alu"}
    return client.post("/journeys", json=choice, headers=auth_headers(driver)).json()


def send(client, driver, journey, reading):
    """Send one reading from the driver's phone."""
    response = client.post(
        f"/journeys/{journey['id']}/locations", json=reading, headers=auth_headers(driver)
    )
    assert response.status_code == 201


def test_anyone_can_get_the_route_and_its_stops_in_order(client, route):
    """The map draws the route line and the 13 stops; no sign-in needed."""
    response = client.get("/route")
    assert response.status_code == 200
    stops = response.json()["stops"]
    assert [stop["sequence"] for stop in stops] == list(range(1, 14))
    assert stops[0]["name"] == "Rebero"
    assert stops[-1]["name"] == "ALU Campus"


def test_route_missing_gives_a_clear_404(client):
    """Before the seed script runs there is no route to draw."""
    assert client.get("/route").status_code == 404


def test_live_buses_show_each_bus_at_its_latest_position(client, driver, journey):
    """A map opening now sees the bus where it was last reported."""
    send(client, driver, journey, AT_REBERO)
    send(client, driver, journey, MOVED_ON)
    [bus] = client.get("/live/buses").json()
    assert bus["plate_number"] == "RAB 123 A"
    assert bus["latitude"] == MOVED_ON["latitude"]
    assert bus["direction"] == "rebero_to_alu"


def test_live_buses_include_the_next_stop_and_eta(client, driver, journey):
    """On the way from Rebero, the next stop is Rujugiro, with a whole-minute ETA (#18)."""
    send(client, driver, journey, MOVED_ON)
    [bus] = client.get("/live/buses").json()
    assert bus["next_stop"] == "Rujugiro"
    assert isinstance(bus["eta_minutes"], int)
    assert bus["eta_minutes"] >= 0


def test_a_journey_without_a_position_yet_is_not_shown(client, journey):
    """Nothing is drawn until the driver's phone has sent its first reading."""
    assert client.get("/live/buses").json() == []


def test_the_bus_is_shown_wherever_it_is(client, driver, journey):
    """Even far from the route (say, the parking station), the latest position is shown."""
    parking = {"latitude": -1.9500, "longitude": 30.0600, "accuracy": 10}
    send(client, driver, journey, parking)
    [bus] = client.get("/live/buses").json()
    assert (bus["latitude"], bus["longitude"]) == (parking["latitude"], parking["longitude"])
    assert bus["next_stop"] is None  # "Not on the route yet" (#18)
    assert bus["eta_minutes"] is None


def test_open_maps_receive_each_new_position_straight_away(client, driver, journey):
    """A map connected over WebSocket gets the reading without reloading (FR-22)."""
    with client.websocket_connect("/live/ws") as live_map:
        send(client, driver, journey, MOVED_ON)
        message = live_map.receive_json()
    assert message["plate_number"] == "RAB 123 A"
    assert message["latitude"] == MOVED_ON["latitude"]
    assert message["journey_id"] == journey["id"]
    assert message["next_stop"] == "Rujugiro"  # each update carries a fresh ETA (#18)
