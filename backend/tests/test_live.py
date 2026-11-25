"""Tests for the route and the live bus positions on the map (issue #17)."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.models import LocationUpdate
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


def test_each_position_says_how_old_it_is(client, driver, journey):
    """A fresh reading is a few seconds old at most, so the map knows it is live (#19)."""
    send(client, driver, journey, MOVED_ON)
    [bus] = client.get("/live/buses").json()
    assert 0 <= bus["age_seconds"] < 5


def test_an_old_position_shows_its_real_age(client, db, driver, journey):
    """If the phone stopped sending 5 minutes ago, the map is told it is about 300 s old."""
    send(client, driver, journey, MOVED_ON)
    reading = db.scalar(select(LocationUpdate))
    reading.recorded_at = datetime.now(UTC) - timedelta(minutes=5)
    db.commit()
    [bus] = client.get("/live/buses").json()
    assert 295 < bus["age_seconds"] < 310


# --- Minutes to every stop ahead (#70) -------------------------------------------------------


def test_live_buses_list_every_stop_ahead_with_minutes(client, driver, journey):
    """From near Rebero: all 12 stops after it, in travel order, each further away than the last."""
    send(client, driver, journey, MOVED_ON)
    [bus] = client.get("/live/buses").json()
    ahead = bus["stops_ahead"]
    assert [stop["name"] for stop in ahead][:2] == ["Rujugiro", "Kwa Kaboyi"]
    assert ahead[-1]["name"] == "ALU Campus"
    assert ahead[0]["minutes"] == bus["eta_minutes"]
    minutes = [stop["minutes"] for stop in ahead]
    assert minutes == sorted(minutes)


def test_no_stops_ahead_while_off_the_route(client, driver, journey):
    """Far from the route there is no ETA, so no list either."""
    send(client, driver, journey, {"latitude": -1.9500, "longitude": 30.0600, "accuracy": 10})
    [bus] = client.get("/live/buses").json()
    assert bus["stops_ahead"] == []
