"""What the admin settings endpoint accepts and returns."""

from pydantic import BaseModel, ConfigDict, Field


class SettingsOut(BaseModel):
    """The settings as the admin screen shows them."""

    model_config = ConfigDict(from_attributes=True)

    arrival_radius_m: float


class SettingsUpdate(BaseModel):
    """A new arrival distance: at least 5 m (the GPS limit) and at most 200 m (about a block)."""

    arrival_radius_m: float = Field(ge=5, le=200)
