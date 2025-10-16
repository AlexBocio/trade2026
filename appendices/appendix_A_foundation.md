# Appendix A: Foundation Details (Phase 1)

**Phase**: Foundation
**Duration**: Week 1 (5 days)
**Priority**: P0-Critical
**Tasks**: 5 detailed instructions

---

## Validation & Quality Requirements

### Validation Gates

Starting with Task 03, every task includes a validation gate that:
- Verifies all previous tasks completed successfully
- Tests integration between previous tasks
- Requires passing all validations before proceeding
- Includes mandatory STOP checkpoint

**Example**: Before starting Task 03, Claude Code must:
1. Verify all Task 01 directories exist
2. Verify all Task 02 networks operational
3. Test integration (can containers mount directories?)
4. Answer proceed/stop questions
5. STOP if anything fails

### Comprehensive Implementation

All implementations in Phase 1 must be:
- **Complete**: No shortcuts or "minimal" configurations
  - Install ALL dependencies (not just minimum)
  - Configure ALL settings (not just basics)
  - Test ALL functionality (not just health checks)
- **Tested**: Component, integration, performance, persistence tests
  - Component test: Service works individually
  - Integration test: Service works with dependencies
  - Performance test: Latency/throughput acceptable
  - Persistence test: Data survives restart
  - Network test: Can communicate with other services
- **Documented**: Every choice explained, every result recorded
  - Configuration choices explained
  - Test results documented
  - Issues encountered noted
  - Decisions justified
- **Official**: All components from official sources only

### Official Sources

All Docker images MUST be from Docker Hub official:

| Component | Image | Official Source |
|-----------|-------|----------------|
| NATS | `nats:2.10-alpine` | https://hub.docker.com/_/nats |
| Valkey | `valkey/valkey:8-alpine` | https://hub.docker.com/r/valkey/valkey |
| QuestDB | `questdb/questdb:latest` | https://hub.docker.com/r/questdb/questdb |
| ClickHouse | `clickhouse/clickhouse-server:24.9` | https://hub.docker.com/r/clickhouse/clickhouse-server |
| SeaweedFS | `chrislusf/seaweedfs:latest` | https://hub.docker.com/r/chrislusf/seaweedfs |
| OpenSearch | `opensearchproject/opensearch:2` | https://hub.docker.com/r/opensearchproject/opensearch |

**authn and OPA**: Built from official source code in Trade2025 repository.

**Verification Required**:
- Check "Official Image" or "Verified Publisher" badge on Docker Hub
- Verify version is stable/recommended
- Document source URL in docker-compose comments

**Prohibited Sources**:
- ❌ Random GitHub repos (not official)
- ❌ Third-party Docker registries
- ❌ Unofficial mirrors or forks
- ❌ Modified/"optimized" versions

### Testing Requirements

Every service must pass ALL of these tests:

**1. Component Test**: Service works individually
```bash
# Example: NATS
curl http://localhost:8222/healthz
# Expected: OK
```

**2. Integration Test**: Service works with dependencies
```bash
# Example: NATS with data directory
ls -la C:\ClaudeDesktop_Projects\Trade2026\data\nats
# Expected: JetStream data files present
```

**3. Performance Test**: Latency/throughput acceptable
```bash
# Example: Valkey
docker exec valkey valkey-cli --latency
# Expected: < 1ms latency
```

**4. Persistence Test**: Data survives restart
```bash
# Example: Valkey
docker exec valkey valkey-cli set test_key test_value
docker restart valkey
docker exec valkey valkey-cli get test_key
# Expected: "test_value" returned
```

**5. Network Test**: Can communicate with other services
```bash
# Example: Test DNS resolution
docker exec nats ping -c 3 valkey
# Expected: 3 successful pings
```

**No service proceeds to next task until ALL tests pass.**

### Quality Gates

Before marking any Phase 1 task as complete:

- [ ] All acceptance criteria met
- [ ] All validation scripts passing
- [ ] All services healthy (if applicable)
- [ ] All integration tests passing
- [ ] Documentation updated
- [ ] No errors in logs
- [ ] Rollback procedure tested (if applicable)

**If ANY gate fails**: STOP, fix issue, re-run validations, only proceed when passing.

---

## Overview

Phase 1 establishes the foundation for Trade2026 by:
1. Creating the unified directory structure
2. Setting up Docker networks (CPGS v1.0)
3. Migrating core infrastructure
4. Configuring base docker-compose files
5. Validating all core services

**Exit Criteria**:
- ✅ Complete directory structure exists
- ✅ All 8 core infrastructure services healthy
- ✅ Docker networks configured and tested
- ✅ Base docker-compose files operational

---

## Task Breakdown

### Task 01: Create Directory Structure
**Time**: 1 hour
**Instruction File**: `01_CREATE_DIRECTORY_STRUCTURE.md`

**What It Does**:
```bash
# Creates this structure:
Trade2026/
├── frontend/
├── backend/
│   └── apps/
├── library/
│   ├── apps/
│   ├── pipelines/
│   └── strategies/
├── infrastructure/
│   ├── docker/
│   ├── k8s/
│   └── nginx/
├── data/
│   ├── nats/
│   ├── valkey/
│   ├── questdb/
│   ├── clickhouse/
│   ├── seaweed/
│   ├── opensearch/
│   ├── postgres/
│   └── mlflow/
├── config/
├── secrets/
├── docs/
├── tests/
└── scripts/
```

**Key Points**:
- All data consolidated in `data/` directory
- Secrets NOT in Git (in `secrets/`)
- Modular structure for each component

---

### Task 02: Setup Docker Networks
**Time**: 30 minutes
**Instruction File**: `02_SETUP_DOCKER_NETWORKS.md`

**What It Does**:
Creates three Docker networks following CPGS v1.0:

```yaml
# infrastructure/docker/docker-compose.networks.yml
networks:
  trade2026-frontend:
    subnet: 172.23.0.0/16
  
  trade2026-lowlatency:
    subnet: 172.22.0.0/16
  
  trade2026-backend:
    subnet: 172.21.0.0/16
```

**Port Allocation**:
- Frontend: 80, 443, 5173 (dev)
- Low-latency: 8000-8199
- Backend: 8300-8499

**Test**:
```bash
docker network ls | grep trade2026
# Should show 3 networks
```

---

### Task 03: Migrate Core Infrastructure
**Time**: 4 hours
**Instruction File**: `03_MIGRATE_CORE_INFRASTRUCTURE.md`

**Core Services** (8 total):

| Service | Port | Network | Data Volume |
|---------|------|---------|-------------|
| NATS | 4222 | lowlatency | `data/nats/` |
| Valkey | 6379 | backend | `data/valkey/` |
| QuestDB | 9000 | backend | `data/questdb/` |
| ClickHouse | 8123 | backend | `data/clickhouse/` |
| SeaweedFS | 8333 | backend | `data/seaweed/` |
| OpenSearch | 9200 | backend | `data/opensearch/` |
| authn | 8114 | frontend/backend | - |
| OPA | 8181 | frontend | - |

**Migration Steps**:
1. Copy docker-compose.core.yml from Trade2025
2. Update all volume paths: `C:/trade2025/trading/` → `C:/ClaudeDesktop_Projects/Trade2026/`
3. Update network references: `trade2025-*` → `trade2026-*`
4. Test each service individually

**Configuration Updates**:
```yaml
# Example: NATS service
nats:
  image: nats:2.10-alpine
  volumes:
    - ../../data/nats:/var/lib/nats  # UPDATED PATH
  networks:
    - trade2026-lowlatency            # UPDATED NETWORK
  ports:
    - "4222:4222"
```

---

### Task 04: Configure Base Docker Compose
**Time**: 2 hours
**Instruction File**: `04_CONFIGURE_BASE_COMPOSE.md`

**Create Main Compose File**:
```yaml
# infrastructure/docker/docker-compose.yml
version: '3.8'

include:
  - docker-compose.networks.yml
  - docker-compose.core.yml
  # Will add later:
  # - docker-compose.apps.yml
  # - docker-compose.frontend.yml
  # - docker-compose.library.yml
```

**Benefits**:
- Single `docker-compose up` command
- Modular architecture (add services incrementally)
- Easy to enable/disable components

**Test**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026
docker-compose -f infrastructure/docker/docker-compose.yml up -d
```

---

### Task 05: Validate Core Services
**Time**: 1 hour
**Instruction File**: `05_VALIDATE_CORE_SERVICES.md`

**Health Checks**:
```bash
# NATS
curl http://localhost:8222/healthz

# Valkey
docker exec valkey valkey-cli ping

# QuestDB
curl http://localhost:9000/

# ClickHouse
curl http://localhost:8123/ping

# SeaweedFS
curl http://localhost:9333/cluster/status

# OpenSearch
curl http://localhost:9200/_cluster/health

# authn
curl http://localhost:8114/health

# OPA
curl http://localhost:8181/health
```

**Success Criteria**:
- ✅ All 8 services respond to health checks
- ✅ No error messages in logs
- ✅ Data directories populated
- ✅ Services can communicate (test NATS pub/sub)

**Troubleshooting Guide** (if services fail):
1. Check logs: `docker logs <service_name>`
2. Verify paths in docker-compose
3. Ensure networks created
4. Check port conflicts
5. Verify Docker DNS resolution

---

## Configuration Templates

### Environment Variables Template
```bash
# secrets/.env.core
NATS_URL=nats://nats:4222
VALKEY_URL=redis://valkey:6379
QUESTDB_HTTP=http://questdb:9000
QUESTDB_PG=questdb:8812
CLICKHOUSE_HTTP=http://clickhouse:8123
SEAWEEDFS_S3=http://seaweedfs:8333
OPENSEARCH_URL=http://opensearch:9200
AUTHN_URL=http://authn:8114
OPA_URL=http://opa:8181
```

### Docker Compose Service Template
```yaml
# Template for any service
service_name:
  image: localhost/service_name:latest
  build:
    context: ../../backend/apps/service_name
    dockerfile: Dockerfile
  volumes:
    - ../../config/backend/service_name:/app/config
    - ../../secrets:/secrets
  networks:
    - trade2026-backend
  ports:
    - "PORT:PORT"
  environment:
    - NATS_URL=${NATS_URL}
    - VALKEY_URL=${VALKEY_URL}
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:PORT/health"]
    interval: 10s
    timeout: 3s
    retries: 3
  restart: unless-stopped
  labels:
    - "com.trade2026.service=service_name"
    - "com.trade2026.cpgs.version=1.0"
```

---

## Common Issues & Solutions

### Issue 1: Network Not Found
**Error**: `network trade2026-frontend not found`
**Solution**: 
```bash
docker-compose -f infrastructure/docker/docker-compose.networks.yml up -d
```

### Issue 2: Volume Permission Denied
**Error**: `permission denied while trying to connect to /var/lib/docker/volumes`
**Solution**: Create directories with proper permissions
```bash
mkdir -p C:\ClaudeDesktop_Projects\Trade2026\data\nats
# Windows handles permissions automatically
```

### Issue 3: Port Already in Use
**Error**: `port is already allocated`
**Solution**: 
```bash
# Find what's using the port
netstat -ano | findstr :4222

# Stop conflicting service
docker stop <container_using_port>
```

### Issue 4: Services Can't Communicate
**Error**: `connection refused` when services try to reach each other
**Solution**: Verify Docker DNS resolution
```bash
docker exec service1 ping service2
# Should resolve to service2's container IP
```

---

## Success Metrics

After Phase 1 completion:

**Infrastructure**:
- [ ] 8/8 core services healthy
- [ ] All health checks passing
- [ ] Zero error logs

**Configuration**:
- [ ] All paths updated to Trade2026
- [ ] Networks configured correctly
- [ ] Environment variables set

**Validation**:
- [ ] Can publish/subscribe to NATS
- [ ] Can read/write to Valkey
- [ ] Can query QuestDB
- [ ] Can query ClickHouse
- [ ] Can write to SeaweedFS

**Documentation**:
- [ ] Phase 1 completion documented
- [ ] Issues encountered noted
- [ ] Solutions applied recorded

---

## Time Estimate

**Optimistic**: 4 hours (if everything works perfectly)
**Realistic**: 1 day (with troubleshooting)
**Pessimistic**: 2 days (if major issues)

**Recommendation**: Allocate 1 full day for Phase 1

---

## Next Phase

After Phase 1 complete → [Appendix B: Backend Migration](./appendix_B_backend.md)

---

**Status**: 📋 Template Ready

**Last Updated**: 2025-10-14
