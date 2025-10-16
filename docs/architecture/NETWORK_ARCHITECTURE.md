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
