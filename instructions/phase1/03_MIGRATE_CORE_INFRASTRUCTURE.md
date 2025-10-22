# Task 03: Migrate Core Infrastructure Services

**Phase**: 1 - Foundation
**Priority**: P0-Critical
**Estimated Time**: 4 hours
**Dependencies**: Task 01 (Directory Structure), Task 02 (Networks)
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
- [ ] **File Operations** - CRITICAL: Read Before Write, Backup, Validation
- [ ] **6-Phase Mandatory Workflow** - EVERY task follows this workflow
- [ ] **External Service Connection Pattern** - Docker networking rules
- [ ] **Testing & Validation Rules** - How to validate your work
- [ ] **Error Handling & Rollback** - What to do when things fail

**Why This Matters**: This task modifies configuration files. The guidelines tell you:
- ✅ How to read source files before modifying
- ✅ How to backup critical files
- ✅ How to handle errors and rollback
- ✅ Token budget management (this is a long task!)
- ✅ Testing each service individually
- ✅ When to stop and ask for help

**Estimated Time**: 10-15 minutes to read the relevant sections

### 2. Project Context (MUST READ AFTER GUIDELINES)
**Location**: `C:\ClaudeDesktop_Projects\Trade2026\MASTER_PLAN.md`
- [ ] Read the full overview

**Location**: `C:\ClaudeDesktop_Projects\Trade2026\appendices\appendix_A_foundation.md`
- [ ] Read Core services list and details

**Location**: `C:\ClaudeDesktop_Projects\Trade2026\docs\architecture\NETWORK_ARCHITECTURE.md`
- [ ] Read Network setup (created in Task 02)

**Estimated Time**: 10 minutes

### 3. Source Files (MUST READ BEFORE MODIFYING)
**Location**: `C:\Trade2025\docker-compose.core.yml`
- [ ] Read the original core services configuration
- [ ] Understand current structure before migrating

**Estimated Time**: 5 minutes

---

## ⚠️ CONSEQUENCES OF NOT READING GUIDELINES

If you skip reading MASTER_GUIDELINES.md, you will:
- ❌ Miss critical "Read Before Write" rule (could corrupt files)
- ❌ Not backup files (can't rollback if things fail)
- ❌ Not follow 6-Phase Workflow (task will fail)
- ❌ Run out of token budget mid-task (this is a 4-hour task!)
- ❌ Skip validation steps (services won't work)
- ❌ Make mistakes that require complete restart

**The guidelines exist to prevent failures. READ THEM FIRST.**

---

## ✅ CHECKLIST BEFORE PROCEEDING

**I confirm I have read and understood**:
- [ ] MASTER_GUIDELINES.md - New Session Startup Protocol
- [ ] MASTER_GUIDELINES.md - Core Development Rules
- [ ] MASTER_GUIDELINES.md - File Operations (Read Before Write!)
- [ ] MASTER_GUIDELINES.md - 6-Phase Mandatory Workflow
- [ ] MASTER_GUIDELINES.md - External Service Connection Pattern
- [ ] MASTER_GUIDELINES.md - Testing & Validation Rules
- [ ] MASTER_GUIDELINES.md - Error Handling & Rollback
- [ ] MASTER_PLAN.md - Project overview
- [ ] appendix_A_foundation.md - Core services details
- [ ] NETWORK_ARCHITECTURE.md - Network setup
- [ ] C:\Trade2025\docker-compose.core.yml - Source configuration

**Total Reading Time**: ~25 minutes

**Only proceed to next section after completing this checklist.**

---

# 🚦 VALIDATION GATE - VERIFY TASKS 01-02

## MANDATORY: Validate ALL Previous Tasks Before Starting

**STOP**: Before starting Task 03, you MUST verify Tasks 01-02 are complete and working.

### Prerequisites Validation

#### Task 01: Directory Structure Validation
```bash
cd C:\ClaudeDesktop_Projects\Trade2026

# Verify all top-level directories exist
echo "Checking top-level directories..."
test -d frontend && echo "✅ frontend/" || echo "❌ frontend/ MISSING"
test -d backend && echo "✅ backend/" || echo "❌ backend/ MISSING"
test -d library && echo "✅ library/" || echo "❌ library/ MISSING"
test -d infrastructure && echo "✅ infrastructure/" || echo "❌ infrastructure/ MISSING"
test -d data && echo "✅ data/" || echo "❌ data/ MISSING"
test -d config && echo "✅ config/" || echo "❌ config/ MISSING"
test -d secrets && echo "✅ secrets/" || echo "❌ secrets/ MISSING"
test -d docs && echo "✅ docs/" || echo "❌ docs/ MISSING"
test -d tests && echo "✅ tests/" || echo "❌ tests/ MISSING"
test -d scripts && echo "✅ scripts/" || echo "❌ scripts/ MISSING"

# Verify critical subdirectories for this task
echo "\nChecking subdirectories needed for Task 03..."
test -d backend/apps && echo "✅ backend/apps/" || echo "❌ backend/apps/ MISSING"
test -d infrastructure/docker && echo "✅ infrastructure/docker/" || echo "❌ infrastructure/docker/ MISSING"
test -d data/nats && echo "✅ data/nats/" || echo "❌ data/nats/ MISSING"
test -d data/valkey && echo "✅ data/valkey/" || echo "❌ data/valkey/ MISSING"
test -d data/questdb && echo "✅ data/questdb/" || echo "❌ data/questdb/ MISSING"
test -d data/clickhouse && echo "✅ data/clickhouse/" || echo "❌ data/clickhouse/ MISSING"
test -d data/seaweed && echo "✅ data/seaweed/" || echo "❌ data/seaweed/ MISSING"
test -d data/opensearch && echo "✅ data/opensearch/" || echo "❌ data/opensearch/ MISSING"
test -d config/backend && echo "✅ config/backend/" || echo "❌ config/backend/ MISSING"
test -d config/infrastructure && echo "✅ config/infrastructure/" || echo "❌ config/infrastructure/ MISSING"

# Verify documentation
test -f DIRECTORY_STRUCTURE.md && echo "✅ DIRECTORY_STRUCTURE.md" || echo "❌ DIRECTORY_STRUCTURE.md MISSING"

echo "\n📊 Task 01 Directory Validation Complete"
```

#### Task 02: Docker Networks Validation
```bash
echo "\nChecking Docker networks..."

# Verify all 3 networks exist
docker network ls | grep trade2026-frontend > /dev/null && echo "✅ trade2026-frontend network" || echo "❌ trade2026-frontend MISSING"
docker network ls | grep trade2026-lowlatency > /dev/null && echo "✅ trade2026-lowlatency network" || echo "❌ trade2026-lowlatency MISSING"
docker network ls | grep trade2026-backend > /dev/null && echo "✅ trade2026-backend network" || echo "❌ trade2026-backend MISSING"

# Verify network subnets
echo "\nVerifying network subnets..."
docker network inspect trade2026-frontend | grep "Subnet" | grep "172.23.0.0/16" && echo "✅ frontend subnet correct" || echo "❌ frontend subnet incorrect"
docker network inspect trade2026-lowlatency | grep "Subnet" | grep "172.22.0.0/16" && echo "✅ lowlatency subnet correct" || echo "❌ lowlatency subnet incorrect"
docker network inspect trade2026-backend | grep "Subnet" | grep "172.21.0.0/16" && echo "✅ backend subnet correct" || echo "❌ backend subnet incorrect"

echo "\n📊 Task 02 Network Validation Complete"
```

#### Integration Test: Directories + Networks
```bash
echo "\nTesting integration: Can networks access directories?"

# Create test container on backend network with volume mount
docker run --rm \
  -v C:/ClaudeDesktop_Projects/Trade2026/data:/test_data \
  --network trade2026-backend \
  alpine sh -c "ls -la /test_data && echo '✅ Networks can access data directories'"

if [ $? -eq 0 ]; then
    echo "✅ Integration Test PASSED: Networks + Directories working together"
else
    echo "❌ Integration Test FAILED: Networks cannot access directories"
    exit 1
fi

echo "\n📊 Integration Validation Complete"
```

### Validation Checklist

**Task 01 - Directory Structure**:
- [ ] All 10 top-level directories exist
- [ ] All subdirectories for Task 03 exist (backend/apps, infrastructure/docker, data/*, config/*)
- [ ] DIRECTORY_STRUCTURE.md documentation exists
- [ ] No errors in directory validation script

**Task 02 - Docker Networks**:
- [ ] trade2026-frontend network exists (172.23.0.0/16)
- [ ] trade2026-lowlatency network exists (172.22.0.0/16)
- [ ] trade2026-backend network exists (172.21.0.0/16)
- [ ] All subnets configured correctly
- [ ] No errors in network validation script

**Integration - Directories + Networks**:
- [ ] Test container can mount Task 01 directories
- [ ] Test container can access directories via networks
- [ ] Integration test passes with exit code 0
- [ ] No permission or access errors

### Proceed/Stop Decision

**Run the validation scripts above and answer**:

1. Did ALL Task 01 validations pass? (YES/NO): _____
2. Did ALL Task 02 validations pass? (YES/NO): _____
3. Did integration test pass? (YES/NO): _____
4. Are there ANY error messages? (YES/NO): _____

**Can I proceed to Task 03?**
- ✅ **YES** - All validations passed, no errors → Continue to OBJECTIVE section
- ❌ **NO** - Something failed → STOP, fix issues, re-run validations

**If ANY validation fails**:
1. ❌ **STOP** - Do NOT proceed with Task 03
2. Review error messages from validation scripts
3. Go back to failed task (01 or 02)
4. Fix the issue
5. Re-run validation scripts
6. Only proceed when ALL validations pass

---

**⚠️ CRITICAL**: Do NOT proceed past this point unless all validations above are complete and passing.

---

## ⚠️ CRITICAL RULES FOR THIS TASK

### Rule 1: Read Before Write
ALWAYS read the source file from Trade2025 BEFORE modifying for Trade2026.

### Rule 2: Update Paths Consistently
**OLD**: `C:/trade2025/trading/`
**NEW**: `C:/ClaudeDesktop_Projects/Trade2026/`

### Rule 3: Update Network Names
**OLD**: `trade2025-frontend`, `trade2025-lowlatency`, `trade2025-backend`
**NEW**: `trade2026-frontend`, `trade2026-lowlatency`, `trade2026-backend`

### Rule 4: Test Each Service
After migrating each service, test it individually before proceeding.

### Rule 5: COMPREHENSIVE IMPLEMENTATION - NO SHORTCUTS

**⚠️ MANDATORY**: All implementations must be COMPLETE and COMPREHENSIVE. No abbreviated implementations "to save time".

#### What This Means:

**✅ DO** - Complete Implementations:
- Install ALL dependencies (not just minimum)
- Configure ALL settings (not just basics)
- Test ALL functionality (not just health checks)
- Document ALL steps (not just key points)
- Validate ALL components (not just critical ones)

**❌ DON'T** - Shortcuts/Abbreviated:
- "Quick" installs that skip optional components
- "Minimal" configurations that skip advanced settings
- "Basic" testing that skips edge cases
- "Brief" documentation that skips details
- "Quick" validation that skips comprehensive checks

#### Specific Requirements:

**Service Configuration**:
- Every service gets FULL configuration (not minimal)
- All environment variables defined (not just required ones)
- All health checks comprehensive (not just ping)
- All resource limits set appropriately (not defaults)

**Testing Requirements**:
- Component test: Each service individually
- Integration test: Service with dependencies
- Performance test: Basic load/latency checks
- Persistence test: Data survives restart
- Network test: Service communication

**Documentation Requirements**:
- Every configuration choice explained
- Every test result documented
- Every issue encountered noted
- Every decision justified

### Rule 6: OFFICIAL SOURCES ONLY - NO UNOFFICIAL PACKAGES

**⚠️ MANDATORY**: All open-source components MUST be acquired from official sources only.

#### Official Sources:

**Docker Images** (from official registries):
- NATS: `nats:2.10-alpine` from Docker Hub (https://hub.docker.com/_/nats)
- Valkey: `valkey/valkey:8-alpine` from Docker Hub (https://hub.docker.com/r/valkey/valkey)
- QuestDB: `questdb/questdb:latest` from Docker Hub (https://hub.docker.com/r/questdb/questdb)
- ClickHouse: `clickhouse/clickhouse-server:24.9` from Docker Hub (https://hub.docker.com/r/clickhouse/clickhouse-server)
- SeaweedFS: `chrislusf/seaweedfs:latest` from Docker Hub (https://hub.docker.com/r/chrislusf/seaweedfs)
- OpenSearch: `opensearchproject/opensearch:2` from Docker Hub (https://hub.docker.com/r/opensearchproject/opensearch)

**CLI Tools** (if needed):
- NATS CLI: https://github.com/nats-io/natscli/releases (official GitHub releases)
- Redis/Valkey CLI: Included in image
- Docker: https://docs.docker.com/get-docker/ (official Docker docs)

**❌ PROHIBITED** - Unofficial Sources:
- Random GitHub repos (not official project repos)
- Third-party Docker registries (not Docker Hub official)
- Unofficial mirrors or forks
- Pre-built binaries from unknown sources
- Modified or patched versions
- "Optimized" or "enhanced" versions

#### Verification:

Before using ANY component:
1. Verify it's from official source
2. Check official documentation
3. Confirm version is stable/recommended
4. Document source URL in implementation

**Example**:
```yaml
# ✅ GOOD - Official source documented
nats:
  image: nats:2.10-alpine  # Official: https://hub.docker.com/_/nats
  
# ❌ BAD - No source verification
nats:
  image: some-random-user/nats:custom
```

---

## 📋 OBJECTIVE

Migrate the 8 core infrastructure services from Trade2025 to Trade2026:
1. NATS (message bus)
2. Valkey (cache)
3. QuestDB (time-series database)
4. ClickHouse (analytics database)
5. SeaweedFS (object storage)
6. OpenSearch (search engine)
7. authn (authentication)
8. OPA (authorization)

**Why This Matters**: These services are the foundation. All application services depend on them.

---

## 🎯 CONTEXT

### Current State (Trade2025)
- Core services defined in: `C:\Trade2025\docker-compose.core.yml`
- Data in: `C:\trade2025\trading\{nats,valkey,questdb,...}`
- Networks: `trade2025-*`
- Status: 8/8 services healthy and operational

### Target State (Trade2026)
- Core services in: `C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker\docker-compose.core.yml`
- Data in: `C:\ClaudeDesktop_Projects\Trade2026\data\{nats,valkey,questdb,...}`
- Networks: `trade2026-*`
- All services healthy

### Core Services Overview

| Service | Port | Network | Purpose | Data Volume |
|---------|------|---------|---------|-------------|
| NATS | 4222 | lowlatency | Message bus | data/nats/ |
| Valkey | 6379 | backend | Cache | data/valkey/ |
| QuestDB | 9000, 8812 | backend | Time-series DB | data/questdb/ |
| ClickHouse | 8123, 9000 | backend | Analytics DB | data/clickhouse/ |
| SeaweedFS | 8333, 9333 | backend | Object storage | data/seaweed/ |
| OpenSearch | 9200 | backend | Search engine | data/opensearch/ |
| authn | 8114 | frontend, backend | Authentication | - |
| OPA | 8181 | frontend | Authorization | - |

---

## ✅ REQUIREMENTS

### Functional Requirements
1. Copy docker-compose.core.yml from Trade2025
2. Update all paths to Trade2026
3. Update network references
4. Create service-specific config directories
5. Test each service individually

### Non-Functional Requirements
- **No Data Loss**: Don't modify original Trade2025 data
- **Idempotent**: Can re-run safely
- **Testable**: Each service can be validated independently

---

## 🔧 IMPLEMENTATION STEPS

### Step 1: Read Source Configuration
**Goal**: Understand current Trade2025 core services setup

**Actions**:
```bash
# Read the source file
cd C:\Trade2025
cat docker-compose.core.yml

# Note the structure, services, volumes, networks
# We'll adapt this for Trade2026
```

**Key Information to Extract**:
- Service names
- Image versions
- Port mappings
- Volume mounts
- Network assignments
- Environment variables
- Health checks

**Checklist**:
- [ ] Source file read and understood
- [ ] Service list confirmed (8 services)
- [ ] Volume paths noted
- [ ] Network assignments noted
- [ ] **Phase 1 complete: Source analyzed** ✅

---

### Step 2: Create Base docker-compose.core.yml
**Goal**: Create the new core services file with updated paths

**Actions**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker

# Create docker-compose.core.yml
cat > docker-compose.core.yml << 'EOF'
version: '3.8'

# Trade2026 Core Infrastructure Services
# Migrated from Trade2025 - Updated paths and networks

networks:
  frontend:
    external: true
    name: trade2026-frontend
  lowlatency:
    external: true
    name: trade2026-lowlatency
  backend:
    external: true
    name: trade2026-backend

services:
  # ==========================================
  # MESSAGE BUS
  # ==========================================
  nats:
    image: nats:2.10-alpine
    container_name: nats
    command: 
      - "--jetstream"
      - "--store_dir=/data"
      - "--http_port=8222"
    ports:
      - "4222:4222"  # Client connections
      - "8222:8222"  # Monitoring
    volumes:
      - ../../data/nats:/data
    networks:
      - lowlatency
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:8222/healthz"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 10s
    restart: unless-stopped
    labels:
      - "com.trade2026.service=nats"
      - "com.trade2026.cpgs.version=1.0"
      - "com.trade2026.component=infrastructure"

  # ==========================================
  # CACHE
  # ==========================================
  valkey:
    image: valkey/valkey:8-alpine
    container_name: valkey
    command:
      - "valkey-server"
      - "--appendonly yes"
      - "--appendfsync everysec"
      - "--maxmemory 2gb"
      - "--maxmemory-policy allkeys-lru"
    ports:
      - "6379:6379"
    volumes:
      - ../../data/valkey:/data
    networks:
      - backend
    healthcheck:
      test: ["CMD", "valkey-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 5s
    restart: unless-stopped
    labels:
      - "com.trade2026.service=valkey"
      - "com.trade2026.cpgs.version=1.0"
      - "com.trade2026.component=infrastructure"

  # ==========================================
  # TIME-SERIES DATABASE
  # ==========================================
  questdb:
    image: questdb/questdb:latest
    container_name: questdb
    ports:
      - "9000:9000"   # HTTP API
      - "8812:8812"   # Postgres wire protocol
      - "9009:9009"   # InfluxDB line protocol
    volumes:
      - ../../data/questdb:/var/lib/questdb
    networks:
      - backend
    environment:
      - QDB_CAIRO_COMMIT_LAG=1000
      - QDB_PG_ENABLED=true
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:9000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped
    labels:
      - "com.trade2026.service=questdb"
      - "com.trade2026.cpgs.version=1.0"
      - "com.trade2026.component=infrastructure"

  # ==========================================
  # ANALYTICS DATABASE
  # ==========================================
  clickhouse:
    image: clickhouse/clickhouse-server:24.9
    container_name: clickhouse
    ports:
      - "8123:8123"   # HTTP API
      - "9000:9000"   # Native TCP
    volumes:
      - ../../data/clickhouse:/var/lib/clickhouse
    networks:
      - backend
    environment:
      - CLICKHOUSE_DB=trade2026
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:8123/ping"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped
    labels:
      - "com.trade2026.service=clickhouse"
      - "com.trade2026.cpgs.version=1.0"
      - "com.trade2026.component=infrastructure"

  # ==========================================
  # OBJECT STORAGE
  # ==========================================
  seaweedfs:
    image: chrislusf/seaweedfs:latest
    container_name: seaweedfs
    command: 'server -s3 -dir=/data -s3.config=/etc/seaweedfs/s3.json'
    ports:
      - "8333:8333"   # S3 API
      - "9333:9333"   # Master
      - "8080:8080"   # Filer
    volumes:
      - ../../data/seaweed:/data
      - ../../config/infrastructure/seaweedfs:/etc/seaweedfs
    networks:
      - backend
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:9333/cluster/status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped
    labels:
      - "com.trade2026.service=seaweedfs"
      - "com.trade2026.cpgs.version=1.0"
      - "com.trade2026.component=infrastructure"

  # ==========================================
  # SEARCH ENGINE
  # ==========================================
  opensearch:
    image: opensearchproject/opensearch:2
    container_name: opensearch
    ports:
      - "9200:9200"   # REST API
      - "9600:9600"   # Performance analyzer
    volumes:
      - ../../data/opensearch:/usr/share/opensearch/data
    networks:
      - backend
    environment:
      - discovery.type=single-node
      - DISABLE_SECURITY_PLUGIN=true
      - "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9200/_cluster/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    restart: unless-stopped
    labels:
      - "com.trade2026.service=opensearch"
      - "com.trade2026.cpgs.version=1.0"
      - "com.trade2026.component=infrastructure"

  # ==========================================
  # AUTHENTICATION
  # ==========================================
  authn:
    image: localhost/authn:latest
    container_name: authn
    build:
      context: ../../backend/apps/authn
      dockerfile: Dockerfile
    ports:
      - "8114:8114"
    volumes:
      - ../../config/backend/authn:/app/config
      - ../../secrets:/secrets
    networks:
      - frontend
      - backend
    environment:
      - JWKS_PATH=/secrets/jwks.json
      - CONFIG_PATH=/app/config/config.yaml
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8114/health"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 10s
    restart: unless-stopped
    labels:
      - "com.trade2026.service=authn"
      - "com.trade2026.cpgs.version=1.0"
      - "com.trade2026.component=infrastructure"

  # ==========================================
  # AUTHORIZATION
  # ==========================================
  opa:
    image: localhost/opa:latest
    container_name: opa
    build:
      context: ../../backend/apps/opa_authorizer
      dockerfile: Dockerfile
    ports:
      - "8181:8181"
    volumes:
      - ../../config/backend/opa:/app/policies
    networks:
      - frontend
    command:
      - "run"
      - "--server"
      - "--addr=0.0.0.0:8181"
      - "/app/policies"
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:8181/health"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 5s
    restart: unless-stopped
    labels:
      - "com.trade2026.service=opa"
      - "com.trade2026.cpgs.version=1.0"
      - "com.trade2026.component=infrastructure"
EOF
```

**Validation**:
```bash
cat docker-compose.core.yml
# Should show complete YAML with 8 services
```

**Checklist**:
- [ ] File created in infrastructure/docker/
- [ ] All 8 services defined
- [ ] Networks reference trade2026-*
- [ ] Volume paths use ../../data/
- [ ] All health checks present
- [ ] **Phase 2 complete: Config file created** ✅

---

### Step 3: Create Service Configuration Directories
**Goal**: Setup config directories for services that need them

**Actions**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026\config

# Backend service configs
mkdir -p backend/authn
mkdir -p backend/opa
mkdir -p infrastructure/seaweedfs

# Create placeholder configs
cd backend/authn
cat > config.yaml << 'EOF'
# authn service configuration
# Migrated from Trade2025

service:
  name: authn
  port: 8114

jwt:
  algorithm: RS256
  issuer: authn
  audience: trade2026
  expiration: 3600

clients:
  # Service clients
  srv:oms:
    scopes: ["orders:submit", "orders:cancel", "fills:read", "positions:read"]
  srv:risk:
    scopes: ["risk:check", "positions:read", "exposures:read"]
  srv:ptrc:
    scopes: ["pnl:compute", "reports:generate"]
  srv:gateway:
    scopes: ["data:publish"]

# Client secrets in environment variables or secrets file
EOF

cd ../opa
cat > example_policy.rego << 'EOF'
package example

# Allow all authenticated users for now
default allow = true
EOF

cd ../../infrastructure/seaweedfs
cat > s3.json << 'EOF'
{
  "identities": [
    {
      "name": "trade2026",
      "credentials": [
        {
          "accessKey": "trade2026",
          "secretKey": "trade2026secret"
        }
      ],
      "actions": [
        "Admin",
        "Read",
        "Write"
      ]
    }
  ]
}
EOF
```

**Validation**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026\config
tree -L 3
# Should show backend/ and infrastructure/ with config files
```

**Checklist**:
- [ ] backend/authn/config.yaml created
- [ ] backend/opa/example_policy.rego created
- [ ] infrastructure/seaweedfs/s3.json created
- [ ] **Phase 3 complete: Configs created** ✅

---

### Step 4: Copy authn and OPA Source Code
**Goal**: Copy authn and OPA services from Trade2025

**Actions**:
```bash
# Copy authn service
cp -r C:\Trade2025\trading\apps\authn C:\ClaudeDesktop_Projects\Trade2026\backend\apps\

# Copy OPA service
cp -r C:\Trade2025\trading\apps\opa_authorizer C:\ClaudeDesktop_Projects\Trade2026\backend\apps\

# Verify
ls C:\ClaudeDesktop_Projects\Trade2026\backend\apps\
# Should show: authn/, opa_authorizer/
```

**Update authn Configuration** (if needed):
```bash
cd C:\ClaudeDesktop_Projects\Trade2026\backend\apps\authn

# Check if config references need updating
grep -r "trade2025" .
grep -r "C:/trade2025" .

# Update any hardcoded paths (if found)
# Usually not needed if using environment variables
```

**Checklist**:
- [ ] authn/ copied to backend/apps/
- [ ] opa_authorizer/ copied to backend/apps/
- [ ] No hardcoded Trade2025 paths in code
- [ ] **Phase 4 complete: Code migrated** ✅

---

### Step 5: Start Core Services
**Goal**: Start all 8 core infrastructure services

**Actions**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker

# Start all core services
docker-compose -f docker-compose.core.yml up -d

# Watch logs
docker-compose -f docker-compose.core.yml logs -f
```

**Expected Output**:
```
Creating nats ... done
Creating valkey ... done
Creating questdb ... done
Creating clickhouse ... done
Creating seaweedfs ... done
Creating opensearch ... done
Building authn ... 
Creating authn ... done
Building opa ...
Creating opa ... done
```

**Monitor Startup**:
```bash
# Check container status
docker ps

# Should show 8 containers with "Up" status
```

**Checklist**:
- [ ] All 8 containers started
- [ ] No error messages in logs
- [ ] All containers show "Up" status
- [ ] **Phase 5 complete: Services started** ✅

---

### Step 6: Validate Each Service
**Goal**: Test each service individually

**NATS**:
```bash
# Check health
curl http://localhost:8222/healthz
# Expected: OK

# Check JetStream
curl http://localhost:8222/jsz
# Expected: JSON with JetStream info
```

**Valkey**:
```bash
# Test connection
docker exec valkey valkey-cli ping
# Expected: PONG

# Set and get a test value
docker exec valkey valkey-cli set test_key test_value
docker exec valkey valkey-cli get test_key
# Expected: "test_value"
```

**QuestDB**:
```bash
# Check HTTP API
curl http://localhost:9000/
# Expected: QuestDB web console HTML

# Test query
curl -G --data-urlencode "query=SELECT 1" http://localhost:9000/exec
# Expected: JSON result
```

**ClickHouse**:
```bash
# Check health
curl http://localhost:8123/ping
# Expected: Ok.

# Test query
echo "SELECT version()" | curl -s "http://localhost:8123/" --data-binary @-
# Expected: ClickHouse version number
```

**SeaweedFS**:
```bash
# Check cluster status
curl http://localhost:9333/cluster/status
# Expected: JSON with cluster info

# Test S3 API (requires awscli)
# Skip if awscli not installed
```

**OpenSearch**:
```bash
# Check cluster health
curl http://localhost:9200/_cluster/health
# Expected: JSON with status "green" or "yellow"

# Check nodes
curl http://localhost:9200/_cat/nodes?v
# Expected: Node information
```

**authn**:
```bash
# Check health
curl http://localhost:8114/health
# Expected: {"status": "healthy"}

# Check JWKS endpoint
curl http://localhost:8114/.well-known/jwks.json
# Expected: JSON with public keys
```

**OPA**:
```bash
# Check health
curl http://localhost:8181/health
# Expected: {} (empty JSON = healthy)

# Test policy query
curl -X POST http://localhost:8181/v1/data/example/allow
# Expected: {"result": true}
```

**Validation Checklist**:
- [ ] NATS responding (4222, 8222)
- [ ] Valkey responding (6379)
- [ ] QuestDB responding (9000, 8812)
- [ ] ClickHouse responding (8123, 9000)
- [ ] SeaweedFS responding (8333, 9333)
- [ ] OpenSearch responding (9200)
- [ ] authn responding (8114)
- [ ] OPA responding (8181)
- [ ] **Phase 6 complete: All validated** ✅

---

## ✅ ACCEPTANCE CRITERIA

The task is complete when ALL of the following are true:

### Configuration
- [ ] docker-compose.core.yml created in infrastructure/docker/
- [ ] All paths updated to Trade2026
- [ ] All networks updated to trade2026-*
- [ ] Service configs created

### Code Migration
- [ ] authn/ copied to backend/apps/
- [ ] opa_authorizer/ copied to backend/apps/
- [ ] No hardcoded Trade2025 paths

### Services Running
- [ ] All 8 containers started
- [ ] All containers healthy (docker ps shows "healthy")
- [ ] No error messages in logs

### Validation
- [ ] Each service responds to health checks
- [ ] NATS JetStream operational
- [ ] Valkey accepts read/write
- [ ] QuestDB accepts queries
- [ ] ClickHouse accepts queries
- [ ] SeaweedFS cluster status OK
- [ ] OpenSearch cluster healthy
- [ ] authn issues JWT tokens
- [ ] OPA evaluates policies

---

## 🔄 ROLLBACK PLAN

If services fail to start:

**Stop All Services**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker
docker-compose -f docker-compose.core.yml down
```

**Check Individual Service**:
```bash
# Start one service at a time
docker-compose -f docker-compose.core.yml up -d nats
docker logs nats

# Debug issues before starting next service
```

**Complete Rollback**:
```bash
# Remove all containers and volumes
docker-compose -f docker-compose.core.yml down -v

# Re-run from Step 2
```

---

## 📝 NOTES FOR CLAUDE CODE

### Key Points
- Test each service individually before validating all
- Health checks may take 30-60 seconds for some services (OpenSearch, QuestDB)
- authn and OPA need to be built first (have Dockerfiles)
- Other services use pre-built images from Docker Hub

### Common Issues

**Issue 1: Port already in use**
```bash
Error: port is already allocated
```
**Solution**: Stop Trade2025 services first
```bash
cd C:\Trade2025
docker-compose down
```

**Issue 2: Permission denied on volumes**
```bash
Error: permission denied
```
**Solution**: Ensure data directories exist and are writable
```bash
cd C:\ClaudeDesktop_Projects\Trade2026
mkdir -p data/{nats,valkey,questdb,clickhouse,seaweed,opensearch}
```

**Issue 3: Build fails for authn/OPA**
```bash
Error: Dockerfile not found
```
**Solution**: Ensure code was copied correctly in Step 4

**Issue 4: Service unhealthy**
```bash
Status: unhealthy
```
**Solution**: Check logs
```bash
docker logs <service_name>
```

### Time Estimate
- Optimistic: 2 hours (everything works first try)
- Realistic: 4 hours (some troubleshooting needed)
- Pessimistic: 6 hours (significant debugging required)

---

## 📊 SUCCESS METRICS

After completion:
- ✅ 8/8 core services healthy
- ✅ All health checks passing
- ✅ Zero error messages
- ✅ Services communicating via Docker DNS
- ✅ Ready for application services (Phase 2)

---

**Status**: ⏳ Pending

**Next Task**: `04_CONFIGURE_BASE_COMPOSE.md`

**Last Updated**: 2025-10-14
