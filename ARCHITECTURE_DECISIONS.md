# Architecture Decision Records (ADR)

**Project**: Trade2026 - Quantitative Trading & Research Platform
**Created**: 2025-10-23
**Last Updated**: 2025-10-23

---

## ADR-001: Production-Ready Design for Local Development

**Date**: 2025-10-23
**Status**: ✅ Accepted
**Decision Makers**: User + Claude Code

### Context

The Trade2026 platform is currently deployed locally on a Windows development machine. The user asked a fundamental question about the architecture approach:

> "I want to build for production even though for the foreseeable future it is only working here locally. I want you to reflect that in the master plan and all downstream documents."

This raised the question: Should we optimize for local development (simpler, fewer components) or production readiness (more complex, production-quality patterns)?

### Decision

**We will build with production-ready architecture patterns while running locally.**

**Core Principle**:
> "Build for production even though for the foreseeable future it is only working here locally."

### Rationale

**Why Production-Ready?**

1. **Zero Refactoring on Migration**: When ready to deploy to cloud (AWS, GCP, Azure), no architectural rework needed
2. **Learn Professional Patterns**: Build muscle memory with industry-standard tools and practices
3. **Confidence & Reliability**: Production-grade tools have better reliability, observability, and support
4. **Future-Proof**: No technical debt from "dev shortcuts" that would need cleanup later
5. **Cloud-Ready**: Easy migration when scale requires it (just change deployment target)

**Trade-offs Accepted**:

1. **Slightly Higher Initial Complexity**: More components and configuration than minimal dev setup
2. **Local Resource Usage**: Modern production stack requires reasonable hardware (manageable for current systems)
3. **Learning Curve**: Need to understand production tools (Traefik, Docker networks, health checks)

### Consequences

**Positive**:
- ✅ Professional architecture from day one
- ✅ No rework needed for production deployment
- ✅ Better reliability and monitoring
- ✅ Industry-standard patterns learned
- ✅ Easier to maintain and extend

**Negative**:
- ⚠️ More complex than minimal dev setup
- ⚠️ Requires understanding production tools
- ⚠️ Local machine must handle production-grade stack

**Accepted**: The benefits far outweigh the complexity cost.

---

## ADR-002: Traefik as Unified Gateway (Single External Entry Point)

**Date**: 2025-10-23
**Status**: ✅ Accepted
**Decision Makers**: User + Claude Code
**Context**: Phase 6.6-6.7 - API Gateway Implementation

### Context

The platform needed a unified entry point for all services. The user raised a critical architectural question:

> "Why did we install Traefik? It is supposed to replace something else, right? Like gateway or nginx? Am I right or wrong?"

The user was RIGHT - we needed to clarify the gateway architecture and avoid multiple overlapping gateways.

### Problem Statement

**Requirements**:
1. **External Simplicity**: Single entry point at `http://localhost`
2. **API Routing**: Dynamic routing to 34+ backend services
3. **Frontend Serving**: Serve React SPA static files
4. **Production Quality**: Professional architecture that scales

**Initial State**:
- nginx deployed as API gateway
- Frontend served by nginx
- Traefik partially configured
- Confusion about roles

### Alternatives Considered

#### Option A: nginx Only (Simple Gateway)
```
http://localhost (nginx)
  ├─ / → React static files
  ├─ /api/* → Backend services (manual upstreams)
```

**Pros**:
- Single component (simpler)
- nginx excellent for static files
- Familiar to many developers

**Cons**:
- Manual configuration for each service
- No dynamic service discovery
- Requires nginx reload for new services
- Not production-standard for microservices

#### Option B: Traefik + Frontend Container (Production Pattern) ✅ SELECTED
```
http://localhost (Traefik)
  ├─ / → Frontend Container (nginx internal)
  │      └─ React static files
  ├─ /api/* → Backend services (auto-discovered)
```

**Pros**:
- Industry-standard production pattern
- Dynamic service discovery (Docker labels)
- Zero-config routing for new services
- Single external entry point
- Professional architecture
- Easy cloud migration (Kubernetes ready)

**Cons**:
- Two components (Traefik + nginx)
- Slightly more complex initial setup

#### Option C: Traefik Only (Serve Static Files via Traefik)
```
http://localhost (Traefik)
  ├─ / → Static file server middleware
  ├─ /api/* → Backend services
```

**Pros**:
- Single component
- Dynamic service discovery

**Cons**:
- Traefik not designed for static files
- Worse performance than nginx
- Not production-standard
- Missing nginx optimizations (gzip, caching, etc.)

### Decision

**Selected: Option B - Traefik + Frontend Container (Production Pattern)**

### Architecture

**External View** (User's requirement - "simplicity"):
```
User → http://localhost (Single Entry Point)
  ├─ / → React application
  └─ /api/* → Backend services
```

**Internal View** (Production-ready - "right tool for each job"):
```
User → http://localhost:80 (Traefik - Reverse Proxy)
  │
  ├─ / → trade2026-frontend (nginx container - internal)
  │      └─ Serves React SPA from /usr/share/nginx/html
  │
  └─ /api/* → Backend services (auto-discovered via Docker labels)
      ├─ /api/portfolio → portfolio-optimizer
      ├─ /api/rl → rl-trading
      ├─ /api/backtest → advanced-backtest
      ├─ /api/factors → factor-models
      ├─ /api/simulation → simulation-engine
      ├─ /api/fracdiff → fractional-diff
      ├─ /api/metalabel → meta-labeling
      └─ /api/screener → stock-screener
```

### Rationale

**Why This Design?**

1. **Single External Endpoint**: User sees `http://localhost` - simple ✅
2. **Right Tool for Each Job**:
   - Traefik: Reverse proxy, dynamic routing (what it's designed for)
   - nginx: Static file serving (what it's designed for)
3. **Production Standard**: This is how modern microservice platforms work (e.g., Kubernetes Ingress + Frontend Pod)
4. **Zero-Config Service Discovery**: New services automatically registered via Docker labels
5. **Cloud-Ready**: Same pattern works in Kubernetes, AWS ECS, GCP Cloud Run

### Comparison to Industry Standards

**Same Pattern Used By**:
- Netflix (Zuul/Spring Cloud Gateway + nginx pods)
- Uber (envoy + static file servers)
- Airbnb (Kong + nginx containers)
- Most Kubernetes deployments (Ingress + nginx pods)

**Why Production Uses This**:
- Reverse proxies handle dynamic routing, TLS termination, load balancing
- Web servers (nginx) optimized for static files (gzip, caching, HTTP/2)
- Separation of concerns = better performance, maintainability

### Implementation Details

**Traefik Configuration**:
- Port: 80 (external)
- Dashboard: 8080
- Service discovery: Docker labels
- Routes: Dynamic via labels on backend services

**Frontend Container**:
- Base: nginx:alpine
- Content: React build (frontend/dist)
- Ports: None exposed externally (Traefik routes to it internally)
- Network: trade2026-frontend

**Result**:
- External complexity: Zero (single URL)
- Internal correctness: Professional (right tools for each job)

### Consequences

**Positive**:
- ✅ Production-ready architecture
- ✅ Single external entry point (user requirement)
- ✅ Dynamic service discovery (zero-config for new services)
- ✅ Professional patterns learned
- ✅ Cloud migration trivial (same pattern)
- ✅ Better performance (nginx for static, Traefik for routing)

**Neutral**:
- Two components instead of one (acceptable for production quality)
- Requires understanding Traefik labels (industry-standard skill)

**Negative**:
- None identified

### Migration Path

**From Current State** (nginx only):
1. ✅ Deploy Traefik (Phase 6.6 - DONE)
2. ✅ Add Docker labels to backend services (Phase 6.7 - DONE)
3. ⏸️ Reconfigure frontend container for internal nginx (Phase 7 - IN PROGRESS)
4. ⏸️ Route / to frontend via Traefik (Phase 7 - IN PROGRESS)
5. Remove old nginx external ports

**To Cloud** (when ready):
1. Change Docker Compose → Kubernetes manifests
2. Traefik → Kubernetes Ingress (or keep Traefik)
3. Docker labels → Ingress annotations
4. Zero application code changes

---

## ADR-003: Container Port & Network Guidelines Standard (CPGS v1.0)

**Date**: Phase 1 (October 2025)
**Status**: ✅ Accepted & Implemented

### Decision

Standardize port ranges and network isolation for all services:

**Port Ranges**:
- **80, 443**: External entry point (Traefik)
- **8000-8199**: Low-latency trading services
- **8300-8499**: Backend application services
- **5000-5099**: Analytics services (Trade2025 migration)
- **4222, 6379, 9000, etc.**: Infrastructure services (standard ports)

**Networks**:
- **trade2026-frontend**: External-facing (Traefik, frontend, authn)
- **trade2026-lowlatency**: Trading core (NATS, gateways, OMS, risk)
- **trade2026-backend**: Supporting services (databases, cache, storage)

### Rationale

- Clear service categories
- No port conflicts
- Network isolation for security
- Production-ready boundaries

---

## ADR-004: Docker Healthchecks for All Services

**Date**: Phase 1-2 (October 2025)
**Status**: ✅ Implemented

### Decision

All services must implement Docker healthchecks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Rationale

- Container orchestration (Docker Compose, Kubernetes) relies on health status
- Traefik only routes to healthy services
- Enables automatic restarts and failover
- Production-standard practice

### Lessons Learned

**Phase 6.5 Issue**: Port mismatches caused all 8 backend services to show unhealthy
**Phase 6.7 Fix**: Standardized SERVICE_PORT environment variable across all services
**Result**: 8/8 services HEALTHY, Traefik registration 100%

---

## ADR-005: Observability First (Prometheus, Grafana, Tracing)

**Date**: Design decision for Phase 9
**Status**: ⏸️ Approved, Pending Implementation

### Decision

Deploy full observability stack from day one:

- **Prometheus**: Metrics collection (Phase 9)
- **Grafana**: Visualization dashboards (Phase 9)
- **Alertmanager**: Alert routing (Phase 9)
- **Distributed Tracing**: Jaeger or Zipkin (Phase 9)

### Rationale

- Production systems require observability
- Easier to add monitoring during build than retrofit later
- Critical for troubleshooting in production
- Industry standard for microservices

---

## Summary

| ADR | Decision | Status | Impact |
|-----|----------|--------|--------|
| 001 | Production-Ready Design | ✅ Accepted | High - Defines overall approach |
| 002 | Traefik + Frontend Container | ✅ Accepted | High - Core architecture |
| 003 | CPGS v1.0 (Ports & Networks) | ✅ Implemented | High - All services follow |
| 004 | Docker Healthchecks | ✅ Implemented | Medium - Reliability |
| 005 | Observability First | ⏸️ Approved | High - Phase 9 implementation |

---

## References

- **Master Plan**: [01_MASTER_PLAN.md](./01_MASTER_PLAN.md)
- **Completion Tracker**: [01_COMPLETION_TRACKER_UPDATED.md](./01_COMPLETION_TRACKER_UPDATED.md)
- **Phase 6.7 Report**: [PHASE_6.7_STATUS_REPORT.md](./PHASE_6.7_STATUS_REPORT.md)
- **Full Completion Plan**: [TRADE2026_COMPLETION_PLAN.md](./TRADE2026_COMPLETION_PLAN.md)

---

**Last Updated**: 2025-10-23
**Document Owner**: Trade2026 Team
**Review Cycle**: As needed for major architectural changes
