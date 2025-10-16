# Task 01: Create Trade2026 Directory Structure

**Phase**: 1 - Foundation
**Priority**: P0-Critical
**Estimated Time**: 1 hour
**Dependencies**: None
**Created**: 2025-10-14
**Assigned To**: Claude Code

---

# 🛑 STOP - READ THIS FIRST 🛑

## MANDATORY READING BEFORE ANY CODE EXECUTION

**Claude Code**: You MUST read these files IN FULL before starting any work. This is NON-NEGOTIABLE.

### 1. MASTER_GUIDELINES.md (CRITICAL - READ FIRST)
**Location**: `C:\ClaudeDesktop_Projects\ClaudeKnowledge\MASTER_GUIDELINES.md`

**YOU MUST READ THESE SECTIONS** (use file_read tool):
- [ ] **New Session Startup Protocol** - How to begin ANY session
- [ ] **Core Development Rules** - Component Isolation, Read Before Write, Backup Critical Files
- [ ] **6-Phase Mandatory Workflow** - EVERY task follows this workflow
- [ ] **File Operations** - Read before write, validation, error handling
- [ ] **Testing & Validation Rules** - How to validate your work
- [ ] **Documentation Standards** - What to document

**Why This Matters**: These guidelines contain critical rules about:
- ✅ How to read files before modifying them
- ✅ How to handle errors and rollback
- ✅ Token budget management (you have limits!)
- ✅ Testing and validation requirements
- ✅ When to stop and ask for help

**Estimated Time**: 5-10 minutes to read the relevant sections

### 2. Project Context (MUST READ AFTER GUIDELINES)
**Location**: `C:\ClaudeDesktop_Projects\Trade2026\MASTER_PLAN.md`
- [ ] Read the full overview to understand the integration project

**Location**: `C:\ClaudeDesktop_Projects\Trade2026\appendices\appendix_A_foundation.md`
- [ ] Read Phase 1 details to understand what you're building

**Estimated Time**: 5 minutes

---

## ⚠️ CONSEQUENCES OF NOT READING GUIDELINES

If you skip reading MASTER_GUIDELINES.md, you will:
- ❌ Miss critical error handling procedures
- ❌ Not follow the 6-Phase Workflow (required for every task)
- ❌ Risk running out of token budget mid-task
- ❌ Skip validation steps (causing failures later)
- ❌ Make mistakes that could have been avoided

**The guidelines exist to prevent failures. READ THEM FIRST.**

---

## ✅ CHECKLIST BEFORE PROCEEDING

**I confirm I have read and understood**:
- [ ] MASTER_GUIDELINES.md - New Session Startup Protocol
- [ ] MASTER_GUIDELINES.md - Core Development Rules
- [ ] MASTER_GUIDELINES.md - 6-Phase Mandatory Workflow  
- [ ] MASTER_GUIDELINES.md - File Operations
- [ ] MASTER_GUIDELINES.md - Testing & Validation Rules
- [ ] MASTER_PLAN.md - Project overview
- [ ] appendix_A_foundation.md - Phase 1 context

**Total Reading Time**: ~15 minutes

**Only proceed to "OBJECTIVE" section below after completing this checklist.**

---

## ⚠️ CRITICAL RULES FOR THIS TASK

### Rule 1: Clean Slate
This is a NEW unified platform. Everything goes in `C:\ClaudeDesktop_Projects\Trade2026\`

### Rule 2: No Code Movement Yet
This task ONLY creates directories. We move code in later tasks.

### Rule 3: Follow Exact Structure
Use the exact directory structure specified. This ensures consistency.

---

## 📋 OBJECTIVE

Create the complete directory structure for Trade2026 that will house:
1. Frontend (from C:\GUI\)
2. Backend (from C:\Trade2025\)
3. ML Library (new development)
4. Infrastructure configs
5. All persistent data
6. Documentation and tests

**Why This Matters**: A well-organized structure makes integration seamless and maintainable.

---

## 🎯 CONTEXT

### Current State
- Backend code in: `C:\Trade2025\`
- Frontend code in: `C:\GUI\`
- ML Pipeline designs in: `C:\ClaudeDesktop_Projects\ML_Pipelines\`
- No unified structure exists

### What We're Building
A single directory that will contain EVERYTHING:
```
Trade2026/
├── frontend/         # React app
├── backend/          # All microservices
├── library/          # ML pipelines & strategies
├── infrastructure/   # Docker, Kubernetes, Nginx
├── data/            # All persistent data (NOT in Git)
├── config/          # Configuration files
├── secrets/         # Secrets (NOT in Git)
├── docs/            # Documentation
├── tests/           # Test suites
└── scripts/         # Helper scripts
```

---

## ✅ REQUIREMENTS

### Functional Requirements
1. Create complete directory structure
2. All directories properly nested
3. Structure matches specification exactly
4. README files in key directories

### Non-Functional Requirements
- **Organization**: Logical grouping of related components
- **Scalability**: Easy to add new services/components
- **Clarity**: Clear purpose for each directory

---

## 🔧 IMPLEMENTATION STEPS

### Step 1: Create Root Directories
**Goal**: Create main top-level directories

**Actions**:
```bash
# Navigate to project root
cd C:\ClaudeDesktop_Projects\Trade2026

# Create main directories
mkdir frontend
mkdir backend
mkdir library
mkdir infrastructure
mkdir data
mkdir config
mkdir secrets
mkdir docs
mkdir tests
mkdir scripts
```

**Validation**:
```bash
ls -la
# Should show all 10 directories
```

**Checklist**:
- [ ] frontend/ exists
- [ ] backend/ exists
- [ ] library/ exists
- [ ] infrastructure/ exists
- [ ] data/ exists
- [ ] config/ exists
- [ ] secrets/ exists
- [ ] docs/ exists
- [ ] tests/ exists
- [ ] scripts/ exists

---

### Step 2: Create Backend Subdirectories
**Goal**: Setup structure for backend microservices

**Actions**:
```bash
cd backend

# Create subdirectories
mkdir apps
mkdir shared
```

**Purpose**:
- `apps/` - Individual microservices (gateway, oms, risk, etc.)
- `shared/` - Shared libraries and utilities

**Validation**:
```bash
cd backend
ls -la
# Should show: apps/, shared/
```

---

### Step 3: Create Library Subdirectories
**Goal**: Setup structure for ML pipelines and strategies

**Actions**:
```bash
cd ../library

# Create subdirectories
mkdir apps
mkdir pipelines
mkdir strategies
```

**Purpose**:
- `apps/` - Library service (registry, API)
- `pipelines/` - ML pipeline implementations
- `strategies/` - Alpha strategies

**Validation**:
```bash
cd library
ls -la
# Should show: apps/, pipelines/, strategies/
```

**Create pipeline subdirectories**:
```bash
cd pipelines
mkdir default_ml
mkdir prism_physics
mkdir hybrid
cd ..
```

---

### Step 4: Create Infrastructure Subdirectories
**Goal**: Setup structure for deployment configs

**Actions**:
```bash
cd ../infrastructure

# Create subdirectories
mkdir docker
mkdir k8s
mkdir nginx
```

**Purpose**:
- `docker/` - Docker Compose files, Dockerfiles
- `k8s/` - Kubernetes manifests
- `nginx/` - Nginx configuration

**Create Docker subdirectories**:
```bash
cd docker
mkdir Dockerfiles
cd ..
```

**Validation**:
```bash
cd infrastructure
ls -la
# Should show: docker/, k8s/, nginx/
```

---

### Step 5: Create Data Subdirectories
**Goal**: Setup structure for persistent data

**Actions**:
```bash
cd ../data

# Create subdirectories for each service
mkdir nats
mkdir valkey
mkdir questdb
mkdir clickhouse
mkdir seaweed
mkdir opensearch
mkdir postgres
mkdir mlflow
```

**Purpose**: Each service gets isolated data directory

**⚠️ IMPORTANT**: Add .gitignore
```bash
cd data
cat > .gitignore << 'EOF'
# Ignore all data files
*

# But keep the directory structure
!.gitignore
!*/
EOF
```

**Validation**:
```bash
cd data
ls -la
# Should show 8 service directories + .gitignore
```

---

### Step 6: Create Config Subdirectories
**Goal**: Setup structure for configuration files

**Actions**:
```bash
cd ../config

# Create subdirectories
mkdir backend
mkdir frontend
mkdir library
mkdir infrastructure
```

**Purpose**: Configuration files organized by component

**Validation**:
```bash
cd config
ls -la
# Should show: backend/, frontend/, library/, infrastructure/
```

---

### Step 7: Create Docs Subdirectories
**Goal**: Setup structure for documentation

**Actions**:
```bash
cd ../docs

# Create subdirectories
mkdir architecture
mkdir api
mkdir deployment
mkdir user_guides
mkdir troubleshooting
```

**Purpose**: Organized documentation by type

**Validation**:
```bash
cd docs
ls -la
# Should show 5 subdirectories
```

---

### Step 8: Create Tests Subdirectories
**Goal**: Setup structure for test suites

**Actions**:
```bash
cd ../tests

# Create subdirectories
mkdir unit
mkdir component
mkdir integration
mkdir e2e
mkdir performance
mkdir security
```

**Purpose**: Tests organized by type/level

**Validation**:
```bash
cd tests
ls -la
# Should show 6 test directories
```

---

### Step 9: Add .gitignore for Secrets
**Goal**: Ensure secrets never committed to Git

**Actions**:
```bash
cd ../secrets

# Create .gitignore
cat > .gitignore << 'EOF'
# Ignore all secrets
*

# But keep directory structure
!.gitignore
!*.template
EOF

# Create template file
cat > secrets.env.template << 'EOF'
# Secret Template - Copy to secrets.env and fill in values

# Database passwords
POSTGRES_PASSWORD=
CLICKHOUSE_PASSWORD=

# API Keys
BINANCE_API_KEY=
BINANCE_SECRET=
ALPACA_API_KEY=
ALPACA_SECRET=

# JWT Signing Key
JWT_SECRET=

# Add other secrets as needed
EOF
```

**Validation**:
```bash
cd secrets
ls -la
# Should show: .gitignore, secrets.env.template
```

---

### Step 10: Create Directory Documentation
**Goal**: Document the structure for future reference

**Actions**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026

# Create DIRECTORY_STRUCTURE.md
cat > DIRECTORY_STRUCTURE.md << 'EOF'
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
EOF
```

**Validation**:
```bash
cat DIRECTORY_STRUCTURE.md
# Should display the complete documentation
```

---

### Step 11: Verify Complete Structure
**Goal**: Ensure all directories created correctly

**Actions**:
```bash
cd C:\ClaudeDesktop_Projects\Trade2026

# Use tree command (if available) or manual check
tree -L 3
# Or manually verify
```

**Expected Structure**:
```
Trade2026/
├── DIRECTORY_STRUCTURE.md
├── backend/
│   ├── apps/
│   └── shared/
├── config/
│   ├── backend/
│   ├── frontend/
│   ├── infrastructure/
│   └── library/
├── data/
│   ├── .gitignore
│   ├── clickhouse/
│   ├── mlflow/
│   ├── nats/
│   ├── opensearch/
│   ├── postgres/
│   ├── questdb/
│   ├── seaweed/
│   └── valkey/
├── docs/
│   ├── api/
│   ├── architecture/
│   ├── deployment/
│   ├── troubleshooting/
│   └── user_guides/
├── frontend/
├── infrastructure/
│   ├── docker/
│   │   └── Dockerfiles/
│   ├── k8s/
│   └── nginx/
├── library/
│   ├── apps/
│   ├── pipelines/
│   │   ├── default_ml/
│   │   ├── hybrid/
│   │   └── prism_physics/
│   └── strategies/
├── scripts/
├── secrets/
│   ├── .gitignore
│   └── secrets.env.template
└── tests/
    ├── component/
    ├── e2e/
    ├── integration/
    ├── performance/
    ├── security/
    └── unit/
```

**Full Validation Checklist**:
- [ ] All 10 top-level directories exist
- [ ] backend/apps/ and backend/shared/ exist
- [ ] library/ has 3 subdirectories (apps, pipelines, strategies)
- [ ] library/pipelines/ has 3 subdirectories
- [ ] infrastructure/ has 3 subdirectories
- [ ] data/ has 8 service directories + .gitignore
- [ ] config/ has 4 subdirectories
- [ ] docs/ has 5 subdirectories
- [ ] tests/ has 6 subdirectories
- [ ] secrets/ has .gitignore and .template
- [ ] DIRECTORY_STRUCTURE.md exists

---

## ✅ ACCEPTANCE CRITERIA

The task is complete when ALL of the following are true:

### Directory Structure
- [ ] All 10 top-level directories created
- [ ] All subdirectories created as specified
- [ ] No extra or missing directories

### Documentation
- [ ] DIRECTORY_STRUCTURE.md created
- [ ] All directories documented

### Git Configuration
- [ ] data/.gitignore exists (excludes all data)
- [ ] secrets/.gitignore exists (excludes secrets)
- [ ] secrets/secrets.env.template exists

### Validation
- [ ] Manual verification of structure complete
- [ ] All checklist items marked complete
- [ ] No errors during creation

---

## 🔄 ROLLBACK PLAN

If something goes wrong:

**Complete Rollback**:
```bash
# Remove entire directory and start over
rm -rf C:\ClaudeDesktop_Projects\Trade2026
mkdir C:\ClaudeDesktop_Projects\Trade2026
# Start from Step 1
```

**Partial Rollback** (if some directories created):
```bash
# Remove only new directories
cd C:\ClaudeDesktop_Projects\Trade2026
rm -rf <directory_name>
# Re-run specific step
```

---

## 📝 NOTES FOR CLAUDE CODE

### Key Points
- This is ONLY directory creation - no code yet
- Follow exact structure (copy-paste commands)
- Validate after each major step
- Document any deviations

### Common Issues
- **Issue**: Directory already exists
  - **Solution**: That's OK, skip that mkdir command
  
- **Issue**: Permission denied
  - **Solution**: Ensure you have write access to C:\ClaudeDesktop_Projects\

- **Issue**: Path too long (Windows)
  - **Solution**: Already using short paths, shouldn't be an issue

### Time Estimate
- Optimistic: 30 minutes
- Realistic: 1 hour
- Pessimistic: 2 hours (if issues)

---

## 📊 SUCCESS METRICS

After completion:
- ✅ Complete directory structure in place
- ✅ Documentation created
- ✅ Git ignores configured
- ✅ Ready for next task (network setup)

---

**Status**: ⏳ Pending

**Next Task**: `02_SETUP_DOCKER_NETWORKS.md`

**Last Updated**: 2025-10-14
