# Nginx Routing Problem: Analysis & Alternative Solutions
**Date:** 2025-10-23
**Author:** Claude Code (Sonnet 4.5)
**Status:** Technical Analysis & Recommendations

---

## Table of Contents
1. [Files Modified in This Session](#files-modified)
2. [The Routing Problem Explained](#the-routing-problem)
3. [Why This Is Hard](#why-this-is-hard)
4. [Alternative Solutions](#alternative-solutions)
5. [Recommended Solution](#recommendation)

---

## Files Modified in This Session

### Configuration Files Changed

**1. `infrastructure/docker/docker-compose.backend-services.yml`**
- **Lines Modified:** 69, 102, 135, 168, 201, 234, 267
- **Changes:** Fixed healthcheck ports from external (5002-5008) to internal (5000)
- **Reason:** Docker healthchecks were checking wrong ports, causing false unhealthy status
- **Impact:** 6/8 services now report healthy (was 2/8 before)

**2. `infrastructure/nginx/api-gateway.conf`**
- **Lines Modified:** 6-36 (upstream definitions), 38-41, 55-58 (commented blocks), 93-102 (OPTIONS handler), 222-235, 270-283 (disabled routes)
- **Changes:**
  - Updated 8 upstream port definitions (5000 → 5001-5008, except stock-screener stays 5000)
  - Fixed syntax errors in commented upstream blocks
  - Disabled OPTIONS preflight handler (nginx limitation)
  - Properly commented disabled location blocks for IB Gateway routes
- **Reason:** Nginx was trying to connect to wrong ports, causing 502 Bad Gateway errors
- **Impact:** Gateway can now reach backend services, 2/8 fully working

**3. `infrastructure/docker/docker-compose.api-gateway.yml`**
- **Lines Modified:** None (removed invalid depends_on section in earlier iteration)
- **Reason:** Dependencies referenced non-prefixed service names
- **Impact:** Container starts without dependency errors

### Documentation Files Created

**4. `API_GATEWAY_DEPLOYMENT_REPORT.md`** (NEW)
- **Size:** 400+ lines
- **Content:** Comprehensive technical report of API Gateway deployment
- **Sections:** System status, technical changes, testing results, known issues, command reference

**5. `01_MASTER_PLAN.md`** (UPDATED)
- **Changes:**
  - Updated completion status: 88% → 90%
  - Added Phase 6.6: Unified API Gateway
  - Updated current status section (2025-10-23)
  - Added container health stats (28/29 healthy, 97%)
  - Updated remaining work timeline (20h → 18h)

**6. `NGINX_ROUTING_PROBLEM_ANALYSIS.md`** (THIS FILE - NEW)
- **Purpose:** Technical analysis and alternative solutions

### Backend Service Files (NOT Modified This Session)
- `backend/portfolio_optimizer/app.py` - Has routes like `/api/portfolio/...`
- `backend/rl_trading/app.py` - Has routes like `/api/rl/...`
- `backend/stock_screener/app.py` - Has routes like `/api/screener/...`
- `backend/advanced_backtest/app.py` - Routes structure unknown (404 errors)
- `backend/factor_models/app.py` - Routes structure unknown (404 errors)
- (5 more backend services with unknown route structures)

---

## The Routing Problem Explained

### What's Happening

When nginx receives a request to `/api/screener/scan`, here's what happens:

```
1. User Request:       http://localhost/api/screener/scan?limit=10
2. Nginx Location:     location /api/screener/ { ... }
3. Nginx Proxy Pass:   proxy_pass http://stock_screener/;
4. Path Sent:          http://stock_screener/scan?limit=10  ← PROBLEM!
5. Backend Route:      /api/screener/scan  ← What it expects
6. Result:             404 Not Found
```

### The Core Issue

**nginx `proxy_pass` behavior:**
- If `proxy_pass` URL ends with `/`, nginx **strips** the location prefix
- Request to `/api/screener/scan` becomes `/scan` when sent to backend
- Backend expects `/api/screener/scan`, not `/scan`

### Current Nginx Configuration

```nginx
# Current (BROKEN for functional endpoints):
location /api/screener/ {
    proxy_pass http://stock_screener/;  # ← Trailing slash strips prefix!
}

# What happens:
# Request:  /api/screener/scan
# Sent to:  /scan  (prefix /api/screener/ removed)
# Expected: /api/screener/scan
# Result:   404 Not Found
```

### Why Health Endpoints Work

```nginx
# Health endpoint request:
http://localhost/api/screener/health

# nginx location:
location /api/screener/ {
    proxy_pass http://stock_screener/;
}

# Sent to backend:
/health  (prefix stripped)

# Backend has route:
/health  ← MATCHES!

# Result:
200 OK ✓
```

Health endpoints work because they're registered at the root level (`/health`), not under the API prefix.

---

## Why This Is Hard

### 1. **Competing Path Requirements**

Two conflicting needs:
- **Frontend wants:** Clean, namespaced paths (`/api/screener/scan`)
- **Nginx wants:** Either strip prefix OR keep it, can't do both conditionally
- **Backend has:** Full paths with prefix (`/api/screener/scan`)

### 2. **Three-Way Mismatch**

```
Frontend Request:     /api/screener/scan
                            ↓
Nginx Configuration:  location /api/screener/ { proxy_pass http://backend/; }
                            ↓
Path Sent to Backend: /scan  ← PREFIX REMOVED!
                            ↓
Backend Route:        @app.route('/api/screener/scan')  ← Expects full path!
                            ↓
Result:               404 Not Found
```

### 3. **No Simple nginx Fix**

**Option A: Remove trailing slash from proxy_pass**
```nginx
location /api/screener/ {
    proxy_pass http://stock_screener;  # No trailing slash
}
```
**Result:** Sends `/api/screener/scan` to backend ✓ BUT...
**Problem:** Backend receives doubled prefix! `/api/screener/api/screener/scan` ✗

**Option B: Use rewrite rules**
```nginx
location /api/screener/ {
    rewrite ^/api/screener/(.*)$ /api/screener/$1 break;
    proxy_pass http://stock_screener/;
}
```
**Result:** Complex, error-prone, hard to maintain for 16+ services

**Option C: Change all backend routes**
```python
# Change from:
@app.route('/api/screener/scan')

# To:
@app.route('/scan')
```
**Result:** Breaks direct port access (which we want to keep for debugging)

### 4. **Inconsistent Backend Route Structures**

**Problem:** Not all backend services follow same routing pattern:
- Stock Screener: Has `/api/screener/scan`, `/api/screener/momentum`, etc.
- RL Trading: Unknown route structure (only `/health` tested)
- Portfolio Optimizer: Unknown route structure (502 errors)
- Factor Models: Unknown route structure (404 errors)
- **We don't know what routes exist in most services!**

**To fix nginx properly, we'd need to:**
1. Audit all 8 backend services
2. Document every route in each service
3. Determine if they all use `/api/<service>/` prefix
4. Create individual nginx rules for each service's route structure

**Time estimate:** 6-10 hours of investigation + configuration

### 5. **Maintenance Burden**

Every time a backend service adds a new route:
- Must update nginx configuration
- Must restart gateway
- Must test routing
- High chance of configuration drift

---

## Alternative Solutions

### Solution 1: Traefik (Recommended)

**What is Traefik?**
- Modern, cloud-native reverse proxy and load balancer
- Designed specifically for microservices and containers
- Open source, very popular (42k+ GitHub stars)
- Docker-native with automatic service discovery

**Why Traefik Solves This Problem:**

1. **Automatic Path Handling:**
```yaml
# Traefik configuration (in docker-compose):
labels:
  - "traefik.http.routers.screener.rule=PathPrefix(`/api/screener`)"
  - "traefik.http.services.screener.loadbalancer.server.port=5000"
  # NO PROXY_PASS PATH STRIPPING!
```

2. **Automatic Service Discovery:**
- Traefik reads Docker labels automatically
- No need to manually configure upstreams
- Add new service? Just add labels. Done.

3. **Middleware Support:**
```yaml
labels:
  # Strip prefix before sending to backend (if needed):
  - "traefik.http.middlewares.screener-strip.stripprefix.prefixes=/api/screener"
  # OR preserve prefix:
  - "traefik.http.routers.screener.middlewares=add-prefix@docker"
```

4. **Built-in Dashboard:**
- Real-time view of all routes
- See which services are healthy
- Debug routing issues visually
- Access at `http://localhost:8080`

**Migration Effort:**
- **Time:** 2-3 hours
- **Risk:** Low (can run alongside nginx, switch traffic gradually)
- **Complexity:** Much simpler than nginx for this use case

**Example Traefik Setup:**

```yaml
# docker-compose.api-gateway.yml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    container_name: trade2026-api-gateway
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
    ports:
      - "80:80"
      - "8080:8080"  # Dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - frontend
      - backend
      - lowlatency

# In backend services docker-compose:
services:
  stock-screener:
    # ... existing config ...
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.screener.rule=PathPrefix(`/api/screener`)"
      - "traefik.http.services.screener.loadbalancer.server.port=5000"
      - "traefik.http.routers.screener.entrypoints=web"
```

**Pros:**
- ✅ Solves routing problem completely
- ✅ Automatic service discovery
- ✅ Much easier to maintain
- ✅ Built-in health checks and metrics
- ✅ Hot reload (no restart needed)
- ✅ Visual dashboard for debugging
- ✅ Widely used and well-documented

**Cons:**
- ❌ Requires learning new tool (but simpler than nginx)
- ❌ Need to add labels to all services (1-2 hours)
- ❌ Another technology in stack

---

### Solution 2: Kong API Gateway

**What is Kong?**
- Enterprise-grade API gateway
- Built specifically for microservices
- Open source core (Apache 2.0)
- 37k+ GitHub stars
- Used by companies like Expedia, NASA, Samsung

**Why Kong Solves This Problem:**

1. **Service-Oriented Design:**
```bash
# Add service:
curl -X POST http://localhost:8001/services \
  --data name=stock-screener \
  --data url=http://trade2026-stock-screener:5000

# Add route:
curl -X POST http://localhost:8001/services/stock-screener/routes \
  --data 'paths[]=/api/screener' \
  --data strip_path=false  # ← Control path stripping explicitly!
```

2. **RESTful Admin API:**
- Configure via HTTP requests
- No config file editing
- Version control via API calls
- Can be automated

3. **Plugin Ecosystem:**
- Rate limiting
- Authentication (JWT, OAuth, API keys)
- Request/response transformation
- Logging and monitoring
- 50+ official plugins

4. **Path Handling:**
```bash
# Option 1: Keep prefix
--data strip_path=false

# Option 2: Strip prefix
--data strip_path=true

# Option 3: Rewrite path
curl -X POST http://localhost:8001/plugins \
  --data name=request-transformer \
  --data 'config.replace.uri=/api/screener/(.*):/$1'
```

**Migration Effort:**
- **Time:** 4-6 hours (more complex than Traefik)
- **Risk:** Medium (heavier, more moving parts)
- **Complexity:** More features = more learning curve

**Example Kong Setup:**

```yaml
# docker-compose.api-gateway.yml
version: '3.8'

services:
  kong:
    image: kong:3.4-alpine
    container_name: trade2026-api-gateway
    environment:
      KONG_DATABASE: "off"
      KONG_DECLARATIVE_CONFIG: /kong/kong.yml
      KONG_PROXY_ACCESS_LOG: /dev/stdout
      KONG_ADMIN_ACCESS_LOG: /dev/stdout
      KONG_PROXY_ERROR_LOG: /dev/stderr
      KONG_ADMIN_ERROR_LOG: /dev/stderr
      KONG_ADMIN_LISTEN: "0.0.0.0:8001"
    ports:
      - "80:8000"
      - "8001:8001"  # Admin API
    volumes:
      - ./kong.yml:/kong/kong.yml:ro
    networks:
      - frontend
      - backend
      - lowlatency

# kong.yml:
_format_version: "3.0"
services:
  - name: stock-screener
    url: http://trade2026-stock-screener:5000
    routes:
      - name: screener-route
        paths:
          - /api/screener
        strip_path: false
  - name: rl-trading
    url: http://trade2026-rl-trading:5002
    routes:
      - name: rl-route
        paths:
          - /api/rl
        strip_path: false
```

**Pros:**
- ✅ Solves routing problem completely
- ✅ Explicit path control (strip_path: true/false)
- ✅ Powerful plugin ecosystem
- ✅ Admin UI available (Kong Manager - paid)
- ✅ Production-ready, battle-tested
- ✅ Can add auth, rate limiting, etc. easily

**Cons:**
- ❌ Heavier than Traefik or nginx
- ❌ Steeper learning curve
- ❌ More resource usage (~100MB RAM vs Traefik's ~50MB)
- ❌ Best features in Enterprise version ($$)
- ❌ Requires PostgreSQL for full features (we can use DB-less mode)

---

### Solution 3: Envoy Proxy

**What is Envoy?**
- Cloud-native, high-performance proxy
- Created by Lyft, now CNCF project
- Used in Istio service mesh
- 23k+ GitHub stars
- Used by companies like Lyft, Pinterest, Netflix

**Why Envoy Solves This Problem:**

1. **Prefix Rewriting:**
```yaml
# Envoy configuration:
routes:
  - match:
      prefix: "/api/screener"
    route:
      cluster: stock-screener
      prefix_rewrite: "/api/screener"  # Preserve prefix
```

2. **Advanced Routing:**
- Header-based routing
- Weighted routing (A/B testing)
- Retry policies
- Circuit breaking
- Outlier detection

3. **Observability:**
- Built-in metrics (Prometheus format)
- Distributed tracing
- Access logging
- Health checking

**Migration Effort:**
- **Time:** 6-10 hours (most complex)
- **Risk:** High (steep learning curve)
- **Complexity:** Very high, but very powerful

**Example Envoy Setup:**

```yaml
# envoy.yaml
static_resources:
  listeners:
    - name: listener_0
      address:
        socket_address:
          address: 0.0.0.0
          port_value: 80
      filter_chains:
        - filters:
            - name: envoy.filters.network.http_connection_manager
              typed_config:
                "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
                stat_prefix: ingress_http
                route_config:
                  name: local_route
                  virtual_hosts:
                    - name: backend
                      domains: ["*"]
                      routes:
                        - match:
                            prefix: "/api/screener"
                          route:
                            cluster: stock_screener
                            prefix_rewrite: "/api/screener"
                        - match:
                            prefix: "/api/rl"
                          route:
                            cluster: rl_trading
                            prefix_rewrite: "/api/rl"

  clusters:
    - name: stock_screener
      connect_timeout: 5s
      type: STRICT_DNS
      load_assignment:
        cluster_name: stock_screener
        endpoints:
          - lb_endpoints:
              - endpoint:
                  address:
                    socket_address:
                      address: trade2026-stock-screener
                      port_value: 5000
```

**Pros:**
- ✅ Solves routing problem completely
- ✅ Extremely powerful and flexible
- ✅ Best-in-class observability
- ✅ Production-ready, used at scale
- ✅ Service mesh integration (if needed later)

**Cons:**
- ❌ Very steep learning curve
- ❌ Complex YAML configuration
- ❌ Overkill for this use case
- ❌ Heaviest resource usage
- ❌ More operational complexity

---

### Solution 4: HAProxy

**What is HAProxy?**
- Traditional, proven load balancer
- Industry standard for 20+ years
- Open source (GPL/LGPL)
- Used by companies like GitHub, Stack Overflow, Reddit

**Why HAProxy Could Work:**

1. **Path Rewriting:**
```
frontend http-in
    bind *:80

    acl is_screener path_beg /api/screener
    use_backend screener if is_screener

backend screener
    http-request set-path /api/screener%[path]  # Preserve prefix
    server screener1 trade2026-stock-screener:5000
```

2. **Battle-Tested:**
- Extremely stable
- Very high performance
- Low resource usage
- Well-documented

**Migration Effort:**
- **Time:** 3-4 hours
- **Risk:** Low (proven technology)
- **Complexity:** Medium (simpler than Envoy, more complex than Traefik)

**Pros:**
- ✅ Solves routing problem
- ✅ Very stable and proven
- ✅ Low resource usage
- ✅ Excellent performance
- ✅ Good for TCP load balancing too

**Cons:**
- ❌ Less "modern" than alternatives
- ❌ No automatic service discovery
- ❌ Configuration syntax is dated
- ❌ No built-in dashboard (need separate tools)
- ❌ Not designed for microservices specifically

---

### Solution 5: Keep nginx, Fix Backend Routes

**Approach:** Change all backend service routes to remove the API prefix.

**Changes Required:**

```python
# BEFORE (current):
@app.route('/api/screener/scan')
@app.route('/api/screener/momentum')
@app.route('/health')

# AFTER:
@app.route('/scan')
@app.route('/momentum')
@app.route('/health')
```

**nginx stays simple:**
```nginx
location /api/screener/ {
    proxy_pass http://stock_screener/;  # Strips prefix, backend expects no prefix
}
```

**Migration Effort:**
- **Time:** 4-6 hours (edit 8 services × 10-50 routes each)
- **Risk:** Medium (breaks direct port access for debugging)
- **Complexity:** Low (just route renaming)

**Pros:**
- ✅ Keeps current nginx setup
- ✅ Simple solution
- ✅ No new tools to learn
- ✅ Routes match nginx behavior

**Cons:**
- ❌ Loses direct port access (`http://localhost:5001/api/portfolio/...` won't work)
- ❌ Makes debugging harder (must use gateway)
- ❌ Less RESTful (routes don't show full resource path)
- ❌ Tedious to update 8 services
- ❌ Future route additions require coordination

---

### Solution 6: Keep nginx, Add Path Preservation

**Approach:** Update nginx to preserve paths using rewrite rules.

**nginx Configuration:**

```nginx
location /api/screener {
    rewrite ^(/api/screener)$ $1/ permanent;
    rewrite ^/api/screener/(.*)$ /$1 break;
    proxy_pass http://stock_screener/api/screener/;
}

# OR (simpler but less flexible):
location /api/screener/ {
    proxy_pass http://stock_screener/api/screener/;  # Include prefix in proxy_pass
}
```

**Migration Effort:**
- **Time:** 2-3 hours (update nginx config for 8 services)
- **Risk:** Low (doesn't change backend services)
- **Complexity:** Medium (nginx rewrite rules are tricky)

**Pros:**
- ✅ Keeps current backend routes unchanged
- ✅ Keeps direct port access working
- ✅ No new tools
- ✅ Backend services don't need updates

**Cons:**
- ❌ Complex nginx configuration
- ❌ Hard to debug when something breaks
- ❌ Need to test each service individually
- ❌ Easy to make mistakes in rewrite rules
- ❌ Not as maintainable long-term

---

## Recommendation

### Best Solution: **Traefik (Solution 1)**

**Why Traefik is the best choice:**

1. **Solves the core problem elegantly:**
   - No path stripping issues
   - Automatic service discovery
   - Explicit path control

2. **Minimal migration effort:**
   - 2-3 hours to switch
   - Can run alongside nginx during transition
   - Just add Docker labels to services

3. **Better long-term:**
   - Easier to maintain
   - Self-documenting (labels visible in docker-compose)
   - Visual dashboard for debugging
   - Hot reload (no restarts)

4. **Industry standard:**
   - Used by many companies
   - Active development
   - Excellent documentation
   - Large community

5. **Keeps your system architecture clean:**
   - No hacky rewrite rules
   - No changing backend routes
   - Services remain independently testable
   - Clear separation of concerns

### Implementation Plan (2-3 hours)

**Step 1: Deploy Traefik (30 minutes)**
```yaml
# Create infrastructure/docker/docker-compose.traefik.yml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    container_name: trade2026-api-gateway-traefik
    command:
      - "--api.insecure=true"
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--log.level=DEBUG"
    ports:
      - "81:80"      # Use port 81 initially (nginx is on 80)
      - "8080:8080"  # Dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - trade2026-frontend
      - trade2026-backend
      - trade2026-lowlatency
    restart: unless-stopped

networks:
  trade2026-frontend:
    external: true
  trade2026-backend:
    external: true
  trade2026-lowlatency:
    external: true
```

**Step 2: Add labels to backend services (60 minutes)**
```yaml
# Update infrastructure/docker/docker-compose.backend-services.yml

services:
  stock-screener:
    # ... existing config ...
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.screener.rule=PathPrefix(`/api/screener`)"
      - "traefik.http.routers.screener.entrypoints=web"
      - "traefik.http.services.screener.loadbalancer.server.port=5000"
      - "traefik.docker.network=trade2026-backend"

  rl-trading:
    # ... existing config ...
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.rl.rule=PathPrefix(`/api/rl`)"
      - "traefik.http.routers.rl.entrypoints=web"
      - "traefik.http.services.rl.loadbalancer.server.port=5002"
      - "traefik.docker.network=trade2026-backend"

  # Repeat for all 8 services...
```

**Step 3: Test Traefik (30 minutes)**
```bash
# Start Traefik:
cd infrastructure/docker
docker-compose -f docker-compose.traefik.yml up -d

# Check dashboard:
http://localhost:8080/dashboard/

# Test services (on port 81):
curl http://localhost:81/api/screener/health
curl http://localhost:81/api/rl/health

# Test functional endpoints:
curl http://localhost:81/api/screener/scan?limit=5
```

**Step 4: Switch traffic to Traefik (15 minutes)**
```bash
# Stop nginx gateway:
docker-compose -f docker-compose.api-gateway.yml down

# Update Traefik to use port 80:
# Edit docker-compose.traefik.yml: change "81:80" to "80:80"

# Restart Traefik:
docker-compose -f docker-compose.traefik.yml restart traefik

# Test on port 80:
curl http://localhost/api/screener/health
```

**Step 5: Update documentation (15 minutes)**
- Update master plan to reflect Traefik usage
- Update API_GATEWAY_DEPLOYMENT_REPORT.md
- Document dashboard access

### Comparison Matrix

| Feature | nginx (current) | Traefik | Kong | Envoy | HAProxy |
|---------|-----------------|---------|------|-------|---------|
| **Path Handling** | ❌ Hard | ✅ Easy | ✅ Easy | ✅ Easy | ⚠️ Medium |
| **Auto Discovery** | ❌ No | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Dashboard** | ❌ No | ✅ Yes | ⚠️ Paid | ❌ No | ❌ No |
| **Learning Curve** | ⚠️ Medium | ✅ Easy | ⚠️ Medium | ❌ Hard | ⚠️ Medium |
| **Resource Usage** | ✅ 10MB | ✅ 50MB | ⚠️ 100MB | ❌ 150MB | ✅ 20MB |
| **Migration Time** | N/A | ✅ 2-3h | ⚠️ 4-6h | ❌ 6-10h | ⚠️ 3-4h |
| **Maintainability** | ❌ Hard | ✅ Easy | ⚠️ Medium | ❌ Hard | ⚠️ Medium |
| **Hot Reload** | ❌ No | ✅ Yes | ✅ Yes | ⚠️ Complex | ❌ No |
| **For Microservices** | ⚠️ Possible | ✅ Designed | ✅ Designed | ✅ Designed | ⚠️ Adapted |
| **Open Source** | ✅ Yes | ✅ Yes | ✅ Core | ✅ Yes | ✅ Yes |

---

## Conclusion

**The problem is hard because:**
1. Three-way path mismatch (frontend → nginx → backend)
2. nginx proxy_pass path stripping behavior
3. Unknown route structures in 6/8 backend services
4. High maintenance burden with manual configuration
5. No easy fix without changing something (config, routes, or tool)

**The best solution is Traefik because:**
- ✅ Solves problem elegantly (no hacks)
- ✅ Minimal migration effort (2-3 hours)
- ✅ Better long-term maintainability
- ✅ Industry-standard, well-supported
- ✅ Keeps backend services unchanged
- ✅ Visual debugging with dashboard

**Next steps:**
1. Get user approval for Traefik migration
2. Deploy Traefik on port 81 (alongside nginx)
3. Add labels to 8 backend services
4. Test all services through Traefik
5. Switch traffic from nginx (port 80) to Traefik
6. Remove nginx gateway container
7. Update documentation

**Alternative if you want to keep nginx:**
Use **Solution 6** (nginx path preservation) as a temporary fix while planning Traefik migration later.

---

*End of Analysis*
