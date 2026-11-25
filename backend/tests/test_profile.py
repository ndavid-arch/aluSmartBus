"""Tests for the student profile, contribution points and leaderboard (issue #34)."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.models import Journey, Role, StopArrival, User
from app.points import leaderboard_name
from app.seed_data import STOPS
from tests.conftest import auth_headers

REMERA, KIMIRONKO = STOPS[8], STOPS[9]


def ride(client, db, driver, bus, student, pickup=None, late=False, days_ago=0):
    """One whole journey for a student: maybe choose a pickup, scan on, and the trip ends.
    `late` makes the scan come after the boarding window closed (#23)."""
    choice = {"bus_id": bus["id"], "direction": "rebero_to_alu"}
    journey = client.post("/journeys", json=choice, headers=auth_headers(driver)).json()
    url = f"/journeys/{journey['id']}"
    if pickup:
        stops = {s["name"]: s["id"] for s in client.get(f"{url}/stops").json()}
        body = {"stop_id": stops[pickup[0]]}
        client.put(f"{url}/selections/pickup", json=body, headers=auth_headers(student))
    if late:
        _, lat, lng = pickup
        reading = {"latitude": lat, "longitude": lng, "accuracy": 5}
        client.post(f"{url}/locations", json=reading, headers=auth_headers(driver))
        for arrival in db.scalars(select(StopArrival)):
            arrival.arrived_at = datetime.now(UTC) - timedelta(minutes=4)
        db.commit()
    client.post("/boardings", json={"qr_code": bus["qr_code"]}, headers=auth_headers(student))
    client.post(f"{url}/end", headers=auth_headers(driver))
    saved = db.get(Journey, uuid.UUID(journey["id"]))
    saved.started_at = datetime.now(UTC) - timedelta(days=days_ago)
    db.commit()


def profile(client, student) -> dict:
    """My profile as the API shows it."""
    response = client.get("/me/profile", headers=auth_headers(student))
    assert response.status_code == 200
    return response.json()


def leaderboard(client, user, period="all") -> list[dict]:
    """The leaderboard entries."""
    url = f"/leaderboard?period={period}"
    return client.get(url, headers=auth_headers(user)).json()["entries"]


@pytest.fixture
def riders(make_user):
    """Three students with two-word names."""
    names = ["Aline Uwase", "Eric Mugisha", "Grace Keza"]
    return [
        make_user(Role.STUDENT, f"rider{n}@alustudent.com", full_name=name)
        for n, name in enumerate(names)
    ]


# --- Box 1: my profile ---------------------------------------------------------------------


def test_a_new_student_starts_with_nothing(client, student):
    """Name, no usual stop, no trips, no points."""
    shown = profile(client, student)
    assert shown["full_name"] == student.full_name
    assert shown["usual_stop"] is None
    assert (shown["trips"], shown["points"], shown["points_this_month"]) == (0, 0, 0)


def test_a_trip_earns_ten_points(client, db, route, driver, bus, student):
    """Scanning on without choosing a stop: just the trip."""
    ride(client, db, driver, bus, student)
    shown = profile(client, student)
    assert (shown["trips"], shown["points"]) == (1, 10)


def test_boarding_on_time_at_my_pickup_earns_five_more(client, db, route, driver, bus, student):
    """Chose a pickup and scanned within the window: 10 + 5."""
    ride(client, db, driver, bus, student, pickup=REMERA)
    assert profile(client, student)["points"] == 15


def test_a_late_boarding_earns_only_the_trip(client, db, route, driver, bus, student):
    """Scanned after the window closed: the pickup was missed, so no on-time points."""
    ride(client, db, driver, bus, student, pickup=REMERA, late=True)
    assert profile(client, student)["points"] == 10


def test_my_usual_stop_is_the_pickup_i_choose_most(client, db, route, driver, bus, student):
    """Two trips from Remera Gare and one from Kimironko Gare."""
    for stop in (REMERA, KIMIRONKO, REMERA):
        ride(client, db, driver, bus, student, pickup=stop)
    assert profile(client, student)["usual_stop"] == "Remera Gare"


def test_points_this_month_leave_out_older_trips(client, db, route, driver, bus, student):
    """A trip 40 days ago counts for all time, not for this month."""
    ride(client, db, driver, bus, student, days_ago=40)
    ride(client, db, driver, bus, student)
    shown = profile(client, student)
    assert (shown["points"], shown["points_this_month"]) == (20, 10)


# --- Box 2, 3: the leaderboard ---------------------------------------------------------------


def test_the_leaderboard_ranks_the_top_contributors(client, db, route, driver, bus, riders):
    """Most points first; equal points share a rank; students with no points are left out."""
    aline, eric, grace = riders
    ride(client, db, driver, bus, aline, pickup=REMERA)  # 15
    ride(client, db, driver, bus, eric)  # 10
    ride(client, db, driver, bus, grace)  # 10
    entries = leaderboard(client, aline)
    assert [(e["rank"], e["name"], e["points"]) for e in entries] == [
        (1, "Aline U.", 15),
        (2, "Eric M.", 10),
        (2, "Grace K.", 10),
    ]


def test_the_monthly_board_only_counts_this_month(client, db, route, driver, bus, riders):
    """An old trip is on the all-time board only."""
    aline, eric, _ = riders
    ride(client, db, driver, bus, aline, days_ago=40)
    ride(client, db, driver, bus, eric)
    assert [e["name"] for e in leaderboard(client, aline, "month")] == ["Eric M."]
    assert [e["name"] for e in leaderboard(client, aline, "all")] == ["Aline U.", "Eric M."]


def test_the_leaderboard_shows_names_and_points_only(client, db, route, driver, bus, riders):
    """Never trips, stops or times (FR-64)."""
    ride(client, db, driver, bus, riders[0], pickup=REMERA)
    [entry] = leaderboard(client, riders[0])
    assert set(entry) == {"rank", "name", "points", "is_me"}
    response = client.get("/leaderboard?period=all", headers=auth_headers(riders[0])).text
    assert "Remera" not in response
    assert riders[0].email not in response


def test_i_can_find_myself_on_the_board(client, db, route, driver, bus, riders):
    """My own row is marked, so the page can highlight it."""
    ride(client, db, driver, bus, riders[0])
    ride(client, db, driver, bus, riders[1])
    flags = {e["name"]: e["is_me"] for e in leaderboard(client, riders[1])}
    assert flags == {"Aline U.": False, "Eric M.": True}


# --- Box 4: hiding my name -------------------------------------------------------------------


def test_hiding_my_name_shows_initials(client, db, route, driver, bus, riders):
    """Still ranked, but as 'A. U.' (FR-65)."""
    ride(client, db, driver, bus, riders[0])
    change = {"hide_name_on_leaderboard": True}
    shown = client.patch("/me/profile", json=change, headers=auth_headers(riders[0])).json()
    assert shown["hide_name_on_leaderboard"] is True
    assert [e["name"] for e in leaderboard(client, riders[0])] == ["A. U."]


@pytest.mark.parametrize(
    ("full_name", "hidden", "shown"),
    [
        ("Aline Uwase", False, "Aline U."),
        ("Aline Uwase", True, "A. U."),
        ("Aline Marie Uwase", False, "Aline U."),
        ("aline", False, "aline"),
        ("aline", True, "A."),
        ("  Aline   Uwase ", False, "Aline U."),
    ],
)
def test_leaderboard_names(full_name, hidden, shown):
    """First name and last initial; initials only when hidden; odd spacing is ignored."""
    user = User(full_name=full_name, hide_name_on_leaderboard=hidden)
    assert leaderboard_name(user) == shown


# --- Who can see what ------------------------------------------------------------------------


def test_only_students_have_a_profile(client, driver):
    """Drivers do not earn points; guests must sign in."""
    assert client.get("/me/profile", headers=auth_headers(driver)).status_code == 403
    assert client.get("/me/profile").status_code == 401


def test_the_leaderboard_needs_a_signed_in_user(client, student):
    """Guests do not see who rides the bus."""
    assert client.get("/leaderboard").status_code == 401
    assert client.get("/leaderboard?period=year", headers=auth_headers(student)).status_code == 422


# --- My rank this month (#75) ------------------------------------------------------------------


def test_my_rank_this_month(client, db, route, driver, bus, riders):
    """Aline 15 points, Eric and Grace 10 each: ranks 1, 2 and 2 (shared, like the board)."""
    aline, eric, grace = riders
    ride(client, db, driver, bus, aline, pickup=REMERA)
    ride(client, db, driver, bus, eric)
    ride(client, db, driver, bus, grace)
    assert [profile(client, r)["rank_this_month"] for r in riders] == [1, 2, 2]


def test_no_rank_without_points_this_month(client, db, route, driver, bus, student):
    """A trip last month gives points for all time, but no place on this month's board."""
    ride(client, db, driver, bus, student, days_ago=40)
    assert profile(client, student)["rank_this_month"] is None
