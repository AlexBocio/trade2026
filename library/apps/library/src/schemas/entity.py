"""
Pydantic schemas for Entity model.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# Base schema with common fields
class EntityBase(BaseModel):
    """Base schema for Entity with common fields."""
    name: str = Field(..., max_length=255, description="Unique entity name")
    type: str = Field(..., max_length=50, description="Entity type (strategy, pipeline, model, etc.)")
    category: Optional[str] = Field(None, max_length=100, description="Entity category")
    description: Optional[str] = Field(None, description="Detailed description")
    version: str = Field(..., max_length=50, description="Entity version")
    author: Optional[str] = Field(None, max_length=255, description="Entity author")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for categorization")
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuration JSON")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Runtime parameters")
    requirements: Optional[List[str]] = Field(default_factory=list, description="Dependencies list")


# Create schema (for POST requests)
class EntityCreate(EntityBase):
    """Schema for creating a new entity."""
    status: str = Field(default='registered', max_length=50, description="Initial status")
    health_status: str = Field(default='unknown', max_length=50, description="Initial health status")
    cpu_limit: Optional[int] = Field(None, gt=0, description="CPU cores limit")
    memory_limit_mb: Optional[int] = Field(None, gt=0, description="Memory limit in MB")
    gpu_required: bool = Field(default=False, description="GPU requirement flag")
    created_by: Optional[str] = Field(None, max_length=255, description="Creator username")


# Update schema (for PUT/PATCH requests)
class EntityUpdate(BaseModel):
    """Schema for updating an existing entity."""
    name: Optional[str] = Field(None, max_length=255)
    type: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    version: Optional[str] = Field(None, max_length=50)
    author: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    requirements: Optional[List[str]] = None
    status: Optional[str] = Field(None, max_length=50)
    health_status: Optional[str] = Field(None, max_length=50)
    cpu_limit: Optional[int] = Field(None, gt=0)
    memory_limit_mb: Optional[int] = Field(None, gt=0)
    gpu_required: Optional[bool] = None
    updated_by: Optional[str] = Field(None, max_length=255)


# Response schema (for GET requests)
class EntityResponse(EntityBase):
    """Schema for entity responses."""
    entity_id: UUID
    status: str
    health_status: str
    deployed_at: Optional[datetime] = None
    deployed_by: Optional[str] = None
    deployment_config: Optional[Dict[str, Any]] = None
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    last_evaluation: Optional[datetime] = None
    cpu_limit: Optional[int] = None
    memory_limit_mb: Optional[int] = None
    gpu_required: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# List response schema
class EntityListResponse(BaseModel):
    """Schema for paginated entity list."""
    items: List[EntityResponse]
    total: int
    page: int
    page_size: int
    pages: int


# Summary schema (lightweight for listings)
class EntitySummary(BaseModel):
    """Lightweight entity summary for list views."""
    entity_id: UUID
    name: str
    type: str
    category: Optional[str]
    version: str
    status: str
    health_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Alias for compatibility with Prompt 04 requirements
class EntityList(BaseModel):
    """Schema for paginated entity list (alias)."""
    entities: List[EntityResponse]
    total: int
    page: int
    page_size: int


# Filter schema for query parameters
class EntityFilter(BaseModel):
    """Schema for entity filtering parameters."""
    type: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    health_status: Optional[str] = None
    search: Optional[str] = None
    tags: Optional[List[str]] = None
