"""Reading the administrator's settings, creating them with defaults the first time."""

from sqlalchemy.orm import Session

from app.models import SystemSettings


def current_settings(db: Session) -> SystemSettings:
    """The one settings row; made with the defaults if no admin has saved settings yet."""
    settings = db.get(SystemSettings, 1)
    if settings is None:
        settings = SystemSettings(id=1)
        db.add(settings)
        db.flush()  # fills in the defaults; saved with the rest of the request's changes
    return settings
