"""Students choose where the bus picks them up and drops them off (#21)."""

import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import DbSession, StudentUser
from app.eta import journey_progress, stops_in_travel_order
from app.models import Journey, JourneyStatus, PickupStatus, SelectionType, StopSelection, User
from app.routers.journeys import get_journey_or_404, latest_reading
from app.schemas.selections import JourneyStop, SelectionChoice, SelectionOut

router = APIRouter(prefix="/journeys", tags=["stop selections"])

# "What you sent cannot be used": the same code Pydantic gives for invalid input
UNPROCESSABLE = 422


def journey_stops(db: Session, journey: Journey) -> list[JourneyStop]:
    """The journey's stops in the order the bus meets them, each marked passed or not."""
    ordered = stops_in_travel_order(journey.route.stops, journey.direction)
    next_index = 0  # no position yet, or off the route: no stop counts as passed
    latest = latest_reading(db, journey)
    if latest is not None:
        progress = journey_progress(journey, latest)
        if progress.next_index is not None:
            next_index = progress.next_index
    return [
        JourneyStop(id=stop.id, name=stop.name, sequence=stop.sequence, passed=place < next_index)
        for place, stop in enumerate(ordered)
    ]


def my_selection(
    db: Session, journey: Journey, student: User, selection_type: SelectionType
) -> StopSelection | None:
    """This student's pickup or drop-off for this journey, if they have chosen one."""
    return db.scalar(
        select(StopSelection).where(
            StopSelection.journey_id == journey.id,
            StopSelection.student_id == student.id,
            StopSelection.type == selection_type,
        )
    )


def check_order(
    stops: list[JourneyStop],
    place: int,
    selection_type: SelectionType,
    other: StopSelection | None,
) -> None:
    """Refuse a pickup at the last stop, a drop-off at the first, or a drop-off before a pickup."""
    if selection_type == SelectionType.PICKUP and place == len(stops) - 1:
        raise HTTPException(UNPROCESSABLE, detail="You cannot be picked up at the last stop")
    if selection_type == SelectionType.DROPOFF and place == 0:
        raise HTTPException(UNPROCESSABLE, detail="You cannot be dropped off at the first stop")
    if other is None:
        return
    other_place = next(i for i, stop in enumerate(stops) if stop.id == other.stop_id)
    pickup, dropoff = (
        (place, other_place) if selection_type == SelectionType.PICKUP else (other_place, place)
    )
    if pickup >= dropoff:
        raise HTTPException(UNPROCESSABLE, detail="Your pickup must come before your drop-off")


@router.get("/{journey_id}/stops")
def list_journey_stops(journey_id: uuid.UUID, db: DbSession) -> list[JourneyStop]:
    """The stops of this journey in travel order, marking the ones already passed (FR-10)."""
    return journey_stops(db, get_journey_or_404(db, journey_id))


@router.get("/{journey_id}/selections/mine")
def list_my_selections(
    journey_id: uuid.UUID, db: DbSession, student: StudentUser
) -> list[SelectionOut]:
    """My chosen pickup and drop-off stops for this journey (FR-12)."""
    journey = get_journey_or_404(db, journey_id)
    selections = db.scalars(
        select(StopSelection).where(
            StopSelection.journey_id == journey.id, StopSelection.student_id == student.id
        )
    )
    return [SelectionOut.model_validate(selection) for selection in selections]


@router.put("/{journey_id}/selections/{selection_type}")
def choose_stop(
    journey_id: uuid.UUID,
    selection_type: SelectionType,
    choice: SelectionChoice,
    db: DbSession,
    student: StudentUser,
) -> SelectionOut:
    """Choose, or change, my pickup or drop-off stop for this journey (FR-07, FR-10, FR-11)."""
    journey = get_journey_or_404(db, journey_id)
    if journey.status != JourneyStatus.ACTIVE:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="This journey has ended")

    stops = journey_stops(db, journey)
    place = next((i for i, stop in enumerate(stops) if stop.id == choice.stop_id), None)
    if place is None:
        raise HTTPException(UNPROCESSABLE, detail="This stop is not on this journey's route")
    if stops[place].passed:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail=f"The bus has already passed {stops[place].name}"
        )
    other_type = (
        SelectionType.DROPOFF if selection_type == SelectionType.PICKUP else SelectionType.PICKUP
    )
    check_order(stops, place, selection_type, my_selection(db, journey, student, other_type))

    selection = my_selection(db, journey, student, selection_type)
    if selection is None:
        selection = StopSelection(
            student_id=student.id,
            journey_id=journey.id,
            stop_id=choice.stop_id,
            type=selection_type,
        )
        db.add(selection)
    elif selection.pickup_status != PickupStatus.PENDING:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="This pickup has already happened or been missed"
        )
    else:
        selection.stop_id = choice.stop_id
    db.commit()
    db.refresh(selection)
    return SelectionOut.model_validate(selection)
