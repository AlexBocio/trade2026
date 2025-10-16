# Task 04: Configure Base Docker Compose

**Phase**: 1 - Foundation
**Priority**: P0-Critical
**Estimated Time**: 2 hours
**Dependencies**: Task 01-03 (Directory, Networks, Core Services)
**Created**: 2025-10-14
**Assigned To**: Claude Code

---

# 🛑 STOP - READ THIS FIRST 🛑

## MANDATORY READING BEFORE ANY CODE EXECUTION

**Claude Code**: You MUST read these files IN FULL before starting any work. This is NON-NEGOTIABLE.

### 1. MASTER_GUIDELINES.md (CRITICAL - READ FIRST)
**Location**: `C:\ClaudeDesktop_Projects\ClaudeKnowledge\MASTER_GUIDELINES.md`

**YOU MUST READ THESE SECTIONS** (use file_read tool):
- [ ] **New Session Startup Protocol** - How to begin ANY session
- [ ] **Core Development Rules** - Component Isolation, Read Before Write, Backup Critical Files
- [ ] **Configuration Management Pattern** - Critical for this task
- [ ] **6-Phase Mandatory Workflow** - EVERY task follows this workflow
- [ ] **File Operations** - Read before write, validation
- [ ] **Testing & Validation Rules** - How to validate your work

**Why This Matters**: This task creates critical configuration files. The guidelines tell you:
- ✅ How to manage configuration properly
- ✅ How to create helper scripts
- ✅ Token budget management
- ✅ Testing requirements
- ✅ When to stop and ask for help

**Estimated Time**: 10 minutes to read the relevant sections

### 2. Project Context (MUST READ AFTER GUIDELINES)
**Location**: `C:\ClaudeDesktop_Projects\Trade2026\MASTER_PLAN.md`
- [ ] Read the full overview

**Estimated Time**: 5 minutes

---

## ⚠️ CONSEQUENCES OF NOT READING GUIDELINES

If you skip reading MASTER_GUIDELINES.md, you will:
- ❌ Not follow Configuration Management Pattern
- ❌ Not follow 6-Phase Workflow (task will fail)
- ❌ Skip testing steps (scripts won't work)
- ❌ Make configuration mistakes
- ❌ Miss critical documentation requirements

**The guidelines exist to prevent failures. READ THEM FIRST.**

---

## ✅ CHECKLIST BEFORE PROCEEDING

**I confirm I have read and understood**:
- [ ] MASTER_GUIDELINES.md - New Session Startup Protocol
- [ ] MASTER_GUIDELINES.md - Core Development Rules
- [ ] MASTER_GUIDELINES.md - Configuration Management Pattern
- [ ] MASTER_GUIDELINES.md - 6-Phase Mandatory Workflow
- [ ] MASTER_GUIDELINES.md - File Operations
- [ ] MASTER_GUIDELINES.md - Testing & Validation Rules
- [ ] MASTER_PLAN.md - Project overview

**Total Reading Time**: ~15 minutes

**Only proceed to next section after completing this checklist.**

---

# 🚦 VALIDATION GATE - VERIFY TASKS 01-03

## MANDATORY: Validate ALL Previous Tasks Before Starting

**STOP**: Before starting Task 04, you MUST verify Tasks 01-03 are complete and working.

### Prerequisites Validation

#### Task 01: Directory Structure Validation
```bash
cd C:\ClaudeDesktop_Projects\Trade2026

echo "Validating Task 01: Directory Structure..."

# Verify critical directories for Task 04
test -d infrastructure/docker && echo "✅ infrastructure/docker/" || echo "❌ MISSING"
test -d scripts && echo "✅ scripts/" || echo "❌ MISSING"
test -d data && echo "✅ data/" || echo "❌ MISSING"
test -d config && echo "✅ config/" || echo "❌ MISSING"

test -f DIRECTORY_STRUCTURE.md && echo "✅ DIRECTORY_STRUCTURE.md" || echo "❌ MISSING"

echo "✅ Task 01 validated"
```

#### Task 02: Docker Networks Validation
```bash
echo "\nValidating Task 02: Docker Networks..."

# Verify all 3 networks exist
docker network ls | grep trade2026-frontend > /dev/null && echo "✅ trade2026-frontend" || echo "❌ MISSING"
docker network ls | grep trade2026-lowlatency > /dev/null && echo "✅ trade2026-lowlatency" || echo "❌ MISSING"
docker network ls | grep trade2026-backend > /dev/null && echo "✅ trade2026-backend" || echo "❌ MISSING"

echo "✅ Task 02 validated"
```

#### Task 03: Core Services Validation
```bash
echo "\nValidating Task 03: Core Infrastructure Services..."

cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker

# Check if docker-compose.core.yml exists
test -f docker-compose.core.yml && echo "✅ docker-compose.core.yml exists" || echo "❌ MISSING"

# Check if services are running
echo "\nChecking service health..."
docker ps --format '{{.Names}}\t{{.Status}}' | grep -E 'nats|valkey|questdb|clickhouse|seaweedfs|opensearch|authn|opa'

# Count healthy services
HEALTHY_COUNT=$(docker ps --format '{{.Names}}\t{{.Status}}' | grep -E 'nats|valkey|questdb|clickhouse|seaweedfs|opensearch|authn|opa' | grep -i 'up' | wc -l)

if [ "$HEALTHY_COUNT" -eq 8 ]; then
    echo "✅ All 8 core services running"
else
    echo "❌ Only $HEALTHY_COUNT/8 services running"
    echo "Run: docker-compose -f docker-compose.core.yml ps"
    exit 1
fi

# Quick health check on key services
curl -s http://localhost:8222/healthz > /dev/null && echo "✅ NATS healthy" || echo "❌ NATS unhealthy"
docker exec valkey valkey-cli ping > /dev/null 2>&1 && echo "✅ Valkey healthy" || echo "❌ Valkey unhealthy"
curl -s http://localhost:9000/ > /dev/null && echo "✅ QuestDB healthy" || echo "❌ QuestDB unhealthy"
curl -s http://localhost:8123/ping > /dev/null && echo "✅ ClickHouse healthy" || echo "❌ ClickHouse unhealthy"

echo "✅ Task 03 validated"
```

#### Integration Test: Can Compose Manage Services?
```bash
echo "\nTesting integration: Can compose manage all services?"

cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker

# Test compose config is valid
echo "Validating compose configuration..."
docker-compose -f docker-compose.core.yml config > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Compose config valid"
else
    echo "❌ Compose config has errors"
    docker-compose -f docker-compose.core.yml config
    exit 1
fi

# Test compose ps works
docker-compose -f docker-compose.core.yml ps > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Compose can query services"
else
    echo "❌ Compose cannot query services"
    exit 1
fi

echo "✅ Integration validated: Compose can manage services"
```

### Validation Checklist

**Task 01 - Directory Structure**:
- [ ] infrastructure/docker/ exists
- [ ] scripts/ exists  
- [ ] data/ and config/ exist
- [ ] DIRECTORY_STRUCTURE.md exists

**Task 02 - Docker Networks**:
- [ ] trade2026-frontend network exists
- [ ] trade2026-lowlatency network exists
- [ ] trade2026-backend network exists

**Task 03 - Core Services**:
- [ ] docker-compose.core.yml exists
- [ ] All 8 services running (nats, valkey, questdb, clickhouse, seaweedfs, opensearch, authn, opa)
- [ ] NATS health check passing
- [ ] Valkey health check passing
- [ ] QuestDB health check passing
- [ ] ClickHouse health check passing

**Integration - Compose Management**:
- [ ] Compose config validates successfully
- [ ] Compose can query service status
- [ ] No errors in compose commands

### Proceed/Stop Decision

**Run the validation scripts above and answer**:

1. Did ALL Task 01 validations pass? (YES/NO): _____
2. Did ALL Task 02 validations pass? (YES/NO): _____
3. Did ALL Task 03 validations pass? (YES/NO): _____
4. Did integration test pass? (YES/NO): _____
5. Are there ANY error messages? (YES/NO): _____

**Can I proceed to Task 04?**
- ✅ **YES** - All validations passed, no errors → Continue to CRITICAL RULES section
- ❌ **NO** - Something failed → STOP, fix issues, re-run validations

**If ANY validation fails**:
1. ❌ **STOP** - Do NOT proceed with Task 04
2. Review error messages from validation scripts
3. Go back to failed task (01, 02, or 03)
4. Fix the issue
5. Re-run validation scripts
6. Only proceed when ALL validations pass

---

**⚠️ CRITICAL**: Do NOT proceed past this point unless all validations above are complete and passing.

---

## ⚠️ CRITICAL RULES FOR THIS TASK

### Rule 1: Modular Compose Files
Never put everything in one docker-compose.yml. Use modular files that can be composed together.

### Rule 2: Use Include Directive
Docker Compose 3.8+ supports `include:` to combine multiple compose files into one command.

### Rule 3: External Networks
Always reference networks as external (created in Task 02).

### Rule 4: COMPREHENSIVE IMPLEMENTATION - NO SHORTCUTS

**⚠️ MANDATORY**: All implementations must be COMPLETE and COMPREHENSIVE. No abbreviated implementations "to save time".

#### What This Means:

**✅ DO** - Complete Implementations:
- Create ALL compose files (not just master)
- Configure ALL environment variables (not just required)
- Create ALL helper scripts (not just basics)
- Test ALL functionality (not just compose up)
- Document ALL usage (not just quick start)

**❌ DON'T** - Shortcuts/Abbreviated:
- "Quick" compose files that skip details
- "Minimal" .env files with only required vars
- "Basic" scripts that skip error handling
- "Simple" testing that skips edge cases
- "Brief" docs that skip details

#### Specific Requirements:

**Compose Files**:
- Master file includes all modular files
- Every service fully configured
- All environment variables templated
- Comments explain every section

**Helper Scripts**:
- up.sh, down.sh, logs.sh, status.sh all created
- Error handling in every script
- Usage instructions in comments
- Test every script works

**Environment Variables**:
- ALL variables defined (not just critical)
- Organized by component
- Comments explain each variable
- Template shows example values

**Testing**:
- Test each script individually
- Test compose up/down
- Test logs and status commands
- Test with all previous tasks
- Verify no errors

**Documentation**:
- Complete usage guide created
- All commands documented
- Troubleshooting section included
- Examples for common operations

---

## 📋 OBJECTIVE

Create the master Docker Compose configuration that orchestrates all Trade2026 components:
1. Main docker-compose.yml (includes all other files)
2. Environment variable templates
3. Helper scripts for common operations
4. Documentation for docker-compose usage

**Why This Matters**: Single command (`docker-compose up`) to start the entire platform.

---

## 🎯 CONTEXT

### Current State
- ✅ Networks created (trade2026-*)
- ✅ Core services running (8 services)
- ❌ No unified compose file
- ❌ No easy way to start everything

### Target State
- ✅ Master docker-compose.yml that includes:
  - docker-compose.networks.yml
  - docker-compose.core.yml
  - (Future: docker-compose.apps.yml, docker-compose.frontend.yml, docker-compose.library.yml)

### Compose File Structure

```
infrastructure/docker/
├── docker-compose.yml               # MASTER (includes all)
├── docker-compose.networks.yml      # Networks (created Task 02)
├── docker-compose.core.yml          # Core services (created Task 03)
├── docker-compose.apps.yml          # Backend services (Phase 2)
├── docker-compose.frontend.yml      # Frontend (Phase 3)
├── docker-compose.library.yml       # ML Library (Phase 4)
└── .env.template                    # Environment variables
```

---

## ✅ REQUIREMENTS

### Functional Requirements
1. Master docker-compose.yml that includes all modular files
2. Environment variable template
3. Helper scripts (up.sh, down.sh, logs.sh, status.sh)
4. Usage documentation

### Non-Functional Requirements
- **Simplicity**: Single command to start/stop
- **Modularity**: Easy to add/remove components
- **Clarity**: Well-documented for future maintainers

---

## 🔧 IMPLEMENTATION STEPS

### Step 1: Create Master docker-compose.yml
**Goal**: Single file that includes all component compose files

**Actions**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker

# Create master compose file
cat > docker-compose.yml << 'EOF'
version: '3.8'

# Trade2026 Master Docker Compose
# This file orchestrates all platform components
# 
# Usage:
#   docker-compose up -d              # Start all services
#   docker-compose down               # Stop all services
#   docker-compose ps                 # Check status
#   docker-compose logs -f            # View logs
#
# Last Updated: 2025-10-14

# Include all modular compose files
include:
  # Networks (CPGS v1.0 three-lane architecture)
  - path: docker-compose.networks.yml
    
  # Core Infrastructure (8 services)
  # NATS, Valkey, QuestDB, ClickHouse, SeaweedFS, OpenSearch, authn, OPA
  - path: docker-compose.core.yml
    
  # Backend Application Services (Phase 2 - NOT YET CREATED)
  # Uncomment when ready:
  # - path: docker-compose.apps.yml
    
  # Frontend Application (Phase 3 - NOT YET CREATED)
  # Uncomment when ready:
  # - path: docker-compose.frontend.yml
    
  # ML Library & Pipelines (Phase 4 - NOT YET CREATED)
  # Uncomment when ready:
  # - path: docker-compose.library.yml

# No additional services defined here
# All services in modular files
EOF
```

**Validation**:
```bash
cat docker-compose.yml
# Should show master file with include directives
```

**Checklist**:
- [ ] Master docker-compose.yml created
- [ ] Includes networks and core services
- [ ] Future includes commented out
- [ ] Documentation in comments
- [ ] **Phase 1 complete: Master file created** ✅

---

### Step 2: Create Environment Variable Template
**Goal**: Template for environment variables

**Actions**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker

# Create .env.template
cat > .env.template << 'EOF'
# Trade2026 Environment Variables Template
# Copy this file to .env and fill in values
#
# IMPORTANT: .env is in .gitignore - never commit secrets!

# ==========================================
# CORE INFRASTRUCTURE
# ==========================================

# NATS
NATS_URL=nats://nats:4222

# Valkey (Redis-compatible)
VALKEY_URL=redis://valkey:6379
VALKEY_MAX_MEMORY=2gb

# QuestDB
QUESTDB_HTTP=http://questdb:9000
QUESTDB_PG=postgresql://admin:quest@questdb:8812/qdb

# ClickHouse
CLICKHOUSE_HTTP=http://clickhouse:8123
CLICKHOUSE_TCP=clickhouse:9000
CLICKHOUSE_DB=trade2026
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=

# SeaweedFS S3
SEAWEEDFS_S3_ENDPOINT=http://seaweedfs:8333
SEAWEEDFS_ACCESS_KEY=trade2026
SEAWEEDFS_SECRET_KEY=trade2026secret

# OpenSearch
OPENSEARCH_URL=http://opensearch:9200
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=

# Authentication
AUTHN_URL=http://authn:8114
JWT_ISSUER=authn
JWT_AUDIENCE=trade2026
JWT_EXPIRATION=3600

# Authorization
OPA_URL=http://opa:8181

# ==========================================
# BACKEND SERVICES (Phase 2 - Add when ready)
# ==========================================

# Gateway (Market Data)
# GATEWAY_URL=http://gateway:8080

# OMS (Order Management)
# OMS_URL=http://oms:8099

# Risk Service
# RISK_URL=http://risk:8103

# ==========================================
# FRONTEND (Phase 3 - Add when ready)
# ==========================================

# FRONTEND_URL=http://localhost

# ==========================================
# ML LIBRARY (Phase 4 - Add when ready)
# ==========================================

# LIBRARY_URL=http://library:8350

# ==========================================
# EXTERNAL SERVICES (Fill in your API keys)
# ==========================================

# Exchange API Keys
BINANCE_API_KEY=
BINANCE_SECRET=
ALPACA_API_KEY=
ALPACA_SECRET=

# ==========================================
# PATHS (Usually don't need to change)
# ==========================================

# Data directory
DATA_PATH=../../data

# Config directory
CONFIG_PATH=../../config

# Secrets directory
SECRETS_PATH=../../secrets
EOF

# Create actual .env file from template
cp .env.template .env

# Add .env to .gitignore (if not already)
cd C:\ClaudeDesktop_Projects\Trade2026
cat >> .gitignore << 'EOF'

# Environment variables (never commit)
.env
*/.env
EOF
```

**Validation**:
```bash
cat .env.template
cat .env
# Should show environment variable template
```

**Checklist**:
- [ ] .env.template created
- [ ] .env created (copy of template)
- [ ] .gitignore updated
- [ ] All core services have variables
- [ ] **Phase 2 complete: Env vars configured** ✅

---

### Step 3: Create Helper Scripts
**Goal**: Easy commands for common operations

**Actions**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026\scripts

# Create up.sh (start services)
cat > up.sh << 'EOF'
#!/bin/bash
# Start Trade2026 services

set -e

cd "$(dirname "$0")/../infrastructure/docker"

echo "🚀 Starting Trade2026 services..."
docker-compose up -d

echo ""
echo "✅ Services started!"
echo ""
echo "📊 Check status:"
echo "   docker-compose ps"
echo ""
echo "📋 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🌐 Access points:"
echo "   - NATS:        http://localhost:8222"
echo "   - Valkey:      localhost:6379"
echo "   - QuestDB:     http://localhost:9000"
echo "   - ClickHouse:  http://localhost:8123"
echo "   - SeaweedFS:   http://localhost:9333"
echo "   - OpenSearch:  http://localhost:9200"
echo "   - authn:       http://localhost:8114"
echo "   - OPA:         http://localhost:8181"
EOF

# Create down.sh (stop services)
cat > down.sh << 'EOF'
#!/bin/bash
# Stop Trade2026 services

set -e

cd "$(dirname "$0")/../infrastructure/docker"

echo "🛑 Stopping Trade2026 services..."
docker-compose down

echo ""
echo "✅ Services stopped!"
EOF

# Create logs.sh (view logs)
cat > logs.sh << 'EOF'
#!/bin/bash
# View logs for Trade2026 services

cd "$(dirname "$0")/../infrastructure/docker"

if [ -z "$1" ]; then
    # No service specified, show all logs
    echo "📋 Showing logs for all services (Ctrl+C to exit)..."
    docker-compose logs -f
else
    # Show logs for specific service
    echo "📋 Showing logs for $1 (Ctrl+C to exit)..."
    docker-compose logs -f "$1"
fi
EOF

# Create status.sh (check service status)
cat > status.sh << 'EOF'
#!/bin/bash
# Check status of Trade2026 services

cd "$(dirname "$0")/../infrastructure/docker"

echo "📊 Trade2026 Service Status"
echo "======================================"
echo ""

# Check if services are running
docker-compose ps

echo ""
echo "🏥 Health Checks:"
echo "======================================"

# NATS
if curl -s http://localhost:8222/healthz > /dev/null 2>&1; then
    echo "✅ NATS:        Healthy"
else
    echo "❌ NATS:        Unhealthy"
fi

# Valkey
if docker exec valkey valkey-cli ping > /dev/null 2>&1; then
    echo "✅ Valkey:      Healthy"
else
    echo "❌ Valkey:      Unhealthy"
fi

# QuestDB
if curl -s http://localhost:9000/ > /dev/null 2>&1; then
    echo "✅ QuestDB:     Healthy"
else
    echo "❌ QuestDB:     Unhealthy"
fi

# ClickHouse
if curl -s http://localhost:8123/ping > /dev/null 2>&1; then
    echo "✅ ClickHouse:  Healthy"
else
    echo "❌ ClickHouse:  Unhealthy"
fi

# SeaweedFS
if curl -s http://localhost:9333/cluster/status > /dev/null 2>&1; then
    echo "✅ SeaweedFS:   Healthy"
else
    echo "❌ SeaweedFS:   Unhealthy"
fi

# OpenSearch
if curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
    echo "✅ OpenSearch:  Healthy"
else
    echo "❌ OpenSearch:  Unhealthy"
fi

# authn
if curl -s http://localhost:8114/health > /dev/null 2>&1; then
    echo "✅ authn:       Healthy"
else
    echo "❌ authn:       Unhealthy"
fi

# OPA
if curl -s http://localhost:8181/health > /dev/null 2>&1; then
    echo "✅ OPA:         Healthy"
else
    echo "❌ OPA:         Unhealthy"
fi

echo ""
EOF

# Make scripts executable
chmod +x up.sh down.sh logs.sh status.sh
```

**Validation**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026\scripts
ls -la
# Should show 4 executable scripts
```

**Checklist**:
- [ ] up.sh created
- [ ] down.sh created
- [ ] logs.sh created
- [ ] status.sh created
- [ ] All scripts executable
- [ ] **Phase 3 complete: Scripts created** ✅

---

### Step 4: Test Master Compose File
**Goal**: Verify master compose file works correctly

**Actions**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker

# Stop services if running
docker-compose down

# Start using master compose file
docker-compose up -d

# Check all services started
docker-compose ps

# Should show 8 services running
```

**Expected Output**:
```
Creating network "trade2026-frontend" with driver "bridge"
Creating network "trade2026-lowlatency" with driver "bridge"
Creating network "trade2026-backend" with driver "bridge"
Creating nats ... done
Creating valkey ... done
Creating questdb ... done
Creating clickhouse ... done
Creating seaweedfs ... done
Creating opensearch ... done
Creating authn ... done
Creating opa ... done
```

**Validation Commands**:
```bash
# Check status
docker-compose ps

# View logs
docker-compose logs --tail=50

# Check networks
docker network ls | grep trade2026
```

**Checklist**:
- [ ] All services started successfully
- [ ] No error messages
- [ ] Networks created/connected
- [ ] Compose ps shows 8 services
- [ ] **Phase 4 complete: Compose tested** ✅

---

### Step 5: Test Helper Scripts
**Goal**: Verify all helper scripts work

**Actions**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026

# Test status script
bash scripts/status.sh

# Expected: Show service status + health checks

# Test logs script (Ctrl+C after a few seconds)
bash scripts/logs.sh

# Expected: Show streaming logs from all services

# Test logs for specific service
bash scripts/logs.sh nats

# Expected: Show only NATS logs

# Test stop
bash scripts/down.sh

# Expected: All services stopped

# Test start
bash scripts/up.sh

# Expected: All services started with summary
```

**Validation**:
```bash
# After running scripts
docker ps
# Should show 8 containers running
```

**Checklist**:
- [ ] status.sh works correctly
- [ ] logs.sh shows all logs
- [ ] logs.sh <service> shows specific service
- [ ] down.sh stops all services
- [ ] up.sh starts all services
- [ ] **Phase 5 complete: Scripts validated** ✅

---

### Step 6: Create Usage Documentation
**Goal**: Document how to use the compose setup

**Actions**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026\docs\deployment

# Create docker-compose guide
cat > DOCKER_COMPOSE_GUIDE.md << 'EOF'
# Docker Compose Usage Guide

**Last Updated**: 2025-10-14

## Quick Start

### Start All Services
```bash
cd C:\ClaudeDesktop_Projects\Trade2026

# Using script
bash scripts/up.sh

# Or directly
cd infrastructure/docker
docker-compose up -d
```

### Stop All Services
```bash
# Using script
bash scripts/down.sh

# Or directly
cd infrastructure/docker
docker-compose down
```

### Check Status
```bash
# Using script (includes health checks)
bash scripts/status.sh

# Or using docker-compose
cd infrastructure/docker
docker-compose ps
```

### View Logs
```bash
# All services
bash scripts/logs.sh

# Specific service
bash scripts/logs.sh nats

# Or using docker-compose
cd infrastructure/docker
docker-compose logs -f nats
```

---

## Compose File Structure

### Master File
**File**: `infrastructure/docker/docker-compose.yml`

Includes all modular compose files:
- docker-compose.networks.yml (networks)
- docker-compose.core.yml (core infrastructure)
- docker-compose.apps.yml (backend services - Phase 2)
- docker-compose.frontend.yml (frontend - Phase 3)
- docker-compose.library.yml (ML library - Phase 4)

### Modular Approach Benefits
- ✅ Start only what you need
- ✅ Easy to understand (one file per component)
- ✅ Simple to modify (change one component without affecting others)
- ✅ Version control friendly

---

## Common Operations

### Start Only Core Infrastructure
```bash
cd infrastructure/docker
docker-compose -f docker-compose.core.yml up -d
```

### Start Core + Backend Apps (Phase 2)
```bash
cd infrastructure/docker
docker-compose -f docker-compose.core.yml -f docker-compose.apps.yml up -d
```

### Restart Specific Service
```bash
docker-compose restart nats
```

### Rebuild Service
```bash
# Rebuild and restart authn
docker-compose up -d --build authn
```

### Remove All Containers and Volumes
```bash
docker-compose down -v
```

---

## Environment Variables

### File Location
**Template**: `infrastructure/docker/.env.template`
**Active**: `infrastructure/docker/.env` (not in Git)

### Updating Variables
1. Edit `.env` file
2. Restart services: `docker-compose up -d`
3. Changed variables will be applied

### Adding New Variables
1. Add to `.env.template` (for version control)
2. Add to `.env` (for active use)
3. Update service configuration to use new variable

---

## Troubleshooting

### Services Won't Start
```bash
# Check logs
docker-compose logs <service_name>

# Common issues:
# - Port already in use
# - Volume permission denied
# - Network not found
```

### Port Conflicts
```bash
# Find what's using port
netstat -ano | findstr :4222

# Stop conflicting service
docker stop <container_id>
```

### Reset Everything
```bash
# Nuclear option: remove everything
docker-compose down -v
docker network rm trade2026-frontend trade2026-lowlatency trade2026-backend

# Start fresh
bash scripts/up.sh
```

### Check Service Health
```bash
# Run health checks
bash scripts/status.sh

# Manual health check
curl http://localhost:8222/healthz  # NATS
docker exec valkey valkey-cli ping  # Valkey
curl http://localhost:9000/         # QuestDB
```

---

## Best Practices

### DO ✅
- Use helper scripts (up.sh, down.sh, status.sh, logs.sh)
- Keep .env file updated
- Check logs when services fail
- Run status checks regularly
- Stop services when not in use (saves resources)

### DON'T ❌
- Commit .env file to Git
- Modify master docker-compose.yml frequently (use modular files)
- Hardcode values (use environment variables)
- Run services on host network (use Docker networks)

---

## Next Steps

**Phase 2**: Add backend application services
- Copy docker-compose.apps.yml.template
- Configure backend services
- Uncomment include in master compose file

**Phase 3**: Add frontend
- Create docker-compose.frontend.yml
- Build React app Docker image
- Uncomment include in master compose file

**Phase 4**: Add ML library
- Create docker-compose.library.yml
- Deploy ML pipelines
- Uncomment include in master compose file

---

**Status**: Phase 1 Complete ✅
**Services**: 8/8 Core Infrastructure Operational
EOF
```

**Validation**:
```bash
cat C:\ClaudeDesktop_Projects\Trade2026\docs\deployment\DOCKER_COMPOSE_GUIDE.md
# Should display complete guide
```

**Checklist**:
- [ ] DOCKER_COMPOSE_GUIDE.md created
- [ ] All common operations documented
- [ ] Troubleshooting guide included
- [ ] Best practices listed
- [ ] **Phase 6 complete: Documentation created** ✅

---

## ✅ ACCEPTANCE CRITERIA

The task is complete when ALL of the following are true:

### Configuration
- [ ] Master docker-compose.yml created
- [ ] Includes all modular compose files
- [ ] .env.template created
- [ ] .env created (not in Git)

### Helper Scripts
- [ ] up.sh works (starts all services)
- [ ] down.sh works (stops all services)
- [ ] logs.sh works (views logs)
- [ ] status.sh works (checks health)

### Testing
- [ ] Can start all services with single command
- [ ] Can stop all services with single command
- [ ] Can view logs easily
- [ ] Health checks pass

### Documentation
- [ ] DOCKER_COMPOSE_GUIDE.md created
- [ ] Usage instructions clear
- [ ] Troubleshooting guide included

---

## 🔄 ROLLBACK PLAN

If master compose doesn't work:

**Revert to Modular Files**:
```bash
# Start using individual files
cd infrastructure/docker
docker-compose -f docker-compose.networks.yml up -d
docker-compose -f docker-compose.core.yml up -d
```

**Fix Master File**:
```bash
# Edit master file
vim docker-compose.yml

# Test
docker-compose config
# Should show merged configuration without errors
```

---

## 📝 NOTES FOR CLAUDE CODE

### Key Points
- Master compose file uses `include:` directive (Docker Compose 3.8+)
- Future compose files are commented out (not created yet)
- Helper scripts make operations easier
- .env file is NOT committed to Git

### Common Issues

**Issue 1: Include directive not supported**
```bash
Error: Unsupported config option for services: 'include'
```
**Solution**: Update Docker Compose to version 1.28.0+

**Issue 2: Networks already exist**
```bash
Error: network already exists
```
**Solution**: This is expected if Task 02 completed. Networks are reused.

**Issue 3: Scripts not executable on Windows**
```bash
bash: scripts/up.sh: Permission denied
```
**Solution**: Use `bash scripts/up.sh` instead of `./scripts/up.sh`

### Time Estimate
- Optimistic: 1 hour
- Realistic: 2 hours
- Pessimistic: 3 hours (if troubleshooting needed)

---

## 📊 SUCCESS METRICS

After completion:
- ✅ Single `docker-compose up` starts everything
- ✅ Helper scripts functional
- ✅ Documentation complete
- ✅ Ready for Phase 2 (Backend services)

---

**Status**: ⏳ Pending

**Next Task**: `05_VALIDATE_CORE_SERVICES.md`

**Last Updated**: 2025-10-14
