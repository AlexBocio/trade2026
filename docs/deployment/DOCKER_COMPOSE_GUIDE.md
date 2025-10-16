# Docker Compose Usage Guide

**Last Updated**: 2025-10-14
**Phase**: 1 - Foundation Complete
**Services**: 8 Core Infrastructure Services

---

## Quick Start

### Start All Services
```bash
cd C:\ClaudeDesktop_Projects\Trade2026

# Using helper script (recommended)
bash scripts/up.sh

# Or using docker-compose directly
cd infrastructure/docker
docker-compose up -d
```

### Stop All Services
```bash
# Using helper script (recommended)
bash scripts/down.sh

# Or using docker-compose directly
cd infrastructure/docker
docker-compose down
```

### Check Status
```bash
# Using helper script (includes health checks)
bash scripts/status.sh

# Or using docker-compose
cd infrastructure/docker
docker-compose ps
```

### View Logs
```bash
# All services (follow mode)
bash scripts/logs.sh

# Specific service (follow mode)
bash scripts/logs.sh nats

# Last 100 lines (all services)
bash scripts/logs.sh --tail=100

# Last 50 lines (specific service)
bash scripts/logs.sh nats --tail=50

# Or using docker-compose directly
cd infrastructure/docker
docker-compose logs -f nats
```

---

## Compose File Structure

### Master File
**File**: `infrastructure/docker/docker-compose.yml`

The master file uses the `include:` directive to combine all modular compose files:

```yaml
include:
  - path: docker-compose.networks.yml    # Networks (CPGS v1.0)
  - path: docker-compose.core.yml        # Core infrastructure (8 services)
  # Future: docker-compose.apps.yml      # Backend services (Phase 2)
  # Future: docker-compose.frontend.yml  # Frontend (Phase 3)
  # Future: docker-compose.library.yml   # ML library (Phase 4)
```

### Modular Files

#### docker-compose.networks.yml
Defines the three-lane network architecture (CPGS v1.0):
- **trade2026-frontend** (172.23.0.0/16) - Public-facing services
- **trade2026-lowlatency** (172.22.0.0/16) - High-performance messaging
- **trade2026-backend** (172.21.0.0/16) - Databases and internal services

#### docker-compose.core.yml
Core infrastructure services (8 services):
1. **NATS** - Message streaming with JetStream
2. **Valkey** - Redis-compatible cache/state store
3. **QuestDB** - Time-series database
4. **ClickHouse** - OLAP analytics database
5. **SeaweedFS** - S3-compatible object storage
6. **OpenSearch** - Full-text search engine
7. **authn** - Authentication service (JWT/JWKS)
8. **OPA** - Open Policy Agent (authorization)

---

## Modular Approach Benefits

### Why Modular Files?
- ✅ **Start only what you need** - Don't need full stack? Start just core services
- ✅ **Easy to understand** - One file per logical component
- ✅ **Simple to modify** - Change one component without affecting others
- ✅ **Version control friendly** - Smaller, focused diffs
- ✅ **Team collaboration** - Different teams can work on different files

### Example: Start Only Core Infrastructure
```bash
cd infrastructure/docker
docker-compose -f docker-compose.core.yml up -d
```

### Example: Start Core + Backend Apps (Phase 2)
```bash
cd infrastructure/docker
docker-compose -f docker-compose.core.yml -f docker-compose.apps.yml up -d
```

---

## Common Operations

### Restart Specific Service
```bash
cd infrastructure/docker
docker-compose restart nats
```

### Rebuild Service (authn or OPA)
```bash
cd infrastructure/docker

# Rebuild and restart authn
docker-compose up -d --build authn

# Or using helper script
bash ../../scripts/up.sh --build
```

### View Service Logs
```bash
# Real-time logs
docker-compose logs -f authn

# Last 100 lines
docker-compose logs --tail=100 authn

# All logs since start
docker-compose logs authn
```

### Execute Command in Container
```bash
# Valkey CLI
docker exec -it valkey valkey-cli

# Check QuestDB tables
docker exec questdb curl http://localhost:9000/exec?query=SHOW%20TABLES

# Check ClickHouse version
docker exec clickhouse clickhouse-client --query="SELECT version()"
```

### Stop and Remove Volumes (DESTRUCTIVE!)
```bash
cd infrastructure/docker

# ⚠️ WARNING: This deletes all data!
docker-compose down -v

# Or using helper script
bash ../../scripts/down.sh -v
```

### Scale Service (if applicable)
```bash
# Scale a stateless service to 3 instances
docker-compose up -d --scale gateway=3
```

---

## Environment Variables

### File Locations
- **Template**: `infrastructure/docker/.env.template` (version controlled)
- **Active**: `infrastructure/docker/.env` (NOT in Git, contains secrets)

### Configuration
The `.env` file contains all configuration for services:

**Core Infrastructure**:
- NATS connection URLs
- Valkey (Redis) settings
- Database connection strings
- S3 credentials
- Authentication settings

**Service Secrets**:
- Client credentials for service-to-service auth
- External API keys (Binance, Alpaca, IB)

**Network Configuration**:
- CPGS v1.0 network names and subnets

### Updating Variables

**Step 1**: Edit `.env` file
```bash
cd infrastructure/docker
vim .env  # or your preferred editor
```

**Step 2**: Restart services
```bash
docker-compose up -d
```

**Step 3**: Verify changes
```bash
docker-compose logs <service_name>
```

### Adding New Variables

**Step 1**: Add to `.env.template` (for version control)
```bash
# In .env.template
NEW_SERVICE_URL=http://new-service:8080
```

**Step 2**: Add to `.env` (for active use)
```bash
# In .env
NEW_SERVICE_URL=http://new-service:8080
```

**Step 3**: Update service configuration
```yaml
# In docker-compose file
environment:
  - NEW_SERVICE_URL=${NEW_SERVICE_URL}
```

---

## Service Access Points

### Core Infrastructure Services

**NATS** (Message Streaming):
- Client: `nats://localhost:4222`
- Monitoring: `http://localhost:8222`
- Health: `http://localhost:8222/healthz`

**Valkey** (Cache):
- TCP: `localhost:6379`
- CLI: `docker exec valkey valkey-cli`

**QuestDB** (Time-Series DB):
- Web Console: `http://localhost:9000`
- PostgreSQL: `localhost:8812`
- InfluxDB: `localhost:9009`

**ClickHouse** (Analytics):
- HTTP API: `http://localhost:8123`
- Native TCP: `localhost:9001`

**SeaweedFS** (S3 Storage):
- S3 API: `http://localhost:8333`
- Master: `http://localhost:9333`
- Filer: `http://localhost:8081`

**OpenSearch** (Search):
- REST API: `http://localhost:9200`
- Performance: `http://localhost:9600`

**authn** (Authentication):
- API: `http://localhost:8114`
- Health: `http://localhost:8114/health`
- JWKS: `http://localhost:8114/.well-known/jwks.json`

**OPA** (Authorization):
- API: `http://localhost:8181`
- Health: `http://localhost:8181/health`

---

## Troubleshooting

### Services Won't Start

**Check logs for errors**:
```bash
docker-compose logs <service_name>

# Look for common issues:
# - Port already in use
# - Volume permission denied
# - Network not found
# - Configuration errors
```

**Verify networks exist**:
```bash
docker network ls | grep trade2026

# Should show:
# - trade2026-frontend
# - trade2026-lowlatency
# - trade2026-backend
```

**Check port conflicts**:
```bash
# Windows
netstat -ano | findstr :4222

# Linux/Mac
lsof -i :4222

# Stop conflicting service
docker stop <container_id>
```

### Health Checks Failing

**Manual health checks**:
```bash
# NATS
curl http://localhost:8222/healthz

# Valkey
docker exec valkey valkey-cli ping

# QuestDB
curl http://localhost:9000/

# ClickHouse
curl http://localhost:8123/ping

# authn
curl http://localhost:8114/health

# OPA
curl http://localhost:8181/health
```

**Check container logs**:
```bash
bash scripts/logs.sh <service_name> --tail=100
```

### Service Keeps Restarting

**Check restart policy**:
```bash
docker inspect <container_name> | grep -A 5 RestartPolicy
```

**View last 200 lines of logs**:
```bash
docker logs --tail=200 <container_name>
```

**Common causes**:
- Configuration file missing or invalid
- Port already in use
- Insufficient memory/resources
- Volume mount permission issues

### Reset Everything (Nuclear Option)

```bash
# Stop and remove all containers
cd infrastructure/docker
docker-compose down -v

# Remove networks
docker network rm trade2026-frontend trade2026-lowlatency trade2026-backend

# Remove all Trade2026 data
rm -rf ../../data/*

# Start fresh
bash ../../scripts/up.sh
```

### Docker Compose Version Issues

**Check version**:
```bash
docker-compose --version

# Need version 1.28.0+ for include: directive
```

**Upgrade Docker Compose**:
```bash
# Windows: Update Docker Desktop
# Linux: https://docs.docker.com/compose/install/
```

### Permission Errors (Linux)

**Fix volume permissions**:
```bash
# Give Docker permission to volumes
sudo chown -R 1000:1000 data/
sudo chown -R 1000:1000 secrets/
```

---

## Best Practices

### DO ✅

**Use helper scripts**:
- Simplifies operations
- Provides consistent commands
- Includes helpful output

**Keep .env file updated**:
- Always match .env to .env.template
- Document any custom changes

**Check logs when services fail**:
- Logs usually reveal the issue
- Use `--tail=100` to limit output

**Run status checks regularly**:
- Verify services are healthy
- Catch issues early

**Stop services when not in use**:
- Saves system resources
- Prevents unnecessary wear

**Use modular compose files**:
- Start only needed services
- Easier to debug issues

### DON'T ❌

**Commit .env file to Git**:
- Contains secrets and API keys
- Use .env.template instead

**Modify master docker-compose.yml frequently**:
- Use modular files instead
- Keeps master file clean

**Hardcode values**:
- Use environment variables
- Makes configuration flexible

**Run services on host network**:
- Use Docker networks (CPGS v1.0)
- Provides isolation and security

**Delete volumes carelessly**:
- Use `down -v` only when intentional
- Volumes contain persistent data

**Ignore warnings or errors**:
- Address issues promptly
- Small issues can cascade

---

## Next Steps

### Phase 2: Backend Application Services

**When**: After Phase 1 validation complete

**Tasks**:
1. Create `docker-compose.apps.yml` for backend services
2. Define 20+ microservices (OMS, Risk, Gateway, etc.)
3. Update .env.template with backend service variables
4. Uncomment include in master compose file
5. Test integration with core infrastructure

**Services**:
- Gateway (market data)
- OMS (order management)
- Risk (pre-trade checks)
- Execution (order routing)
- FillProcessor (post-trade)
- PositionTracker (real-time positions)
- PnL (profit & loss)
- PTRC (portfolio/trades/risk/compliance)

### Phase 3: Frontend Application

**When**: After Phase 2 backend deployed

**Tasks**:
1. Create `docker-compose.frontend.yml`
2. Build React app Docker image
3. Configure nginx for routing
4. Update .env.template with frontend variables
5. Uncomment include in master compose file

**Components**:
- React frontend app
- nginx reverse proxy
- Static asset serving

### Phase 4: ML Library & Pipelines

**When**: After Phase 3 frontend integrated

**Tasks**:
1. Create `docker-compose.library.yml`
2. Deploy ML model serving
3. Configure training pipelines
4. Set up feature stores
5. Uncomment include in master compose file

**Components**:
- Model serving endpoints
- Training pipelines
- Feature store
- ML experiment tracking

---

## Maintenance

### Regular Tasks

**Daily**:
- Check service status: `bash scripts/status.sh`
- Monitor logs for errors: `bash scripts/logs.sh --tail=100`

**Weekly**:
- Review resource usage: `docker stats`
- Check disk space: `df -h data/`
- Update .env if needed

**Monthly**:
- Update Docker images: `docker-compose pull`
- Review and clean old data
- Backup important volumes

### Monitoring

**Service Health**:
```bash
# Automated status check
bash scripts/status.sh

# Manual checks per service
curl http://localhost:8222/healthz  # NATS
curl http://localhost:8114/health   # authn
```

**Resource Usage**:
```bash
# Real-time stats
docker stats

# Container resource limits
docker inspect <container> | grep -A 10 Resources
```

**Network Connectivity**:
```bash
# Check networks
docker network ls | grep trade2026

# Inspect network
docker network inspect trade2026-backend
```

---

## Appendix

### File Locations Reference

```
Trade2026/
├── infrastructure/docker/
│   ├── docker-compose.yml              # Master file
│   ├── docker-compose.networks.yml     # Networks
│   ├── docker-compose.core.yml         # Core infrastructure
│   ├── .env.template                   # Template (in Git)
│   └── .env                            # Active config (NOT in Git)
├── scripts/
│   ├── up.sh                           # Start services
│   ├── down.sh                         # Stop services
│   ├── logs.sh                         # View logs
│   └── status.sh                       # Check health
├── data/                                # Persistent volumes
│   ├── nats/
│   ├── valkey/
│   ├── questdb/
│   ├── clickhouse/
│   ├── seaweed/
│   └── opensearch/
└── docs/deployment/
    └── DOCKER_COMPOSE_GUIDE.md         # This file
```

### Port Reference

| Service     | Ports                          | Purpose                      |
|-------------|--------------------------------|------------------------------|
| NATS        | 4222, 8222                     | Client, Monitoring           |
| Valkey      | 6379                           | Redis protocol               |
| QuestDB     | 9000, 8812, 9009               | HTTP, Postgres, InfluxDB     |
| ClickHouse  | 8123, 9001                     | HTTP, Native TCP             |
| SeaweedFS   | 8333, 9333, 8081               | S3, Master, Filer            |
| OpenSearch  | 9200, 9600                     | REST API, Performance        |
| authn       | 8114                           | Authentication API           |
| OPA         | 8181                           | Authorization API            |

### Network Reference (CPGS v1.0)

| Network                | Subnet         | Purpose                     |
|------------------------|----------------|----------------------------|
| trade2026-frontend     | 172.23.0.0/16  | Public-facing services     |
| trade2026-lowlatency   | 172.22.0.0/16  | High-performance messaging |
| trade2026-backend      | 172.21.0.0/16  | Internal services          |

---

**Status**: Phase 1 Complete ✅
**Services**: 8/8 Core Infrastructure Operational
**Next**: Task 05 - Validate Core Services
