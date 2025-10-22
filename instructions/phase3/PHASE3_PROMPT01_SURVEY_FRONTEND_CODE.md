# Phase 3 - Prompt 01: Survey Frontend Codebase

**Phase**: 3 - Frontend Integration  
**Prompt**: 01 of 08  
**Purpose**: Survey and document the GUI frontend codebase  
**Duration**: 2 hours  
**Status**: ⏸️ Ready after Phase 3 Validation Gate passes

---

## 🛑 PREREQUISITES

- [ ] Phase 3 Validation Gate passed
- [ ] Phase 2 complete (backend services operational)
- [ ] GUI frontend source code location known

---

## 🎯 TASK OVERVIEW

### What This Prompt Does

This prompt surveys the existing React/TypeScript frontend at `C:\GUI\` and:
1. Documents the complete codebase structure
2. Identifies all mock API clients
3. Maps frontend pages to backend services
4. Catalogs all dependencies
5. Documents build process
6. Identifies configuration needs
7. Creates integration plan

---

## 📋 STEP-BY-STEP INSTRUCTIONS

### Step 1: Locate Frontend Source Code

**Expected Location**: `C:\GUI\`

```bash
# Check if GUI exists
ls -la C:\GUI\

# Alternative locations to check:
ls -la C:\Trade2025\gui\
ls -la C:\Trade2025\frontend\
ls -la ~\GUI\
ls -la ~\trade-gui\
```

**Document Location**:
```
Frontend source found at: ___________________________
```

**If not found**:
- Ask user for correct location
- Check project documentation
- Search for React/package.json files

---

### Step 2: Analyze Directory Structure

```bash
cd [GUI_LOCATION]

# Show complete directory tree
tree -L 3 -I 'node_modules|dist|build'

# Or use find
find . -maxdepth 3 -type d | grep -v node_modules
```

**Document Structure**:
```
GUI/
├── src/
│   ├── components/      # React components
│   ├── pages/           # Page components
│   ├── api/             # API client layer (MOCK)
│   ├── hooks/           # React hooks
│   ├── utils/           # Utilities
│   ├── styles/          # CSS/styling
│   ├── types/           # TypeScript types
│   ├── contexts/        # React contexts
│   ├── routes/          # Routing config
│   └── App.tsx          # Root component
├── public/              # Static assets
├── package.json         # Dependencies
├── tsconfig.json        # TypeScript config
├── vite.config.ts       # Vite config (or webpack)
├── .env                 # Environment variables
└── README.md            # Documentation
```

**Create**: `docs/FRONTEND_STRUCTURE.md` with complete structure

---

### Step 3: Identify All Mock API Clients

```bash
# Find all API client files
find src -name "*api*" -o -name "*client*" -o -name "*service*"

# Search for mock data
grep -r "mock" src/ --include="*.ts" --include="*.tsx"

# Look for hardcoded data
grep -r "const.*data.*=" src/api/ --include="*.ts"
```

**Common patterns to find**:
- `src/api/mockData.ts`
- `src/api/mockClient.ts`
- `src/services/mockServices.ts`
- Inline `return { data: [...] }` in API functions

**Document All Mock APIs**:

| File | Service | What It Mocks |
|------|---------|---------------|
| `src/api/ordersApi.ts` | OMS | Order submission, positions |
| `src/api/marketDataApi.ts` | Gateway | Ticker data, candles |
| `src/api/riskApi.ts` | Risk | Risk checks, limits |
| ... | ... | ... |

**Create**: `docs/MOCK_API_INVENTORY.md`

---

### Step 4: Map Pages to Backend Services

```bash
# List all page components
find src/pages -name "*.tsx" -o -name "*.ts"

# Check which APIs each page uses
for file in src/pages/*.tsx; do
  echo "=== $file ==="
  grep -h "import.*from.*api" "$file"
done
```

**Document Page → Service Mapping**:

| Page | Backend Service(s) | API Endpoints Needed |
|------|-------------------|---------------------|
| Dashboard | OMS, Gateway, Risk | /positions, /orders, /tickers |
| Orders | OMS, Risk | /orders, /risk/check |
| Positions | OMS | /positions, /pnl |
| MarketData | Gateway | /tickers, /candles |
| Analytics | ClickHouse, PTRC | /analytics, /reports |
| Settings | authn | /user, /settings |
| ... | ... | ... |

**Create**: `docs/FRONTEND_BACKEND_MAPPING.md`

---

### Step 5: Catalog Dependencies

```bash
cd [GUI_LOCATION]

# Check package.json
cat package.json

# Key sections to document:
# - dependencies (runtime)
# - devDependencies (build time)
# - scripts (build, dev, test)
```

**Document Key Dependencies**:

**UI Framework**:
- React version: _______
- TypeScript version: _______
- Build tool: (Vite/Webpack/Other): _______

**Key Libraries**:
- Routing: (react-router-dom): _______
- State management: (Redux/Zustand/Jotai/Context): _______
- HTTP client: (axios/fetch): _______
- UI components: (MUI/Ant Design/Tailwind/Custom): _______
- Charts: (recharts/chartjs/d3): _______
- Forms: (react-hook-form/formik): _______

**Create**: `docs/FRONTEND_DEPENDENCIES.md`

---

### Step 6: Document Build Process

```bash
# Check build scripts
cat package.json | grep "scripts"

# Typical scripts:
# - npm run dev     (development server)
# - npm run build   (production build)
# - npm run preview (preview build)
# - npm run test    (tests)
```

**Document Build Process**:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest"
  }
}
```

**Build Configuration**:
- Build tool: _______
- Output directory: _______ (usually `dist/` or `build/`)
- Environment variables: _______ (check `.env` files)
- Base URL: _______ (for API calls)

**Create**: `docs/FRONTEND_BUILD.md`

---

### Step 7: Identify Configuration Needs

```bash
# Check environment files
ls -la .env*

# Common files:
# .env
# .env.local
# .env.development
# .env.production

# Check vite.config.ts or webpack.config.js
cat vite.config.ts
```

**Document Current Config**:

```bash
# Example .env
VITE_API_URL=http://localhost:3000/api
VITE_WS_URL=ws://localhost:3000/ws
VITE_ENV=development
```

**Configuration Changes Needed**:
- API base URL: `http://localhost:3000` → `http://localhost` (Nginx)
- WebSocket URL: Update if needed
- Service endpoints: Map to real backend ports
- Authentication: Update to use authn service

**Create**: `docs/FRONTEND_CONFIGURATION.md`

---

### Step 8: Document API Client Architecture

```bash
# Find API client implementation
cat src/api/client.ts  # or similar

# Look for:
# - Base URL configuration
# - HTTP client setup (axios/fetch)
# - Request interceptors
# - Response interceptors
# - Error handling
# - Authentication headers
```

**Current API Client Pattern**:

```typescript
// Example current implementation
const API_BASE_URL = 'http://localhost:3000/api';

export const apiClient = {
  get: (endpoint: string) => {
    // Mock implementation
    return Promise.resolve(mockData);
  },
  post: (endpoint: string, data: any) => {
    // Mock implementation
    return Promise.resolve({ success: true });
  }
};
```

**Changes Needed**:
- Replace mock implementation with real HTTP calls
- Add authentication headers
- Configure base URLs per service
- Add retry logic
- Add error handling

**Create**: `docs/API_CLIENT_ARCHITECTURE.md`

---

### Step 9: Check for WebSocket Usage

```bash
# Search for WebSocket usage
grep -r "WebSocket\|ws://" src/ --include="*.ts" --include="*.tsx"

# Search for real-time features
grep -r "subscribe\|stream\|live" src/ --include="*.ts" --include="*.tsx"
```

**WebSocket Requirements**:
- Market data streaming: YES/NO
- Order updates: YES/NO
- Position updates: YES/NO
- Alert notifications: YES/NO

**If YES, document**:
- Which pages need WebSocket
- What data they subscribe to
- Current WebSocket implementation (mock or real)

**Create**: `docs/WEBSOCKET_REQUIREMENTS.md` (if applicable)

---

### Step 10: Document Authentication Flow

```bash
# Find auth-related code
grep -r "login\|logout\|auth\|token" src/ --include="*.ts" --include="*.tsx"

# Check for auth context
find src -name "*auth*" -o -name "*Auth*"
```

**Authentication Architecture**:
- Current implementation: Mock/Real/None
- Token storage: localStorage/sessionStorage/cookie
- Auth provider: Context/Redux/Other
- Protected routes: YES/NO
- Login page: Location: _______

**Changes Needed**:
- Integrate with authn service (port 8001)
- Token management
- Protected route configuration
- Session handling

**Create**: `docs/AUTHENTICATION_INTEGRATION.md`

---

## 📊 CREATE FRONTEND SURVEY DOCUMENT

### Consolidate All Findings

Create comprehensive survey document: `docs/FRONTEND_SURVEY_COMPLETE.md`

**Include**:
1. **Executive Summary**
   - Total pages: _____
   - Total components: _____
   - Mock APIs to replace: _____
   - Estimated integration effort: _____ hours

2. **Directory Structure** (from Step 2)
3. **Mock API Inventory** (from Step 3)
4. **Page-Service Mapping** (from Step 4)
5. **Dependencies List** (from Step 5)
6. **Build Process** (from Step 6)
7. **Configuration Needs** (from Step 7)
8. **API Client Architecture** (from Step 8)
9. **WebSocket Requirements** (from Step 9) - if applicable
10. **Authentication Integration** (from Step 10)

---

## 📋 INTEGRATION PRIORITIES

### Categorize Frontend Components

**Priority 1 - Core Trading** (Must have for MVP):
- [ ] Dashboard page
- [ ] Orders page
- [ ] Positions page
- [ ] Market data display
- [ ] Order entry form

**Priority 2 - Essential Features**:
- [ ] Login/Authentication
- [ ] Settings page
- [ ] Risk monitoring
- [ ] P&L display

**Priority 3 - Advanced Features**:
- [ ] Analytics page
- [ ] Reports page
- [ ] Strategy management
- [ ] Backtesting UI

**Priority 4 - Optional**:
- [ ] Admin pages
- [ ] User management
- [ ] System monitoring UI

---

## 🎯 INTEGRATION PLAN

### Based on Survey Results

**Phase 3 Integration Steps** (Prompts 02-08):

1. **Prompt 02**: Copy frontend code to Trade2026
2. **Prompt 03**: Replace Priority 1 mock APIs (core trading)
3. **Prompt 04**: Replace Priority 2 mock APIs (essential)
4. **Prompt 05**: Setup Nginx reverse proxy
5. **Prompt 06**: Build and containerize frontend
6. **Prompt 07**: Integration testing
7. **Prompt 08**: Polish and optimization

**Estimated Time Per Priority**:
- P1 (Core): 10-12 hours
- P2 (Essential): 6-8 hours
- P3 (Advanced): 4-6 hours (optional)
- P4 (Optional): 2-4 hours (optional)

**MVP Focus**: Priorities 1-2 only (16-20 hours)

---

## ✅ PROMPT 01 DELIVERABLES

### Documents Created

- [ ] `docs/FRONTEND_SURVEY_COMPLETE.md` - Master survey doc
- [ ] `docs/FRONTEND_STRUCTURE.md` - Directory structure
- [ ] `docs/MOCK_API_INVENTORY.md` - All mock APIs
- [ ] `docs/FRONTEND_BACKEND_MAPPING.md` - Page-service mapping
- [ ] `docs/FRONTEND_DEPENDENCIES.md` - All dependencies
- [ ] `docs/FRONTEND_BUILD.md` - Build process
- [ ] `docs/FRONTEND_CONFIGURATION.md` - Config needs
- [ ] `docs/API_CLIENT_ARCHITECTURE.md` - API client design
- [ ] `docs/WEBSOCKET_REQUIREMENTS.md` - WebSocket needs (if applicable)
- [ ] `docs/AUTHENTICATION_INTEGRATION.md` - Auth integration

### Survey Data Gathered

- [ ] Total pages counted
- [ ] Total components counted
- [ ] All mock APIs identified
- [ ] Backend service dependencies mapped
- [ ] Build process understood
- [ ] Configuration requirements known
- [ ] Integration priorities established

---

## 🚦 VALIDATION GATE

### Survey Complete?

**Check**:
- [ ] All 10 steps completed
- [ ] All documents created
- [ ] Frontend source code location confirmed
- [ ] Mock APIs all identified
- [ ] Backend service mapping complete
- [ ] Integration plan established

**Decision**:
- ✅ ALL COMPLETE → Proceed to Prompt 02
- ❌ INCOMPLETE → Finish survey first

---

## 📊 PROMPT 01 COMPLETION CRITERIA

Prompt 01 complete when:

- [ ] Frontend source code surveyed
- [ ] All documents created
- [ ] Mock APIs cataloged
- [ ] Backend mapping complete
- [ ] Integration plan ready
- [ ] COMPLETION_TRACKER.md updated

**Next Prompt**: PHASE3_PROMPT02_COPY_FRONTEND_CODE.md

---

**Prompt Status**: ⏸️ READY (after Phase 3 Validation Gate)

**Estimated Time**: 2 hours

**Outcome**: Complete understanding of frontend, ready for integration
