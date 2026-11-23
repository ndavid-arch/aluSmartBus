"""The driver's phone sends the bus position during an active journey (#16)."""

import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from app.core.deps import DbSession, DriverUser
from app.live import live_updates
from app.models import JourneyStatus, LocationUpdate
from app.routers.journeys import get_journey_or_404
from app.schemas.live import LiveBus
from app.schemas.locations import LocationIn, LocationOut

router = APIRouter(prefix="/journeys", tags=["locations"])


@router.post("/{journey_id}/locations", status_code=status.HTTP_201_CREATED)
def share_location(
    journey_id: uuid.UUID,
    reading: LocationIn,
    db: DbSession,
    driver: DriverUser,
    background_tasks: BackgroundTasks,
) -> LocationOut:
    """Save one position of the bus, then push it to every open map (FR-20 to FR-22)."""
    journey = get_journey_or_404(db, journey_id)
    if journey.driver_id != driver.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="This is not your journey")
    if journey.status != JourneyStatus.ACTIVE:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="This journey has ended")

    location = LocationUpdate(journey_id=journey.id, **reading.model_dump())
    db.add(location)
    db.commit()
    db.refresh(location)
    # Sent just after the reply, so the driver's phone never waits for the maps
    live_bus = LiveBus.from_parts(journey, location).model_dump(mode="json")
    background_tasks.add_task(live_updates.broadcast, live_bus)
    return LocationOut.model_validate(location)
