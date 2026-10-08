"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from cryptomaka.config import get_settings
from cryptomaka.database import check_db_connection

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Application health check. Never exposes secrets or internal paths."""
    settings = get_settings()
    db_ok = check_db_connection()

    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "unavailable",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }
