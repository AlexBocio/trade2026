# Trade2026 Integration - Master Plan (Lean Version)

**Created**: 2025-10-14
**Status**: Ready for Execution
**Timeline**: 6-8 weeks (MVP in 3-4 weeks)

---

## 🎯 ONE-PAGE SUMMARY

### What We're Integrating

```
Trade2025 Backend (C:\Trade2025\)     ──┐
  • 20+ microservices                   │
  • 89% operational                     │
  • No frontend                         ├──→  Trade2026
                                        │    (Unified Platform)
GUI Frontend (C:\GUI\)                ──┤
  • React + TypeScript                  │
  • 50+ pages, complete                 │
  • Mock APIs only                      │
                                        │
ML Pipelines (Design only)            ──┘
  • Strategy Library
  • Default ML + PRISM Physics
```

### Project Structure

```
Trade2026/
├── frontend/         # React app (from C:\GUI\)
├── backend/          # Microservices (from C:\Trade2025\)
├── library/          # ML pipelines (NEW - to build)
├── infrastructure/   # Docker, configs
├── data/             # All persistent data
└── docs/             # Documentation
```

### 8-Phase Plan

| Phase | Name | Duration | Priority | Details |
|-------|------|----------|----------|---------|
| 1 | Foundation | Week 1 | P0-Critical | [See Appendix A](#appendix-a-foundation) |
| 2 | Backend Migration | Week 2-3 | P0-Critical | [See Appendix B](#appendix-b-backend) |
| 3 | Frontend Integration | Week 3-4 | P0-Critical | [See Appendix C](#appendix-c-frontend) |
| 4 | ML Library | Week 4-5 | P1-High | [See Appendix D](#appendix-d-ml-library) |
| 5 | PRISM Physics | Week 5-6 | P2-Optional | [See Appendix E](#appendix-e-physics) |
| 6 | Hybrid Pipeline | Week 6 | P2-Optional | [See Appendix F](#appendix-f-hybrid) |
| 7 | Testing | Week 7 | P1-High | [See Appendix G](#appendix-g-testing) |
| 8 | Documentation | Week 8 | P1-High | [See Appendix H](#appendix-h-docs) |

### Quick Start

**MVP (3-4 weeks)**: Complete Phases 1-3 only
- ✅ Backend + Frontend working together
- ✅ Real API connections
- ✅ Production-ready platform
- ⏸️ ML pipelines deferred

**Full Build (6-8 weeks)**: Complete all phases
- ✅ Everything above
- ✅ ML Strategy Library
- ✅ Default ML Pipeline
- ⏸️ PRISM Physics optional

---

## 📋 PHASE OVERVIEW

### Phase 1: Foundation (Week 1) - P0
**Goal**: Create unified directory structure and core infrastructure

**Tasks**: 5 instructions (detailed in [Appendix A](#appendix-a-foundation))
- Create Trade2026 directory structure
- Setup Docker networks (CPGS v1.0)
- Migrate core infrastructure (NATS, Valkey, databases)
- Configure unified docker-compose
- Test core services health

**Exit Criteria**:
- ✅ Directory structure exists
- ✅ 8/8 core services healthy
- ✅ Networks configured (frontend, lowlatency, backend)

#### Phase 1 Quality Assurance

**Validation Gates**:
Starting with Task 03, every task includes a validation gate that:
- Verifies all previous tasks completed successfully
- Tests integration between previous tasks
- Requires passing all validations before proceeding
- Includes mandatory STOP checkpoint

**Testing Flow Per Task**:
```
Component → Test → Integrate → Test → Deploy → Test → Validate
                                                          ↓
                                                   Validation Gate
                                                          ↓
                                                    Next Task
```

**Task-by-Task Breakdown**:

**Task 01**: Create directories
- Component: Directories created
- Test: All directories exist
- No validation gate (first task)

**Task 02**: Create networks
- Component: Networks created
- Test: Connectivity & isolation
- No validation gate yet (added in Task 03)

**Task 03**: Migrate services
- **Validation Gate**: Verify Tasks 01-02 + integration
- Component: 8 services migrated
- Test: Each service individually
- Integrate: Services use networks + directories
- Test: All services working together
- Deploy: All services operational
- Validate: Comprehensive service tests

**Task 04**: Docker Compose
- **Validation Gate**: Verify Tasks 01-03 + integration
- Component: Compose files + scripts
- Test: Each script works
- Integrate: Compose orchestrates all previous tasks
- Test: Bring up/down all services
- Deploy: Single-command deployment
- Validate: Complete platform operational

**Task 05**: Final Validation
- **Validation Gate**: Verify Tasks 01-04 + integration
- Comprehensive testing of everything
- Integration testing across all components
- Performance testing
- Documentation of all results
- **Phase 1 COMPLETE**

**Comprehensive Implementation**:
All implementations in Phase 1 must be:
- **Complete**: No shortcuts or "minimal" configurations
- **Tested**: Component, integration, performance, persistence tests
- **Documented**: Every choice explained, every result recorded
- **Official**: All components from official sources only

**Official Sources**:
All Docker images from Docker Hub official:
- NATS: `nats:2.10-alpine`
- Valkey: `valkey/valkey:8-alpine`
- QuestDB: `questdb/questdb:latest`
- ClickHouse: `clickhouse/clickhouse-server:24.9`
- SeaweedFS: `chrislusf/seaweedfs:latest`
- OpenSearch: `opensearchproject/opensearch:2`

authn and OPA built from source (official project code).

**Testing Requirements**:
Every service must pass:
1. Component test: Service works individually
2. Integration test: Service works with dependencies
3. Performance test: Latency and throughput acceptable
4. Persistence test: Data survives restart
5. Network test: Can communicate with other services

No service proceeds to next task until all tests pass.

---

### Phase 2: Backend Migration (Week 2-3) - P0
**Goal**: Move all backend services to Trade2026

**Tasks**: 10 instructions (detailed in [Appendix B](#appendix-b-backend))
- Copy 20+ backend services
- Update all configuration paths
- Build Docker images
- Create docker-compose.apps.yml
- Test each service individually

**Exit Criteria**:
- ✅ All services in Trade2026/backend/
- ✅ 18/18 services healthy
- ✅ Service-to-service communication working

---

### Phase 3: Frontend Integration (Week 3-4) - P0
**Goal**: Connect React frontend to real backend APIs

**Tasks**: 8 instructions (detailed in [Appendix C](#appendix-c-frontend))
- Copy frontend code
- Replace mock API clients with real API calls
- Setup Nginx reverse proxy
- Build frontend Docker image
- Test all API integrations

**Exit Criteria**:
- ✅ Frontend at http://localhost
- ✅ All API clients using real backends
- ✅ No mock data remaining
- ✅ UI fully functional

---

### Phase 4: ML Library (Week 4-5) - P1
**Goal**: Build Strategy & ML Library service with Default ML Pipeline

**Tasks**: 14 instructions (detailed in [Appendix D](#appendix-d-ml-library))
- Build Library registry service
- Implement CRUD API
- Build Default ML Pipeline (XGBoost)
- Setup Feast feature store
- Deploy first alpha strategy

**Exit Criteria**:
- ✅ Library service running (port 8350)
- ✅ Default ML Pipeline operational
- ✅ Feature store materialization working
- ✅ Alpha strategy generating signals

---

### Phases 5-8: Optional/Deferred
See appendices for details. These can be skipped or done later.

---

## 🚀 EXECUTION STRATEGY

### Recommended Approach

**Week 1**: Foundation
```bash
# Generate 5 instructions for Phase 1
# Execute sequentially with Claude Code
# Validate all core services healthy
```

**Week 2-3**: Backend Migration
```bash
# Generate 10 instructions for Phase 2
# Migrate services one-by-one
# Test each service individually
```

**Week 3-4**: Frontend Integration
```bash
# Generate 8 instructions for Phase 3
# Update API clients progressively
# Test each API integration
```

**Decision Point**: After Phase 3
- ✅ If working well → Continue to Phase 4 (ML Library)
- ⏸️ If issues → Fix before proceeding
- ✅ If MVP sufficient → Stop here, polish, deploy

---

## 🎯 CRITICAL SUCCESS FACTORS

### 1. Docker DNS Names (Never localhost)
❌ Bad: `nats_url: localhost:4222`
✅ Good: `nats_url: nats:4222`

### 2. Unified Data Directory
All data in: `C:\ClaudeDesktop_Projects\Trade2026\data\`

### 3. CPGS v1.0 Compliance
- Frontend: 80, 443
- Low-latency: 8000-8199
- Backend: 8300-8499

### 4. Sequential Execution
Complete one phase before starting next

### 5. Test Each Component
Before integrating with others

---

## 📊 INSTRUCTION GENERATION PLAN

### Total Instructions Needed: 45

**Group A - MVP (23 instructions)**: 
- Phase 1: 5 instructions
- Phase 2: 10 instructions
- Phase 3: 8 instructions

**Group B - ML Library (14 instructions)**:
- Phase 4: 14 instructions

**Group C - Optional (8 instructions)**:
- Phase 5-8: 8 instructions

### Generation Strategy

**Option 1: Phased Generation (Recommended)**
- Generate 5 instructions (Phase 1)
- Execute and validate
- Generate next batch when ready

**Option 2: MVP Batch**
- Generate all 23 MVP instructions
- Execute Phases 1-3
- Decide on Phase 4 later

**Option 3: Full Batch**
- Generate all 45 instructions
- Execute sequentially

---

## 💬 NEXT STEPS

### Tell Me What You Want

**A**: "Generate Phase 1 instructions (5 tasks)"
- Lowest risk, test approach first
- Can continue after validation

**B**: "Generate MVP instructions (23 tasks)"
- Backend + Frontend integration
- ML pipelines deferred

**C**: "Generate all instructions (45 tasks)"
- Full platform build
- Commit to 6-8 weeks

**D**: "I have questions about [X]"
- Ask anything
- Modify plan as needed

---

## 📚 APPENDICES (Separate Files)

**Navigation**:
- [Appendix A: Foundation Details](./appendix_A_foundation.md)
- [Appendix B: Backend Migration Details](./appendix_B_backend.md)
- [Appendix C: Frontend Integration Details](./appendix_C_frontend.md)
- [Appendix D: ML Library Details](./appendix_D_ml_library.md)
- [Appendix E: PRISM Physics Details](./appendix_E_physics.md)
- [Appendix F: Hybrid Pipeline Details](./appendix_F_hybrid.md)
- [Appendix G: Testing Details](./appendix_G_testing.md)
- [Appendix H: Documentation Details](./appendix_H_docs.md)
- [Appendix I: Configuration Reference](./appendix_I_config.md)
- [Appendix J: Docker Compose Reference](./appendix_J_compose.md)

Each appendix contains:
- Detailed task breakdown
- Code examples
- Configuration templates
- Troubleshooting guides

---

**Status**: 📋 Ready for Instruction Generation

**Main Document Size**: ~500 words (vs 29,000 words before)

**Last Updated**: 2025-10-14

---

**This lean document + appendices approach means:**
- ✅ Quick to read and understand
- ✅ Reference details only when needed
- ✅ Claude Code can read just what's necessary
- ✅ Modular and maintainable

**Ready when you are!** 🚀
