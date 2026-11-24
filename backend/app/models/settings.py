"""Settings the administrator can change while the app is running."""

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

# A bus this close to a stop has arrived there (FR-28). 30 m, not the SRS's first 5 m: phones are
# accurate to about +-7 m and send a position every 5 s (spike #9), so 5 m would miss most arrivals.
DEFAULT_ARRIVAL_RADIUS_M = 30.0


class SystemSettings(Base):
    """The one row of app-wide settings; the database refuses a second row."""

    __tablename__ = "system_settings"
    __table_args__ = (CheckConstraint("id = 1", name="only_one_settings_row"),)

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    arrival_radius_m: Mapped[float] = mapped_column(
        default=DEFAULT_ARRIVAL_RADIUS_M, server_default=str(DEFAULT_ARRIVAL_RADIUS_M)
    )
