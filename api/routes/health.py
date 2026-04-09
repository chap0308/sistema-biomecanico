"""Health-check endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Service health check")
async def health_check() -> dict[str, str]:
    """Return service status for smoke testing and monitoring."""
    return {"status": "ok"}

