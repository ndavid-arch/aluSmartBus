"""The route and the live bus positions, open to everyone including guests (#17)."""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.deps import DbSession
from app.live import live_updates
from app.models import Journey, JourneyStatus, Route
from app.road_path import load_road_path
from app.routers.journeys import latest_reading
from app.schemas.live import LiveBus, RouteOut
from app.seed_data import ROUTE_NAME

router = APIRouter(tags=["live map"])


@router.get("/route")
def get_route(db: DbSession) -> RouteOut:
    """The Rebero - ALU route, its stops in order and the line to draw (FR-09, #79)."""
    route = db.scalar(
        select(Route).where(Route.name == ROUTE_NAME).options(selectinload(Route.stops))
    )
    if route is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="The route is not set up yet")
    shown = RouteOut.model_validate(route)
    straight = [(stop.latitude, stop.longitude) for stop in shown.stops]
    return shown.model_copy(update={"path": load_road_path() or straight})


@router.get("/live/buses")
def list_live_buses(db: DbSession) -> list[LiveBus]:
    """The latest position of every bus on the road, used when a map first opens."""
    journeys = db.scalars(select(Journey).where(Journey.status == JourneyStatus.ACTIVE))
    buses = []
    for journey in journeys:
        latest = latest_reading(db, journey)
        if latest is not None:  # a journey that has not sent a position yet has nothing to show
            buses.append(LiveBus.from_parts(journey, latest))
    return buses


@router.websocket("/live/ws")
async def live_map_updates(websocket: WebSocket) -> None:
    """Keep a map connected and push each new bus position to it (FR-22, FR-23)."""
    await live_updates.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # maps never send anything; this waits until they leave
    except WebSocketDisconnect:
        live_updates.disconnect(websocket)
