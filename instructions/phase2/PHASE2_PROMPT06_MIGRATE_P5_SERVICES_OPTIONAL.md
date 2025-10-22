# Phase 2 - Prompt 06: Migrate Priority 5 Services (ML/Optional)

**Phase**: 2 - Backend Migration  
**Prompt**: 06 of 06 (OPTIONAL)  
**Services**: serving, bt-orchestrator, ml-training, marketplace, modelops  
**Priority**: P5 (ML Services - OPTIONAL)  
**Estimated Time**: 22 hours  
**Dependencies**: Prompts 02-05 complete  
**Status**: ⏸️ OPTIONAL - **Recommend skipping for MVP**

---

## ⚠️ RECOMMENDATION: SKIP THIS PROMPT

### Why Skip Prompt 06?

**1. Not Required for MVP**
- ML services not needed for core trading
- Phase 2 MVP complete after Prompt 05
- Can trade without ML features

**2. Better to Do in Phase 4**
- Phase 4 (ML Library) will build unified ML infrastructure
- Doing now = duplicate work
- Phase 4 approach is more comprehensive

**3. Saves 22 Hours**
- Focus on Phase 3 (Frontend Integration)
- Get to production faster
- Add ML later when needed

**4. Phase 2 MVP Already Complete**
- All core services operational (Prompts 01-05)
- Full trading platform working
- Supporting services deployed

---

## 🚦 RECOMMENDED PATH

### After Prompt 05

**OPTION A (STRONGLY RECOMMENDED)**: Proceed to Phase 3
```
Phase 3: Frontend Integration
- Connect React app to backend APIs
- Build unified user interface
- Production-ready platform
- 1-2 weeks of work
```

**OPTION B**: Deploy Current MVP
```
- Current platform is production-ready
- Start paper trading
- Polish and optimize
- Add features iteratively
```

**OPTION C**: Do Prompt 06 (This prompt)
```
- 5 ML services
- 22 hours of work
- Duplicates Phase 4 work
- Not recommended
```

**My Strong Recommendation**: **Choose Option A (Phase 3)**

---

## 📋 IF YOU DECIDE TO DO PROMPT 06

### Services Overview

| Service | Port | Time | Purpose |
|---------|------|------|---------|
| serving | 8103 | 5h | ML model inference (BentoML) |
| bt-orchestrator | 8095 | 4h | Backtesting engine |
| ml-training | 8102 | 4h | Distributed training (Ray) |
| marketplace | 8350 | 3h | Strategy hosting |
| modelops | TBD | 2h | Model governance (Marquez) |

### Quick Notes

All services follow the same 10-step pattern used in Prompts 02-05.

**serving**: 
- BentoML for model serving
- Feast for feature retrieval
- MLflow for model loading
- Complex dependencies

**bt-orchestrator**:
- Strategy backtesting
- ClickHouse for historical data
- Docker sandbox for strategy execution

**ml-training**:
- Ray cluster for distributed training
- MLflow for experiment tracking
- Feature engineering

**marketplace**:
- Strategy code hosting
- Git integration
- Sandbox execution

**modelops**:
- Model lineage (Marquez)
- Model signing (Cosign)
- Governance and compliance

---

## ⏸️ DEFERRAL PLAN

### If Skipping Prompt 06 (Recommended)

**Phase 2 Complete**: After Prompt 05
- 11-13 services operational
- Core trading platform working
- Supporting services deployed

**Phase 3**: Frontend Integration
- Connect UI to backend
- Build user interface
- Production deployment

**Phase 4**: ML Library (Later)
- Unified ML infrastructure
- Strategy library
- Default ML + PRISM Physics pipelines
- Better architecture than Prompt 06

**Phase 5-8**: Optional advanced features

---

## ✅ PHASE 2 COMPLETION (WITHOUT PROMPT 06)

### What You Have After Prompt 05

**Infrastructure** (8 services):
- NATS, Valkey, QuestDB, ClickHouse, SeaweedFS, OpenSearch, authn, OPA

**Application Services** (11-13 services):
- **P1**: normalizer, sink-ticks, sink-alt
- **P2**: gateway, live-gateway
- **P3**: risk, oms
- **P4**: ptrc, feast-pipeline, execution-quality, (others optional)

**Capabilities**:
- ✅ Market data ingestion
- ✅ Real-time normalization
- ✅ Order execution (paper trading)
- ✅ Risk management
- ✅ Position tracking
- ✅ P&L calculation
- ✅ Feature store
- ✅ Reporting

**What's Missing (Can Add Later)**:
- ⏸️ ML model serving
- ⏸️ Backtesting
- ⏸️ ML training
- ⏸️ Strategy marketplace
- ⏸️ Model governance

**Status**: **PRODUCTION-READY TRADING PLATFORM** ✅

---

## 📊 PHASE 2 FINAL STATUS

### Completion Summary

**Prompts Complete**:
- ✅ Prompt 00: Validation Gate
- ✅ Prompt 01: Survey (2h)
- ✅ Prompt 02: P1 Services (8h)
- ✅ Prompt 03: P2 Services (11h)
- ✅ Prompt 04: P3 Services (14h) + CRITICAL validation
- ✅ Prompt 05: P4 Services (13h)
- ⏸️ Prompt 06: P5 Services (22h) - **SKIPPED (Recommended)**

**Total Time Invested**: 48 hours (excluding Prompt 06)
**Services Migrated**: 11-13 services (excluding P5)
**Phase 2 MVP Status**: ✅ **COMPLETE**

---

## 🚀 NEXT STEPS

### Recommended: Proceed to Phase 3

**Give Claude Code this prompt**:

```
Phase 2 MVP is complete! All core backend services are operational.

Please proceed to Phase 3: Frontend Integration

Goals:
1. Copy React frontend from C:\GUI\
2. Replace mock API clients with real backend calls
3. Setup Nginx reverse proxy
4. Build unified user interface
5. Test all integrations

This will connect the UI to our operational backend and create a complete, production-ready trading platform.

Begin with Phase 3 instructions.
```

---

## 📋 IF YOU INSIST ON DOING PROMPT 06

### Migration Steps (Brief)

**Follow same 10-step pattern as Prompts 02-05**:

1. Copy source code from Trade2025
2. Create config files
3. Update URLs (localhost → Docker names)
4. Build Docker images
5. Add to docker-compose.apps.yml (entries already exist)
6. Component testing
7. Integration testing
8. Performance validation
9. Validation gate
10. Update tracker

**Services docker-compose entries**: Already in docker-compose.apps.yml ✅

**Estimated Time**: 22 hours

**Value**: Low (will redo in Phase 4)

---

## ✅ FINAL RECOMMENDATION

### DO NOT DO PROMPT 06

**Instead**:
1. ✅ Celebrate Phase 2 MVP completion
2. ✅ Move to Phase 3 (Frontend Integration)
3. ✅ Defer ML services to Phase 4 (better architecture)

**Phase 2 is COMPLETE without Prompt 06**

**You have a fully functional trading platform** ✅

---

**Prompt Status**: ⏸️ OPTIONAL (Not Recommended)

**Recommended Next**: Phase 3 - Frontend Integration

**Phase 2 Final Status**: ✅ **MVP COMPLETE** (Prompts 01-05)
