# Trade2026 Complete System Map & Operational Procedures
**Generated**: 2025-10-27 11:05 EDT
**Status**: Comprehensive System Discovery

---

## EXECUTIVE SUMMARY

**Total Containers**: 42 (28 running, 14 stopped)
**Managed by Trade2026**: 28 running containers
**External Dependencies**: IB Gateway (Paper Trading on port 7497)
**Overall Health**: 25/28 healthy (89%), 3 unhealthy

**CRITICAL ISSUE**: Data ingestion connected to IBKR but NO market data flowing
**ROOT CAUSE**: Paper trading account requires market data subscriptions
**ACTION REQUIRED**: Subscribe to "US Securities Snapshot Bundle" (free, 15-min delayed)

---

## 1. SYSTEM ARCHITECTURE OVERVIEW

```
Trade2026 Platform (28 Running Containers)
├── Data Layer (4) - 100% Healthy
│   ├── QuestDB - Time-series database for market data
│   ├── ClickHouse - Analytics database
│   ├── Valkey - Redis-compatible cache
│   └── PostgreSQL - Reference data storage
│
├── Messaging & Storage (3) - 100% Healthy
│   ├── NATS - Event streaming backbone
│   ├── OpenSearch - Log aggregation
│   └── SeaweedFS - Object storage
│
├── Data Ingestion (1) - UNHEALTHY ⚠️
│   └── data-ingestion - IBKR + FRED adapter (NO MARKET DATA)
│
├── Trading Core (6) - 83% Healthy
│   ├── OMS - Order Management
│   ├── Risk - Risk Management
│   ├── PTRC - Position/Trade/Risk Control
│   ├── Live Gateway - Execution
│   ├── Normalizer - UNHEALTHY ⚠️
│   └── Authn - Authentication
│
├── Data Sinks (2) - 100% Healthy
│   ├── sink-ticks - Tick data processor
│   └── sink-alt - Alternative data processor
│
├── Backend Analytics (8) - 100% Healthy ✅
│   ├── portfolio-optimizer (5001) - Portfolio optimization
│   ├── rl-trading (5002) - Reinforcement learning
│   ├── advanced-backtest (5003) - Walk-forward testing
│   ├── factor-models (5004) - Barra models
│   ├── simulation-engine (5005) - Monte Carlo
│   ├── fractional-diff (5006) - Stationarity
│   ├── meta-labeling (5007) - ML filtering
│   └── stock-screener (5008) - Screening + regime
│
├── API Gateway (2) - 50% Healthy
│   ├── Traefik - Reverse proxy (UNHEALTHY but functional) ⚠️
│   └── OPA - Policy engine
│
├── Library Services (2) - 100% Healthy
│   ├── library - Reference data API
│   └── postgres-library - Reference data DB
│
└── Frontend (1) - 100% Healthy
    └── frontend - React SPA

EXTERNAL (Not managed by Trade2026):
└── IB Gateway - Interactive Brokers API (Paper Trading, port 7497)
```

---

## 2. DETAILED COMPONENT INVENTORY

### 2.1 Data Layer (4/4 Healthy)

| Container | Image | Uptime | Ports | Purpose |
|-----------|-------|--------|-------|---------|
| questdb | questdb/questdb:latest | 4 days | 8812, 9000, 9009 | Time-series DB, 1,349 historical bars |
| clickhouse | clickhouse/clickhouse-server:24.9 | 4 days | 8123, 9001 | Analytics database |
| valkey | valkey/valkey:8-alpine | 4 days | 6379 | Cache (15 symbols cached) |
| postgres-library | postgres:16-alpine | 4 days | 5433 | Reference data |

**Health**: 100% ✅
**Critical**: YES - Foundation for all services

---

### 2.2 Data Ingestion (0/1 Healthy) ⚠️ CRITICAL

| Container | Status | Uptime | Connection | Data Flow |
|-----------|--------|--------|------------|-----------|
| data-ingestion | UNHEALTHY | 24 min | host.docker.internal:7497 | ❌ NO TICKS |

**Current State**:
- ✅ Connected to IB Gateway (Paper Trading port 7497)
- ✅ Market data farm connection OK: usfarm
- ✅ All 15 symbols subscribed successfully:
  - Sectors: XLK, XLV, XLF, XLY, XLI, XLP, XLE, XLB, XLRE, XLU, XLC
  - Major ETFs: SPY, QQQ, IWM, DIA
- ✅ FRED economic data flowing (VIX, yields, spreads) every 60 min
- ❌ **NO TICK DATA FLOWING** - Requires market data subscriptions

**IBKR Configuration**:
```yaml
port: 7497  # Paper trading (4002 for live)
reconnect_delay_seconds: 10
max_reconnect_attempts: 999999  # Infinite auto-reconnection
```

**Error 10092 (Expected)**: "Deep market data not supported" - Level 2 requires subscription, but Level 1 (bid/ask/last) should work with subscriptions

---

### 2.3 Backend Analytics Services (8/8 Healthy) ✅

All services healthy, connected to Traefik, and have access to 1,349 historical bars across 23 symbols.

| Service | Port | Purpose | Data Range |
|---------|------|---------|------------|
| portfolio-optimizer | 5001 | Mean-variance, HRP, HERC | 40-93 days |
| rl-trading | 5002 | DQN and PPO agents | 40-93 days |
| advanced-backtest | 5003 | Walk-forward, PBO | 40-93 days |
| factor-models | 5004 | Barra, PCA | 40-93 days |
| simulation-engine | 5005 | Monte Carlo | 40-93 days |
| fractional-diff | 5006 | Stationarity transform | 40-93 days |
| meta-labeling | 5007 | ML model filtering | 40-93 days |
| stock-screener | 5008 | 100+ endpoints, real market | 40-93 days |

**Traefik Registration**: 8/8 services UP and accessible via http://localhost/api/{service}

---

## 3. STARTUP SEQUENCE

### 3.1 Correct Order (Dependency-Aware)

```
1. Networks
   └─> docker-compose.networks.yml

2. Data Layer (FOUNDATIONAL)
   ├─> QuestDB (market data storage)
   ├─> ClickHouse (analytics)
   ├─> Valkey (cache)
   └─> PostgreSQL-Library (reference data)

3. Messaging & Storage
   ├─> NATS (event streaming - CRITICAL for inter-service communication)
   ├─> OpenSearch (logs)
   └─> SeaweedFS (object storage)

4. Library Services
   ├─> postgres-library (DB first)
   └─> library (API second)

5. Authentication
   └─> authn (before trading core)

6. Trading Core
   ├─> oms (Order Management)
   ├─> risk (Risk Management)
   ├─> ptrc (Position/Trade/Risk)
   ├─> live-gateway (Execution)
   ├─> normalizer (Data normalization)
   ├─> sink-ticks (Tick processor)
   └─> sink-alt (Alt data processor)

7. Data Ingestion (DEPENDS ON EXTERNAL: IB Gateway must be running)
   └─> data-ingestion
       ├─> Connects to IB Gateway on host (7497)
       ├─> Writes to QuestDB + Valkey
       └─> Publishes to NATS

8. Backend Analytics (Can start in parallel)
   └─> All 8 services (portfolio-optimizer, rl-trading, etc.)

9. API Gateway
   ├─> traefik (Reverse proxy)
   └─> opa (Policy engine)

10. Frontend
    └─> frontend (React SPA)
```

**Startup Time**: 2-3 minutes (with cached images)

---

## 4. OPERATIONAL FLOW

### 4.1 Normal Operation (When Working Correctly)

```
┌─────────────────────────────────────────────────────────────┐
│                  IB Gateway (Host Machine)                   │
│              Paper Trading Port 7497                         │
│              Running with Market Data Subscriptions          │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ TCP Connection
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Trade2026 data-ingestion Container              │
│  - Connects via host.docker.internal:7497                   │
│  - Subscribes to 15 symbols (Level 1, Level 2, T&S)        │
└─────────────────────────────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
    ┌─────────┐       ┌─────────┐     ┌──────────┐
    │ QuestDB │       │ Valkey  │     │   NATS   │
    │ (Persist)│       │ (Cache) │     │ (Stream) │
    └─────────┘       └─────────┘     └──────────┘
          │                 │                 │
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │    Backend Analytics Services (8)     │
        │    Query QuestDB for historical       │
        │    Subscribe to NATS for real-time    │
        └───────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │         Traefik API Gateway           │
        │    Routes: /api/{service}/...         │
        └───────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │        Frontend (React SPA)           │
        │    http://localhost:5173              │
        └───────────────────────────────────────┘
```

**Market Hours**: 9:30 AM - 4:00 PM ET (Mon-Fri)
**Data Flow**: Continuous (24/7 connection, data only during market hours)

---

### 4.2 IBKR Disconnection & Reconnection

**Auto-Reconnection Flow**:
```
1. IB Gateway Shuts Down
   ├─> Manual close by user
   ├─> Automatic shutdown (configurable in IB Gateway)
   └─> Network issue

2. Trade2026 Detects Disconnection
   └─> Log: "IBKR Connection Lost at {timestamp}"

3. Auto-Reconnection Loop Starts (INFINITE)
   ├─> Wait 10 seconds
   ├─> Attempt reconnection (attempt X/999999)
   ├─> Log: "Attempting reconnection... (attempt X/999999)"
   ├─> ConnectionRefusedError (Gateway not running)
   └─> Repeat indefinitely

4. User Restarts IB Gateway
   └─> Launches IB Gateway
   └─> Logs in (Paper Trading account)

5. Trade2026 Detects Gateway is Back
   ├─> Within 10 seconds of Gateway startup
   └─> Log: "Connected to IBKR at host.docker.internal:7497"

6. Automatic Re-Subscription
   ├─> Log: "Subscribed to XLK (Level 1, Level 2, Time & Sales)"
   ├─> ... (all 15 symbols)
   └─> Log: "IBKR Adapter started successfully"

7. Data Collection Resumes
   └─> If market open + subscriptions active: Tick data flows
```

**Key Points**:
- ✅ Fully automatic - NO manual steps required
- ✅ Infinite retries - Never gives up
- ✅ All subscriptions restored automatically
- ✅ Connection state logged for monitoring

---

## 5. CURRENT SYSTEM STATUS (2025-10-27 11:05 EDT)

### 5.1 Health Summary

| Category | Healthy | Total | % |
|----------|---------|-------|---|
| Data Layer | 4 | 4 | 100% |
| Messaging & Storage | 3 | 3 | 100% |
| **Data Ingestion** | **0** | **1** | **0%** ⚠️ |
| Trading Core | 5 | 6 | 83% |
| Data Sinks | 2 | 2 | 100% |
| Backend Analytics | 8 | 8 | 100% |
| API Gateway | 1 | 2 | 50% |
| Library Services | 2 | 2 | 100% |
| Frontend | 1 | 1 | 100% |
| **OVERALL** | **26** | **29** | **90%** |

### 5.2 CRITICAL ISSUES

**1. Data Ingestion - NO MARKET DATA (P0 - CRITICAL)**
- **Status**: UNHEALTHY
- **Root Cause**: IBKR paper trading account has NO market data subscriptions
- **Impact**: No real-time or delayed tick data flowing
- **Symptoms**:
  - Connection to IB Gateway: ✅ ESTABLISHED (7497)
  - Symbol subscriptions: ✅ ACTIVE (all 15)
  - Market data farm: ✅ CONNECTED (usfarm)
  - Tick data flow: ❌ ZERO TICKS
- **Solution**: Subscribe to market data in IBKR Account Management Portal
  - Subscription: "US Securities Snapshot and Futures Value Bundle"
  - Cost: FREE (15-20 minute delayed data)
  - Activation: 5-10 minutes after subscription
  - URL: https://www.interactivebrokers.com/portal

**2. Traefik - UNHEALTHY but Functional (P2 - MEDIUM)**
- **Status**: UNHEALTHY (but all routes working)
- **Root Cause**: Healthcheck misconfiguration
- **Impact**: Minimal (all 8 backend services accessible)
- **Solution**: Fix healthcheck endpoint

**3. Normalizer - UNHEALTHY (P3 - LOW)**
- **Status**: UNHEALTHY
- **Root Cause**: Unknown (needs investigation)
- **Impact**: Minimal (data normalization may be degraded)
- **Solution**: Check logs and restart if needed

---

### 5.3 Data Availability

**Historical Data (QuestDB)**:
- **Symbols**: 23 total
- **Bars**: 1,349 daily OHLCV
- **Date Range**: July 25 - Oct 23, 2025
- **Coverage**:
  - SPY, QQQ, TLT: 93 days each (Jul 25 - Oct 23)
  - Indices (^NDX, ^RUT, ^RVX): 51 days each
  - Commodities (GC=F, SI=F, XAU=F, HG=F): 52-53 days
  - Semiconductors (SMH): 51 days
  - Sector ETFs: 41-197 days (XLE has most at 197)

**Real-Time Data (IBKR)**:
- **Status**: ❌ NOT FLOWING
- **Connection**: ✅ CONNECTED
- **Subscriptions**: ✅ ACTIVE (15 symbols)
- **Blocker**: No market data subscriptions in IBKR account

**Economic Data (FRED)**:
- **Status**: ✅ FLOWING every 60 minutes
- **Indicators**: VIX, 10Y/2Y yields, T10Y2Y spread, High Yield spread, TED spread, Fed Funds rate

---

## 6. DOCKER COMPOSE FILES

| File | Services | Purpose | Status |
|------|----------|---------|--------|
| docker-compose.yml | Infrastructure | QuestDB, ClickHouse, NATS, etc. | Active |
| docker-compose.core.yml | Trading Core | OMS, Risk, PTRC, Live Gateway | Active |
| docker-compose.backend-services.yml | Analytics (8) | Portfolio optimizer, RL, etc. | Active |
| docker-compose.data-ingestion.yml | Data Ingestion | IBKR + FRED adapters | Active |
| docker-compose.frontend.yml | Frontend | React SPA | Active |
| docker-compose.traefik.yml | API Gateway | Reverse proxy | Active |
| docker-compose.library.yml | Library Services | Reference data API | Active |
| docker-compose.library-db.yml | Library DB | Postgres for library | Active |
| docker-compose.apps.yml | Apps Layer | Market data gateway | Active |
| docker-compose.networks.yml | Networks | Docker network definitions | Active |
| docker-compose.api-gateway.yml | Legacy Gateway | Old nginx gateway | Inactive |

---

## 7. TROUBLESHOOTING

### 7.1 "No tick data flowing" (CURRENT ISSUE)

**Checklist**:
1. ✅ Is IB Gateway running?
2. ✅ Are you using the correct port (7497 paper, 4002 live)?
3. ✅ Is data-ingestion container connected to IBKR?
4. ✅ Are all 15 symbols subscribed?
5. ❌ **Do you have market data subscriptions?** ← **THIS IS THE ISSUE**
6. ⏸️ Are markets currently open?

**Commands to Verify**:
```bash
# Check IBKR connection
docker logs trade2026-data-ingestion | grep "Connected to IBKR"

# Check subscriptions
docker logs trade2026-data-ingestion | grep "Subscribed to"

# Check for tick data
curl -s "http://localhost:9000/exec?query=SELECT COUNT(*) FROM market_data_l1"

# Check for any errors
docker logs trade2026-data-ingestion --tail 100 | grep -i error
```

**Solution**: Subscribe to market data (see Section 8.1)

---

### 7.2 "Container is unhealthy"

```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# Check specific container logs
docker logs <container-name> --tail 100

# Check healthcheck definition
docker inspect <container-name> | grep -A 20 Health

# Restart container
docker restart <container-name>

# Rebuild if config changed
docker-compose -f <compose-file> up -d --build <service-name>
```

---

### 7.3 "IBKR won't connect"

**Common Issues**:
1. **Wrong port**: Paper trading = 7497, Live trading = 4002
2. **API not enabled**: Check IB Gateway → Configuration → API → Settings → Enable ActiveX and Socket Clients
3. **Trusted IPs not configured**: Must add 192.168.65.254 and 192.168.65.0/24
4. **Gateway not running**: Launch IB Gateway and log in

---

## 8. ACTION PLAN TO GET DATA FLOWING

### 8.1 Subscribe to IBKR Market Data (5-15 minutes)

**Step 1: Login to IBKR Portal**
1. Go to: https://www.interactivebrokers.com/portal
2. Log in with your paper trading account credentials

**Step 2: Navigate to Market Data Subscriptions**
1. Click: Settings (gear icon)
2. Click: User Settings
3. Click: Market Data Subscriptions

**Step 3: Subscribe to Delayed Data (FREE)**
1. Find: "US Securities Snapshot and Futures Value Bundle"
2. Click: Subscribe
3. Confirm: Subscription (FREE, no payment required)

**Step 4: Wait for Activation**
1. Wait: 5-10 minutes for subscription to activate
2. Status will change from "Pending" to "Active"

**Step 5: Restart IB Gateway**
1. Close IB Gateway
2. Relaunch and log in
3. Trade2026 will auto-reconnect within 10 seconds

**Step 6: Verify Data Flow**
```bash
# Monitor logs for connection
docker logs trade2026-data-ingestion --follow | grep -E "IBKR|tick|Connected"

# After 15-20 minutes (delayed data), check for ticks:
curl -s "http://localhost:9000/exec?query=SELECT symbol, COUNT(*) FROM market_data_l1 WHERE timestamp > now() - interval '10 minutes' GROUP BY symbol"
```

**Expected Timeline**:
- Subscription activation: 5-10 minutes
- First delayed tick: 15-20 minutes after market event
- Steady data flow: Within 30 minutes of market open

---

### 8.2 Alternative: Real-Time Data ($4.50/month)

If you need real-time (not delayed) data:

**Subscribe to**: "US Equity and Options Add-On Streaming Bundle"
**Cost**: $4.50/month (waived if you make 30+ trades/month)
**Delay**: Real-time (no 15-minute delay)

---

## 9. MONITORING & HEALTH CHECKS

### 9.1 Quick Health Check Commands

```bash
# Overall system health
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "healthy|unhealthy"

# Data ingestion health
curl http://localhost:8500/health

# Check IBKR connection
docker logs trade2026-data-ingestion | grep -E "Connected to IBKR|Subscribed" | tail -20

# Check for recent tick data
curl -s "http://localhost:9000/exec?query=SELECT COUNT(*) FROM market_data_l1 WHERE timestamp > now() - interval '5 minutes'"

# Check Traefik routes
curl -s http://localhost:8080/api/http/services | python -m json.tool

# Check backend service health
for port in 5001 5002 5003 5004 5005 5006 5007 5008; do
  echo "Port $port:" && timeout 2 curl -s http://localhost:$port/health || echo "Not responding"
done
```

### 9.2 Data Ingestion Health Endpoint

**URL**: http://localhost:8500/health

**Healthy Response**:
```json
{
  "status": "healthy",
  "ibkr_status": "connected",
  "ibkr_connected_at": "2025-10-27T14:54:13Z",
  "symbols_subscribed": 15,
  "fred_status": "active",
  "last_tick_received": "2025-10-27T15:05:42Z"
}
```

**Unhealthy Response (Current State)**:
```json
{
  "status": "degraded",
  "ibkr_status": "connected",
  "ibkr_connected_at": "2025-10-27T14:54:13Z",
  "symbols_subscribed": 15,
  "fred_status": "active",
  "last_tick_received": null,
  "message": "No tick data flowing - check market data subscriptions"
}
```

---

## 10. NEXT STEPS

### Immediate (P0 - To Get System Fully Operational)
1. ✅ Subscribe to IBKR market data subscriptions
2. ⏸️ Wait for subscription activation (5-10 min)
3. ⏸️ Restart IB Gateway
4. ⏸️ Verify tick data flowing (15-20 min for delayed data)

### Short-Term (P1 - System Health)
1. Fix Traefik healthcheck (30 min)
2. Investigate normalizer unhealthy status (30 min)
3. Document frontend access patterns (15 min)

### Medium-Term (P2 - Testing)
1. Phase 7: Complete backend service testing (6-8 hours)
2. Phase 7: End-to-end testing (3-4 hours)
3. Phase 7: Load testing 1000 orders/sec (4-6 hours)

### Long-Term (P3 - Enhancement)
1. Phases 8-14: Additional features per TRADE2026_COMPLETION_PLAN.md (94-146 hours)

---

## 11. KEY CONFIGURATION FILES

| File | Purpose | Critical Settings |
|------|---------|-------------------|
| `backend/apps/data_ingestion/config/config.yaml` | Data ingestion | IBKR port (7497), reconnection (999999 attempts) |
| `infrastructure/docker/docker-compose.*.yml` | Service orchestration | Container definitions, networks, volumes |
| `backend/shared/data_fetcher.py` | Unified data access | QuestDB dual-table UNION query, yfinance fallback |
| `IBKR_AUTO_RECONNECT_AND_TIMEFRAMES.md` | IBKR documentation | Auto-reconnection, 11 timeframes configuration |
| `IBKR_SETUP_GUIDE.md` | IB Gateway setup | API configuration, trusted IPs, port settings |

---

## APPENDIX: System Discovery Commands

```bash
# Container inventory
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

# Network discovery
docker network ls

# Volume discovery
docker volume ls

# Health status summary
docker ps --format "{{.Names}}: {{.Status}}" | grep -E "healthy|unhealthy|starting"

# Resource usage
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Log aggregation
docker logs trade2026-data-ingestion --since 1h | grep -E "ERROR|WARN|IBKR"
```

---

**Document Version**: 1.0
**Last Updated**: 2025-10-27 11:05 EDT
**Next Review**: After market data subscriptions activated and verified
**Status**: READY FOR USER ACTION - Subscribe to IBKR market data

---

## SUMMARY

Trade2026 is **90% operational** with **26/29 services healthy**. The system architecture is solid, all core services are running, and 8 backend analytics services have access to 1,349 historical bars.

**CRITICAL BLOCKER**: IBKR connection is established and all 15 symbols are subscribed, but NO tick data is flowing because the paper trading account needs market data subscriptions.

**ACTION REQUIRED**: Subscribe to "US Securities Snapshot and Futures Value Bundle" (FREE, delayed) at https://www.interactivebrokers.com/portal

**After subscription**: System will automatically start receiving and storing tick data within 15-20 minutes (delayed) or immediately (if real-time subscription). NO code changes or restarts required - the system is already configured and waiting for data.