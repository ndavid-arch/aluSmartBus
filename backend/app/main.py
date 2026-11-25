"""Creates the FastAPI app and registers its routers."""

from fastapi import FastAPI

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
    reports,
    selections,
)

app = FastAPI(title="ALU SmartBus API")
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
