"""Drivers start journeys; drivers and admins see which buses are on the road (#15)."""

import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from sqlalchemy import ColumnElement, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import DbSession, DriverUser, StaffUser
from app.live import journey_ended_message, live_updates
from app.models import Availability, Journey, JourneyStatus, LocationUpdate, Route
from app.routers.buses import get_bus_or_404
from app.schemas.journeys import JourneyOut, JourneyStart
from app.seed_data import ROUTE_NAME

router = APIRouter(prefix="/journeys", tags=["journeys"])

BUS_ALREADY_RUNNING = "This bus is already on a journey"


def get_route_or_503(db: Session) -> Route:
    """The Rebero - ALU route; without it no journey can start, so say how to fix it."""
    route = db.scalar(select(Route).where(Route.name == ROUTE_NAME))
    if route is None:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The route is not set up yet. Run the seed script.",
        )
    return route


def get_journey_or_404(db: Session, journey_id: uuid.UUID) -> Journey:
    """Find a journey by its ID, or answer 404 if there is no such journey."""
    journey = db.get(Journey, journey_id)
    if journey is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Journey not found")
    return journey


def latest_reading(db: Session, journey: Journey) -> LocationUpdate | None:
    """The newest position saved for this journey so far, if any."""
    return db.scalar(
        select(LocationUpdate)
        .where(LocationUpdate.journey_id == journey.id)
        .order_by(LocationUpdate.recorded_at.desc())
        .limit(1)
    )


def complete(journey: Journey) -> None:
    """Mark a journey as finished now; the row and its positions are kept for reports (FR-19)."""
    journey.status = JourneyStatus.COMPLETED
    journey.ended_at = func.now()


def has_active_journey(db: Session, condition: ColumnElement[bool]) -> bool:
    """Whether any active journey matches the condition (a given bus or a given driver)."""
    query = select(Journey.id).where(Journey.status == JourneyStatus.ACTIVE, condition)
    return db.scalar(query) is not None


@router.post("", status_code=status.HTTP_201_CREATED)
def start_journey(choice: JourneyStart, db: DbSession, driver: DriverUser) -> JourneyOut:
    """Start a journey on the chosen bus in the chosen direction (FR-13 to FR-17)."""
    route = get_route_or_503(db)
    bus = get_bus_or_404(db, choice.bus_id)
    if bus.availability == Availability.UNAVAILABLE:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="This bus is marked Unavailable")
    if has_active_journey(db, Journey.driver_id == driver.id):
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="You already have a journey in progress"
        )
    if has_active_journey(db, Journey.bus_id == bus.id):
        raise HTTPException(status.HTTP_409_CONFLICT, detail=BUS_ALREADY_RUNNING)

    journey = Journey(bus=bus, driver=driver, route_id=route.id, direction=choice.direction)
    db.add(journey)
    try:
        db.commit()
    except IntegrityError:
        # Another driver started this bus between our check and our save; the database said no
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail=BUS_ALREADY_RUNNING) from None
    db.refresh(journey)
    return JourneyOut.model_validate(journey)


@router.get("/active")
def list_active_journeys(db: DbSession, _staff: StaffUser) -> list[JourneyOut]:
    """Every bus on the road right now, most recently started first."""
    journeys = db.scalars(
        select(Journey)
        .where(Journey.status == JourneyStatus.ACTIVE)
        .order_by(Journey.started_at.desc())
    )
    return [JourneyOut.model_validate(journey) for journey in journeys]


@router.post("/{journey_id}/end")
def end_journey(
    journey_id: uuid.UUID, db: DbSession, driver: DriverUser, background_tasks: BackgroundTasks
) -> JourneyOut:
    """The driver ends their journey by hand, for example if it stops before the terminal."""
    journey = get_journey_or_404(db, journey_id)
    if journey.driver_id != driver.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="This is not your journey")
    if journey.status != JourneyStatus.ACTIVE:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="This journey has already ended")

    complete(journey)
    db.commit()
    db.refresh(journey)
    background_tasks.add_task(live_updates.broadcast, journey_ended_message(journey.id))
    return JourneyOut.model_validate(journey)
