-- ==================================================
-- Library Service Database Schema
-- Version: 1.0
-- Component: Strategy & ML Library Registry
-- ==================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search

-- ==================================================
-- ENTITIES TABLE
-- Stores all registered entities (strategies, pipelines, models)
-- ==================================================

CREATE TABLE IF NOT EXISTS entities (
    -- Primary identification
    entity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,

    -- Entity type and classification
    type VARCHAR(50) NOT NULL CHECK (type IN (
        'strategy',
        'pipeline',
        'model',
        'feature_set',
        'transformer',
        'validator',
        'optimizer'
    )),
    category VARCHAR(100),

    -- Metadata
    description TEXT,
    version VARCHAR(50) NOT NULL,
    author VARCHAR(255),
    tags TEXT[],  -- Array of tags for search

    -- Configuration
    config JSONB DEFAULT '{}',
    parameters JSONB DEFAULT '{}',
    requirements TEXT[],  -- Dependencies list

    -- Status and lifecycle
    status VARCHAR(50) NOT NULL DEFAULT 'registered' CHECK (status IN (
        'registered',
        'validated',
        'deployed',
        'active',
        'inactive',
        'deprecated',
        'failed'
    )),
    health_status VARCHAR(50) DEFAULT 'unknown' CHECK (health_status IN (
        'healthy',
        'degraded',
        'unhealthy',
        'unknown'
    )),

    -- Deployment tracking
    deployed_at TIMESTAMP WITH TIME ZONE,
    deployed_by VARCHAR(255),
    deployment_config JSONB,

    -- Performance metrics
    performance_metrics JSONB DEFAULT '{}',
    last_evaluation TIMESTAMP WITH TIME ZONE,

    -- Resource usage
    cpu_limit INTEGER,  -- CPU cores
    memory_limit_mb INTEGER,
    gpu_required BOOLEAN DEFAULT FALSE,

    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),

    -- Soft delete
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by VARCHAR(255)
);

-- Indexes for entities table
CREATE INDEX idx_entities_type ON entities(type) WHERE deleted_at IS NULL;
CREATE INDEX idx_entities_status ON entities(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_entities_category ON entities(category) WHERE deleted_at IS NULL;
CREATE INDEX idx_entities_health ON entities(health_status) WHERE deleted_at IS NULL;
CREATE INDEX idx_entities_created ON entities(created_at DESC);
CREATE INDEX idx_entities_tags ON entities USING GIN(tags);  -- GIN index for array search
CREATE INDEX idx_entities_name_search ON entities USING GIN(name gin_trgm_ops);  -- Full-text search
CREATE INDEX idx_entities_config ON entities USING GIN(config);  -- JSONB search

-- ==================================================
-- DEPLOYMENTS TABLE
-- Tracks deployment history and rollback capability
-- ==================================================

CREATE TABLE IF NOT EXISTS deployments (
    deployment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,

    -- Deployment details
    version VARCHAR(50) NOT NULL,
    environment VARCHAR(50) NOT NULL CHECK (environment IN (
        'development',
        'staging',
        'production',
        'testing'
    )),

    -- Configuration at deployment time
    config_snapshot JSONB NOT NULL,
    parameters_snapshot JSONB,

    -- Status tracking
    status VARCHAR(50) NOT NULL CHECK (status IN (
        'pending',
        'deploying',
        'active',
        'inactive',
        'failed',
        'rolled_back'
    )),

    -- Deployment metadata
    deployed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deployed_by VARCHAR(255) NOT NULL,
    deployment_method VARCHAR(50),  -- 'manual', 'automated', 'ci_cd'

    -- Rollback tracking
    rolled_back_at TIMESTAMP WITH TIME ZONE,
    rolled_back_by VARCHAR(255),
    rollback_reason TEXT,
    previous_deployment_id UUID REFERENCES deployments(deployment_id),

    -- Health and monitoring
    health_checks JSONB DEFAULT '[]',
    last_health_check TIMESTAMP WITH TIME ZONE,
    error_logs TEXT,

    -- Performance during deployment
    deployment_duration_seconds INTEGER,
    validation_results JSONB,

    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for deployments
CREATE INDEX idx_deployments_entity ON deployments(entity_id);
CREATE INDEX idx_deployments_status ON deployments(status);
CREATE INDEX idx_deployments_environment ON deployments(environment);
CREATE INDEX idx_deployments_active ON deployments(entity_id, status) WHERE status = 'active';
CREATE INDEX idx_deployments_deployed_at ON deployments(deployed_at DESC);

-- ==================================================
-- SWAPS TABLE
-- Tracks hot-swap operations and their outcomes
-- ==================================================

CREATE TABLE IF NOT EXISTS swaps (
    swap_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Swap operation details
    from_entity_id UUID NOT NULL REFERENCES entities(entity_id),
    to_entity_id UUID NOT NULL REFERENCES entities(entity_id),
    from_deployment_id UUID REFERENCES deployments(deployment_id),
    to_deployment_id UUID NOT NULL REFERENCES deployments(deployment_id),

    -- Swap metadata
    swap_type VARCHAR(50) NOT NULL CHECK (swap_type IN (
        'manual',
        'scheduled',
        'automatic',
        'emergency',
        'rollback'
    )),
    reason TEXT,

    -- Status tracking
    status VARCHAR(50) NOT NULL CHECK (status IN (
        'initiated',
        'in_progress',
        'completed',
        'failed',
        'partially_completed',
        'rolled_back'
    )),

    -- Timing
    initiated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,

    -- Execution details
    initiated_by VARCHAR(255) NOT NULL,
    approved_by VARCHAR(255),
    execution_method VARCHAR(50),

    -- Validation and testing
    pre_swap_validation JSONB,
    post_swap_validation JSONB,
    validation_passed BOOLEAN,

    -- Impact tracking
    affected_systems TEXT[],
    downtime_seconds INTEGER DEFAULT 0,

    -- Results
    success BOOLEAN,
    error_message TEXT,
    logs TEXT,

    -- Rollback capability
    can_rollback BOOLEAN DEFAULT TRUE,
    rolled_back_at TIMESTAMP WITH TIME ZONE,
    rollback_reason TEXT,

    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for swaps
CREATE INDEX idx_swaps_from_entity ON swaps(from_entity_id);
CREATE INDEX idx_swaps_to_entity ON swaps(to_entity_id);
CREATE INDEX idx_swaps_status ON swaps(status);
CREATE INDEX idx_swaps_type ON swaps(swap_type);
CREATE INDEX idx_swaps_initiated_at ON swaps(initiated_at DESC);
CREATE INDEX idx_swaps_success ON swaps(success) WHERE status = 'completed';

-- ==================================================
-- PERFORMANCE_METRICS TABLE
-- Detailed performance tracking for deployed entities
-- ==================================================

CREATE TABLE IF NOT EXISTS performance_metrics (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    deployment_id UUID REFERENCES deployments(deployment_id),

    -- Timestamp
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Performance metrics
    execution_count INTEGER DEFAULT 0,
    avg_latency_ms NUMERIC(10, 3),
    p50_latency_ms NUMERIC(10, 3),
    p95_latency_ms NUMERIC(10, 3),
    p99_latency_ms NUMERIC(10, 3),
    max_latency_ms NUMERIC(10, 3),

    -- Success/failure tracking
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    timeout_count INTEGER DEFAULT 0,
    success_rate NUMERIC(5, 4),

    -- Resource usage
    avg_cpu_percent NUMERIC(5, 2),
    max_cpu_percent NUMERIC(5, 2),
    avg_memory_mb NUMERIC(10, 2),
    max_memory_mb NUMERIC(10, 2),

    -- Trading performance (if applicable)
    sharpe_ratio NUMERIC(10, 6),
    win_rate NUMERIC(5, 4),
    total_return NUMERIC(15, 6),
    max_drawdown NUMERIC(15, 6),
    profit_factor NUMERIC(10, 4),

    -- Custom metrics (flexible)
    custom_metrics JSONB DEFAULT '{}',

    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance_metrics
CREATE INDEX idx_perf_entity ON performance_metrics(entity_id);
CREATE INDEX idx_perf_deployment ON performance_metrics(deployment_id);
CREATE INDEX idx_perf_recorded_at ON performance_metrics(recorded_at DESC);
CREATE INDEX idx_perf_period ON performance_metrics(period_start, period_end);
CREATE INDEX idx_perf_success_rate ON performance_metrics(success_rate DESC);

-- ==================================================
-- EVENTS TABLE
-- Audit log for all significant events
-- ==================================================

CREATE TABLE IF NOT EXISTS events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Event classification
    event_type VARCHAR(100) NOT NULL,
    event_category VARCHAR(50) NOT NULL CHECK (event_category IN (
        'entity_lifecycle',
        'deployment',
        'swap',
        'performance',
        'health',
        'error',
        'audit'
    )),
    severity VARCHAR(20) NOT NULL CHECK (severity IN (
        'debug',
        'info',
        'warning',
        'error',
        'critical'
    )),

    -- Related entities
    entity_id UUID REFERENCES entities(entity_id),
    deployment_id UUID REFERENCES deployments(deployment_id),
    swap_id UUID REFERENCES swaps(swap_id),

    -- Event details
    message TEXT NOT NULL,
    details JSONB DEFAULT '{}',

    -- Context
    user_id VARCHAR(255),
    source VARCHAR(255),  -- Which service generated the event

    -- Timestamp
    occurred_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for events
CREATE INDEX idx_events_entity ON events(entity_id);
CREATE INDEX idx_events_deployment ON events(deployment_id);
CREATE INDEX idx_events_swap ON events(swap_id);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_category ON events(event_category);
CREATE INDEX idx_events_severity ON events(severity);
CREATE INDEX idx_events_occurred_at ON events(occurred_at DESC);
CREATE INDEX idx_events_details ON events USING GIN(details);

-- ==================================================
-- DEPENDENCIES TABLE
-- Track dependencies between entities
-- ==================================================

CREATE TABLE IF NOT EXISTS dependencies (
    dependency_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Relationship
    entity_id UUID NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    depends_on_entity_id UUID NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,

    -- Dependency type
    dependency_type VARCHAR(50) NOT NULL CHECK (dependency_type IN (
        'required',
        'optional',
        'recommended',
        'conflicts_with'
    )),

    -- Version constraints
    min_version VARCHAR(50),
    max_version VARCHAR(50),

    -- Status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN (
        'active',
        'inactive',
        'broken'
    )),

    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Prevent circular dependencies at DB level (partial check)
    UNIQUE(entity_id, depends_on_entity_id)
);

-- Indexes for dependencies
CREATE INDEX idx_deps_entity ON dependencies(entity_id);
CREATE INDEX idx_deps_depends_on ON dependencies(depends_on_entity_id);
CREATE INDEX idx_deps_type ON dependencies(dependency_type);
CREATE INDEX idx_deps_status ON dependencies(status);

-- ==================================================
-- TRIGGERS
-- ==================================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to all tables with updated_at
CREATE TRIGGER update_entities_updated_at BEFORE UPDATE ON entities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_deployments_updated_at BEFORE UPDATE ON deployments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_swaps_updated_at BEFORE UPDATE ON swaps
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dependencies_updated_at BEFORE UPDATE ON dependencies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==================================================
-- VIEWS
-- ==================================================

-- Active deployments view
CREATE OR REPLACE VIEW active_deployments AS
SELECT
    d.deployment_id,
    d.entity_id,
    e.name AS entity_name,
    e.type AS entity_type,
    d.version,
    d.environment,
    d.status,
    d.deployed_at,
    d.deployed_by
FROM deployments d
JOIN entities e ON d.entity_id = e.entity_id
WHERE d.status = 'active'
  AND e.deleted_at IS NULL;

-- Entity health summary view
CREATE OR REPLACE VIEW entity_health_summary AS
SELECT
    e.entity_id,
    e.name,
    e.type,
    e.status,
    e.health_status,
    d.deployment_id,
    d.environment,
    pm.success_rate,
    pm.avg_latency_ms,
    e.updated_at
FROM entities e
LEFT JOIN deployments d ON e.entity_id = d.entity_id AND d.status = 'active'
LEFT JOIN LATERAL (
    SELECT
        success_rate,
        avg_latency_ms
    FROM performance_metrics
    WHERE entity_id = e.entity_id
    ORDER BY recorded_at DESC
    LIMIT 1
) pm ON TRUE
WHERE e.deleted_at IS NULL;

-- ==================================================
-- GRANTS
-- ==================================================

-- Grant permissions to library service user (will be created in next script)
-- This is a placeholder - actual user will be created in 02_users.sql

-- ==================================================
-- COMMENTS
-- ==================================================

COMMENT ON TABLE entities IS 'Registry of all ML entities (strategies, pipelines, models)';
COMMENT ON TABLE deployments IS 'Deployment history and tracking';
COMMENT ON TABLE swaps IS 'Hot-swap operation tracking';
COMMENT ON TABLE performance_metrics IS 'Performance metrics for deployed entities';
COMMENT ON TABLE events IS 'Audit log of all significant events';
COMMENT ON TABLE dependencies IS 'Dependencies between entities';

COMMENT ON COLUMN entities.config IS 'Entity configuration in JSON format';
COMMENT ON COLUMN entities.parameters IS 'Runtime parameters in JSON format';
COMMENT ON COLUMN entities.tags IS 'Array of tags for categorization and search';
COMMENT ON COLUMN entities.deleted_at IS 'Soft delete timestamp';

-- ==================================================
-- END OF SCHEMA
-- ==================================================
