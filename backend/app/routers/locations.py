"""The driver's phone sends the bus position during an active journey (#16, #20, #22, #23)."""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from app.arrivals import record_arrivals
from app.boarding import expire_missed_pickups
from app.core.deps import DbSession, DriverUser
from app.eta import stops_in_travel_order
from app.geo import distance_m
from app.live import journey_ended_message, live_updates
from app.models import Journey, JourneyStatus, LocationUpdate
from app.routers.journeys import complete, get_journey_or_404, latest_reading
from app.schemas.live import LiveBus
from app.schemas.locations import LocationIn, LocationOut, LocationSaved
from app.system_settings import current_settings

router = APIRouter(prefix="/journeys", tags=["locations"])


def reached_terminal(
    journey: Journey, reading: LocationIn, previous: LocationUpdate | None, radius_m: float
) -> bool:
    """True when this reading is at the last stop and the one before was not (FR-18).

    Needing a reading away from the terminal first means a bus that starts its journey parked
    at the terminal is not ended straight away.
    """
    terminal = stops_in_travel_order(journey.route.stops, journey.direction)[-1]

    def at_terminal(lat: float, lng: float) -> bool:
        return distance_m(lat, lng, terminal.latitude, terminal.longitude) <= radius_m

    return (
        previous is not None
        and at_terminal(reading.latitude, reading.longitude)
        and not at_terminal(previous.latitude, previous.longitude)
    )


@router.post("/{journey_id}/locations", status_code=status.HTTP_201_CREATED)
def share_location(
    journey_id: uuid.UUID,
    reading: LocationIn,
    db: DbSession,
    driver: DriverUser,
    background_tasks: BackgroundTasks,
) -> LocationSaved:
    """Save one position of the bus, note any stop it has reached, push it to every open map,
    and end the journey at the terminal (FR-18, FR-20 to FR-22, FR-28 to FR-30)."""
    journey = get_journey_or_404(db, journey_id)
    if journey.driver_id != driver.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="This is not your journey")
    if journey.status != JourneyStatus.ACTIVE:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="This journey has ended")

    radius_m = current_settings(db).arrival_radius_m
    arrived = reached_terminal(journey, reading, latest_reading(db, journey), radius_m)
    location = LocationUpdate(journey_id=journey.id, **reading.model_dump())
    db.add(location)
    record_arrivals(journey, reading.latitude, reading.longitude, radius_m)
    db.flush()  # so the new arrivals have their times before the window check below
    expire_missed_pickups(db, journey, datetime.now(UTC))
    if arrived:
        complete(journey)
    db.commit()
    db.refresh(location)
    db.refresh(journey)

    # Sent just after the reply, so the driver's phone never waits for the maps
    if arrived:
        background_tasks.add_task(live_updates.broadcast, journey_ended_message(journey.id))
    else:
        live_bus = LiveBus.from_parts(journey, location).model_dump(mode="json")
        background_tasks.add_task(live_updates.broadcast, live_bus)

    saved = LocationOut.model_validate(location).model_dump()
    return LocationSaved(**saved, journey_status=journey.status)
