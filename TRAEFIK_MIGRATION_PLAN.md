# Traefik Migration Plan: Trade2025 → Trade2026
**Date:** 2025-10-23
**Source:** Existing Trade2025 Traefik v3.0 configuration
**Target:** Trade2026 unified API gateway
**Estimated Time:** 1-2 hours (much faster than starting from scratch!)

---

## Executive Summary

**GREAT NEWS:** Trade2025 already has a **complete, production-ready Traefik v3.0 setup!**

Instead of building from scratch, we'll:
1. Copy existing Traefik configuration from Trade2025
2. Update network names (trade2025 → trade2026)
3. Add labels to 8 backend analytics services
4. Test and deploy

**Why this is better:**
- ✅ Proven configuration already working in Trade2025
- ✅ Complete middleware setup (CORS, rate limiting, security headers)
- ✅ TLS/HTTPS configuration ready
- ✅ Prometheus metrics integration
- ✅ Dashboard access pre-configured
- ✅ 90% less work than building from scratch

---

## What We Found in Trade2025

### Complete Traefik Configuration

**Files Found:**
```
C:\trade2025\
├── docker-compose.traefik.yml          # Main Traefik container config
├── traefik/
│   ├── traefik.yml                     # Static configuration
│   ├── dynamic/
│   │   ├── middlewares.yml             # CORS, rate limiting, security
│   │   ├── tcp.yml                     # TCP routing (gRPC)
│   │   └── tls.yml                     # TLS certificates
│   └── certs/                          # Certificate directory
└── deploy/compose/traefik/             # Production configs
```

### Traefik Features Already Configured

**1. Entry Points:**
- HTTP (port 80) → Auto-redirects to HTTPS
- HTTPS (port 443) → TLS termination
- Dashboard (port 8080) → Dev access
- gRPC (port 8443) → Optional

**2. Middlewares:**
- ✅ CORS (permissive & strict modes)
- ✅ Rate limiting (basic, strict, API modes)
- ✅ Security headers (HSTS, CSP, XSS protection)
- ✅ Compression
- ✅ Circuit breaker
- ✅ Retry policy
- ✅ Path stripping
- ✅ IP whitelisting
- ✅ Forward auth (OAuth2/OIDC ready)

**3. Services Already Using Traefik:**
- OMS (Order Management)
- Risk Management
- PTRC (P&L Tracking)
- Gateway (Market Data)
- Live Gateway
- Backtest Orchestrator
- Serving
- AuthN

**4. Docker Auto-Discovery:**
```yaml
providers:
  docker:
    watch: true
    exposedByDefault: false  # Explicit opt-in
    network: trade2025-frontend
```

**5. Monitoring:**
- Prometheus metrics enabled
- Access logs (JSON format)
- Dashboard at http://localhost:8080/dashboard/

---

## Migration Steps (1-2 hours)

### Step 1: Copy Traefik Configuration (15 minutes)

```bash
# Copy entire Traefik directory
cd /c/claudedesktop_projects/trade2026
mkdir -p infrastructure/traefik

# Copy Traefik files from Trade2025
cp /c/trade2025/docker-compose.traefik.yml infrastructure/docker/
cp -r /c/trade2025/traefik/* infrastructure/traefik/

# Create necessary directories
mkdir -p infrastructure/traefik/certs
mkdir -p infrastructure/traefik/dynamic
mkdir -p data/traefik/acme
mkdir -p data/traefik/logs
```

### Step 2: Update Network Names (10 minutes)

**File:** `infrastructure/docker/docker-compose.traefik.yml`

```yaml
# BEFORE:
networks:
  frontend:
    external: true
    name: trade2025-frontend

# AFTER:
networks:
  frontend:
    external: true
    name: trade2026-frontend
  backend:
    external: true
    name: trade2026-backend
  lowlatency:
    external: true
    name: trade2026-lowlatency
```

**File:** `infrastructure/traefik/traefik.yml`

```yaml
# BEFORE:
providers:
  docker:
    network: trade2025-frontend

# AFTER:
providers:
  docker:
    network: trade2026-frontend
```

**File:** `infrastructure/traefik/dynamic/middlewares.yml`

```yaml
# Update IP whitelist ranges if needed
whitelist-local:
  ipWhiteList:
    sourceRange:
      - "127.0.0.1/32"
      - "::1/128"
      - "172.20.0.0/16"  # trade2026-frontend
      - "172.21.0.0/16"  # trade2026-backend
      - "172.22.0.0/16"  # trade2026-lowlatency
```

### Step 3: Update Volume Paths (5 minutes)

**File:** `infrastructure/docker/docker-compose.traefik.yml`

```yaml
# BEFORE (Linux paths):
volumes:
  - /home/user/trading/secrets/traefik/certs:/etc/traefik/certs:ro
  - /home/user/trading/traefik/acme:/etc/traefik/acme
  - /home/user/trading/logs/traefik:/var/log/traefik

# AFTER (Windows paths):
volumes:
  - ../../infrastructure/traefik/certs:/etc/traefik/certs:ro
  - ../../data/traefik/acme:/etc/traefik/acme
  - ../../data/traefik/logs:/var/log/traefik
```

### Step 4: Add Labels to Backend Services (30 minutes)

**File:** `infrastructure/docker/docker-compose.backend-services.yml`

Add these labels to each service:

**Example: Stock Screener**
```yaml
stock-screener:
  # ... existing config ...
  labels:
    # Enable Traefik
    - "traefik.enable=true"

    # HTTP router
    - "traefik.http.routers.screener.rule=PathPrefix(`/api/screener`)"
    - "traefik.http.routers.screener.entrypoints=web,websecure"
    - "traefik.http.routers.screener.tls=true"

    # Service
    - "traefik.http.services.screener.loadbalancer.server.port=5000"
    - "traefik.docker.network=trade2026-backend"

    # Middlewares
    - "traefik.http.routers.screener.middlewares=api-standard@file"
```

**Apply to all 8 services:**
1. Stock Screener (port 5000, prefix `/api/screener`)
2. Portfolio Optimizer (port 5001, prefix `/api/portfolio`)
3. RL Trading (port 5002, prefix `/api/rl`)
4. Advanced Backtest (port 5003, prefix `/api/backtest`)
5. Factor Models (port 5004, prefix `/api/factors`)
6. Simulation Engine (port 5005, prefix `/api/simulation`)
7. Fractional Diff (port 5006, prefix `/api/fracdiff`)
8. Meta-Labeling (port 5007, prefix `/api/metalabel`)

### Step 5: Update Existing Service Labels (10 minutes)

Services already in Trade2026 that need Traefik labels:

**OMS:**
```yaml
oms:
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.oms.rule=PathPrefix(`/api/orders`)"
    - "traefik.http.routers.oms.entrypoints=web,websecure"
    - "traefik.http.services.oms.loadbalancer.server.port=8099"
```

**Risk:**
```yaml
risk:
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.risk.rule=PathPrefix(`/api/risk`)"
    - "traefik.http.routers.risk.entrypoints=web,websecure"
    - "traefik.http.services.risk.loadbalancer.server.port=8103"
```

**PTRC:**
```yaml
ptrc:
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.ptrc.rule=PathPrefix(`/api/pnl`)"
    - "traefik.http.routers.ptrc.entrypoints=web,websecure"
    - "traefik.http.services.ptrc.loadbalancer.server.port=8109"
```

**Data Ingestion:**
```yaml
data-ingestion:
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.data.rule=PathPrefix(`/api/data`)"
    - "traefik.http.routers.data.entrypoints=web,websecure"
    - "traefik.http.services.data.loadbalancer.server.port=8500"
```

### Step 6: Deploy Traefik (10 minutes)

```bash
cd /c/claudedesktop_projects/trade2026/infrastructure/docker

# Deploy Traefik (initially on port 81 to test alongside nginx)
# Edit docker-compose.traefik.yml: change ports to "81:80"
docker-compose -f docker-compose.traefik.yml up -d

# Check logs
docker logs trade2026-traefik --tail 50

# Access dashboard
http://localhost:8080/dashboard/
```

### Step 7: Test Services (15 minutes)

```bash
# Test through Traefik (port 81 initially)
curl http://localhost:81/api/screener/health
curl http://localhost:81/api/rl/health
curl http://localhost:81/api/portfolio/health

# Test functional endpoints
curl http://localhost:81/api/screener/scan?limit=5
curl http://localhost:81/api/rl/

# Check Traefik dashboard
# http://localhost:8080/dashboard/
# Should see all services registered
```

### Step 8: Switch Traffic to Traefik (5 minutes)

```bash
# Stop nginx gateway
docker-compose -f docker-compose.api-gateway.yml down

# Update Traefik to use port 80
# Edit docker-compose.traefik.yml: change "81:80" to "80:80"
docker-compose -f docker-compose.traefik.yml restart

# Test on port 80
curl http://localhost/api/screener/health
curl http://localhost/health
```

### Step 9: Clean Up (5 minutes)

```bash
# Rename containers
# Edit docker-compose.traefik.yml:
# container_name: traefik → trade2026-api-gateway

# Remove old nginx files (backup first)
mv infrastructure/nginx infrastructure/nginx.backup
mv infrastructure/docker/docker-compose.api-gateway.yml infrastructure/docker/docker-compose.api-gateway.yml.backup

# Rename Traefik compose file for consistency
mv infrastructure/docker/docker-compose.traefik.yml infrastructure/docker/docker-compose.api-gateway.yml
```

---

## Configuration Files to Create/Update

### 1. Update `docker-compose.traefik.yml`

**Location:** `infrastructure/docker/docker-compose.traefik.yml`

**Changes:**
```yaml
# Line 16: Update container name
container_name: trade2026-api-gateway  # was: traefik

# Line 19-22: Update ports (initially test on 81, then switch to 80)
ports:
  - "80:80"       # HTTP (was on port 81 for testing)
  - "443:443"     # HTTPS
  - "8080:8080"   # Dashboard

# Line 31: Update network
- "--providers.docker.network=trade2026-frontend"  # was: trade2025-frontend

# Line 46-61: Update volume paths (Windows compatibility)
volumes:
  - ./traefik/traefik.yml:/etc/traefik/traefik.yml:ro
  - ./traefik/dynamic:/etc/traefik/dynamic:ro
  - ../../infrastructure/traefik/certs:/etc/traefik/certs:ro
  - ../../data/traefik/acme:/etc/traefik/acme
  - ../../data/traefik/logs:/var/log/traefik
  - /var/run/docker.sock:/var/run/docker.sock:ro

# Line 63-65: Update networks
networks:
  frontend:
    external: true
    name: trade2026-frontend
  backend:
    external: true
    name: trade2026-backend
  lowlatency:
    external: true
    name: trade2026-lowlatency

# Line 98-102: Update metadata labels
labels:
  - "com.trade2026.service.name=traefik"  # was: trade2025
  - "com.trade2026.service.role=reverse-proxy"
  - "com.trade2026.cpgs.version=1.0"
  - "com.trade2026.cpgs.compliant=true"
  - "com.trade2026.network.lane=frontend,backend,lowlatency"
```

### 2. Update `traefik.yml`

**Location:** `infrastructure/traefik/traefik.yml`

**Changes:**
```yaml
# Line 57: Update network
providers:
  docker:
    network: trade2026-frontend  # was: trade2025-frontend
```

### 3. Update `middlewares.yml`

**Location:** `infrastructure/traefik/dynamic/middlewares.yml`

**No changes needed** - middlewares are perfect as-is!

### 4. Add Labels to Backend Services

**Location:** `infrastructure/docker/docker-compose.backend-services.yml`

**Template for all 8 services:**
```yaml
service-name:
  # ... existing config ...
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.{name}.rule=PathPrefix(`/api/{prefix}`)"
    - "traefik.http.routers.{name}.entrypoints=web,websecure"
    - "traefik.http.routers.{name}.tls=false"  # HTTP only for now
    - "traefik.http.services.{name}.loadbalancer.server.port={port}"
    - "traefik.docker.network=trade2026-backend"
    - "traefik.http.routers.{name}.middlewares=api-standard@file"
```

---

## Complete Label Configurations

### Stock Screener
```yaml
stock-screener:
  # ... existing config ...
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.screener.rule=PathPrefix(`/api/screener`)"
    - "traefik.http.routers.screener.entrypoints=web"
    - "traefik.http.services.screener.loadbalancer.server.port=5000"
    - "traefik.docker.network=trade2026-backend"
    - "traefik.http.routers.screener.middlewares=cors-permissive@file,rate-limit-api@file"
```

### Portfolio Optimizer
```yaml
portfolio-optimizer:
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.portfolio.rule=PathPrefix(`/api/portfolio`)"
    - "traefik.http.routers.portfolio.entrypoints=web"
    - "traefik.http.services.portfolio.loadbalancer.server.port=5001"
    - "traefik.docker.network=trade2026-backend"
    - "traefik.http.routers.portfolio.middlewares=cors-permissive@file,rate-limit-api@file"
```

### RL Trading
```yaml
rl-trading:
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.rl.rule=PathPrefix(`/api/rl`)"
    - "traefik.http.routers.rl.entrypoints=web"
    - "traefik.http.services.rl.loadbalancer.server.port=5002"
    - "traefik.docker.network=trade2026-backend"
    - "traefik.http.routers.rl.middlewares=cors-permissive@file,rate-limit-api@file"
```

### Advanced Backtest
```yaml
advanced-backtest:
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.backtest.rule=PathPrefix(`/api/backtest`)"
    - "traefik.http.routers.backtest.entrypoints=web"
    - "traefik.http.services.backtest.loadbalancer.server.port=5003"
    - "traefik.docker.network=trade2026-backend"
    - "traefik.http.routers.backtest.middlewares=cors-permissive@file,rate-limit-api@file"
```

### Factor Models
```yaml
factor-models:
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.factors.rule=PathPrefix(`/api/factors`)"
    - "traefik.http.routers.factors.entrypoints=web"
    - "traefik.http.services.factors.loadbalancer.server.port=5004"
    - "traefik.docker.network=trade2026-backend"
    - "traefik.http.routers.factors.middlewares=cors-permissive@file,rate-limit-api@file"
```

### Simulation Engine
```yaml
simulation-engine:
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.simulation.rule=PathPrefix(`/api/simulation`)"
    - "traefik.http.routers.simulation.entrypoints=web"
    - "traefik.http.services.simulation.loadbalancer.server.port=5005"
    - "traefik.docker.network=trade2026-backend"
    - "traefik.http.routers.simulation.middlewares=cors-permissive@file,rate-limit-api@file"
```

### Fractional Diff
```yaml
fractional-diff:
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.fracdiff.rule=PathPrefix(`/api/fracdiff`)"
    - "traefik.http.routers.fracdiff.entrypoints=web"
    - "traefik.http.services.fracdiff.loadbalancer.server.port=5006"
    - "traefik.docker.network=trade2026-backend"
    - "traefik.http.routers.fracdiff.middlewares=cors-permissive@file,rate-limit-api@file"
```

### Meta-Labeling
```yaml
meta-labeling:
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.metalabel.rule=PathPrefix(`/api/metalabel`)"
    - "traefik.http.routers.metalabel.entrypoints=web"
    - "traefik.http.services.metalabel.loadbalancer.server.port=5007"
    - "traefik.docker.network=trade2026-backend"
    - "traefik.http.routers.metalabel.middlewares=cors-permissive@file,rate-limit-api@file"
```

---

## Testing Checklist

### Phase 1: Initial Deployment
- [ ] Traefik container starts without errors
- [ ] Dashboard accessible at http://localhost:8080/dashboard/
- [ ] All 8 backend services visible in dashboard
- [ ] No routing errors in Traefik logs

### Phase 2: Health Endpoints
- [ ] `/api/screener/health` returns 200
- [ ] `/api/rl/health` returns 200
- [ ] `/api/portfolio/health` returns 200
- [ ] `/api/backtest/health` returns 200
- [ ] `/api/factors/health` returns 200
- [ ] `/api/simulation/health` returns 200
- [ ] `/api/fracdiff/health` returns 200
- [ ] `/api/metalabel/health` returns 200

### Phase 3: Functional Endpoints
- [ ] `/api/screener/scan?limit=5` returns results
- [ ] `/api/screener/momentum?min_roc=5` returns results
- [ ] `/api/rl/` returns API documentation
- [ ] Other services return valid responses (not 404)

### Phase 4: Middleware Functionality
- [ ] CORS headers present in responses
- [ ] Rate limiting works (test with rapid requests)
- [ ] Compression enabled (check Content-Encoding header)
- [ ] Security headers present (check X-Frame-Options, CSP, etc.)

### Phase 5: Integration
- [ ] OMS accessible at `/api/orders/`
- [ ] Risk accessible at `/api/risk/`
- [ ] PTRC accessible at `/api/pnl/`
- [ ] Data Ingestion accessible at `/api/data/`

### Phase 6: Performance
- [ ] Response times < 50ms additional latency
- [ ] No memory leaks over 1 hour
- [ ] Dashboard shows healthy metrics

---

## Advantages Over nginx

| Feature | nginx (current) | Traefik (migrated) |
|---------|-----------------|-------------------|
| **Path Handling** | ❌ Manual rewrite rules | ✅ PathPrefix() automatic |
| **Service Discovery** | ❌ Manual upstream config | ✅ Docker label auto-discovery |
| **Configuration** | ❌ Complex nginx.conf | ✅ Simple Docker labels |
| **Dashboard** | ❌ None | ✅ Visual dashboard at :8080 |
| **Hot Reload** | ❌ Restart required | ✅ Automatic on label change |
| **Middleware** | ❌ Manual config | ✅ Pre-configured (CORS, rate limit, etc.) |
| **Metrics** | ⚠️ Need separate exporter | ✅ Built-in Prometheus metrics |
| **TLS** | ⚠️ Manual cert management | ✅ Let's Encrypt automatic |
| **Maintenance** | ❌ Error-prone | ✅ Self-documenting labels |
| **Debugging** | ❌ Read logs | ✅ Visual dashboard + logs |

---

## Rollback Plan

If Traefik doesn't work:

```bash
# Stop Traefik
docker-compose -f docker-compose.traefik.yml down

# Restart nginx
docker-compose -f docker-compose.api-gateway.yml.backup up -d

# All services still accessible via direct ports
# No data loss, no service interruption
```

---

## Post-Migration Tasks

### 1. Update Documentation (15 minutes)
- Update `API_GATEWAY_DEPLOYMENT_REPORT.md`
- Update `01_MASTER_PLAN.md`
- Create `TRAEFIK_USAGE_GUIDE.md`

### 2. Remove nginx Files (5 minutes)
```bash
rm -rf infrastructure/nginx.backup
rm infrastructure/docker/docker-compose.api-gateway.yml.backup
```

### 3. Update Frontend API Clients (Phase 7)
- No changes needed! URLs remain the same
- Still access via `http://localhost/api/...`

---

## Timeline Summary

| Step | Task | Time | Total |
|------|------|------|-------|
| 1 | Copy Traefik files | 15 min | 0:15 |
| 2 | Update network names | 10 min | 0:25 |
| 3 | Update volume paths | 5 min | 0:30 |
| 4 | Add backend service labels | 30 min | 1:00 |
| 5 | Update existing service labels | 10 min | 1:10 |
| 6 | Deploy Traefik | 10 min | 1:20 |
| 7 | Test services | 15 min | 1:35 |
| 8 | Switch traffic | 5 min | 1:40 |
| 9 | Clean up | 5 min | 1:45 |
| 10 | Update docs | 15 min | 2:00 |

**Total:** ~2 hours (includes testing and documentation)

---

## Conclusion

**This is MUCH easier than building Traefik from scratch!**

We're essentially just:
1. Copying existing working config
2. Changing network names
3. Adding 8 service labels
4. Testing

The Trade2025 Traefik configuration is production-ready with:
- Complete middleware suite
- TLS/HTTPS support
- Prometheus metrics
- Dashboard
- Rate limiting
- CORS
- Security headers

**Recommendation:** Proceed with this migration. It's lower risk and faster than fixing nginx path routing issues.

---

*Ready to start? Let me know and I'll begin the migration!*
