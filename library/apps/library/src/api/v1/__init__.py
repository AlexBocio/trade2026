"""
API v1 router registration.
"""
from fastapi import APIRouter
from .health import router as health_router
from .endpoints import entities, deployments, swaps

# Create v1 router
api_router = APIRouter()

# Include health router
api_router.include_router(health_router)

# Include entity router
api_router.include_router(entities.router)

# Include deployment router
api_router.include_router(deployments.router)

# Include swap router (hotswap engine)
api_router.include_router(swaps.router)

# Export
__all__ = ['api_router']
