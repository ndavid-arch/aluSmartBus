"""Students scan the QR code inside the bus to record that they got on (#27).

FR-38 to FR-43, NFR-07: one boarding per student per journey, safe to retry; no exit scan.
"""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.boarding import expire_missed_pickups, waiting_pickups
from app.clock import as_utc
from app.core.deps import DbSession, StudentUser
from app.models import BoardingRecord, Bus, Journey, JourneyStatus, PickupStatus, User
from app.schemas.boardings import BoardingOut, BoardingScan

router = APIRouter(prefix="/boardings", tags=["boardings"])


def bus_with_qr_code(db: Session, qr_code: str) -> Bus:
    """The registered bus this QR code belongs to, or 404 'Invalid QR code' (FR-40)."""
    bus = db.scalar(select(Bus).where(Bus.qr_code == qr_code))
    if bus is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Invalid QR code")
    return bus


def active_journey_of(db: Session, bus: Bus) -> Journey:
    """The journey this bus is on right now, or 409 'No active journey' (FR-41)."""
    journey = db.scalar(
        select(Journey).where(Journey.bus_id == bus.id, Journey.status == JourneyStatus.ACTIVE)
    )
    if journey is None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="No active journey")
    return journey


def my_boarding(db: Session, student: User, journey: Journey) -> BoardingRecord | None:
    """This student's boarding on this journey, if they have already scanned."""
    return db.scalar(
        select(BoardingRecord).where(
            BoardingRecord.student_id == student.id, BoardingRecord.journey_id == journey.id
        )
    )


def mark_pickup_boarded(db: Session, journey: Journey, student: User) -> None:
    """Mark my pickup boarded if its window is still open (or the bus has not been seen there);
    a scan after the 3 minutes leaves it missed (#23)."""
    expire_missed_pickups(db, journey, datetime.now(UTC))
    for pickup in waiting_pickups(db, journey):
        if pickup.student_id == student.id:
            pickup.pickup_status = PickupStatus.BOARDED


def boarding_out(record: BoardingRecord, journey: Journey, already: bool) -> BoardingOut:
    """What the student's phone shows after the scan."""
    return BoardingOut(
        journey_id=journey.id,
        plate_number=journey.bus.plate_number,
        direction=journey.direction,
        boarded_at=as_utc(record.boarded_at),  # with its zone, so phones show local time
        already_boarded=already,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def board(
    scan: BoardingScan, response: Response, db: DbSession, student: StudentUser
) -> BoardingOut:
    """Record that I got on this bus (FR-38, FR-39, FR-43). Scanning again, or a retry after
    the network dropped, returns the first boarding with 200 instead of a duplicate (FR-42)."""
    journey = active_journey_of(db, bus_with_qr_code(db, scan.qr_code))

    existing = my_boarding(db, student, journey)
    if existing is not None:
        response.status_code = status.HTTP_200_OK
        return boarding_out(existing, journey, already=True)

    record = BoardingRecord(student_id=student.id, journey_id=journey.id)
    db.add(record)
    try:
        db.flush()
    except IntegrityError:
        # Two scans arrived at the same moment: the other one was saved first
        db.rollback()
        response.status_code = status.HTTP_200_OK
        return boarding_out(my_boarding(db, student, journey), journey, already=True)

    mark_pickup_boarded(db, journey, student)
    db.commit()
    db.refresh(record)
    return boarding_out(record, journey, already=False)
