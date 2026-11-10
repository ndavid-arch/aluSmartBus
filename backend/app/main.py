"""Creates the FastAPI app and registers its routers."""

from fastapi import FastAPI

from app.routers import health

app = FastAPI(title="ALU SmartBus API")
app.include_router(health.router)
