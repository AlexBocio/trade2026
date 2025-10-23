# Phase 6.7: System Stabilization

**Priority**: P0 (CRITICAL)
**Timeline**: 3-5 hours
**Status**: STARTING NOW

---

## Objectives

1. Stabilize all 34 containers to healthy state
2. Complete Traefik integration (8/8 backend services registered)
3. Verify end-to-end data flow

---

## Tasks

### Task 6.7.1: Service Health Stabilization (1-2 hours)

**Current State**: 13/27 healthy, 11/27 unhealthy (warming up)
**Target**: 28/34 healthy (excluding stopped services)

**Actions**:
- [ ] Monitor healthcheck progression (services up 20+ min)
- [ ] Investigate services failing healthchecks after 40+ min
- [ ] Fix healthcheck configurations if needed
- [ ] Verify internal service ports vs healthcheck ports

**Deliverable**: All running services show (healthy) status

---

### Task 6.7.2: Restart Missing Services (1-2 hours)

**7 services stopped from previous crash**:
- [ ] feast-pipeline (port 8113)
- [ ] execution-quality (port 8092)
- [ ] hot_cache (port 8088)
- [ ] questdb_writer (port 8090)
- [ ] pnl (port 8100)
- [ ] exeq (port 8095)
- [ ] nginx (port 5173) - OR integrate with Traefik

**Actions**:
- [ ] Check config files exist for each service
- [ ] Copy configs from source if missing (like live-gateway fix)
- [ ] Start services via docker-compose
- [ ] Monitor startup and healthchecks
- [ ] Verify NATS connectivity

**Deliverable**: 34/34 containers running

---

### Task 6.7.3: Traefik Service Registration (0.5-1 hour)

**Current**: 1/8 backend services registered
**Blocker**: Services marked unhealthy, Traefik won't register

**Once Task 6.7.1 complete**:
- [ ] Verify Traefik auto-discovers all healthy backend services
- [ ] Check dashboard: http://localhost:8080/dashboard/
- [ ] Confirm all 8 routes appear in Traefik API

**Expected routes**:
- ✅ /api/portfolio → portfolio-optimizer:5000
- ✅ /api/rl → rl-trading:5000
- ✅ /api/backtest → advanced-backtest:5000
- ✅ /api/factors → factor-models:5000
- ✅ /api/simulation → simulation-engine:5000
- ✅ /api/fracdiff → fractional-diff:5000
- ✅ /api/metalabel → meta-labeling:5000
- ✅ /api/screener → stock-screener:5000

**Deliverable**: 8/8 backend services accessible via Traefik

---

### Task 6.7.4: End-to-End Testing (1-2 hours)

**Test Scenarios**:
- [ ] Test all backend service health endpoints via Traefik
  - curl -k https://localhost/api/portfolio/health
  - curl -k https://localhost/api/screener/health
  - (repeat for all 8 services)

- [ ] Test functional endpoints
  - Stock screener scan
  - Portfolio optimization
  - RL agent listing

- [ ] Test OMS order flow
  - Submit test order
  - Verify NATS message
  - Check risk validation
  - Confirm persistence to QuestDB

- [ ] Test frontend connectivity
  - Access http://localhost:5173 OR http://localhost
  - Verify API calls reach backend through Traefik
  - Check WebSocket connections

**Deliverable**: All critical paths validated

---

## Exit Criteria

- ✅ 34/34 containers running
- ✅ 28+ containers healthy (82%+)
- ✅ Traefik registering 8/8 backend services
- ✅ All health endpoints responding via gateway
- ✅ End-to-end order flow working
- ✅ Frontend accessible and connected

---

## Risk Mitigation

**Risk**: Healthchecks continue failing
**Mitigation**: Adjust healthcheck intervals/retries or disable for non-critical services

**Risk**: Port conflicts prevent service startup
**Mitigation**: Document port allocation, use dynamic ports where possible

---

**Reference**: See `TRADE2026_COMPLETION_PLAN.md` for full details
