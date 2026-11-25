"""A student's profile and the contribution leaderboard (#34, FR-62 to FR-65, NFR-26)."""

import uuid
from collections import Counter
from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.clock import start_of_this_month
from app.core.deps import CurrentUser, DbSession, StudentUser
from app.models import User
from app.points import leaderboard_name, points_by_student, trips_by_student, usual_stop
from app.schemas.profile import (
    Leaderboard,
    LeaderboardEntry,
    LeaderboardPeriod,
    ProfileOut,
    ProfileUpdate,
)

router = APIRouter(tags=["profile"])

TOP = 10  # places shown on the leaderboard


def ranked(points: Counter, names: dict[uuid.UUID, str], me: uuid.UUID) -> list[LeaderboardEntry]:
    """The top students by points; equal points share a rank (1, 2, 2, 4)."""
    order = sorted(points.items(), key=lambda item: (-item[1], names[item[0]]))[:TOP]
    entries: list[LeaderboardEntry] = []
    for place, (student_id, score) in enumerate(order, start=1):
        rank = entries[-1].rank if entries and entries[-1].points == score else place
        entries.append(
            LeaderboardEntry(
                rank=rank, name=names[student_id], points=score, is_me=student_id == me
            )
        )
    return entries


def rank_of(points: Counter, student_id: uuid.UUID) -> int | None:
    """A student's place by points, with the same shared ranks as the leaderboard (1, 2, 2, 4);
    None for a student with no points yet."""
    mine = points[student_id]
    if mine == 0:
        return None
    return 1 + sum(1 for score in points.values() if score > mine)


def profile_of(db: DbSession, student: User) -> ProfileOut:
    """Everything my profile page shows."""
    this_month = points_by_student(db, start_of_this_month())
    return ProfileOut(
        full_name=student.full_name,
        usual_stop=usual_stop(db, student),
        trips=trips_by_student(db)[student.id],
        points=points_by_student(db)[student.id],
        points_this_month=this_month[student.id],
        rank_this_month=rank_of(this_month, student.id),
        hide_name_on_leaderboard=student.hide_name_on_leaderboard,
    )


@router.get("/me/profile")
def read_profile(db: DbSession, student: StudentUser) -> ProfileOut:
    """My name, usual stop, number of trips and points (FR-62, FR-63)."""
    return profile_of(db, student)


@router.patch("/me/profile")
def update_profile(changes: ProfileUpdate, db: DbSession, student: StudentUser) -> ProfileOut:
    """Show or hide my name on the leaderboard (FR-65)."""
    student.hide_name_on_leaderboard = changes.hide_name_on_leaderboard
    db.commit()
    return profile_of(db, student)


@router.get("/leaderboard")
def read_leaderboard(
    db: DbSession, user: CurrentUser, period: Annotated[LeaderboardPeriod, Query()] = "month"
) -> Leaderboard:
    """The top contributors this month or of all time: names or initials and points only, never
    trips, stops or times (FR-64, NFR-26)."""
    points = points_by_student(db, start_of_this_month() if period == "month" else None)
    students = db.scalars(select(User).where(User.id.in_(points.keys())))
    names = {student.id: leaderboard_name(student) for student in students}
    return Leaderboard(period=period, entries=ranked(points, names, user.id))
