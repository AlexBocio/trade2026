"""
Pydantic schemas for health endpoints.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class HealthResponse(BaseModel):
    """Basic health check response."""
    status: str = Field(..., description="Service status (healthy/unhealthy)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")


class DetailedHealthResponse(BaseModel):
    """Detailed health check response with component status."""
    status: str = Field(..., description="Overall service status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    service: Dict[str, Any] = Field(..., description="Service information")
    components: Dict[str, Dict[str, Any]] = Field(..., description="Component health status")
    version: str = Field(..., description="Service version")
