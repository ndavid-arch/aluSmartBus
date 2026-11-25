"""What the profile and leaderboard endpoints return (#34)."""

from typing import Literal

from pydantic import BaseModel

LeaderboardPeriod = Literal["month", "all"]


class ProfileOut(BaseModel):
    """My own profile: only I see my trips and usual stop (FR-62, FR-63)."""

    full_name: str
    usual_stop: str | None
    trips: int
    points: int
    points_this_month: int
    hide_name_on_leaderboard: bool


class ProfileUpdate(BaseModel):
    """What a student can change on their profile."""

    hide_name_on_leaderboard: bool


class LeaderboardEntry(BaseModel):
    """One place on the leaderboard: a name (or initials) and points, nothing else (FR-64)."""

    rank: int
    name: str
    points: int
    is_me: bool


class Leaderboard(BaseModel):
    """The top contributors for this month or for all time (FR-65)."""

    period: LeaderboardPeriod
    entries: list[LeaderboardEntry]
