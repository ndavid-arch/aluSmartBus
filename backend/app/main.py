"""Creates the FastAPI app and registers its routers."""

from fastapi import FastAPI

from app.routers import auth, bus_status, buses, drivers, health, journeys

app = FastAPI(title="ALU SmartBus API")
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(drivers.router)
app.include_router(buses.router)
app.include_router(bus_status.router)
app.include_router(journeys.router)
