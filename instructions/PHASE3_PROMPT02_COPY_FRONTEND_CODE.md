# Phase 3 - Prompt 02: Copy Frontend Code

**Phase**: 3 - Frontend Integration  
**Prompt**: 02 of 08  
**Purpose**: Copy frontend code to Trade2026 and prepare structure  
**Duration**: 2 hours  
**Status**: ⏸️ Ready after Prompt 01 survey complete

---

## 🛑 PREREQUISITES

- [ ] Prompt 01 survey complete
- [ ] Frontend source location known
- [ ] Mock APIs identified
- [ ] Integration plan ready

---

## 🎯 TASK OVERVIEW

### What This Prompt Does

1. Copy complete frontend codebase to Trade2026
2. Create frontend directory structure
3. Preserve all source code
4. Setup initial configuration
5. Install dependencies
6. Verify build process works
7. Document what was copied

---

## 📋 STEP-BY-STEP INSTRUCTIONS

### Step 1: Create Frontend Directory Structure

```bash
cd C:\ClaudeDesktop_Projects\Trade2026

# Create frontend directory
mkdir -p frontend

# Expected structure after copy:
# frontend/
# ├── src/              # Source code
# ├── public/           # Static assets
# ├── package.json      # Dependencies
# ├── tsconfig.json     # TypeScript config
# ├── vite.config.ts    # Build config
# ├── .env.example      # Environment template
# └── README.md         # Documentation
```

**Checklist**:
- [ ] frontend/ directory created

---

### Step 2: Copy Frontend Source Code

```bash
# From survey, GUI location was: [FILL FROM PROMPT 01]
GUI_SOURCE="C:\GUI"  # Or actual location from survey
TARGET="C:\ClaudeDesktop_Projects\Trade2026\frontend"

# Copy all files
cp -r "$GUI_SOURCE"/* "$TARGET"/

# Exclude node_modules and build artifacts
rm -rf "$TARGET/node_modules"
rm -rf "$TARGET/dist"
rm -rf "$TARGET/build"
rm -rf "$TARGET/.next"

# Verify copy
ls -la "$TARGET"
```

**What to Copy**:
- ✅ src/ directory (all source code)
- ✅ public/ directory (static assets)
- ✅ package.json
- ✅ package-lock.json or yarn.lock
- ✅ tsconfig.json
- ✅ vite.config.ts (or webpack.config.js)
- ✅ .env files (as .env.example)
- ✅ README.md
- ✅ Any other config files

**What NOT to Copy**:
- ❌ node_modules/ (will reinstall)
- ❌ dist/ or build/ (will rebuild)
- ❌ .git/ (if separate repo)
- ❌ .env with secrets (copy as .env.example)

**Checklist**:
- [ ] All source files copied
- [ ] Configuration files copied
- [ ] node_modules excluded
- [ ] Build artifacts excluded

---

### Step 3: Create Trade2026-Specific Configuration

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\frontend

# Create .env for Trade2026
cat > .env << 'EOF'
# Trade2026 Frontend Configuration
# This file is for local development only

# API Configuration
VITE_API_URL=http://localhost
VITE_API_TIMEOUT=30000

# Backend Service Endpoints (via Nginx reverse proxy)
VITE_OMS_URL=http://localhost/api/oms
VITE_RISK_URL=http://localhost/api/risk
VITE_GATEWAY_URL=http://localhost/api/gateway
VITE_LIVE_GATEWAY_URL=http://localhost/api/live-gateway
VITE_PTRC_URL=http://localhost/api/ptrc
VITE_AUTH_URL=http://localhost/api/auth

# WebSocket Endpoints (if needed)
VITE_WS_URL=ws://localhost/ws

# Application Settings
VITE_APP_NAME=Trade2026
VITE_ENV=development
VITE_LOG_LEVEL=info

# Feature Flags
VITE_ENABLE_PAPER_TRADING=true
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_BACKTESTING=false
EOF

# Create .env.example (no secrets)
cp .env .env.example

# Create .env.production
cat > .env.production << 'EOF'
# Trade2026 Production Configuration

VITE_API_URL=http://localhost
VITE_OMS_URL=http://localhost/api/oms
VITE_RISK_URL=http://localhost/api/risk
VITE_GATEWAY_URL=http://localhost/api/gateway
VITE_LIVE_GATEWAY_URL=http://localhost/api/live-gateway
VITE_PTRC_URL=http://localhost/api/ptrc
VITE_AUTH_URL=http://localhost/api/auth

VITE_APP_NAME=Trade2026
VITE_ENV=production
VITE_LOG_LEVEL=warn

VITE_ENABLE_PAPER_TRADING=true
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_BACKTESTING=false
EOF
```

**Checklist**:
- [ ] .env created with Trade2026 settings
- [ ] .env.example created (no secrets)
- [ ] .env.production created
- [ ] All backend URLs configured

---

### Step 4: Update package.json

```bash
cd frontend

# Update package.json for Trade2026
# Manually edit or use jq/Node script

# Example changes:
# - name: "trade2026-frontend"
# - version: "1.0.0"
# - description: "Trade2026 Trading Platform Frontend"
```

**Update these fields**:
```json
{
  "name": "trade2026-frontend",
  "version": "1.0.0",
  "description": "Trade2026 Trading Platform Frontend",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0"
  }
}
```

**Checklist**:
- [ ] package.json updated
- [ ] Project name changed
- [ ] Scripts verified

---

### Step 5: Install Dependencies

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\frontend

# Install dependencies
npm install

# This will:
# - Create node_modules/
# - Create package-lock.json (if not copied)
# - Install all dependencies from package.json

# Expected output:
# added 1234 packages...
```

**If errors occur**:
- Check Node.js version (need v18+)
- Check npm version
- Delete package-lock.json and try again
- Check for conflicting dependencies

**Checklist**:
- [ ] npm install successful
- [ ] node_modules/ created
- [ ] No critical errors

---

### Step 6: Verify Build Process

```bash
cd frontend

# Test development build
npm run dev

# Expected:
# VITE v5.x.x ready in XXX ms
# ➜ Local:   http://localhost:5173/
# ➜ Network: use --host to expose

# Open browser to http://localhost:5173
# Should see app running (with mock data still)

# Stop dev server (Ctrl+C)

# Test production build
npm run build

# Expected:
# vite v5.x.x building for production...
# ✓ 1234 modules transformed.
# dist/index.html                  X.XX kB
# dist/assets/index-ABC123.js      XXX.XX kB

# Check dist/ directory created
ls -la dist/
```

**Build Success Criteria**:
- [ ] Development server starts
- [ ] App loads in browser (even with mock data)
- [ ] No build errors
- [ ] Production build creates dist/
- [ ] dist/ contains index.html and assets

---

### Step 7: Create Frontend README

```bash
cat > frontend/README.md << 'EOF'
# Trade2026 Frontend

React + TypeScript frontend for Trade2026 trading platform.

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Configuration

Environment variables in `.env`:
- `VITE_API_URL` - Base API URL
- `VITE_OMS_URL` - OMS service URL
- `VITE_RISK_URL` - Risk service URL
- etc.

## Integration Status

- [x] Copied from original GUI
- [x] Dependencies installed
- [x] Build process working
- [ ] Mock APIs replaced (Phase 3 Prompts 03-04)
- [ ] Nginx integration (Phase 3 Prompt 05)
- [ ] Dockerized (Phase 3 Prompt 06)
- [ ] Production ready (Phase 3 Prompt 08)

## Backend Services

Connects to:
- OMS (port 8099) - Order management
- Risk (port 8103) - Risk checks
- Gateway (port 8080) - Market data
- Live Gateway (port 8200) - Order execution
- PTRC (port 8109) - P&L and reports
- authn (port 8001) - Authentication

## Development

```bash
# Run with mock APIs (current state)
npm run dev

# Run with real backends (after Prompt 03-04)
npm run dev
```

## Build

```bash
# Production build
npm run build

# Output: dist/
```

## Notes

- Currently uses mock APIs
- Phase 3 will replace mocks with real backend calls
- Nginx will be setup as reverse proxy
- Authentication will be integrated

See Phase 3 prompts for integration steps.
EOF
```

**Checklist**:
- [ ] README.md created
- [ ] Installation instructions
- [ ] Configuration documented
- [ ] Integration status tracked

---

### Step 8: Document Copy Results

Create: `docs/FRONTEND_COPY_REPORT.md`

```markdown
# Frontend Copy Report

**Date**: [DATE]
**Source**: C:\GUI (or actual location)
**Target**: C:\ClaudeDesktop_Projects\Trade2026\frontend

## Files Copied

**Total Files**: XXXX
**Total Size**: XX MB

### Directory Structure
- src/ (XXX files)
- public/ (XX files)
- Config files (X files)

### Key Files
- package.json ✓
- tsconfig.json ✓
- vite.config.ts ✓
- .env.example ✓

## Dependencies

**Total Dependencies**: XXX
**Dev Dependencies**: XX

### Key Dependencies
- react: vX.X.X
- typescript: vX.X.X
- vite: vX.X.X
- [other key deps]

## Build Verification

- [x] Dependencies installed
- [x] Development build works
- [x] Production build works
- [x] No critical errors

## Integration Status

- [x] Code copied
- [x] Configuration created
- [x] Dependencies installed
- [x] Build verified
- [ ] Mock APIs to replace: XX files
- [ ] Backend integration: Pending (Prompt 03-04)

## Next Steps

1. Prompt 03: Replace Priority 1 mock APIs (core trading)
2. Prompt 04: Replace Priority 2 mock APIs (essential features)
3. Prompt 05: Setup Nginx reverse proxy
4. Prompt 06: Build and containerize frontend
5. Prompt 07: Integration testing
6. Prompt 08: Polish and production ready

## Notes

- All mock APIs still in place
- App runs but uses fake data
- Real backend integration in next prompts
```

**Checklist**:
- [ ] Copy report created
- [ ] All stats documented
- [ ] Next steps clear

---

### Step 9: Update Git (Optional)

```bash
cd C:\ClaudeDesktop_Projects\Trade2026

# Add frontend to git
git add frontend/

# Create .gitignore for frontend
cat > frontend/.gitignore << 'EOF'
# Dependencies
node_modules/

# Build outputs
dist/
build/
.next/

# Environment files
.env
.env.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*

# Testing
coverage/
EOF

# Commit
git commit -m "Phase 3 Prompt 02: Copy frontend code to Trade2026"
```

**Checklist**:
- [ ] .gitignore created
- [ ] Frontend added to git (optional)

---

### Step 10: Verify Frontend Directory

```bash
cd C:\ClaudeDesktop_Projects\Trade2026

# Check structure
tree frontend -L 2 -I 'node_modules|dist'

# Expected:
# frontend/
# ├── src/
# │   ├── components/
# │   ├── pages/
# │   ├── api/
# │   ├── hooks/
# │   ├── utils/
# │   ├── types/
# │   └── App.tsx
# ├── public/
# ├── package.json
# ├── tsconfig.json
# ├── vite.config.ts
# ├── .env
# ├── .env.example
# ├── .env.production
# ├── .gitignore
# └── README.md
```

**Checklist**:
- [ ] All source code present
- [ ] Configuration files present
- [ ] Dependencies installed
- [ ] Build working
- [ ] Documentation created

---

## ✅ PROMPT 02 DELIVERABLES

### Files and Directories

- [ ] `frontend/` directory with complete codebase
- [ ] `frontend/src/` - all source code
- [ ] `frontend/public/` - static assets
- [ ] `frontend/package.json` - dependencies
- [ ] `frontend/.env` - development config
- [ ] `frontend/.env.example` - config template
- [ ] `frontend/.env.production` - production config
- [ ] `frontend/README.md` - documentation
- [ ] `frontend/.gitignore` - git exclusions

### Documentation

- [ ] `docs/FRONTEND_COPY_REPORT.md` - copy results

### Verification

- [ ] npm install successful
- [ ] npm run dev works
- [ ] npm run build works
- [ ] App loads in browser (with mock data)

---

## 🚦 VALIDATION GATE

### Copy Complete?

**Check**:
- [ ] All source code copied
- [ ] Dependencies installed successfully
- [ ] Development build works
- [ ] Production build works
- [ ] App runs (even with mock data)
- [ ] Configuration files created
- [ ] Documentation complete

**Decision**:
- ✅ ALL COMPLETE → Proceed to Prompt 03
- ❌ BUILD FAILS → Fix build issues first
- ❌ MISSING FILES → Copy missing files

---

## 📊 PROMPT 02 COMPLETION CRITERIA

Prompt 02 complete when:

- [ ] Frontend code copied to Trade2026/frontend/
- [ ] All dependencies installed
- [ ] Build process verified working
- [ ] Configuration files created
- [ ] Documentation complete
- [ ] App runs in browser (mock data OK)
- [ ] COMPLETION_TRACKER.md updated

**Next Prompt**: PHASE3_PROMPT03_REPLACE_MOCK_APIS_P1.md

---

**Prompt Status**: ⏸️ READY (after Prompt 01 survey)

**Estimated Time**: 2 hours

**Outcome**: Frontend code in Trade2026, build working, ready for API integration
