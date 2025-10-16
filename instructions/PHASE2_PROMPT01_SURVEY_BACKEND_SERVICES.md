# Phase 2 Task 01: Survey and Document Backend Services

**Phase**: 2 - Backend Migration
**Task**: 01 of 10
**Priority**: P0-Critical
**Estimated Time**: 2 hours
**Dependencies**: Phase 1 Complete, Validation Gate Passed
**Created**: 2025-10-14

---

# 🛑 STOP - READ THIS FIRST 🛑

## MANDATORY READING BEFORE ANY WORK

**YOU MUST READ THESE FILES COMPLETELY**:

### 1. MASTER_GUIDELINES.md (CRITICAL)
**Location**: `C:\ClaudeDesktop_Projects\ClaudeKnowledge\MASTER_GUIDELINES.md`

**READ THESE SECTIONS**:
- [ ] New Session Startup Protocol
- [ ] Core Development Rules (Component Isolation, Read Before Write)
- [ ] 6-Phase Mandatory Workflow (IMPLEMENT → TEST → INTEGRATE → TEST → DEPLOY → VALIDATE)
- [ ] Testing & Validation Rules
- [ ] Validation Gates Between Tasks
- [ ] Comprehensive Implementation Requirements
- [ ] Official Sources Only
- [ ] Documentation Standards

**Time**: 10-15 minutes

### 2. Phase 1 Validation Results
**Location**: `C:\ClaudeDesktop_Projects\Trade2026\instructions\PHASE2_00_VALIDATION_GATE.md`

- [ ] Confirm all Phase 1 validation checks passed
- [ ] Verify you have 26/26 required checks complete

**Time**: 5 minutes

### 3. Project Context
**Location**: `C:\ClaudeDesktop_Projects\Backend_TRADE2025_BRIEFING.md`

- [ ] Read Executive Summary
- [ ] Read Application Services section
- [ ] Understand current Trade2025 architecture

**Time**: 10 minutes

---

## 🚦 VALIDATION GATE - VERIFY PHASE 1 COMPLETE

### MANDATORY: Run Phase 1 Validation First

**Before starting this task, YOU MUST**:

1. Open: `C:\ClaudeDesktop_Projects\Trade2026\instructions\PHASE2_00_VALIDATION_GATE.md`
2. Run ALL validation checks
3. Confirm 26/26 checks passed
4. Document results in validation gate file

**IF ANY CHECK FAILS**:
- ❌ STOP - Do NOT proceed
- Fix Phase 1 issues
- Re-run validation
- Only proceed when ALL pass

**Proceed/Stop Decision**:
- ✅ YES (26/26 passed) → Continue to OBJECTIVE
- ❌ NO (any failed) → STOP and fix Phase 1

---

## 📋 OBJECTIVE

**Goal**: Survey all backend services in Trade2025, document their purpose, dependencies, and configuration requirements to plan migration to Trade2026.

**Why This Matters**: 
- We need to know EXACTLY what services exist before migrating
- Understanding dependencies prevents broken migrations
- Proper documentation ensures nothing is missed
- Creates migration checklist for subsequent tasks

**Deliverables**:
1. Complete service inventory (BACKEND_SERVICES_INVENTORY.md)
2. Dependency map (service → service dependencies)
3. Configuration requirements per service
4. Migration priority order
5. Estimated migration effort per service

---

## 🎯 CONTEXT

### Current State
- **Location**: `C:\Trade2025\trading\apps\` (20+ microservices)
- **Status**: 89% operational (16/18 services healthy)
- **Architecture**: Docker Compose orchestration
- **Configuration**: Various YAML/JSON files per service

### What We're Doing
Systematically catalog every backend service to understand:
- What it does (purpose)
- What it depends on (NATS, databases, other services)
- What ports it uses
- What configuration it needs
- What data it stores
- Which CPGS network lane it belongs to

### What We're NOT Doing
- NOT migrating services yet (that's tasks 02-09)
- NOT modifying any code
- NOT starting any services
- ONLY surveying and documenting

---

## ✅ REQUIREMENTS

### Functional Requirements
1. Identify all backend services in Trade2025
2. Document each service's purpose and function
3. Map all service dependencies
4. Identify configuration files per service
5. Determine CPGS network assignment per service
6. Create migration priority order

### Non-Functional Requirements
- **Completeness**: Every service documented
- **Accuracy**: Correct dependencies and configs
- **Clarity**: Clear service descriptions
- **Actionable**: Migration checklist ready for next tasks

---

## 🔧 IMPLEMENTATION STEPS

### Step 1: List All Backend Services

**Goal**: Get complete list of services from Trade2025

**Actions**:

```bash
# Navigate to Trade2025 apps directory
cd C:\Trade2025\trading\apps

# List all service directories
ls -la

# Count services
ls -la | grep "^d" | wc -l

# For each service directory, check for Dockerfile
for dir in */; do
    if [ -f "$dir/Dockerfile" ]; then
        echo "$dir: Has Dockerfile"
    fi
done
```

**Create service list file**:

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\docs

# Create initial inventory file
cat > BACKEND_SERVICES_INVENTORY.md << 'EOF'
# Backend Services Inventory

**Source**: C:\Trade2025\trading\apps\
**Survey Date**: 2025-10-14
**Purpose**: Complete catalog for Trade2026 migration

---

## Services List

| # | Service Name | Directory | Dockerfile | Status |
|---|--------------|-----------|------------|--------|

EOF
```

**Checklist**:
- [ ] All service directories listed
- [ ] Dockerfile presence noted
- [ ] Service count recorded
- [ ] Initial inventory file created

---

### Step 2: Document Each Service

**Goal**: For each service, gather comprehensive information

**For EACH service, document**:

1. **Service Name & Purpose**
2. **Port(s) Used**
3. **Dependencies**:
   - Infrastructure (NATS, Valkey, databases)
   - Other services
4. **Configuration Files**:
   - config.yaml location
   - Environment variables
5. **Data Storage**: What data does it persist?
6. **Network Lane**: Frontend / Lowlatency / Backend (CPGS v1.0)
7. **Build Requirements**: Special dependencies?

**Template per service**:

```markdown
### [Service Name]

**Purpose**: [What does this service do?]

**Port(s)**: [e.g., 8301]

**Dependencies**:
- Infrastructure: [e.g., NATS, Valkey, QuestDB]
- Services: [e.g., depends on normalizer]

**Configuration**:
- Config file: [path]
- Key settings: [important configs]

**Data**: [What data does it store?]

**CPGS Network**: [frontend / lowlatency / backend]

**Migration Priority**: [1-5, where 1=first, 5=last]

**Notes**: [Special considerations]

---
```

**Read source files to understand each service**:

```bash
# For each service, check these files
cd C:\Trade2025\trading\apps\[service-name]

# 1. Check main application file
ls -la *.py src/*.py app/*.py

# 2. Check configuration
cat config/*.yaml 2>/dev/null
cat config.yaml 2>/dev/null

# 3. Check Dockerfile for port and dependencies
cat Dockerfile

# 4. Check requirements for Python dependencies
cat requirements.txt 2>/dev/null
cat pyproject.toml 2>/dev/null

# 5. Check for README
cat README.md 2>/dev/null
```

**Checklist per service**:
- [ ] Service purpose identified
- [ ] Port number documented
- [ ] Dependencies mapped
- [ ] Configuration files located
- [ ] Data storage identified
- [ ] Network lane assigned
- [ ] Migration priority set

---

### Step 3: Map Service Dependencies

**Goal**: Create dependency graph to determine migration order

**Create dependency map**:

```markdown
## Service Dependency Graph

### Core Infrastructure Dependencies
Services depending on core infrastructure:
- **NATS**: [list services]
- **Valkey**: [list services]
- **QuestDB**: [list services]
- **ClickHouse**: [list services]
- **OpenSearch**: [list services]

### Service-to-Service Dependencies
Services depending on other services:
- **gateway** → [depends on: X, Y, Z]
- **normalizer** → [depends on: NATS]
- **oms** → [depends on: gateway, risk, normalizer]
- [continue for all services]

### Reverse Dependencies
Who depends on each service:
- **gateway** ← [used by: oms, live-gateway, ptrc]
- **normalizer** ← [used by: sink-ticks, sink-alt]
- [continue for all services]
```

**Determine migration order**:

**Migration Phases**:
1. **Phase 1**: No dependencies on other app services (only infrastructure)
2. **Phase 2**: Depends on Phase 1 services
3. **Phase 3**: Depends on Phase 1 & 2 services
4. **Phase 4**: Complex dependencies
5. **Phase 5**: Optional / Low priority

**Checklist**:
- [ ] All dependencies mapped
- [ ] Reverse dependencies documented
- [ ] Migration order determined
- [ ] Dependencies grouped by phase

---

### Step 4: Identify Configuration Requirements

**Goal**: Document what configuration each service needs

**For each service, identify**:

1. **Environment Variables**:
   - Required vs optional
   - Default values
   - Sensitive values (passwords, keys)

2. **Configuration Files**:
   - YAML files needed
   - JSON files needed
   - Location in Trade2026

3. **Secrets**:
   - API keys
   - Passwords
   - Certificates
   - JWT keys

4. **External Dependencies**:
   - External APIs (Binance, Alpaca, etc.)
   - External databases
   - External services

**Create configuration checklist**:

```markdown
## Configuration Requirements Per Service

### [Service Name]

**Environment Variables**:
- `NATS_URL` (required): nats://nats:4222
- `VALKEY_URL` (required): redis://valkey:6379
- [continue...]

**Config Files**:
- `config/[service]/config.yaml`: [contents]
- `secrets/[service].env`: [sensitive vars]

**Secrets Needed**:
- [ ] API keys: [which ones]
- [ ] Passwords: [which ones]
- [ ] Certificates: [which ones]

**External Dependencies**:
- Binance API (if applicable)
- [others...]
```

**Checklist**:
- [ ] All environment variables documented
- [ ] All config files identified
- [ ] All secrets cataloged
- [ ] External dependencies noted

---

### Step 5: Assign CPGS Network Lanes

**Goal**: Determine which network(s) each service should use

**CPGS v1.0 Guidelines**:
- **Frontend Lane** (172.23.0.0/16): Public-facing APIs, authentication
- **Lowlatency Lane** (172.22.0.0/16): Real-time data, trading execution
- **Backend Lane** (172.21.0.0/16): Analytics, batch processing, storage

**Assignment Rules**:
1. If service has **public API** → Frontend lane
2. If service handles **real-time trading** → Lowlatency lane
3. If service does **analytics/storage** → Backend lane
4. Services can be on **multiple lanes** if needed

**Example assignments**:

```markdown
## CPGS Network Assignments

### Frontend Lane Services
- authn (authentication)
- gateway (external API)
- oms (order entry API)
- live-gateway (WebSocket API)
- serving (ML serving API)

### Lowlatency Lane Services
- NATS (already assigned)
- normalizer (data processing)
- execution (trade execution)
- risk (pre-trade risk)

### Backend Lane Services
- All databases (already assigned)
- sink-ticks (data storage)
- sink-alt (data storage)
- analytics services
- batch processes

### Multi-Lane Services
- oms: frontend (API) + lowlatency (execution) + backend (storage)
- gateway: frontend (API) + lowlatency (data feed)
- risk: frontend (API) + lowlatency (checks) + backend (storage)
```

**Checklist**:
- [ ] Every service assigned to network lane(s)
- [ ] Assignments follow CPGS v1.0 rules
- [ ] Multi-lane services justified
- [ ] Network diagram updated

---

### Step 6: Estimate Migration Effort

**Goal**: Estimate time/complexity per service for planning

**Complexity Factors**:
- **Simple** (1-2 hours): Stateless, few dependencies, standard config
- **Medium** (3-4 hours): Stateful, moderate dependencies, custom config
- **Complex** (5-8 hours): Many dependencies, complex config, external APIs
- **Very Complex** (8+ hours): Critical path, intricate dependencies, extensive testing

**Create effort matrix**:

```markdown
## Migration Effort Estimates

| Service | Complexity | Est. Time | Rationale |
|---------|------------|-----------|-----------|
| normalizer | Simple | 2 hours | Stateless, only NATS dependency |
| gateway | Complex | 6 hours | External APIs, multi-lane, critical |
| oms | Very Complex | 8 hours | Central hub, many dependencies |
| sink-ticks | Medium | 3 hours | Database writes, config |
| [continue...] | | | |

**Total Estimated Time**: [sum] hours
**Total Services**: [count]
**Average per Service**: [average] hours
```

**Checklist**:
- [ ] Complexity assessed per service
- [ ] Time estimates realistic
- [ ] Rationale provided
- [ ] Total effort calculated

---

### Step 7: Create Migration Checklist

**Goal**: Actionable checklist for Tasks 02-09

**Create prioritized migration list**:

```markdown
## Backend Services Migration Checklist

### Priority 1: Core Data Services (No app dependencies)
- [ ] normalizer (Task 02)
- [ ] sink-ticks (Task 03)
- [ ] sink-alt (Task 04)

### Priority 2: Gateway Services
- [ ] gateway (Task 05)
- [ ] live-gateway (Task 06)

### Priority 3: Trading Core
- [ ] oms (Task 07)
- [ ] risk (Task 07)
- [ ] execution (Task 07)

### Priority 4: Supporting Services
- [ ] ptrc (Task 08)
- [ ] compliance (Task 08)
- [ ] analytics (Task 08)

### Priority 5: Optional/Advanced
- [ ] serving (ML) (Task 09)
- [ ] bt-orchestrator (Backtesting) (Task 09)
- [ ] [others] (Task 09)

**Migration Strategy Per Priority**:
- Priority 1: Can migrate in parallel, no cross-dependencies
- Priority 2: Depends on Priority 1 complete
- Priority 3: Depends on Priority 1 & 2 complete
- Priority 4: Depends on Priority 1-3 complete
- Priority 5: Depends on all above complete
```

**Checklist**:
- [ ] Services grouped by priority
- [ ] Migration order logical
- [ ] Dependencies respected
- [ ] Tasks assigned (02-09)

---

### Step 8: Document Trade2025 Current State

**Goal**: Snapshot of what's currently running

**Check Trade2025 status**:

```bash
# Check if Trade2025 services are running
cd C:\Trade2025

# Check docker-compose status
docker-compose ps

# Check service health
docker-compose ps --services | while read service; do
    echo "$service: $(docker inspect $service --format='{{.State.Health.Status}}' 2>/dev/null || echo 'no healthcheck')"
done

# Check ports in use
docker-compose ps --format "table {{.Name}}\t{{.Ports}}"
```

**Document findings**:

```markdown
## Trade2025 Current State (2025-10-14)

**Services Running**: [count]
**Services Healthy**: [count]
**Services with Issues**: [count]

### Running Services
- [service 1]: healthy
- [service 2]: healthy
- [service 3]: unhealthy (reason)

### Port Allocations
- [service]: port XXXX
- [continue...]

### Known Issues
- gateway: External API HTTP 451 (geo-restriction)
- opa: Cosmetic healthcheck (functional)

### Notes
- [Any important observations]
```

**Checklist**:
- [ ] Current status documented
- [ ] Running services listed
- [ ] Health status recorded
- [ ] Known issues documented

---

### Step 9: Create Migration Risk Assessment

**Goal**: Identify potential migration risks

**Risk Categories**:
1. **Service Dependencies**: Breaking changes if order wrong
2. **Data Migration**: Data loss or corruption risks
3. **Configuration**: Missing or incorrect configs
4. **External APIs**: API keys, rate limits, geo-restrictions
5. **Testing**: Insufficient testing causing failures

**Create risk matrix**:

```markdown
## Migration Risk Assessment

### High Risk Services
| Service | Risk | Impact | Mitigation |
|---------|------|--------|------------|
| oms | High | Critical trading disruption | Extensive testing, rollback plan |
| gateway | High | Data feed loss | External API validation, fallback |

### Medium Risk Services
| Service | Risk | Impact | Mitigation |
|---------|------|--------|------------|
| normalizer | Medium | Data processing delays | Thorough testing, monitoring |

### Low Risk Services
| Service | Risk | Impact | Mitigation |
|---------|------|--------|------------|
| sink-ticks | Low | Historical data only | Backup, verify writes |

### Risk Mitigation Strategies
1. **Test each service individually** before integration
2. **Keep Trade2025 running** during migration for fallback
3. **Migrate non-critical services first** to test process
4. **Comprehensive validation** at each step
5. **Document rollback procedures** per service
```

**Checklist**:
- [ ] Risks identified per service
- [ ] Impact assessed
- [ ] Mitigation strategies defined
- [ ] Rollback plans noted

---

### Step 10: Finalize and Review Inventory

**Goal**: Complete, accurate, review-ready documentation

**Final deliverables checklist**:

```markdown
## Deliverables Review Checklist

### BACKEND_SERVICES_INVENTORY.md
- [ ] All services documented (complete)
- [ ] Purpose clear for each service
- [ ] Dependencies accurate
- [ ] Configuration requirements complete
- [ ] Network assignments correct
- [ ] Migration priorities set

### Dependency graph
- [ ] All dependencies mapped
- [ ] Reverse dependencies shown
- [ ] Migration order logical

### Configuration requirements
- [ ] Environment variables documented
- [ ] Config files identified
- [ ] Secrets cataloged

### CPGS network assignments
- [ ] Every service assigned
- [ ] Assignments justified
- [ ] Follows CPGS v1.0 rules

### Migration checklist
- [ ] Prioritized list created
- [ ] Grouped by dependencies
- [ ] Tasks assigned (02-09)

### Risk assessment
- [ ] Risks identified
- [ ] Mitigation strategies defined
- [ ] Rollback plans noted

### Effort estimates
- [ ] Complexity assessed
- [ ] Time estimated
- [ ] Total effort calculated
```

**Validation**:
- [ ] All deliverables complete
- [ ] Documentation clear and accurate
- [ ] Ready for Phase 2 Task 02

---

## 📊 ACCEPTANCE CRITERIA

Task is complete when ALL of the following are true:

### Documentation Complete
- [ ] BACKEND_SERVICES_INVENTORY.md created
- [ ] Every service documented with all required fields
- [ ] Dependency graph complete
- [ ] Migration checklist created
- [ ] Risk assessment complete

### Accuracy Verified
- [ ] Service purposes accurate
- [ ] Dependencies correctly mapped
- [ ] Configuration requirements complete
- [ ] Network assignments follow CPGS v1.0

### Actionable Outputs
- [ ] Migration priority order clear
- [ ] Next tasks (02-09) well-defined
- [ ] Effort estimates realistic
- [ ] Risk mitigation strategies defined

### Quality Standards
- [ ] No services missed
- [ ] No incomplete documentation
- [ ] No contradictory information
- [ ] Clear and professional writing

---

## 🔄 ROLLBACK PLAN

If this task needs to be restarted:

**No rollback needed** - this is a documentation task only.
- Delete `BACKEND_SERVICES_INVENTORY.md`
- Re-run survey from Step 1
- No system changes made

---

## 📝 NOTES FOR CLAUDE

### Key Points
- This is **ONLY documentation** - no code changes
- Be **thorough** - completeness is critical
- **Read source files** to understand each service
- **Follow CPGS v1.0** for network assignments
- **Prioritize correctly** - dependencies matter

### Common Issues
- **Issue**: Service purpose unclear
  - **Solution**: Read main Python file, README, docstrings

- **Issue**: Dependencies not obvious
  - **Solution**: Check Dockerfile, config files, imports

- **Issue**: Configuration files scattered
  - **Solution**: Search recursively in service directory

### Time Management
- **Optimistic**: 1.5 hours (if services well-documented)
- **Realistic**: 2 hours (normal case)
- **Pessimistic**: 3 hours (if discovery needed)

---

## 📊 SUCCESS METRICS

After completion:
- ✅ Complete inventory of all backend services
- ✅ Clear understanding of dependencies
- ✅ Ready-to-execute migration plan
- ✅ Risk assessment complete
- ✅ Ready for Task 02 (first service migration)

---

## 🔄 UPDATE COMPLETION TRACKER

**After completing this task**:

1. Open `C:\ClaudeDesktop_Projects\Trade2026\COMPLETION_TRACKER.md`
2. Update Phase 2 Task 01 status to ✅ Complete
3. Mark all sub-steps as complete [x]
4. Update "Last Updated" timestamp
5. Add session log entry

---

**Status**: ⏸️ Not Started

**Next Task**: Phase 2 Task 02 - Migrate First Service

**Last Updated**: 2025-10-14
