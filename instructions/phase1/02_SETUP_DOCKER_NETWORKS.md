# Task 02: Setup Docker Networks (CPGS v1.0)

**Phase**: 1 - Foundation
**Priority**: P0-Critical
**Estimated Time**: 30 minutes
**Dependencies**: Task 01 (Directory Structure)
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
- [ ] **6-Phase Mandatory Workflow** - EVERY task follows this workflow
- [ ] **External Service Connection Pattern** - Critical for this task
- [ ] **Testing & Validation Rules** - How to validate your work
- [ ] **Documentation Standards** - What to document

**Why This Matters**: These guidelines contain critical rules about:
- ✅ How to handle errors and rollback
- ✅ Token budget management (you have limits!)
- ✅ Testing and validation requirements
- ✅ When to stop and ask for help

**Estimated Time**: 5-10 minutes to read the relevant sections

### 2. Project Context (MUST READ AFTER GUIDELINES)
**Location**: `C:\ClaudeDesktop_Projects\Trade2026\appendices\appendix_A_foundation.md`
- [ ] Read Network architecture details

**Estimated Time**: 5 minutes

---

## ⚠️ CONSEQUENCES OF NOT READING GUIDELINES

If you skip reading MASTER_GUIDELINES.md, you will:
- ❌ Miss critical error handling procedures
- ❌ Not follow the 6-Phase Workflow (required for every task)
- ❌ Risk running out of token budget mid-task
- ❌ Skip validation steps (causing failures later)
- ❌ Make mistakes that could have been avoided

**The guidelines exist to prevent failures. READ THEM FIRST.**

---

## ✅ CHECKLIST BEFORE PROCEEDING

**I confirm I have read and understood**:
- [ ] MASTER_GUIDELINES.md - New Session Startup Protocol
- [ ] MASTER_GUIDELINES.md - Core Development Rules
- [ ] MASTER_GUIDELINES.md - 6-Phase Mandatory Workflow
- [ ] MASTER_GUIDELINES.md - External Service Connection Pattern
- [ ] MASTER_GUIDELINES.md - Testing & Validation Rules
- [ ] appendix_A_foundation.md - Network architecture

**Total Reading Time**: ~15 minutes

**Only proceed to next section after completing this checklist.**

---

## ⚠️ CRITICAL RULES FOR THIS TASK

### Rule 1: CPGS v1.0 Compliance
**Communication & Port Governance Standard v1.0** must be followed exactly.

Three-lane network architecture:
- **Frontend Lane**: 172.23.0.0/16 (ports 80, 443, 5173)
- **Low-Latency Lane**: 172.22.0.0/16 (ports 8000-8199)
- **Backend Lane**: 172.21.0.0/16 (ports 8300-8499)

### Rule 2: Network Naming
Networks MUST use `trade2026-*` prefix (not trade2025)

### Rule 3: Create Networks First
Networks must exist BEFORE starting any services

---

## 📋 OBJECTIVE

Create three Docker bridge networks following CPGS v1.0 specification to enable:
1. **Service Isolation** - Different performance/security requirements per lane
2. **Inter-Lane Communication** - Services can span multiple networks
3. **Port Organization** - Clear port allocation prevents conflicts

**Why This Matters**: Proper network setup is foundational. All services depend on these networks.

---

## 🎯 CONTEXT

### CPGS v1.0 Three-Lane Architecture

```
┌─────────────────────────────────────────┐
│    Frontend Lane (172.23.0.0/16)        │
│    - Public-facing APIs                 │
│    - Web UIs                            │
│    - User authentication                │
│    Ports: 80, 443, 5173                 │
└─────────────────────────────────────────┘
              ↓ (routing)
┌─────────────────────────────────────────┐
│  Low-Latency Lane (172.22.0.0/16)       │
│    - Trading execution (sub-ms)         │
│    - NATS event streaming               │
│    - Real-time data processing          │
│    Ports: 8000-8199                     │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│    Backend Lane (172.21.0.0/16)         │
│    - Analytics & batch processing       │
│    - Databases & storage                │
│    - ML training (non-real-time)        │
│    Ports: 8300-8499                     │
└─────────────────────────────────────────┘
```

### Service Network Assignment Examples

| Service | Networks | Reason |
|---------|----------|--------|
| frontend (Nginx) | frontend | Public-facing |
| gateway | frontend, lowlatency, backend | Data ingestion spans all |
| NATS | lowlatency | Message bus performance |
| oms | frontend, lowlatency, backend | Order entry + execution + storage |
| Valkey, databases | backend | Data layer |
| authn | frontend, backend | Auth needed by all |

---

## ✅ REQUIREMENTS

### Functional Requirements
1. Create 3 Docker bridge networks
2. Assign correct subnets (CPGS v1.0)
3. Networks must allow inter-container communication
4. Networks must be external (survive docker-compose down)

### Non-Functional Requirements
- **Isolation**: Services in different lanes isolated by default
- **Performance**: Low-latency lane optimized for speed
- **Scalability**: Subnets large enough for growth (/16 = 65K hosts)

---

## 🔧 IMPLEMENTATION STEPS

### Step 1: Create Docker Compose Networks File
**Goal**: Define networks in Docker Compose format

**Actions**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker

# Create networks file
cat > docker-compose.networks.yml << 'EOF'
version: '3.8'

# CPGS v1.0 - Three-Lane Network Architecture
# Trade2026 Platform Networks

networks:
  trade2026-frontend:
    name: trade2026-frontend
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.23.0.0/16
          gateway: 172.23.0.1
    labels:
      - "com.trade2026.cpgs.version=1.0"
      - "com.trade2026.cpgs.lane=frontend"
      - "com.trade2026.cpgs.ports=80,443,5173"
    driver_opts:
      com.docker.network.bridge.name: trade2026-front

  trade2026-lowlatency:
    name: trade2026-lowlatency
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.22.0.0/16
          gateway: 172.22.0.1
    labels:
      - "com.trade2026.cpgs.version=1.0"
      - "com.trade2026.cpgs.lane=lowlatency"
      - "com.trade2026.cpgs.ports=8000-8199"
    driver_opts:
      com.docker.network.bridge.name: trade2026-lowlat

  trade2026-backend:
    name: trade2026-backend
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.21.0.0/16
          gateway: 172.21.0.1
    labels:
      - "com.trade2026.cpgs.version=1.0"
      - "com.trade2026.cpgs.lane=backend"
      - "com.trade2026.cpgs.ports=8300-8499"
    driver_opts:
      com.docker.network.bridge.name: trade2026-back
EOF
```

**Validation**:
```bash
cat docker-compose.networks.yml
# Should display the complete YAML file
```

**Checklist**:
- [ ] File created in infrastructure/docker/
- [ ] All 3 networks defined
- [ ] Subnets match CPGS v1.0 (172.23, 172.22, 172.21)
- [ ] CPGS labels present
- [ ] **Phase 1 partial: Config created** ✅

---

### Step 2: Create Networks
**Goal**: Actually create the networks in Docker

**Actions**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker

# Create networks using docker-compose
docker-compose -f docker-compose.networks.yml up -d

# Or create manually (alternative approach)
# docker network create trade2026-frontend --subnet=172.23.0.0/16
# docker network create trade2026-lowlatency --subnet=172.22.0.0/16
# docker network create trade2026-backend --subnet=172.21.0.0/16
```

**Expected Output**:
```
Creating network "trade2026-frontend" with driver "bridge"
Creating network "trade2026-lowlatency" with driver "bridge"
Creating network "trade2026-backend" with driver "bridge"
```

**Validation**:
```bash
# List networks
docker network ls | grep trade2026

# Should output:
# NETWORK ID     NAME                    DRIVER    SCOPE
# <id>           trade2026-frontend      bridge    local
# <id>           trade2026-lowlatency    bridge    local
# <id>           trade2026-backend       bridge    local
```

**Checklist**:
- [ ] 3 networks created
- [ ] No error messages
- [ ] All networks visible in `docker network ls`
- [ ] **Phase 1 complete: Networks created** ✅

---

### Step 3: Inspect Networks
**Goal**: Verify network configuration is correct

**Actions**:
```bash
# Inspect frontend network
docker network inspect trade2026-frontend

# Key checks:
# - Subnet: 172.23.0.0/16
# - Gateway: 172.23.0.1
# - Driver: bridge
# - Labels present

# Inspect lowlatency network
docker network inspect trade2026-lowlatency

# Inspect backend network
docker network inspect trade2026-backend
```

**Expected JSON Structure** (example for frontend):
```json
[
    {
        "Name": "trade2026-frontend",
        "Driver": "bridge",
        "Scope": "local",
        "IPAM": {
            "Config": [
                {
                    "Subnet": "172.23.0.0/16",
                    "Gateway": "172.23.0.1"
                }
            ]
        },
        "Labels": {
            "com.trade2026.cpgs.version": "1.0",
            "com.trade2026.cpgs.lane": "frontend"
        }
    }
]
```

**Checklist**:
- [ ] Subnets correct (172.23, 172.22, 172.21)
- [ ] Gateways correct (.0.1)
- [ ] Driver is "bridge"
- [ ] CPGS labels present
- [ ] **Phase 2 complete: Networks inspected** ✅

---

### Step 4: Test Network Connectivity
**Goal**: Verify containers can communicate within networks

**Actions**:
```bash
# Start two test containers on frontend network
docker run -d --name test1 --network trade2026-frontend alpine sleep 3600
docker run -d --name test2 --network trade2026-frontend alpine sleep 3600

# Test connectivity
docker exec test1 ping -c 3 test2

# Expected: 3 successful pings
# 64 bytes from test2.trade2026-frontend: ...

# Test DNS resolution
docker exec test1 nslookup test2

# Expected: Resolves to test2's IP in 172.23.0.0/16 range

# Cleanup test containers
docker stop test1 test2
docker rm test1 test2
```

**Validation Checks**:
```bash
# Verify cleanup
docker ps -a | grep test
# Should show no results
```

**Checklist**:
- [ ] Containers can ping each other by name
- [ ] DNS resolution works
- [ ] IP addresses in correct subnet
- [ ] Test containers cleaned up
- [ ] **Phase 3 complete: Connectivity tested** ✅

---

### Step 5: Test Network Isolation
**Goal**: Verify containers on different networks are isolated

**Actions**:
```bash
# Start containers on different networks
docker run -d --name test-front --network trade2026-frontend alpine sleep 3600
docker run -d --name test-back --network trade2026-backend alpine sleep 3600

# Try to ping across networks (should fail)
docker exec test-front ping -c 3 test-back

# Expected: "ping: bad address 'test-back'" or timeout
# This is CORRECT behavior - networks are isolated

# Cleanup
docker stop test-front test-back
docker rm test-front test-back
```

**Why This Matters**: Isolation is a key CPGS v1.0 feature. Services must explicitly join multiple networks to communicate across lanes.

**Checklist**:
- [ ] Cross-network ping fails (expected behavior)
- [ ] Test containers cleaned up
- [ ] **Phase 4 complete: Isolation verified** ✅

---

### Step 6: Create Network Documentation
**Goal**: Document network configuration for reference

**Actions**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026\docs\architecture

# Create network documentation
cat > NETWORK_ARCHITECTURE.md << 'EOF'
# Trade2026 Network Architecture

**Standard**: CPGS v1.0 (Communication & Port Governance Standard)
**Last Updated**: 2025-10-14

## Three-Lane Architecture

Trade2026 uses three isolated Docker bridge networks:

### 1. Frontend Lane (trade2026-frontend)
**Subnet**: 172.23.0.0/16
**Gateway**: 172.23.0.1
**Port Range**: 80, 443, 5173 (dev)

**Purpose**: Public-facing services and user interfaces

**Services**:
- Nginx (reverse proxy)
- React frontend
- authn (authentication)
- Public API endpoints

**Characteristics**:
- Direct internet access
- Rate limiting enforced
- CORS policies applied

---

### 2. Low-Latency Lane (trade2026-lowlatency)
**Subnet**: 172.22.0.0/16
**Gateway**: 172.22.0.1
**Port Range**: 8000-8199

**Purpose**: High-performance, real-time operations

**Services**:
- NATS (message bus)
- normalizer (data processing)
- gateway (market data ingestion)
- Real-time execution path

**Characteristics**:
- Optimized for sub-millisecond latency
- Critical path for trading
- Minimal overhead

---

### 3. Backend Lane (trade2026-backend)
**Subnet**: 172.21.0.0/16
**Gateway**: 172.21.0.1
**Port Range**: 8300-8499

**Purpose**: Data storage, analytics, ML training

**Services**:
- Valkey (cache)
- QuestDB (time-series)
- ClickHouse (analytics)
- SeaweedFS (object storage)
- OpenSearch (search)
- ML training services
- Batch processing

**Characteristics**:
- High throughput over low latency
- Large data volumes
- Non-real-time operations

---

## Multi-Network Services

Some services span multiple networks:

| Service | Networks | Reason |
|---------|----------|--------|
| **gateway** | frontend, lowlatency, backend | API + data ingestion + storage |
| **oms** | frontend, lowlatency, backend | Order entry + execution + persistence |
| **authn** | frontend, backend | Auth needed across all services |
| **risk** | frontend, lowlatency, backend | Pre-trade checks + monitoring + storage |

---

## Network Access Rules

### Rule 1: Service Discovery via DNS
**Always use**: Service name (e.g., `nats:4222`)
**Never use**: `localhost`, `127.0.0.1`, or IPs

### Rule 2: Port Allocation
- Frontend: 80, 443, 5173
- Low-latency: 8000-8199
- Backend: 8300-8499

### Rule 3: Cross-Lane Communication
Services must explicitly join multiple networks to communicate across lanes.

Example:
```yaml
services:
  oms:
    networks:
      - trade2026-frontend
      - trade2026-lowlatency
      - trade2026-backend
```

### Rule 4: Network Isolation
By default, services on different networks CANNOT communicate.
This is intentional for security and performance.

---

## Testing Networks

### Test Connectivity
```bash
docker run --rm --network trade2026-frontend alpine ping -c 3 <service>
```

### Test DNS Resolution
```bash
docker run --rm --network trade2026-frontend alpine nslookup <service>
```

### Test Isolation
```bash
# Should fail (expected)
docker run --rm --network trade2026-frontend alpine ping -c 3 service-on-backend
```

---

## Troubleshooting

### Issue: Service can't reach another service
**Check**: Are both services on the same network?
**Solution**: Add both services to required networks in docker-compose

### Issue: DNS resolution fails
**Check**: Using service name (not localhost/IP)?
**Solution**: Always use Docker service names

### Issue: Port conflicts
**Check**: Port within correct range?
**Solution**: Use CPGS v1.0 port allocation

---

## Labels

All networks have CPGS v1.0 labels:
```yaml
labels:
  - "com.trade2026.cpgs.version=1.0"
  - "com.trade2026.cpgs.lane=<lane_name>"
  - "com.trade2026.cpgs.ports=<port_range>"
```

---

**Status**: Complete
**Compliance**: CPGS v1.0 ✅
EOF
```

**Validation**:
```bash
cat NETWORK_ARCHITECTURE.md
# Should display complete documentation
```

**Checklist**:
- [ ] Documentation created
- [ ] All lanes documented
- [ ] Rules documented
- [ ] Troubleshooting guide included
- [ ] **Phase 5 complete: Documentation** ✅

---

### Step 7: Update Project Status
**Goal**: Record network setup completion

**Actions**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026

# Update README
# (This step records progress for tracking)
```

**Document in task completion summary**:
- Networks created: trade2026-frontend, trade2026-lowlatency, trade2026-backend
- Subnets: 172.23.0.0/16, 172.22.0.0/16, 172.21.0.0/16
- CPGS v1.0 compliant: ✅
- Documentation: NETWORK_ARCHITECTURE.md created

**Checklist**:
- [ ] Progress documented
- [ ] **Phase 6 complete: Status updated** ✅

---

## ✅ ACCEPTANCE CRITERIA

The task is complete when ALL of the following are true:

### Networks Created
- [ ] trade2026-frontend exists (172.23.0.0/16)
- [ ] trade2026-lowlatency exists (172.22.0.0/16)
- [ ] trade2026-backend exists (172.21.0.0/16)

### Configuration
- [ ] docker-compose.networks.yml created
- [ ] CPGS v1.0 labels applied
- [ ] Subnets and gateways correct

### Testing
- [ ] Connectivity test passed
- [ ] Isolation test passed
- [ ] DNS resolution works

### Documentation
- [ ] NETWORK_ARCHITECTURE.md created
- [ ] Network rules documented
- [ ] Troubleshooting guide included

---

## 🔄 ROLLBACK PLAN

If networks need to be removed:

**Remove Networks**:
```bash
# Stop any containers using the networks first
docker-compose down

# Remove networks
docker network rm trade2026-frontend
docker network rm trade2026-lowlatency
docker network rm trade2026-backend

# Or use compose
docker-compose -f docker-compose.networks.yml down
```

**Recreate**:
```bash
# Re-run Step 2
docker-compose -f docker-compose.networks.yml up -d
```

---

## 📝 NOTES FOR CLAUDE CODE

### Key Points
- Networks are foundational - all services depend on them
- CPGS v1.0 compliance is mandatory
- Use exact subnet ranges specified
- Test both connectivity AND isolation

### Common Issues

**Issue 1: Network already exists**
```bash
Error: network with name trade2026-frontend already exists
```
**Solution**: That's OK if this is a re-run. Verify with `docker network ls`

**Issue 2: Subnet conflict**
```bash
Error: Pool overlaps with other networks
```
**Solution**: Another network uses 172.2x.0.0/16. Remove conflicting networks or use different subnet.

**Issue 3: Permission denied**
```bash
Error: permission denied
```
**Solution**: Run Docker with appropriate permissions. On Windows, Docker Desktop should handle this.

### Time Estimate
- Optimistic: 15 minutes
- Realistic: 30 minutes
- Pessimistic: 1 hour (if troubleshooting subnet conflicts)

---

## 📊 SUCCESS METRICS

After completion:
- ✅ 3 networks operational
- ✅ CPGS v1.0 compliant
- ✅ Connectivity verified
- ✅ Isolation verified
- ✅ Documentation complete
- ✅ Ready for service deployment

---

**Status**: ⏳ Pending

**Next Task**: `03_MIGRATE_CORE_INFRASTRUCTURE.md`

**Last Updated**: 2025-10-14
