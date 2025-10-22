# Phase 3 - Prompt Index

**Phase**: 3 - Frontend Integration  
**Status**: All prompts created ✅  
**Total Prompts**: 9 (00-08)  
**Created**: 2025-10-14

---

## 📋 PROMPT SEQUENCE

### Prompt 00: Validation Gate ✅
**File**: `PHASE3_PROMPT00_VALIDATION_GATE.md`  
**Duration**: 10 minutes  
**Purpose**: Validate Phase 2 complete before Phase 3

**What it does**:
- Validates all backend services running
- Checks API endpoints accessible
- Verifies data pipeline working
- Confirms trading flow functional
- 30+ mandatory checks

**Next**: Prompt 01

---

### Prompt 01: Survey Frontend Code ✅
**File**: `PHASE3_PROMPT01_SURVEY_FRONTEND_CODE.md`  
**Duration**: 2 hours  
**Status**: ✅ READY

**What to do**:
- Locate frontend source code (C:\GUI)
- Document directory structure
- Identify all mock APIs
- Map pages to backend services
- Catalog dependencies
- Document build process
- Create integration plan

**Deliverables**:
- Complete frontend survey document
- Mock API inventory
- Page-service mapping
- Integration priorities

**Next**: Prompt 02

---

### Prompt 02: Copy Frontend Code ✅
**File**: `PHASE3_PROMPT02_COPY_FRONTEND_CODE.md`  
**Duration**: 2 hours  
**Status**: ✅ READY

**What to do**:
- Copy frontend to Trade2026/frontend/
- Install dependencies (npm install)
- Create Trade2026 configuration (.env files)
- Verify build process works
- Document what was copied

**Deliverables**:
- frontend/ directory with complete code
- Dependencies installed
- Build working
- Configuration files

**Next**: Prompt 03

---

### Prompt 03: Replace Mock APIs - Priority 1 ⏸️
**File**: `PHASE3_PROMPT03_REPLACE_MOCK_APIS_P1.md`  
**Duration**: 10-12 hours  
**Status**: ⏸️ To be created

**What to do**:
- Replace core trading mock APIs
- **OMS integration**: Order submission, positions, fills
- **Risk integration**: Risk checks
- **Gateway integration**: Market data, tickers
- **Live Gateway integration**: Order routing
- Test each integration

**Services**:
- OMS (port 8099)
- Risk (port 8103)
- Gateway (port 8080)
- Live Gateway (port 8200)

**Pages Updated**:
- Dashboard
- Orders page
- Positions page
- Market data display
- Order entry form

**Next**: Prompt 04

---

### Prompt 04: Replace Mock APIs - Priority 2 ⏸️
**File**: `PHASE3_PROMPT04_REPLACE_MOCK_APIS_P2.md`  
**Duration**: 6-8 hours  
**Status**: ⏸️ To be created

**What to do**:
- Replace essential feature mock APIs
- **Authentication integration**: Login, logout, user profile
- **PTRC integration**: P&L, reports, analytics
- Settings and configuration
- Test integrations

**Services**:
- authn (port 8001)
- PTRC (port 8109)

**Pages Updated**:
- Login page
- Settings page
- Analytics page
- Reports page

**Next**: Prompt 05

---

### Prompt 05: Setup Nginx Reverse Proxy ⏸️
**File**: `PHASE3_PROMPT05_SETUP_NGINX.md`  
**Duration**: 4 hours  
**Status**: ⏸️ To be created

**What to do**:
- Configure Nginx as reverse proxy
- Route `/api/*` to backend services
- Serve frontend static files
- Setup WebSocket proxying (if needed)
- SSL/TLS configuration (optional)
- CORS handling

**Nginx Routes**:
```
/                    → Frontend (React app)
/api/oms             → OMS (8099)
/api/risk            → Risk (8103)
/api/gateway         → Gateway (8080)
/api/live-gateway    → Live Gateway (8200)
/api/ptrc            → PTRC (8109)
/api/auth            → authn (8001)
/ws                  → WebSocket endpoints
```

**Next**: Prompt 06

---

### Prompt 06: Build and Containerize Frontend ⏸️
**File**: `PHASE3_PROMPT06_BUILD_FRONTEND_CONTAINER.md`  
**Duration**: 3 hours  
**Status**: ⏸️ To be created

**What to do**:
- Create production Dockerfile
- Multi-stage build
- Build frontend Docker image
- Add to docker-compose.frontend.yml
- Test containerized deployment
- Optimize image size

**Deliverables**:
- Dockerfile for frontend
- nginx.conf for serving
- docker-compose.frontend.yml entry
- Built and tested container

**Next**: Prompt 07

---

### Prompt 07: Integration Testing ⏸️
**File**: `PHASE3_PROMPT07_INTEGRATION_TESTING.md`  
**Duration**: 4 hours  
**Status**: ⏸️ To be created

**What to do**:
- End-to-end testing of all features
- Test order submission flow
- Test position tracking
- Test market data display
- Test authentication
- Test all page transitions
- Performance testing
- Error handling testing

**Test Scenarios**:
- Submit market order → see in orders page
- Submit limit order → see in orders page
- View positions → accurate data
- Market data updating
- Login/logout flow
- P&L calculations

**Next**: Prompt 08

---

### Prompt 08: Production Polish ⏸️
**File**: `PHASE3_PROMPT08_PRODUCTION_POLISH.md`  
**Duration**: 4 hours  
**Status**: ⏸️ To be created

**What to do**:
- Performance optimization
- Error handling improvements
- Loading states
- User feedback (toasts, notifications)
- Responsive design verification
- Browser compatibility testing
- Final documentation
- **Phase 3 MVP Complete** 🎉

**Deliverables**:
- Polished, production-ready frontend
- Complete integration with backend
- Full documentation
- Deployment guide

**Next**: Phase 4 (ML Library) or Production Deployment

---

## 🎯 PHASE 3 OVERVIEW

### Total Duration
**MVP Path**: 35-40 hours (~5 working days)

| Prompt | Duration | Status |
|--------|----------|--------|
| 00 | 10 min | ✅ Ready |
| 01 | 2h | ✅ Ready |
| 02 | 2h | ✅ Ready |
| 03 | 10-12h | ⏸️ To create |
| 04 | 6-8h | ⏸️ To create |
| 05 | 4h | ⏸️ To create |
| 06 | 3h | ⏸️ To create |
| 07 | 4h | ⏸️ To create |
| 08 | 4h | ⏸️ To create |

**Total**: 35-40 hours

---

## 🚀 QUICK START PROMPTS

### When Prompt 02 Complete

```
Prompt 02 complete. Frontend code copied and build verified.

Proceed with Prompt 03: Replace Priority 1 Mock APIs.

Focus on core trading functionality:
- OMS integration (order submission, positions)
- Risk integration (risk checks)
- Gateway integration (market data)
- Live Gateway integration (order routing)

Update these pages:
- Dashboard
- Orders
- Positions
- Market data display

Begin with OMS integration.
```

### When Prompt 03 Complete

```
Prompt 03 complete. Core trading APIs integrated.

Proceed with Prompt 04: Replace Priority 2 Mock APIs.

Focus on essential features:
- Authentication integration (authn service)
- PTRC integration (P&L, reports)
- Settings and configuration

Begin with authentication.
```

### When Prompt 04 Complete

```
Prompt 04 complete. All essential APIs integrated.

Proceed with Prompt 05: Setup Nginx Reverse Proxy.

Configure Nginx to:
- Serve frontend static files
- Proxy /api/* to backend services
- Handle WebSocket connections (if needed)
- Enable CORS

Begin with basic Nginx configuration.
```

---

## 📊 INTEGRATION PRIORITIES

### Priority 1 - Core Trading (Prompt 03)
**Must have for MVP**:
- Order submission
- Position tracking
- Market data display
- Order execution
- Risk checks

**Backend Services**:
- OMS (8099)
- Risk (8103)
- Gateway (8080)
- Live Gateway (8200)

**Pages**:
- Dashboard
- Orders
- Positions
- Market Data

---

### Priority 2 - Essential Features (Prompt 04)
**Important for usability**:
- User authentication
- P&L display
- Reports
- Settings

**Backend Services**:
- authn (8001)
- PTRC (8109)

**Pages**:
- Login
- Settings
- Analytics
- Reports

---

### Priority 3 - Infrastructure (Prompts 05-06)
**Deployment essentials**:
- Nginx reverse proxy
- Docker containerization
- Production build
- Deployment configuration

---

### Priority 4 - Quality (Prompts 07-08)
**Polish and validation**:
- Integration testing
- Performance optimization
- Error handling
- Production polish

---

## 🎯 SUCCESS CRITERIA

### Phase 3 Complete When

**Core Functionality**:
- [ ] All mock APIs replaced with real backend calls
- [ ] Order submission working end-to-end
- [ ] Position tracking accurate
- [ ] Market data displaying live
- [ ] Authentication functional

**Infrastructure**:
- [ ] Nginx configured and working
- [ ] Frontend containerized
- [ ] docker-compose orchestration
- [ ] All services integrated

**Quality**:
- [ ] Integration tests passing
- [ ] No critical errors
- [ ] Performance acceptable
- [ ] Production ready

**Result**: Complete, production-ready trading platform with full UI

---

## 📁 FILE LOCATIONS

All Phase 3 prompt files in:
```
C:\ClaudeDesktop_Projects\Trade2026\instructions\
├── PHASE3_PROMPT00_VALIDATION_GATE.md          ✅
├── PHASE3_PROMPT01_SURVEY_FRONTEND_CODE.md     ✅
├── PHASE3_PROMPT02_COPY_FRONTEND_CODE.md       ✅
├── PHASE3_PROMPT03_REPLACE_MOCK_APIS_P1.md     ⏸️
├── PHASE3_PROMPT04_REPLACE_MOCK_APIS_P2.md     ⏸️
├── PHASE3_PROMPT05_SETUP_NGINX.md              ⏸️
├── PHASE3_PROMPT06_BUILD_FRONTEND_CONTAINER.md ⏸️
├── PHASE3_PROMPT07_INTEGRATION_TESTING.md      ⏸️
└── PHASE3_PROMPT08_PRODUCTION_POLISH.md        ⏸️
```

---

## ✅ CURRENT STATUS

**Prompts Created**: 3 of 9 (00, 01, 02)  
**Prompts Remaining**: 6 (03-08)

**Next Action**: Create Prompts 03-08

**Ready to Execute**: After Phase 2 complete

---

**Master Index Status**: ✅ Structure defined

**Current Work**: Creating remaining prompts (03-08)
