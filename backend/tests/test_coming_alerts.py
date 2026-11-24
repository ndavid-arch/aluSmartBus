"""Tests for the 'bus is coming' alerts, 10 and 5 minutes before the pickup stop (issue #25).

At the average 20 km/h, the pickup Kimironko Gare is 16 minutes from Rwandex, 10 minutes from
Sonatube and 4 minutes from Remera Gare.
"""

import pytest

from app.alerts import coming_alert_due
from app.models import NotificationType, Role
from app.seed_data import STOPS
from tests.conftest import auth_headers

RWANDEX, SONATUBE, REMERA, KIMIRONKO = STOPS[6], STOPS[7], STOPS[8], STOPS[9]
FAR_FROM_THE_ROUTE = {"latitude": -1.9441, "longitude": 30.0619, "accuracy": 5}  # city centre


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


def my_alerts(client, student, journey) -> list[str]:
    """The kinds of alert I have received for this journey, oldest first."""
    url = f"/journeys/{journey['id']}/notifications/mine"
    return [alert["type"] for alert in client.get(url, headers=auth_headers(student)).json()]


# --- Which alert fits how far away the bus is -------------------------------------------


@pytest.mark.parametrize(
    ("minutes", "kind"),
    [
        (11, None),
        (10, NotificationType.TEN_MINUTES),
        (6, NotificationType.TEN_MINUTES),
        (5, NotificationType.FIVE_MINUTES),
        (0, NotificationType.FIVE_MINUTES),
    ],
)
def test_the_alert_due_depends_on_minutes_away(minutes, kind):
    """Within 10 minutes: the 10-minute alert; within 5: the 5-minute one."""
    assert coming_alert_due(minutes) == kind


# --- Through the API ---------------------------------------------------------------------


def test_alerts_come_at_ten_then_five_minutes(client, driver, student, journey):
    """No alert 16 minutes away; then 10 minutes; then 5 minutes (FR-44, FR-45)."""
    choose(client, student, journey, "pickup", KIMIRONKO)
    send(client, driver, journey, at(RWANDEX))
    assert my_alerts(client, student, journey) == []
    send(client, driver, journey, at(SONATUBE))
    assert my_alerts(client, student, journey) == ["ten_minutes"]
    send(client, driver, journey, at(REMERA))
    # Both now (in a test they can share a second, so their order is not checked)
    assert set(my_alerts(client, student, journey)) == {"ten_minutes", "five_minutes"}


def test_each_alert_is_sent_only_once(client, driver, student, journey):
    """More readings at the same distance do not repeat the alert."""
    choose(client, student, journey, "pickup", KIMIRONKO)
    for _ in range(3):
        send(client, driver, journey, at(SONATUBE))
    assert my_alerts(client, student, journey) == ["ten_minutes"]


def test_a_late_choice_gets_only_the_five_minute_alert(client, driver, student, journey):
    """Choosing when the bus is already 4 minutes away skips the 10-minute alert."""
    choose(client, student, journey, "pickup", KIMIRONKO)
    send(client, driver, journey, at(REMERA))
    assert my_alerts(client, student, journey) == ["five_minutes"]


def test_no_ten_minute_alert_after_the_five_minute_one(client, driver, student, journey):
    """If the ETA jumps back up (traffic, GPS), the student is not told '10 minutes' again."""
    choose(client, student, journey, "pickup", KIMIRONKO)
    send(client, driver, journey, at(REMERA))
    send(client, driver, journey, at(SONATUBE))
    assert my_alerts(client, student, journey) == ["five_minutes"]


def test_no_coming_alert_once_the_bus_is_at_the_stop(client, driver, student, journey):
    """At the stop, 'the bus has arrived' is the alert that fits (#26), not '5 minutes'."""
    choose(client, student, journey, "pickup", KIMIRONKO)
    send(client, driver, journey, at(KIMIRONKO))
    assert my_alerts(client, student, journey) == []


def test_no_alert_while_the_bus_is_off_the_route(client, driver, student, journey):
    """Without a trustworthy ETA, no alert goes out on a guess."""
    choose(client, student, journey, "pickup", KIMIRONKO)
    send(client, driver, journey, FAR_FROM_THE_ROUTE)
    assert my_alerts(client, student, journey) == []


def test_only_students_waiting_for_a_pickup_get_alerts(client, driver, student, journey):
    """A drop-off alone does not mean the student is waiting at a stop."""
    choose(client, student, journey, "dropoff", KIMIRONKO)
    send(client, driver, journey, at(SONATUBE))
    assert my_alerts(client, student, journey) == []


def test_i_only_see_my_own_alerts(client, make_user, driver, student, journey):
    """Another student's alerts are not mine."""
    classmate = make_user(Role.STUDENT, "classmate@alustudent.com")
    choose(client, classmate, journey, "pickup", KIMIRONKO)
    send(client, driver, journey, at(SONATUBE))
    assert my_alerts(client, classmate, journey) == ["ten_minutes"]
    assert my_alerts(client, student, journey) == []


def test_guests_cannot_read_alerts(client, journey):
    """Alerts belong to a signed-in student."""
    response = client.get(f"/journeys/{journey['id']}/notifications/mine")
    assert response.status_code == 401
