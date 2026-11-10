"""Health check so we(and the hosting platform) know that thw API is up and running."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Return a simple status so the callers know that the API is Up"""
    return {"status": "ok"}
