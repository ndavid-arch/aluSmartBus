"""What the alerts endpoint returns."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import NotificationType


class NotificationOut(BaseModel):
    """One alert sent to the student."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: NotificationType
    message: str
    sent_at: datetime
