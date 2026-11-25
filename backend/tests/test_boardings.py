"""Tests for boarding by scanning the bus QR code (issue #27)."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select

import app.routers.boardings as boardings
from app.models import BoardingRecord, Role, StopArrival
from app.seed_data import STOPS
from tests.conftest import auth_headers

REMERA = STOPS[8]


@pytest.fixture
def journey(client, route, driver, bus):
    """An active Rebero -> ALU journey on the bus, as the API returned it."""
    choice = {"bus_id": bus["id"], "direction": "rebero_to_alu"}
    return client.post("/journeys", json=choice, headers=auth_headers(driver)).json()


def scan(client, user, qr_code):
    """Send what the phone read from the QR code."""
    return client.post("/boardings", json={"qr_code": qr_code}, headers=auth_headers(user))


def boardings_saved(db) -> int:
    """How many boarding records exist."""
    return db.scalar(select(func.count()).select_from(BoardingRecord))


def my_pickup_state(client, student, journey) -> str:
    """Where my pickup stands, as the student page shows it (#23)."""
    url = f"/journeys/{journey['id']}/selections/mine"
    [pickup] = client.get(url, headers=auth_headers(student)).json()
    return pickup["window_state"]


def choose_pickup(client, student, journey, stop):
    """Choose my pickup stop."""
    stops = {s["name"]: s["id"] for s in client.get(f"/journeys/{journey['id']}/stops").json()}
    client.put(
        f"/journeys/{journey['id']}/selections/pickup",
        json={"stop_id": stops[stop[0]]},
        headers=auth_headers(student),
    )


def bus_at(client, driver, journey, stop):
    """The driver's phone reports the bus exactly at a stop."""
    _, lat, lng = stop
    reading = {"latitude": lat, "longitude": lng, "accuracy": 5}
    client.post(f"/journeys/{journey['id']}/locations", json=reading, headers=auth_headers(driver))


# --- Box 1: a valid scan -----------------------------------------------------------------


def test_a_valid_scan_records_the_boarding(client, db, student, bus, journey):
    """Student, bus, journey and time are saved, and the answer confirms it (FR-38, FR-39)."""
    response = scan(client, student, bus["qr_code"])
    assert response.status_code == 201
    body = response.json()
    assert body["journey_id"] == journey["id"]
    assert body["plate_number"] == bus["plate_number"]
    assert body["already_boarded"] is False
    record = db.scalar(select(BoardingRecord))
    assert str(record.journey_id) == journey["id"]
    assert record.student_id == student.id
    assert record.boarded_at is not None


def test_spaces_around_the_code_do_not_matter(client, student, bus, journey):
    """Some scanners add a space or a line break at the end."""
    assert scan(client, student, f"  {bus['qr_code']}\n").status_code == 201


# --- Box 2, 3: codes that cannot be boarded ------------------------------------------------


def test_an_unknown_code_is_an_invalid_qr_code(client, db, student, journey):
    """A QR code that is not a registered bus (FR-40)."""
    response = scan(client, student, "not-a-smartbus-code")
    assert response.status_code == 404
    assert response.json()["detail"] == "Invalid QR code"
    assert boardings_saved(db) == 0


def test_a_bus_without_an_active_journey_cannot_be_boarded(client, db, student, bus):
    """No journey started on this bus: nothing is recorded (FR-41)."""
    response = scan(client, student, bus["qr_code"])
    assert response.status_code == 409
    assert response.json()["detail"] == "No active journey"
    assert boardings_saved(db) == 0


def test_a_finished_journey_cannot_be_boarded(client, db, driver, student, bus, journey):
    """Once the driver ends the journey, the bus has no active journey."""
    client.post(f"/journeys/{journey['id']}/end", headers=auth_headers(driver))
    assert scan(client, student, bus["qr_code"]).status_code == 409
    assert boardings_saved(db) == 0


@pytest.mark.parametrize("qr_code", ["", "   ", "x" * 65])
def test_empty_or_too_long_codes_are_refused(client, student, journey, qr_code):
    """Nothing to look up, or longer than any bus code can be."""
    assert scan(client, student, qr_code).status_code == 422


# --- Box 4: one boarding per journey -----------------------------------------------------


def test_scanning_twice_says_already_boarded(client, db, student, bus, journey):
    """The second scan returns the first boarding; no duplicate (FR-42)."""
    first = scan(client, student, bus["qr_code"]).json()
    second = scan(client, student, bus["qr_code"])
    assert second.status_code == 200
    assert second.json()["already_boarded"] is True
    assert second.json()["boarded_at"] == first["boarded_at"]
    assert boardings_saved(db) == 1


def test_two_scans_at_the_same_moment_still_save_one(
    client, db, student, bus, journey, monkeypatch
):
    """A retry racing the first request: the database rule catches it (NFR-07)."""
    scan(client, student, bus["qr_code"])
    # Pretend the second request checked before the first one was saved
    real_lookup = boardings.my_boarding
    calls = []

    def misses_the_first_time(*args):
        calls.append(args)
        return None if len(calls) == 1 else real_lookup(*args)

    monkeypatch.setattr(boardings, "my_boarding", misses_the_first_time)
    response = scan(client, student, bus["qr_code"])
    assert response.status_code == 200
    assert response.json()["already_boarded"] is True
    assert boardings_saved(db) == 1


def test_each_student_boards_on_their_own(client, db, make_user, student, bus, journey):
    """Another student's scan is a separate boarding."""
    classmate = make_user(Role.STUDENT, "classmate@alustudent.com")
    scan(client, student, bus["qr_code"])
    assert scan(client, classmate, bus["qr_code"]).status_code == 201
    assert boardings_saved(db) == 2


# --- The pickup and its boarding window (#23) --------------------------------------------


def test_boarding_in_the_window_marks_my_pickup_boarded(client, driver, student, bus, journey):
    """The bus is at my stop and I scan within 3 minutes."""
    choose_pickup(client, student, journey, REMERA)
    bus_at(client, driver, journey, REMERA)
    scan(client, student, bus["qr_code"])
    assert my_pickup_state(client, student, journey) == "boarded"


def test_boarding_before_the_arrival_was_seen_still_counts(client, student, bus, journey):
    """GPS can miss an arrival; being on the bus is what matters."""
    choose_pickup(client, student, journey, REMERA)
    scan(client, student, bus["qr_code"])
    assert my_pickup_state(client, student, journey) == "boarded"


def test_a_scan_after_the_window_is_recorded_but_the_pickup_stays_missed(
    client, db, driver, student, bus, journey
):
    """3:01 is too late for the pickup (#23), but I am on the bus, so the boarding is saved."""
    choose_pickup(client, student, journey, REMERA)
    bus_at(client, driver, journey, REMERA)
    arrival = db.scalar(select(StopArrival))
    arrival.arrived_at = datetime.now(UTC) - timedelta(minutes=3, seconds=1)
    db.commit()
    assert scan(client, student, bus["qr_code"]).status_code == 201
    assert my_pickup_state(client, student, journey) == "missed"


# --- Who can scan ------------------------------------------------------------------------


def test_only_students_scan_to_board(client, driver, bus, journey):
    """Drivers do not board their own bus; guests must sign in first."""
    assert scan(client, driver, bus["qr_code"]).status_code == 403
    response = client.post("/boardings", json={"qr_code": bus["qr_code"]})
    assert response.status_code == 401
