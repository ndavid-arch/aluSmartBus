"""Drivers start journeys; drivers and admins see which buses are on the road (#15)."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import ColumnElement, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import DbSession, DriverUser, StaffUser
from app.models import Availability, Journey, JourneyStatus, Route
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
