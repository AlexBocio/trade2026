"""
Main FastAPI application for Library Service.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .core.config import settings
from .db.database import init_db, check_db_connection
from .api.v1 import api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"API prefix: {settings.API_V1_PREFIX}")

    # Initialize database
    try:
        init_db()
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

    # Check database connection
    if not check_db_connection():
        logger.error("Database connection check failed")
        raise RuntimeError("Database connection failed")

    # Connect to NATS (graceful degradation if unavailable)
    try:
        from .messaging import nats_client
        await nats_client.connect()
        logger.info("NATS connected successfully")
    except Exception as e:
        logger.warning(f"NATS connection failed: {e} - continuing without messaging")

    logger.info(f"{settings.SERVICE_NAME} startup complete")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.SERVICE_NAME}")

    # Disconnect NATS
    try:
        from .messaging import nats_client
        await nats_client.disconnect()
        logger.info("NATS disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting NATS: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.SERVICE_NAME,
    description="ML Library Registry - Manages strategies, pipelines, models, and hot-swap operations",
    version=settings.VERSION,
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Include routers
app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with service information."""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
