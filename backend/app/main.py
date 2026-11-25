"""Creates the FastAPI app and registers its routers."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import (
    arrivals,
    auth,
    boardings,
    bus_status,
    buses,
    drivers,
    health,
    journeys,
    live,
    locations,
    notifications,
    profile,
    reports,
    selections,
)

app = FastAPI(title="ALU SmartBus API")
# The deployed website lives on another address than the API, so the browser must be told it may
# call it (#32); only the addresses in CORS_ORIGINS are allowed
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().allowed_origins,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(drivers.router)
app.include_router(buses.router)
app.include_router(bus_status.router)
app.include_router(journeys.router)
app.include_router(locations.router)
app.include_router(live.router)
app.include_router(selections.router)
app.include_router(arrivals.router)
app.include_router(notifications.router)
app.include_router(boardings.router)
app.include_router(reports.router)
app.include_router(profile.router)
