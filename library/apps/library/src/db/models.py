"""
SQLAlchemy models for Library Service.

Maps to PostgreSQL schema defined in 01_schema.sql.
"""
from sqlalchemy import (
    Column, String, Integer, Boolean, Text, TIMESTAMP, ARRAY,
    CheckConstraint, ForeignKey, NUMERIC, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .database import Base


class Entity(Base):
    """
    Registry of all ML entities (strategies, pipelines, models).

    Maps to: entities table
    """
    __tablename__ = "entities"

    # Primary identification
    entity_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)

    # Entity type and classification
    type = Column(String(50), nullable=False)
    category = Column(String(100))

    # Metadata
    description = Column(Text)
    version = Column(String(50), nullable=False)
    author = Column(String(255))
    tags = Column(ARRAY(Text))

    # Configuration
    config = Column(JSONB, default={})
    parameters = Column(JSONB, default={})
    requirements = Column(ARRAY(Text))

    # Status and lifecycle
    status = Column(String(50), nullable=False, default='registered')
    health_status = Column(String(50), default='unknown')

    # Deployment tracking
    deployed_at = Column(TIMESTAMP(timezone=True))
    deployed_by = Column(String(255))
    deployment_config = Column(JSONB)

    # Performance metrics
    performance_metrics = Column(JSONB, default={})
    last_evaluation = Column(TIMESTAMP(timezone=True))

    # Resource usage
    cpu_limit = Column(Integer)
    memory_limit_mb = Column(Integer)
    gpu_required = Column(Boolean, default=False)

    # Audit fields
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    updated_by = Column(String(255))

    # Soft delete
    deleted_at = Column(TIMESTAMP(timezone=True))
    deleted_by = Column(String(255))

    # Relationships
    deployments = relationship("Deployment", back_populates="entity", cascade="all, delete-orphan")
    performance_metrics_records = relationship("PerformanceMetric", back_populates="entity", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="entity")
    dependencies_as_entity = relationship(
        "Dependency",
        foreign_keys="[Dependency.entity_id]",
        back_populates="entity",
        cascade="all, delete-orphan"
    )
    dependencies_as_depends_on = relationship(
        "Dependency",
        foreign_keys="[Dependency.depends_on_entity_id]",
        back_populates="depends_on_entity",
        cascade="all, delete-orphan"
    )

    # Check constraints
    __table_args__ = (
        CheckConstraint(
            type.in_([
                'strategy', 'pipeline', 'model', 'feature_set',
                'transformer', 'validator', 'optimizer'
            ]),
            name='entities_type_check'
        ),
        CheckConstraint(
            status.in_([
                'registered', 'validated', 'deployed', 'active',
                'inactive', 'deprecated', 'failed'
            ]),
            name='entities_status_check'
        ),
        CheckConstraint(
            health_status.in_(['healthy', 'degraded', 'unhealthy', 'unknown']),
            name='entities_health_status_check'
        ),
    )


class Deployment(Base):
    """
    Tracks deployment history and rollback capability.

    Maps to: deployments table
    """
    __tablename__ = "deployments"

    deployment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(UUID(as_uuid=True), ForeignKey('entities.entity_id', ondelete='CASCADE'), nullable=False)

    # Deployment details
    version = Column(String(50), nullable=False)
    environment = Column(String(50), nullable=False)

    # Configuration at deployment time
    config_snapshot = Column(JSONB, nullable=False)
    parameters_snapshot = Column(JSONB)

    # Status tracking
    status = Column(String(50), nullable=False)

    # Deployment metadata
    deployed_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    deployed_by = Column(String(255), nullable=False)
    deployment_method = Column(String(50))

    # Rollback tracking
    rolled_back_at = Column(TIMESTAMP(timezone=True))
    rolled_back_by = Column(String(255))
    rollback_reason = Column(Text)
    previous_deployment_id = Column(UUID(as_uuid=True), ForeignKey('deployments.deployment_id'))

    # Health and monitoring
    health_checks = Column(JSONB, default=[])
    last_health_check = Column(TIMESTAMP(timezone=True))
    error_logs = Column(Text)

    # Performance during deployment
    deployment_duration_seconds = Column(Integer)
    validation_results = Column(JSONB)

    # Audit
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    entity = relationship("Entity", back_populates="deployments")
    swaps_from = relationship(
        "Swap",
        foreign_keys="[Swap.from_deployment_id]",
        back_populates="from_deployment"
    )
    swaps_to = relationship(
        "Swap",
        foreign_keys="[Swap.to_deployment_id]",
        back_populates="to_deployment"
    )
    performance_metrics = relationship("PerformanceMetric", back_populates="deployment")
    events = relationship("Event", back_populates="deployment")

    # Check constraints
    __table_args__ = (
        CheckConstraint(
            environment.in_(['development', 'staging', 'production', 'testing']),
            name='deployments_environment_check'
        ),
        CheckConstraint(
            status.in_([
                'pending', 'deploying', 'active', 'inactive',
                'failed', 'rolled_back'
            ]),
            name='deployments_status_check'
        ),
    )


class Swap(Base):
    """
    Tracks hot-swap operations and their outcomes.

    Maps to: swaps table
    """
    __tablename__ = "swaps"

    swap_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Swap operation details
    from_entity_id = Column(UUID(as_uuid=True), ForeignKey('entities.entity_id'), nullable=False)
    to_entity_id = Column(UUID(as_uuid=True), ForeignKey('entities.entity_id'), nullable=False)
    from_deployment_id = Column(UUID(as_uuid=True), ForeignKey('deployments.deployment_id'))
    to_deployment_id = Column(UUID(as_uuid=True), ForeignKey('deployments.deployment_id'))
    environment = Column(String(50), nullable=False)

    # Swap metadata
    swap_type = Column(String(50), nullable=False)
    reason = Column(Text)
    config_snapshot = Column(JSONB, default={})

    # Status tracking
    status = Column(String(50), nullable=False)

    # Timing
    initiated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    completed_at = Column(TIMESTAMP(timezone=True))
    failed_at = Column(TIMESTAMP(timezone=True))
    duration_seconds = Column(Integer)
    downtime_milliseconds = Column(Integer)

    # Execution details
    initiated_by = Column(String(255), nullable=False)
    approved_by = Column(String(255))
    execution_method = Column(String(50))
    execution_logs = Column(ARRAY(Text), default=[])

    # Validation and testing
    validation_results = Column(JSONB, default={})
    pre_swap_validation = Column(JSONB)
    post_swap_validation = Column(JSONB)
    validation_passed = Column(Boolean)

    # Impact tracking
    affected_systems = Column(ARRAY(Text))
    downtime_seconds = Column(Integer, default=0)

    # Results
    success = Column(Boolean)
    error_message = Column(Text)
    logs = Column(Text)

    # Rollback capability
    can_rollback = Column(Boolean, default=True)
    rolled_back_at = Column(TIMESTAMP(timezone=True))
    rolled_back_by = Column(String(255))
    rollback_reason = Column(Text)
    previous_swap_id = Column(UUID(as_uuid=True), ForeignKey('swaps.swap_id'))

    # Audit
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    from_entity = relationship("Entity", foreign_keys=[from_entity_id])
    to_entity = relationship("Entity", foreign_keys=[to_entity_id])
    from_deployment = relationship("Deployment", foreign_keys=[from_deployment_id], back_populates="swaps_from")
    to_deployment = relationship("Deployment", foreign_keys=[to_deployment_id], back_populates="swaps_to")
    events = relationship("Event", back_populates="swap")

    # Check constraints
    __table_args__ = (
        CheckConstraint(
            swap_type.in_(['manual', 'scheduled', 'automatic', 'emergency', 'rollback']),
            name='swaps_type_check'
        ),
        CheckConstraint(
            status.in_([
                'initiated', 'in_progress', 'completed', 'failed',
                'partially_completed', 'rolled_back'
            ]),
            name='swaps_status_check'
        ),
    )


class PerformanceMetric(Base):
    """
    Detailed performance tracking for deployed entities.

    Maps to: performance_metrics table
    """
    __tablename__ = "performance_metrics"

    metric_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(UUID(as_uuid=True), ForeignKey('entities.entity_id', ondelete='CASCADE'), nullable=False)
    deployment_id = Column(UUID(as_uuid=True), ForeignKey('deployments.deployment_id'))

    # Timestamp
    recorded_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    period_start = Column(TIMESTAMP(timezone=True), nullable=False)
    period_end = Column(TIMESTAMP(timezone=True), nullable=False)

    # Performance metrics
    execution_count = Column(Integer, default=0)
    avg_latency_ms = Column(NUMERIC(10, 3))
    p50_latency_ms = Column(NUMERIC(10, 3))
    p95_latency_ms = Column(NUMERIC(10, 3))
    p99_latency_ms = Column(NUMERIC(10, 3))
    max_latency_ms = Column(NUMERIC(10, 3))

    # Success/failure tracking
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    timeout_count = Column(Integer, default=0)
    success_rate = Column(NUMERIC(5, 4))

    # Resource usage
    avg_cpu_percent = Column(NUMERIC(5, 2))
    max_cpu_percent = Column(NUMERIC(5, 2))
    avg_memory_mb = Column(NUMERIC(10, 2))
    max_memory_mb = Column(NUMERIC(10, 2))

    # Trading performance (if applicable)
    sharpe_ratio = Column(NUMERIC(10, 6))
    win_rate = Column(NUMERIC(5, 4))
    total_return = Column(NUMERIC(15, 6))
    max_drawdown = Column(NUMERIC(15, 6))
    profit_factor = Column(NUMERIC(10, 4))

    # Custom metrics (flexible)
    custom_metrics = Column(JSONB, default={})

    # Audit
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    entity = relationship("Entity", back_populates="performance_metrics_records")
    deployment = relationship("Deployment", back_populates="performance_metrics")


class Event(Base):
    """
    Audit log for all significant events.

    Maps to: events table
    """
    __tablename__ = "events"

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Event classification
    event_type = Column(String(100), nullable=False)
    event_category = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)

    # Related entities
    entity_id = Column(UUID(as_uuid=True), ForeignKey('entities.entity_id'))
    deployment_id = Column(UUID(as_uuid=True), ForeignKey('deployments.deployment_id'))
    swap_id = Column(UUID(as_uuid=True), ForeignKey('swaps.swap_id'))

    # Event details
    message = Column(Text, nullable=False)
    details = Column(JSONB, default={})

    # Context
    user_id = Column(String(255))
    source = Column(String(255))

    # Timestamp
    occurred_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Audit
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    entity = relationship("Entity", back_populates="events")
    deployment = relationship("Deployment", back_populates="events")
    swap = relationship("Swap", back_populates="events")

    # Check constraints
    __table_args__ = (
        CheckConstraint(
            event_category.in_([
                'entity_lifecycle', 'deployment', 'swap', 'performance',
                'health', 'error', 'audit'
            ]),
            name='events_category_check'
        ),
        CheckConstraint(
            severity.in_(['debug', 'info', 'warning', 'error', 'critical']),
            name='events_severity_check'
        ),
    )


class Dependency(Base):
    """
    Track dependencies between entities.

    Maps to: dependencies table
    """
    __tablename__ = "dependencies"

    dependency_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relationship
    entity_id = Column(UUID(as_uuid=True), ForeignKey('entities.entity_id', ondelete='CASCADE'), nullable=False)
    depends_on_entity_id = Column(UUID(as_uuid=True), ForeignKey('entities.entity_id', ondelete='CASCADE'), nullable=False)

    # Dependency type
    dependency_type = Column(String(50), nullable=False)

    # Version constraints
    min_version = Column(String(50))
    max_version = Column(String(50))

    # Status
    status = Column(String(50), default='active')

    # Audit
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    entity = relationship("Entity", foreign_keys=[entity_id], back_populates="dependencies_as_entity")
    depends_on_entity = relationship("Entity", foreign_keys=[depends_on_entity_id], back_populates="dependencies_as_depends_on")

    # Check constraints
    __table_args__ = (
        CheckConstraint(
            dependency_type.in_(['required', 'optional', 'recommended', 'conflicts_with']),
            name='dependencies_type_check'
        ),
        CheckConstraint(
            status.in_(['active', 'inactive', 'broken']),
            name='dependencies_status_check'
        ),
        # Prevent duplicate dependencies
        Index('uq_entity_depends_on', entity_id, depends_on_entity_id, unique=True),
    )
