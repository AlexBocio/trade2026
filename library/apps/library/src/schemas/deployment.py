"""
Pydantic schemas for Deployment API.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class DeploymentEnvironment(str, Enum):
    """Deployment environment enumeration."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class DeploymentStatus(str, Enum):
    """Deployment status enumeration."""
    PENDING = "pending"
    DEPLOYING = "deploying"
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class DeploymentCreate(BaseModel):
    """Schema for creating deployment."""
    entity_id: UUID
    environment: DeploymentEnvironment
    deployed_by: str = Field(..., min_length=1, max_length=255)
    deployment_method: Optional[str] = Field(None, max_length=50)
    config_override: Optional[Dict[str, Any]] = Field(default_factory=dict)
    parameters_override: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DeploymentUpdate(BaseModel):
    """Schema for updating deployment."""
    status: Optional[DeploymentStatus] = None
    error_logs: Optional[str] = None
    validation_results: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra='forbid')


class DeploymentResponse(BaseModel):
    """Schema for deployment response."""
    deployment_id: UUID
    entity_id: UUID
    version: str
    environment: DeploymentEnvironment
    config_snapshot: Dict[str, Any]
    parameters_snapshot: Optional[Dict[str, Any]]
    status: DeploymentStatus
    deployed_at: datetime
    deployed_by: str
    deployment_method: Optional[str]
    rolled_back_at: Optional[datetime]
    rolled_back_by: Optional[str]
    rollback_reason: Optional[str]
    previous_deployment_id: Optional[UUID]
    health_checks: list
    last_health_check: Optional[datetime]
    error_logs: Optional[str]
    deployment_duration_seconds: Optional[int]
    validation_results: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeploymentList(BaseModel):
    """Schema for list of deployments."""
    deployments: list[DeploymentResponse]
    total: int
    page: int
    page_size: int


class RollbackRequest(BaseModel):
    """Schema for rollback request."""
    reason: str = Field(..., min_length=1)
    rolled_back_by: str = Field(..., min_length=1, max_length=255)
    target_deployment_id: Optional[UUID] = Field(
        None,
        description="Specific deployment to rollback to (if not provided, uses previous)"
    )


class DeploymentValidation(BaseModel):
    """Schema for deployment validation results."""
    passed: bool
    checks: Dict[str, Any]
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
