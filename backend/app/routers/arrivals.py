"""Which stops a journey has reached (#22), and the admin's arrival distance setting."""

import uuid

from fastapi import APIRouter
from sqlalchemy import select

from app.core.deps import AdminUser, DbSession
from app.models import Stop, StopArrival
from app.routers.journeys import get_journey_or_404
from app.schemas.arrivals import ArrivalOut
from app.schemas.settings import SettingsOut, SettingsUpdate
from app.system_settings import current_settings

router = APIRouter(tags=["arrivals"])


@router.get("/journeys/{journey_id}/arrivals")
def list_arrivals(journey_id: uuid.UUID, db: DbSession) -> list[ArrivalOut]:
    """The stops this journey has reached so far, earliest first, with time and status (FR-30)."""
    journey = get_journey_or_404(db, journey_id)
    arrivals = db.scalars(
        select(StopArrival)
        .join(Stop)
        .where(StopArrival.journey_id == journey.id)
        # Two arrivals in the same second (possible in tests) fall back to route order
        .order_by(StopArrival.arrived_at, Stop.sequence)
    )
    return [ArrivalOut.model_validate(arrival) for arrival in arrivals]


@router.get("/admin/settings")
def read_settings(db: DbSession, _admin: AdminUser) -> SettingsOut:
    """The settings the administrator can change."""
    return SettingsOut.model_validate(current_settings(db))


@router.patch("/admin/settings")
def change_settings(changes: SettingsUpdate, db: DbSession, _admin: AdminUser) -> SettingsOut:
    """Change the arrival distance; it applies from the next bus position onwards (FR-29)."""
    settings = current_settings(db)
    settings.arrival_radius_m = changes.arrival_radius_m
    db.commit()
    return SettingsOut.model_validate(settings)
