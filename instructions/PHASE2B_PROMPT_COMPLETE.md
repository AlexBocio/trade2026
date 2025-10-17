# PHASE 2B PROMPT - Supporting Services Migration

**For**: Claude Code  
**Phase**: 2B - Backend Migration (Supporting Services)  
**Services**: ptrc, pnl, hot_cache, questdb_writer, feast-pipeline, execution-quality  
**Estimated Time**: 16 hours  
**Prerequisites**: Phase 2A complete (risk, oms, exeq operational)  
**Status**: Ready to Execute After Phase 2A

---

## 🎯 OBJECTIVE

Migrate and deploy supporting services that provide P&L calculation, reporting, compliance, data optimization, and analytics.

These services are non-critical for basic trading but essential for production operations.

---

## 📋 SERVICES TO MIGRATE

### Group 1: P&L and Reporting (7 hours)

#### 1.1 ptrc (Post-Trade, Risk & Compliance)
- **Port**: 8109 (health), 9109 (metrics)
- **Priority**: P4 (Medium)
- **Source**: C:\Trade2025\trading\apps\ptrc\
- **Dependencies**: NATS, QuestDB, ClickHouse, SeaweedFS
- **Purpose**: Position tracking, P&L, reconciliation, compliance
- **Complexity**: High (multi-store system)

#### 1.2 pnl (Profit & Loss Calculator)
- **Port**: 8100
- **Priority**: P2 (Medium)
- **Source**: C:\Trade2025\trading\apps\pnl\
- **Dependencies**: QuestDB, Valkey, PTRC
- **Purpose**: Real-time P&L calculation, position valuation
- **Complexity**: Medium

### Group 2: Data Optimization (4 hours)

#### 2.1 hot_cache (Hot Data Caching)
- **Port**: 8088
- **Priority**: P2 (Medium)
- **Source**: C:\Trade2025\trading\apps\hot_cache\
- **Dependencies**: Valkey, QuestDB
- **Purpose**: Performance optimization, recent bars/positions caching
- **Complexity**: Low

#### 2.2 questdb_writer (Optimized Batch Writer)
- **Port**: 8090
- **Priority**: P2 (Medium)
- **Source**: C:\Trade2025\trading\apps\questdb_writer\
- **Dependencies**: NATS, QuestDB
- **Purpose**: Batch write optimization for QuestDB
- **Complexity**: Low

### Group 3: Analytics & ML Support (5 hours)

#### 3.1 feast-pipeline (Feature Store Pipeline)
- **Port**: 8104
- **Priority**: P4 (Low)
- **Source**: C:\Trade2025\trading\apps\feast_pipeline\
- **Dependencies**: NATS, QuestDB, Feast
- **Purpose**: Feature materialization for ML
- **Complexity**: Medium

#### 3.2 execution-quality (Execution Analytics)
- **Port**: 8096
- **Priority**: P4 (Low)
- **Source**: C:\Trade2025\trading\apps\execution_quality\
- **Dependencies**: NATS, QuestDB, ClickHouse
- **Purpose**: Execution quality monitoring and analytics
- **Complexity**: Low

---

## 🔄 UNIVERSAL MIGRATION PATTERN

For EACH service, follow the same 10-step pattern from Phase 2A:

### Quick Reference - 10 Steps
1. **Survey Service** - Check if code exists, document
2. **Create Configuration** - config.yaml with correct ports
3. **Verify/Update Code** - Fix localhost → service names
4. **Verify Dockerfile** - Check health checks, ports
5. **Build Docker Image** - docker build -t localhost/{service}:latest
6. **Verify docker-compose Entry** - Check service definition
7. **Start Service** - docker-compose up -d {service}
8. **Component Testing** - Health check, logs, basic functionality
9. **Integration Testing** - NATS, Redis, DB connectivity, service communication
10. **Validation Gate** - All tests pass → proceed

---

## 🚀 EXECUTION ORDER

### Phase 2B-1: PTRC Service (4 hours)

**Prerequisites**:
- [ ] Phase 2A complete (risk, oms, exeq operational)
- [ ] ClickHouse healthy
- [ ] QuestDB healthy
- [ ] SeaweedFS healthy

**Special Considerations**:
- Complex multi-module system (PnL, tax, risk, compliance)
- Multiple data stores
- May have multiple entry points

**Execute**:
1. Survey ptrc directory structure
2. Identify all modules and dependencies
3. Create comprehensive config.yaml
4. Configure all data store connections
5. Build and deploy
6. Test each module independently

**Validation**:
```bash
curl http://localhost:8109/health
curl http://localhost:8109/pnl/summary
curl http://localhost:8109/positions
curl http://localhost:8109/reports
```

**Success Criteria**:
- [ ] PTRC service healthy
- [ ] P&L calculation working
- [ ] Position tracking accurate
- [ ] Reports generating
- [ ] All data stores connected

---

### Phase 2B-2: PNL Service (3 hours)

**Prerequisites**:
- [ ] PTRC service operational
- [ ] Phase 2A services operational

**Execute**:
1. Follow 10-step pattern
2. Configure PTRC integration
3. Set up position data subscriptions
4. Configure price data sources

**Validation**:
```bash
curl http://localhost:8100/health
curl http://localhost:8100/pnl/realtime
curl http://localhost:8100/pnl/history
```

**Success Criteria**:
- [ ] PNL service healthy
- [ ] Real-time P&L calculation
- [ ] Position valuation accurate
- [ ] Historical P&L tracking

---

### Phase 2B-3: Hot Cache Service (2 hours)

**Prerequisites**:
- [ ] Valkey healthy
- [ ] QuestDB healthy

**Execute**:
1. Follow 10-step pattern
2. Configure cache policies
3. Set up data refresh intervals
4. Test cache hit rates

**Validation**:
```bash
curl http://localhost:8088/health
curl http://localhost:8088/cache/stats
```

**Success Criteria**:
- [ ] Hot cache service healthy
- [ ] Caching recent bars
- [ ] Cache hit rate > 80%
- [ ] Data freshness acceptable

---

### Phase 2B-4: QuestDB Writer Service (2 hours)

**Prerequisites**:
- [ ] NATS healthy
- [ ] QuestDB healthy

**Execute**:
1. Follow 10-step pattern
2. Configure batch sizes
3. Set up write intervals
4. Test write throughput

**Validation**:
```bash
curl http://localhost:8090/health
curl http://localhost:8090/stats
```

**Success Criteria**:
- [ ] Writer service healthy
- [ ] Batching writes efficiently
- [ ] No write errors
- [ ] Throughput > 10k writes/sec

---

### Phase 2B-5: Feast Pipeline Service (3 hours)

**Prerequisites**:
- [ ] NATS healthy
- [ ] QuestDB healthy
- [ ] Feast configured (if separate)

**Execute**:
1. Follow 10-step pattern
2. Configure feature definitions
3. Set up materialization schedule
4. Test feature availability

**Validation**:
```bash
curl http://localhost:8104/health
curl http://localhost:8104/features/status
```

**Success Criteria**:
- [ ] Feast pipeline healthy
- [ ] Features materializing
- [ ] Feature store accessible
- [ ] No materialization errors

---

### Phase 2B-6: Execution Quality Service (2 hours)

**Prerequisites**:
- [ ] NATS healthy
- [ ] QuestDB healthy
- [ ] ClickHouse healthy

**Execute**:
1. Follow 10-step pattern
2. Configure quality metrics
3. Set up analytics dashboards
4. Test metric collection

**Validation**:
```bash
curl http://localhost:8096/health
curl http://localhost:8096/metrics/execution
curl http://localhost:8096/analytics/summary
```

**Success Criteria**:
- [ ] Execution quality service healthy
- [ ] Metrics collecting
- [ ] Analytics generating
- [ ] No data gaps

---

## 🔒 PHASE 2B VALIDATION GATE

After ALL services are deployed:

### Test 1: P&L Accuracy
```
- Submit test trades
- Verify P&L calculation
- Check position tracking
- Validate reports
```

### Test 2: Data Flow
```
Trades → PTRC → P&L → Reports
Market Data → Hot Cache → Fast Access
Data → QuestDB Writer → Batch Writes → QuestDB
```

### Test 3: Performance
```
- Hot cache hit rate > 80%
- QuestDB writer throughput > 10k/sec
- P&L calculation latency < 100ms
- Report generation < 5 seconds
```

### Test 4: Integration
```
- All services communicating
- Data flowing correctly
- No errors in logs
- All health checks passing
```

**Decision**: PASS ✓ → Phase 2C | FAIL ✗ → Fix issues

---

## 📊 SUCCESS METRICS

### Per-Service Success
- [ ] Service builds and starts
- [ ] Health check passes
- [ ] Dependencies connected
- [ ] Core functionality working
- [ ] No errors in logs

### Phase 2B Success
- [ ] All 6 services operational
- [ ] P&L calculation accurate
- [ ] Data optimization working
- [ ] Analytics generating
- [ ] All validation tests pass

---

## 🛠️ COMMON PATTERNS

### Multi-Store Services (PTRC)
```yaml
# config.yaml pattern
databases:
  questdb:
    host: questdb
    port: 9000
  clickhouse:
    host: clickhouse
    port: 8123
  
storage:
  seaweedfs:
    endpoint: http://seaweedfs:8333
    bucket: trader2025
```

### Cache Services (Hot Cache, PNL)
```yaml
# config.yaml pattern
cache:
  redis:
    host: valkey
    port: 6379
    db: 4
    ttl: 300  # 5 minutes
```

### Batch Processing (QuestDB Writer)
```yaml
# config.yaml pattern
batch:
  size: 1000
  interval_sec: 1
  max_retry: 3
```

---

## ⚠️ CRITICAL NOTES

### PTRC Complexity
- Multi-module system
- May need separate configs for each module
- Test each module independently
- Allow extra time for troubleshooting

### PNL Dependencies
- Requires PTRC operational
- Needs accurate position data
- Depends on price data from gateway

### Performance Services
- Hot cache and QuestDB writer are optimizations
- Not critical for functionality
- Focus on correctness first, performance second

### ML Services
- Feast pipeline is optional
- Can skip if not using ML features
- Defer to Phase 4 if time constrained

---

## 🎯 DELIVERABLES

When Phase 2B is complete:

1. **6 Services Running**:
   - ptrc (8109)
   - pnl (8100)
   - hot_cache (8088)
   - questdb_writer (8090)
   - feast-pipeline (8104)
   - execution-quality (8096)

2. **All Configs Created**:
   - config/backend/ptrc/config.yaml
   - config/backend/pnl/config.yaml
   - config/backend/hot_cache/config.yaml
   - config/backend/questdb_writer/config.yaml
   - config/backend/feast_pipeline/config.yaml
   - config/backend/execution_quality/config.yaml

3. **Integration Validated**:
   - P&L calculation working
   - Reports generating
   - Data optimization active
   - Analytics operational

4. **Documentation Updated**:
   - COMPLETION_TRACKER.md
   - Session summary

---

## 📝 OPTIONAL SERVICES

If time is limited, these can be skipped or deferred:

### Can Skip:
- **feast-pipeline** - Only needed for ML features
- **execution-quality** - Nice to have analytics

### Must Have:
- **ptrc** - Essential for production (P&L, compliance)
- **pnl** - Core trading functionality
- **hot_cache** - Significant performance improvement
- **questdb_writer** - Write performance optimization

---

## 🚦 NEXT STEPS

After Phase 2B validation passes:
→ **Phase 2C** (if needed) - Any remaining services
→ **Phase 2 Final Validation** - Complete system test
→ **Phase 3** - Frontend Integration

If validation fails:
→ Debug and fix
→ Re-run validation
→ Do NOT proceed

---

## 📁 REFERENCE

**Instructions**:
- instructions/PHASE2_PROMPT05_MIGRATE_P4_SERVICES.md
- instructions/PHASE2A_PROMPT_COMPLETE.md (for pattern reference)

**Inventory**:
- docs/BACKEND_SERVICES_INVENTORY.md

**Compose**:
- infrastructure/docker/docker-compose.apps.yml

**Tracker**:
- COMPLETION_TRACKER.md

---

**Prompt Status**: ✅ READY FOR CLAUDE CODE

**Execute After**: Phase 2A complete and validated

**Execution Time**: 16 hours

**Complexity**: Medium (supporting services, not critical path)

**Validation**: Mandatory gate before Phase 2C/3

---

**Created By**: Claude (Sonnet 4.5)  
**Date**: 2025-10-16  
**For**: Claude Code Execution  
**Phase**: 2B - Supporting Services
