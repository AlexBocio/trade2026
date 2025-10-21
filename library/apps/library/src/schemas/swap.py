"""
Pydantic schemas for Swap API.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class SwapType(str, Enum):
    """Swap type enumeration."""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    AUTOMATIC = "automatic"
    EMERGENCY = "emergency"
    ROLLBACK = "rollback"


class SwapStatus(str, Enum):
    """Swap status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class SwapCreate(BaseModel):
    """Schema for creating a new swap."""
    from_entity_id: UUID = Field(..., description="Entity being replaced")
    to_entity_id: UUID = Field(..., description="Entity replacing the old one")
    environment: str = Field(..., min_length=1, max_length=50, description="Target environment")
    swap_type: SwapType = Field(default=SwapType.MANUAL, description="Type of swap")
    initiated_by: str = Field(..., min_length=1, max_length=255, description="User/system initiating swap")
    reason: Optional[str] = Field(None, max_length=1000, description="Reason for swap")
    config_override: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Config overrides for new entity")
    parameters_override: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Parameter overrides")
    dry_run: bool = Field(default=False, description="Validate only, don't execute")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "from_entity_id": "123e4567-e89b-12d3-a456-426614174000",
            "to_entity_id": "123e4567-e89b-12d3-a456-426614174001",
            "environment": "production",
            "swap_type": "manual",
            "initiated_by": "admin@trade2026.com",
            "reason": "Upgrading to improved strategy version",
            "dry_run": False
        }
    })


class SwapUpdate(BaseModel):
    """Schema for updating an existing swap."""
    status: Optional[SwapStatus] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    rolled_back_at: Optional[datetime] = None
    rolled_back_by: Optional[str] = Field(None, max_length=255)
    rollback_reason: Optional[str] = Field(None, max_length=1000)
    execution_logs: Optional[List[str]] = Field(default_factory=list)
    error_message: Optional[str] = Field(None, max_length=2000)

    model_config = ConfigDict(from_attributes=True)


class SwapResponse(BaseModel):
    """Schema for swap response."""
    swap_id: UUID
    from_entity_id: UUID
    to_entity_id: UUID
    from_deployment_id: Optional[UUID] = None
    to_deployment_id: Optional[UUID] = None
    environment: str
    swap_type: SwapType
    status: SwapStatus
    initiated_by: str
    initiated_at: datetime
    reason: Optional[str] = None
    config_snapshot: Optional[Dict[str, Any]] = Field(default_factory=dict)
    validation_results: Optional[Dict[str, Any]] = Field(default_factory=dict)
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    rolled_back_at: Optional[datetime] = None
    rolled_back_by: Optional[str] = None
    rollback_reason: Optional[str] = None
    previous_swap_id: Optional[UUID] = None
    downtime_milliseconds: Optional[int] = None
    execution_logs: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "swap_id": "123e4567-e89b-12d3-a456-426614174002",
            "from_entity_id": "123e4567-e89b-12d3-a456-426614174000",
            "to_entity_id": "123e4567-e89b-12d3-a456-426614174001",
            "environment": "production",
            "swap_type": "manual",
            "status": "completed",
            "initiated_by": "admin@trade2026.com",
            "initiated_at": "2025-10-20T10:00:00Z",
            "completed_at": "2025-10-20T10:00:05Z",
            "downtime_milliseconds": 150
        }
    })


class SwapList(BaseModel):
    """Schema for paginated swap list."""
    swaps: List[SwapResponse]
    total: int
    page: int
    page_size: int

    model_config = ConfigDict(from_attributes=True)


class SwapRollbackRequest(BaseModel):
    """Schema for swap rollback request."""
    rolled_back_by: str = Field(..., min_length=1, max_length=255, description="User initiating rollback")
    reason: Optional[str] = Field(None, max_length=1000, description="Reason for rollback")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "rolled_back_by": "admin@trade2026.com",
            "reason": "New strategy version showing errors in production"
        }
    })


class SwapValidation(BaseModel):
    """Schema for swap validation results."""
    passed: bool = Field(..., description="Whether validation passed")
    checks: Dict[str, Any] = Field(default_factory=dict, description="Individual check results")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    can_proceed: bool = Field(..., description="Whether swap can proceed")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "passed": True,
            "checks": {
                "entity_types_match": True,
                "from_entity_deployed": True,
                "to_entity_ready": True,
                "same_environment": True
            },
            "errors": [],
            "warnings": ["Config override will change 5 parameters"],
            "can_proceed": True
        }
    })
