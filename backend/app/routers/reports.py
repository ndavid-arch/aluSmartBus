"""The admin's journey, boarding and demand report for a chosen period (#30)."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.core.deps import AdminUser, DbSession
from app.reports import build_report
from app.routers.journeys import get_route_or_503
from app.schemas.reports import Report

router = APIRouter(prefix="/admin/reports", tags=["reports"])

UNPROCESSABLE = 422
MAX_DAYS = 366  # one school year at most, so a report stays quick to build


@router.get("")
def get_report(
    start: Annotated[date, Query(description="First day, e.g. 2026-11-01 (Kigali time)")],
    end: Annotated[date, Query(description="Last day, included")],
    db: DbSession,
    _admin: AdminUser,
) -> Report:
    """Completed journeys, boarding totals and demand by stop between two dates, for admins only
    (FR-57 to FR-59)."""
    if end < start:
        raise HTTPException(UNPROCESSABLE, detail="The end date is before the start date")
    if (end - start).days + 1 > MAX_DAYS:
        raise HTTPException(UNPROCESSABLE, detail=f"Choose a period of at most {MAX_DAYS} days")
    return build_report(db, get_route_or_503(db), start, end)
