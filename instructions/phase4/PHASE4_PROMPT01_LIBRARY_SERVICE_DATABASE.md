# PHASE 4 - PROMPT 01: Library Service Database Setup
# Comprehensive PostgreSQL Registry Implementation

**Task ID**: PHASE4_PROMPT01
**Estimated Time**: 2-3 hours
**Component**: Library Service Database (PostgreSQL)

---

## 🎯 OBJECTIVE

**Create a COMPREHENSIVE PostgreSQL database for the Library Service registry.**

This includes:
- Full PostgreSQL 16 installation (official image)
- Complete database schema with ALL entities
- Comprehensive indexes for performance
- Connection pooling and optimization
- Health monitoring and logging
- Backup configuration
- Full testing before integration

**This is the FOUNDATION for all ML Library functionality. No shortcuts.**

---

## ⚠️ MANDATORY PRINCIPLES

### Component Isolation
- **FIX ERRORS WITHIN THIS COMPONENT ONLY**
- Do NOT modify other services
- Do NOT change NATS, backend services, or frontend
- PostgreSQL configuration stays within PostgreSQL scope

### Comprehensive Implementation
- ✅ FULL installation (not minimal)
- ✅ ALL configuration options (not just basics)
- ✅ ALL indexes and constraints (not just primary keys)
- ✅ COMPLETE testing (not just health check)
- ✅ FULL documentation (not brief notes)

### Official Sources Only
- PostgreSQL: https://hub.docker.com/_/postgres (Official Image)
- Extensions from official PostgreSQL channels only
- No custom/modified versions

---

## 📋 VALIDATION GATE

**Before starting, verify Phase 3 is complete:**

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker

# 1. Backend services must be running
docker-compose -f docker-compose.base.yml -f docker-compose.apps.yml ps | grep -E "Up|healthy"

# 2. At least 12 services healthy
HEALTHY=$(docker-compose -f docker-compose.base.yml -f docker-compose.apps.yml ps --services --filter "status=running" | wc -l)
echo "Healthy services: $HEALTHY (need 12+)"

# 3. No PostgreSQL service exists yet (we're creating it)
! docker ps | grep -q postgres-library && echo "✅ No conflicts" || echo "❌ Library DB already exists"
```

**STOP if validation fails. Complete previous phase first.**

---

## 🏗️ IMPLEMENTATION

### STEP 1: Create Database Directory Structure

```bash
cd C:\ClaudeDesktop_Projects\Trade2026

# Create data directory for PostgreSQL
mkdir -p data/postgres-library

# Create backup directory
mkdir -p data/postgres-library/backups

# Create init scripts directory
mkdir -p infrastructure/docker/init-scripts/postgres-library

# Create config directory
mkdir -p config/postgres

# Verify creation
ls -la data/postgres-library/
ls -la infrastructure/docker/init-scripts/postgres-library/
ls -la config/postgres/
```

**COMPONENT TEST 1**: Directory structure created
```bash
# Must all exist
test -d data/postgres-library && echo "✅ Data dir exists" || echo "❌ FAILED"
test -d data/postgres-library/backups && echo "✅ Backup dir exists" || echo "❌ FAILED"
test -d infrastructure/docker/init-scripts/postgres-library && echo "✅ Init scripts dir exists" || echo "❌ FAILED"
test -d config/postgres && echo "✅ Config dir exists" || echo "❌ FAILED"
```

---

### STEP 2: Create Comprehensive Database Schema

Create the COMPLETE schema with ALL tables, relationships, and constraints:

```bash
cat > infrastructure/docker/init-scripts/postgres-library/01_schema.sql << 'EOF'
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
EOF

echo "✅ Schema file created: infrastructure/docker/init-scripts/postgres-library/01_schema.sql"
```

**COMPONENT TEST 2**: Schema file created and valid SQL
```bash
# Check file exists
test -f infrastructure/docker/init-scripts/postgres-library/01_schema.sql && \
    echo "✅ Schema file exists" || echo "❌ FAILED"

# Check file not empty
test -s infrastructure/docker/init-scripts/postgres-library/01_schema.sql && \
    echo "✅ Schema file has content" || echo "❌ FAILED"

# Count tables (should be 6+)
TABLE_COUNT=$(grep -c "CREATE TABLE" infrastructure/docker/init-scripts/postgres-library/01_schema.sql)
echo "Tables defined: $TABLE_COUNT (need 6+)"
test $TABLE_COUNT -ge 6 && echo "✅ Sufficient tables" || echo "❌ INSUFFICIENT"
```

---

### STEP 3: Create Database Users and Permissions

```bash
cat > infrastructure/docker/init-scripts/postgres-library/02_users.sql << 'EOF'
-- ==================================================
-- User Creation and Permissions
-- ==================================================

-- Create library service user
CREATE USER library_service WITH PASSWORD 'change_in_production_2025';

-- Grant schema usage
GRANT USAGE ON SCHEMA public TO library_service;

-- Grant table permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO library_service;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO library_service;

-- Grant future permissions (for new tables)
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO library_service;
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT USAGE, SELECT ON SEQUENCES TO library_service;

-- Grant execute on functions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO library_service;

-- Create read-only user for monitoring
CREATE USER library_readonly WITH PASSWORD 'readonly_2025';
GRANT USAGE ON SCHEMA public TO library_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO library_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT SELECT ON TABLES TO library_readonly;

-- ==================================================
-- END OF USER SETUP
-- ==================================================
EOF

echo "✅ Users file created: infrastructure/docker/init-scripts/postgres-library/02_users.sql"
```

---

### STEP 4: Create Sample Data for Testing

```bash
cat > infrastructure/docker/init-scripts/postgres-library/03_sample_data.sql << 'EOF'
-- ==================================================
-- Sample Data for Testing
-- ==================================================

-- Insert sample strategy
INSERT INTO entities (
    name, 
    type, 
    category, 
    description, 
    version, 
    author,
    tags,
    status,
    health_status,
    config,
    parameters
) VALUES (
    'default_ml_strategy',
    'strategy',
    'ml_based',
    'Default XGBoost-based trading strategy with RSI, MACD, and Bollinger Bands',
    '1.0.0',
    'Trade2026 Team',
    ARRAY['ml', 'xgboost', 'technical_analysis'],
    'registered',
    'unknown',
    '{"model_type": "xgboost", "features": ["rsi", "macd", "bbands"]}'::jsonb,
    '{"n_estimators": 100, "max_depth": 5, "learning_rate": 0.1}'::jsonb
);

-- Insert sample pipeline
INSERT INTO entities (
    name, 
    type, 
    category, 
    description, 
    version, 
    author,
    tags,
    status,
    health_status,
    config
) VALUES (
    'default_ml_pipeline',
    'pipeline',
    'feature_engineering',
    'Feature engineering pipeline for default ML strategy',
    '1.0.0',
    'Trade2026 Team',
    ARRAY['pipeline', 'features', 'preprocessing'],
    'registered',
    'unknown',
    '{"features": ["RSI", "MACD", "BBands"], "lookback": 20}'::jsonb
);

-- Insert sample event
INSERT INTO events (
    event_type,
    event_category,
    severity,
    entity_id,
    message,
    details,
    source
) VALUES (
    'entity_registered',
    'entity_lifecycle',
    'info',
    (SELECT entity_id FROM entities WHERE name = 'default_ml_strategy'),
    'Default ML strategy registered in library',
    '{"version": "1.0.0", "author": "Trade2026 Team"}'::jsonb,
    'init_script'
);

-- ==================================================
-- END OF SAMPLE DATA
-- ==================================================
EOF

echo "✅ Sample data file created: infrastructure/docker/init-scripts/postgres-library/03_sample_data.sql"
```

---

### STEP 5: Create PostgreSQL Configuration

```bash
cat > config/postgres/postgresql.conf << 'EOF'
# ==================================================
# PostgreSQL Configuration for Library Service
# Performance optimized for registry workload
# ==================================================

# Connection settings
max_connections = 100
superuser_reserved_connections = 3

# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
work_mem = 16MB

# Query planning
random_page_cost = 1.1  # Optimized for SSD
effective_io_concurrency = 200

# Write-ahead log
wal_buffers = 16MB
min_wal_size = 1GB
max_wal_size = 4GB
wal_compression = on

# Checkpoints
checkpoint_completion_target = 0.9
checkpoint_timeout = 10min

# Logging
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = 1000  # Log slow queries (1s+)
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_statement = 'ddl'  # Log all DDL statements

# Query statistics
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all

# Autovacuum (important for JSONB tables)
autovacuum = on
autovacuum_naptime = 1min
autovacuum_vacuum_threshold = 50
autovacuum_analyze_threshold = 50

# ==================================================
# END OF CONFIGURATION
# ==================================================
EOF

echo "✅ Config file created: config/postgres/postgresql.conf"
```

---

### STEP 6: Create Docker Compose Service

```bash
cat > infrastructure/docker/docker-compose.library-db.yml << 'EOF'
version: '3.8'

services:
  postgres-library:
    # Official PostgreSQL image
    # Source: https://hub.docker.com/_/postgres
    # Verified: "Official Image" badge on Docker Hub
    image: postgres:16-alpine
    
    container_name: postgres-library
    hostname: postgres-library
    
    # Environment variables
    environment:
      POSTGRES_DB: library
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres_admin_2025
      PGDATA: /var/lib/postgresql/data
      
    # Ports
    ports:
      - "5433:5432"  # External:Internal (avoid conflict with other PostgreSQL)
    
    # Volumes
    volumes:
      # Data persistence
      - ../../data/postgres-library:/var/lib/postgresql/data
      
      # Init scripts (run in alphabetical order)
      - ../../infrastructure/docker/init-scripts/postgres-library:/docker-entrypoint-initdb.d
      
      # Configuration
      - ../../config/postgres/postgresql.conf:/etc/postgresql/postgresql.conf
      
      # Backups
      - ../../data/postgres-library/backups:/backups
    
    # Command - use custom config
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    
    # Health check
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d library"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    
    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
    
    # Restart policy
    restart: unless-stopped
    
    # Logging
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    
    # Networks
    networks:
      - trade2026-backend

networks:
  trade2026-backend:
    external: true
    name: trade2026-backend

EOF

echo "✅ Docker Compose file created: infrastructure/docker/docker-compose.library-db.yml"
```

**COMPONENT TEST 3**: Docker Compose file valid
```bash
# Validate compose file syntax
cd infrastructure/docker
docker-compose -f docker-compose.library-db.yml config > /dev/null 2>&1 && \
    echo "✅ Compose file valid" || echo "❌ SYNTAX ERROR"

# Check service defined
grep -q "postgres-library:" docker-compose.library-db.yml && \
    echo "✅ Service defined" || echo "❌ SERVICE MISSING"
```

---

## 🧪 COMPREHENSIVE COMPONENT TESTING

### TEST 1: Start PostgreSQL Service

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker

# Start PostgreSQL
echo "Starting PostgreSQL library database..."
docker-compose -f docker-compose.library-db.yml up -d

# Wait for health check to pass
echo "Waiting for PostgreSQL to be healthy..."
sleep 10

# Check container status
docker ps | grep postgres-library
```

**Expected output**: Container running and healthy

**If Failed:**
- Check logs: `docker logs postgres-library`
- Verify port 5433 not in use: `netstat -an | grep 5433`
- Check data directory permissions
- **Fix within PostgreSQL component only**

---

### TEST 2: Connection Test

```bash
# Test connection from host
echo "Testing PostgreSQL connection..."

# Using psql (if available)
psql -h localhost -p 5433 -U postgres -d library -c "SELECT version();" 2>/dev/null || \
    echo "⚠️ psql not available on host (this is OK)"

# Using docker exec
docker exec postgres-library psql -U postgres -d library -c "SELECT version();"
```

**Expected**: Version information displayed

---

### TEST 3: Schema Validation

```bash
echo "Validating database schema..."

# Check all tables created
docker exec postgres-library psql -U postgres -d library -c "
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_type = 'BASE TABLE'
ORDER BY table_name;
"

# Expected tables:
# - entities
# - deployments
# - swaps
# - performance_metrics
# - events
# - dependencies

# Count tables
TABLE_COUNT=$(docker exec postgres-library psql -U postgres -d library -t -c "
SELECT COUNT(*) 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_type = 'BASE TABLE';
" | tr -d ' ')

echo "Tables created: $TABLE_COUNT"
test $TABLE_COUNT -ge 6 && echo "✅ All tables created" || echo "❌ MISSING TABLES"
```

---

### TEST 4: Index Validation

```bash
echo "Validating indexes..."

# Count indexes
INDEX_COUNT=$(docker exec postgres-library psql -U postgres -d library -t -c "
SELECT COUNT(*) 
FROM pg_indexes 
WHERE schemaname = 'public';
" | tr -d ' ')

echo "Indexes created: $INDEX_COUNT"
test $INDEX_COUNT -ge 20 && echo "✅ Sufficient indexes" || echo "⚠️ May need more indexes"

# List indexes
docker exec postgres-library psql -U postgres -d library -c "
SELECT tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
"
```

---

### TEST 5: User Permissions Test

```bash
echo "Testing user permissions..."

# Test library_service user can read
docker exec postgres-library psql -U library_service -d library -c "
SELECT COUNT(*) FROM entities;
"

# Test library_service user can write
docker exec postgres-library psql -U library_service -d library -c "
INSERT INTO entities (name, type, version) 
VALUES ('test_entity', 'strategy', '1.0.0') 
RETURNING entity_id, name;
"

# Test readonly user can read but not write
docker exec postgres-library psql -U library_readonly -d library -c "
SELECT COUNT(*) FROM entities;
" && echo "✅ Readonly can read"

# This should fail (and that's correct)
docker exec postgres-library psql -U library_readonly -d library -c "
INSERT INTO entities (name, type, version) 
VALUES ('should_fail', 'strategy', '1.0.0');
" 2>&1 | grep -q "permission denied" && \
    echo "✅ Readonly correctly denied write" || \
    echo "❌ Readonly should not be able to write"
```

---

### TEST 6: Sample Data Validation

```bash
echo "Validating sample data..."

# Check sample entities loaded
ENTITY_COUNT=$(docker exec postgres-library psql -U postgres -d library -t -c "
SELECT COUNT(*) FROM entities;
" | tr -d ' ')

echo "Sample entities: $ENTITY_COUNT"
test $ENTITY_COUNT -ge 2 && echo "✅ Sample data loaded" || echo "⚠️ Sample data may not have loaded"

# Display sample data
docker exec postgres-library psql -U postgres -d library -c "
SELECT entity_id, name, type, version, status 
FROM entities;
"
```

---

### TEST 7: Performance Test

```bash
echo "Running performance tests..."

# Test INSERT performance
docker exec postgres-library psql -U postgres -d library -c "
EXPLAIN ANALYZE
INSERT INTO entities (name, type, category, version, status)
VALUES ('perf_test', 'strategy', 'test', '1.0.0', 'registered');
"

# Test SELECT performance with index
docker exec postgres-library psql -U postgres -d library -c "
EXPLAIN ANALYZE
SELECT * FROM entities WHERE type = 'strategy' AND status = 'registered';
"

# Test JOIN performance
docker exec postgres-library psql -U postgres -d library -c "
EXPLAIN ANALYZE
SELECT e.name, d.status, d.deployed_at
FROM entities e
LEFT JOIN deployments d ON e.entity_id = d.entity_id
WHERE e.type = 'strategy';
"
```

---

### TEST 8: JSONB Query Test

```bash
echo "Testing JSONB query capabilities..."

# Test JSONB contains
docker exec postgres-library psql -U postgres -d library -c "
SELECT name, config
FROM entities
WHERE config @> '{\"model_type\": \"xgboost\"}'::jsonb;
"

# Test JSONB extract
docker exec postgres-library psql -U postgres -d library -c "
SELECT name, 
       config->>'model_type' as model_type,
       parameters->>'learning_rate' as learning_rate
FROM entities
WHERE type = 'strategy';
"
```

---

### TEST 9: Trigger Test

```bash
echo "Testing triggers..."

# Update an entity and check updated_at changes
docker exec postgres-library psql -U postgres -d library -c "
UPDATE entities 
SET description = 'Updated description'
WHERE name = 'default_ml_strategy'
RETURNING name, updated_at;
"

# Verify updated_at was modified
docker exec postgres-library psql -U postgres -d library -c "
SELECT name, created_at, updated_at
FROM entities
WHERE name = 'default_ml_strategy';
"
```

---

### TEST 10: View Test

```bash
echo "Testing views..."

# Test active_deployments view
docker exec postgres-library psql -U postgres -d library -c "
SELECT * FROM active_deployments;
"

# Test entity_health_summary view
docker exec postgres-library psql -U postgres -d library -c "
SELECT * FROM entity_health_summary;
"
```

---

## 🔗 INTEGRATION TESTING

### INTEGRATION TEST 1: Connect from Another Container

```bash
echo "Testing connection from another container..."

# Start a test container
docker run --rm --network trade2026-backend postgres:16-alpine \
    psql -h postgres-library -p 5432 -U postgres -d library \
    -c "SELECT 'Connection from external container successful!' AS test;"
```

**Expected**: Connection successful message

---

### INTEGRATION TEST 2: Connection Pooling Test

```bash
echo "Testing concurrent connections..."

# Open multiple connections
for i in {1..10}; do
    docker exec postgres-library psql -U postgres -d library -c "
    SELECT pg_sleep(1), 'Connection $i' AS conn;
    " &
done

wait

echo "✅ Concurrent connections test complete"

# Check active connections
docker exec postgres-library psql -U postgres -d library -c "
SELECT count(*) as active_connections FROM pg_stat_activity;
"
```

---

### INTEGRATION TEST 3: Backup Test

```bash
echo "Testing backup functionality..."

# Create backup
docker exec postgres-library pg_dump -U postgres library > \
    data/postgres-library/backups/test_backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup created
ls -lh data/postgres-library/backups/

# Check backup is valid SQL
head -20 data/postgres-library/backups/test_backup_*.sql
```

---

## 🚀 DEPLOYMENT

### DEPLOY 1: Add to Main Compose

```bash
# Update main docker-compose to include library database
cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker

# Check if library database is listed in main compose
if ! grep -q "docker-compose.library-db.yml" docker-compose.yml 2>/dev/null; then
    echo "⚠️ Need to add library DB to main compose file"
    echo ""
    echo "Add this to docker-compose.yml includes section:"
    echo "  - docker-compose.library-db.yml"
fi
```

---

### DEPLOY 2: Verify Deployment

```bash
# Restart with full stack
docker-compose -f docker-compose.base.yml \
               -f docker-compose.apps.yml \
               -f docker-compose.library-db.yml \
               up -d

# Check all services
docker-compose -f docker-compose.base.yml \
               -f docker-compose.apps.yml \
               -f docker-compose.library-db.yml \
               ps
```

---

## ✅ FINAL VALIDATION

### Validation Checklist

```bash
echo "=== FINAL VALIDATION CHECKLIST ==="

# 1. Container running
docker ps | grep postgres-library && echo "✅ Container running" || echo "❌ FAILED"

# 2. Health check passing
docker inspect postgres-library | grep -q "\"healthy\"" && \
    echo "✅ Health check passing" || echo "❌ UNHEALTHY"

# 3. All tables created
TABLE_COUNT=$(docker exec postgres-library psql -U postgres -d library -t -c "
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
" | tr -d ' ')
test $TABLE_COUNT -ge 6 && echo "✅ All tables created ($TABLE_COUNT)" || echo "❌ MISSING TABLES"

# 4. Indexes created
INDEX_COUNT=$(docker exec postgres-library psql -U postgres -d library -t -c "
SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';
" | tr -d ' ')
test $INDEX_COUNT -ge 20 && echo "✅ Indexes created ($INDEX_COUNT)" || echo "⚠️ FEW INDEXES"

# 5. Users created
USER_COUNT=$(docker exec postgres-library psql -U postgres -d library -t -c "
SELECT COUNT(*) FROM pg_user WHERE usename IN ('library_service', 'library_readonly');
" | tr -d ' ')
test $USER_COUNT -eq 2 && echo "✅ Users created" || echo "❌ MISSING USERS"

# 6. Sample data loaded
ENTITY_COUNT=$(docker exec postgres-library psql -U postgres -d library -t -c "
SELECT COUNT(*) FROM entities;
" | tr -d ' ')
test $ENTITY_COUNT -ge 2 && echo "✅ Sample data loaded ($ENTITY_COUNT entities)" || echo "⚠️ NO SAMPLE DATA"

# 7. No errors in logs
ERROR_COUNT=$(docker logs postgres-library 2>&1 | grep -i "error\|fatal" | wc -l)
test $ERROR_COUNT -eq 0 && echo "✅ No errors in logs" || echo "⚠️ $ERROR_COUNT errors found"

# 8. Can connect from outside
docker run --rm --network trade2026-backend postgres:16-alpine \
    psql -h postgres-library -p 5432 -U postgres -d library -c "SELECT 1;" > /dev/null 2>&1 && \
    echo "✅ External connection works" || echo "❌ CONNECTION FAILED"

echo ""
echo "=== VALIDATION COMPLETE ==="
```

---

## 📊 MONITOR FOR 5 MINUTES

```bash
echo "Monitoring PostgreSQL for 5 minutes..."
echo "Press Ctrl+C to stop early if all looks good"

# Monitor logs in real-time
timeout 300 docker logs postgres-library -f 2>&1 | grep -i "ready\|started\|error\|fatal"

# After 5 minutes, check status
echo ""
echo "=== 5 MINUTE CHECK ==="
docker ps | grep postgres-library
docker exec postgres-library psql -U postgres -d library -c "SELECT COUNT(*) FROM entities;"
docker exec postgres-library psql -U postgres -d library -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## 📝 DOCUMENTATION

Create session documentation:

```bash
cat > C:\ClaudeDesktop_Projects\Trade2026\docs\PHASE4_PROMPT01_COMPLETION.md << 'EOF'
# Phase 4 - Prompt 01 Completion Report

**Date**: $(date +%Y-%m-%d)
**Task**: PostgreSQL Library Database Setup
**Status**: COMPLETE ✅

## What Was Implemented

### Database Infrastructure
- PostgreSQL 16 Alpine (official image)
- Comprehensive schema (6 tables)
- 20+ indexes for performance
- Full-text search capabilities
- JSONB support for flexible config

### Tables Created
1. **entities** - Registry of all ML entities
2. **deployments** - Deployment tracking
3. **swaps** - Hot-swap operations
4. **performance_metrics** - Performance tracking
5. **events** - Audit log
6. **dependencies** - Entity dependencies

### Features Implemented
- ✅ User management (service + readonly)
- ✅ Triggers for auto-update timestamps
- ✅ Views for common queries
- ✅ Sample data for testing
- ✅ Backup capability
- ✅ Health monitoring
- ✅ Performance optimization

## Testing Results

All tests passed:
- ✅ Container health check
- ✅ Schema validation
- ✅ Index creation
- ✅ User permissions
- ✅ Sample data loaded
- ✅ Performance benchmarks
- ✅ JSONB queries
- ✅ Triggers working
- ✅ Views accessible
- ✅ External connection
- ✅ Concurrent connections
- ✅ Backup capability

## Connection Details

- **Host**: localhost
- **Port**: 5433 (external)
- **Database**: library
- **Admin User**: postgres / postgres_admin_2025
- **Service User**: library_service / change_in_production_2025
- **Readonly User**: library_readonly / readonly_2025
- **Internal hostname**: postgres-library (in Docker network)

## Next Steps

Ready for PHASE4_PROMPT02: Library Service Core API
- FastAPI application
- CRUD operations
- Entity management
- Deployment lifecycle

## Issues Encountered

[Document any issues and resolutions]

## Lessons Learned

[Document any insights gained]

EOF

echo "✅ Documentation created"
```

---

## ✅ SUCCESS CRITERIA

This task is complete when ALL of the following are true:

- [ ] PostgreSQL container running and healthy
- [ ] All 6 tables created with proper schema
- [ ] 20+ indexes created and functional
- [ ] Users created with correct permissions
- [ ] Sample data loaded successfully
- [ ] Health checks passing
- [ ] Can connect from external containers
- [ ] No errors in logs
- [ ] Performance tests show good query times
- [ ] Backup capability tested
- [ ] System stable for 5+ minutes
- [ ] Documentation complete

---

## 🚨 TROUBLESHOOTING

### Issue: Container won't start
**Check**: `docker logs postgres-library`
**Fix**: Verify port 5433 is available, check data directory permissions

### Issue: Schema not created
**Check**: Look in logs for init script errors
**Fix**: Verify SQL syntax in init scripts, check file permissions

### Issue: Can't connect
**Check**: Network configuration, firewall
**Fix**: Ensure container on trade2026-backend network

### Issue: Slow queries
**Check**: EXPLAIN ANALYZE output
**Fix**: Add missing indexes, adjust configuration

**Remember: Fix errors WITHIN PostgreSQL component only. Do not modify other services.**

---

**NEXT PROMPT**: PHASE4_PROMPT02_LIBRARY_CORE_API.md
**Estimated Time**: 3-4 hours
