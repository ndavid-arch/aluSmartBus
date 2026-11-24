"""Students fetch the alerts sent to them for a journey (#25)."""

import uuid

from fastapi import APIRouter
from sqlalchemy import select

from app.core.deps import DbSession, StudentUser
from app.models import Notification
from app.routers.journeys import get_journey_or_404
from app.schemas.notifications import NotificationOut

router = APIRouter(prefix="/journeys", tags=["notifications"])


@router.get("/{journey_id}/notifications/mine")
def list_my_notifications(
    journey_id: uuid.UUID, db: DbSession, student: StudentUser
) -> list[NotificationOut]:
    """My alerts for this journey, oldest first; the page shows the ones it has not shown yet."""
    journey = get_journey_or_404(db, journey_id)
    alerts = db.scalars(
        select(Notification)
        .where(Notification.journey_id == journey.id, Notification.student_id == student.id)
        .order_by(Notification.sent_at)
    )
    return [NotificationOut.model_validate(alert) for alert in alerts]
