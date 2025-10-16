# Trade2026 Directory Structure

**Last Updated**: 2025-10-14

## Overview

This document describes the complete directory structure for Trade2026.

## Top-Level Structure

```
Trade2026/
├── frontend/         # React web application
├── backend/          # Backend microservices
├── library/          # ML pipelines & strategies
├── infrastructure/   # Deployment configs
├── data/            # Persistent data (NOT in Git)
├── config/          # Configuration files
├── secrets/         # Secrets (NOT in Git)
├── docs/            # Documentation
├── tests/           # Test suites
└── scripts/         # Helper scripts
```

## Component Details

### frontend/
React 18.2 + TypeScript application
- Will contain code from C:\GUI\trade2025-frontend\
- 50+ pages, 41 routes, production-ready

### backend/
All backend microservices
- Will contain code from C:\Trade2025\trading\apps\
- 20+ services: gateway, normalizer, oms, risk, etc.
- Subdirectories:
  - apps/ - Individual services
  - shared/ - Shared utilities

### library/
ML pipelines and alpha strategies
- NEW development (not migrated)
- Subdirectories:
  - apps/ - Library registry service
  - pipelines/ - ML pipeline implementations
    - default_ml/ - XGBoost strategy
    - prism_physics/ - Physics-based analysis
    - hybrid/ - Combined ML + Physics
  - strategies/ - Alpha strategy implementations

### infrastructure/
Deployment and orchestration
- Subdirectories:
  - docker/ - Docker Compose + Dockerfiles
  - k8s/ - Kubernetes manifests
  - nginx/ - Nginx reverse proxy configs

### data/
Persistent data for all services
- **NOT tracked in Git**
- Subdirectories (one per service):
  - nats/ - Message bus persistence
  - valkey/ - Cache data
  - questdb/ - Time-series database
  - clickhouse/ - Analytics database
  - seaweed/ - Object storage
  - opensearch/ - Search index
  - postgres/ - Relational database
  - mlflow/ - ML tracking

### config/
Configuration files
- Subdirectories:
  - backend/ - Service configs
  - frontend/ - Frontend configs
  - library/ - ML pipeline configs
  - infrastructure/ - Deployment configs

### secrets/
Sensitive credentials and keys
- **NOT tracked in Git**
- Use .env.template files
- Contains: API keys, passwords, certificates

### docs/
Project documentation
- Subdirectories:
  - architecture/ - System design docs
  - api/ - API specifications
  - deployment/ - Deployment guides
  - user_guides/ - User documentation
  - troubleshooting/ - Common issues

### tests/
Test suites
- Subdirectories:
  - unit/ - Unit tests
  - component/ - Component tests
  - integration/ - Integration tests
  - e2e/ - End-to-end tests
  - performance/ - Performance tests
  - security/ - Security scans

### scripts/
Helper and automation scripts
- setup.sh - Initial setup
- migrate.sh - Data migration
- deploy.sh - Deployment automation
- cleanup.sh - Cleanup utilities

## Git Ignore Patterns

The following directories are excluded from Git:
- data/ - All persistent data
- secrets/ - All secrets (except templates)

## Maintenance

When adding new components:
1. Follow existing structure patterns
2. Document new directories here
3. Update .gitignore if needed
4. Add README.md to new directories

---

**Created**: 2025-10-14
**Status**: Complete
