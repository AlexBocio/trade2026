"""
Event schemas for NATS messages.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class EventType(str, Enum):
    """Event type enumeration."""
    # Entity lifecycle
    ENTITY_REGISTERED = "entity.registered"
    ENTITY_UPDATED = "entity.updated"
    ENTITY_DELETED = "entity.deleted"
    ENTITY_VALIDATED = "entity.validated"

    # Deployment
    DEPLOYMENT_STARTED = "deployment.started"
    DEPLOYMENT_COMPLETED = "deployment.completed"
    DEPLOYMENT_FAILED = "deployment.failed"
    DEPLOYMENT_ROLLED_BACK = "deployment.rolled_back"

    # Swap
    SWAP_INITIATED = "swap.initiated"
    SWAP_VALIDATED = "swap.validated"
    SWAP_COMPLETED = "swap.completed"
    SWAP_FAILED = "swap.failed"
    SWAP_ROLLED_BACK = "swap.rolled_back"

    # Health
    HEALTH_DEGRADED = "health.degraded"
    HEALTH_RECOVERED = "health.recovered"

    # Performance
    PERFORMANCE_THRESHOLD_EXCEEDED = "performance.threshold_exceeded"


class LibraryEvent(BaseModel):
    """Base event schema."""
    event_id: UUID
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "library_service"
    entity_id: Optional[UUID] = None
    deployment_id: Optional[UUID] = None
    swap_id: Optional[UUID] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EntityRegisteredEvent(LibraryEvent):
    """Entity registered event."""
    event_type: EventType = EventType.ENTITY_REGISTERED
    entity_id: UUID
    entity_name: str
    entity_type: str
    version: str


class DeploymentCompletedEvent(LibraryEvent):
    """Deployment completed event."""
    event_type: EventType = EventType.DEPLOYMENT_COMPLETED
    entity_id: UUID
    deployment_id: UUID
    environment: str
    version: str


class SwapRequest(BaseModel):
    """Swap request schema."""
    from_entity_id: UUID
    to_entity_id: UUID
    reason: str
    initiated_by: str
    validate_only: bool = False


class SwapResponse(BaseModel):
    """Swap response schema."""
    swap_id: UUID
    status: str
    success: bool
    message: str
    validation_results: Optional[Dict[str, Any]] = None


# NATS subject patterns
class Subjects:
    """NATS subject definitions."""
    # Entity events
    ENTITY_ALL = "library.entity.*"
    ENTITY_REGISTERED = "library.entity.registered"
    ENTITY_UPDATED = "library.entity.updated"
    ENTITY_DELETED = "library.entity.deleted"

    # Deployment events
    DEPLOYMENT_ALL = "library.deployment.*"
    DEPLOYMENT_COMPLETED = "library.deployment.completed"
    DEPLOYMENT_FAILED = "library.deployment.failed"

    # Swap events and commands
    SWAP_ALL = "library.swap.*"
    SWAP_INITIATED = "library.swap.initiated"
    SWAP_COMPLETED = "library.swap.completed"
    SWAP_COMMAND = "library.swap.command"  # Request/reply

    # Health
    HEALTH_ALL = "library.health.*"
    HEALTH_DEGRADED = "library.health.degraded"
