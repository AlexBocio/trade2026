"""
Health check endpoints for Library Service.
"""
from fastapi import APIRouter, status
from datetime import datetime
import logging

from ...schemas.health import HealthResponse, DetailedHealthResponse
from ...db.database import check_db_connection
from ...core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


def _get_nats_status() -> str:
    """Get NATS connection status."""
    if not settings.NATS_ENABLED:
        return "disabled"
    try:
        from ...messaging import nats_client
        return "connected" if nats_client.connected else "disconnected"
    except:
        return "unknown"


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Basic health check",
    description="Returns basic service health status"
)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.

    Returns:
        HealthResponse with status and timestamp
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow()
    )


@router.get(
    "/health/detailed",
    response_model=DetailedHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Detailed health check",
    description="Returns detailed health status including all component checks"
)
async def detailed_health_check() -> DetailedHealthResponse:
    """
    Detailed health check endpoint.

    Checks:
    - Database connectivity
    - Service configuration

    Returns:
        DetailedHealthResponse with component-level health information
    """
    # Check database connection
    db_healthy = check_db_connection()

    # Determine overall status
    overall_status = "healthy" if db_healthy else "unhealthy"

    # Build response
    response = DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version=settings.VERSION,
        service={
            "name": settings.SERVICE_NAME,
            "version": settings.VERSION,
            "port": settings.PORT,
            "debug": settings.DEBUG,
        },
        components={
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "type": "postgresql",
                "url": settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else "N/A",  # Hide credentials
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_MAX_OVERFLOW,
            },
            "nats": {
                "status": _get_nats_status(),
                "enabled": settings.NATS_ENABLED,
                "url": settings.NATS_URL if settings.NATS_ENABLED else "N/A",
            }
        }
    )

    logger.info(f"Detailed health check performed: {overall_status}")

    return response
