# Trade2026 Frontend

React + TypeScript + Vite frontend for Trade2026 trading platform.

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

### Environment Variables

Copy `.env.example` to `.env` and configure:

#### API Mode
- `VITE_API_MODE` - Set to 'mock' or 'real' to control API implementation
  - `mock` - Uses mock data from `src/services/mock-data/`
  - `real` - Connects to real backend services

#### Backend Service URLs
- `VITE_OMS_URL` - Order Management System (port 8099)
- `VITE_RISK_URL` - Risk Management (port 8103)
- `VITE_GATEWAY_URL` - Market Data Gateway (port 8080)
- `VITE_LIVE_GATEWAY_URL` - Live Order Gateway (port 8200)
- `VITE_PTRC_URL` - Position Tracker (port 8109)
- `VITE_PNL_URL` - P&L Service (port 8107)
- `VITE_NORMALIZER_URL` - Data Normalizer (port 8110)
- `VITE_AUTH_URL` - Authentication (port 8114)

#### WebSocket URLs
- `VITE_WS_GATEWAY_URL` - Market data websocket
- `VITE_WS_LIVE_URL` - Live trading websocket

#### Feature Flags
- `VITE_ENABLE_PAPER_TRADING` - Enable paper trading mode
- `VITE_ENABLE_ANALYTICS` - Enable analytics tracking
- `VITE_ENABLE_BACKTESTING` - Enable backtesting features
- `VITE_ENABLE_LIVE_TRADING` - Enable live trading (production only)

## Architecture

### Technology Stack
- **React** 18.2 - UI framework
- **TypeScript** 5.3 - Type safety
- **Vite** 5.0 - Build tool
- **Zustand** 4.4 - State management
- **axios** 1.6 - HTTP client
- **TailwindCSS** 3.4 - Styling
- **AG Grid** 31.0 - Data tables
- **Lightweight Charts** 4.1 - Charting
- **Plotly** 3.1 - Advanced charts
- **Three.js** 0.180 - 3D visualizations

### API Architecture

The frontend uses an **APIFactory** pattern to switch between mock and real APIs:

```typescript
// src/services/api/APIFactory.ts
class APIFactory {
  getAPI() {
    if (mode === 'mock') return MockAPI;
    return RealAPI;
  }
}
```

**Current State**: Using `MockAPI` with fake data
**After Phase 3**: Will use `RealAPI` with backend integration

### Directory Structure

```
frontend/
├── src/
│   ├── api/              # API client configuration
│   ├── assets/           # Static assets (images, fonts)
│   ├── components/       # Reusable UI components
│   ├── pages/            # Page components (77 pages)
│   ├── services/         # API services and mock data
│   │   ├── api/          # API client (APIFactory, RealAPI, MockAPI)
│   │   └── mock-data/    # Mock data files (12 files)
│   ├── store/            # Zustand state management
│   ├── styles/           # Global styles
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions
│   ├── App.tsx           # Root component
│   ├── Router.tsx        # Route definitions
│   └── main.tsx          # Entry point
├── public/               # Public assets
├── dist/                 # Production build output
├── .env                  # Environment config (development)
├── .env.example          # Environment template
├── .env.production       # Production config
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
├── vite.config.ts        # Build config
└── tailwind.config.js    # Tailwind config
```

## Integration Status

### Phase 3 Progress

- [x] **Prompt 01**: Frontend code surveyed
- [x] **Prompt 02**: Code copied to Trade2026 (CURRENT)
- [ ] **Prompt 03**: Replace Priority 1 mock APIs (core trading)
- [ ] **Prompt 04**: Replace Priority 2 mock APIs (essential features)
- [ ] **Prompt 05**: Setup Nginx reverse proxy
- [ ] **Prompt 06**: Build and containerize frontend
- [ ] **Prompt 07**: Integration testing
- [ ] **Prompt 08**: Production polish

### Mock APIs to Replace

**Priority 1 - Core Trading** (Prompt 03):
- `trading-data.ts` - Positions, orders, fills
- `risk-data.ts` - Risk metrics, breaches
- `account-data.ts` - Account info, balances

**Priority 2 - Essential Features** (Prompt 04):
- `market-data.ts` - Tickers, quotes, orderbooks
- `strategy-data.ts` - Strategies, parameters
- `backtest-data.ts` - Backtest results
- `reports-data.ts` - Reports, analytics

**Priority 3 - Supporting Features** (Future):
- `settings-data.ts` - User settings
- `alerts-data.ts` - Alerts, notifications
- `news-data.ts` - News, events
- `options-data.ts` - Options data
- `futures-data.ts` - Futures data

## Backend Service Mapping

| Page/Feature | Backend Service | Port | Endpoint |
|-------------|----------------|------|----------|
| Trading Dashboard | OMS | 8099 | /orders, /positions |
| Risk Management | Risk | 8103 | /check, /limits |
| Market Data | Gateway | 8080 | /tickers, /quotes |
| Live Trading | Live Gateway | 8200 | /submit, /cancel |
| P&L Reports | PTRC | 8109 | /positions, /pnl |
| Position Tracking | PTRC | 8109 | /history |
| Authentication | authn | 8114 | /login, /verify |

## Development

### Running with Mock Data (Current)

```bash
# Uses MockAPI with fake data
npm run dev

# Opens on http://localhost:5173
```

### Running with Real Backend (After Prompt 03-04)

```bash
# 1. Ensure backend services running:
docker-compose ps

# 2. Set API mode to real:
# In .env: VITE_API_MODE=real

# 3. Run frontend:
npm run dev

# 4. Open http://localhost:5173
```

## Build

### Development Build
```bash
npm run dev
# Output: Runs dev server on http://localhost:5173
```

### Production Build
```bash
npm run build
# Output: dist/ directory (38 MB)
# - index.html
# - assets/ (JS, CSS bundles)
```

### Preview Production
```bash
npm run build && npm run preview
# Opens production build on http://localhost:4173
```

## Testing

```bash
# Run tests
npm run test

# Run linter
npm run lint
```

## Docker Deployment (Phase 3 Prompt 06)

```bash
# Build Docker image
docker build -t trade2026-frontend .

# Run container
docker run -p 80:80 trade2026-frontend

# Or use docker-compose
docker-compose up frontend
```

## Nginx Integration (Phase 3 Prompt 05)

Nginx will serve as reverse proxy:
- Frontend: http://localhost/
- API Gateway: http://localhost/api/*

Benefits:
- Single origin (no CORS issues)
- Load balancing
- SSL termination
- Static file caching

## Notes

### Current State
- **API Mode**: mock (fake data)
- **Backend**: Not connected
- **Authentication**: Disabled
- **WebSockets**: Not connected

### After Phase 3
- **API Mode**: real (backend connected)
- **Backend**: All 14 services integrated
- **Authentication**: Enabled via authn service
- **WebSockets**: Connected for live data

### Known Warnings
- Large bundle sizes (charts library 5.4 MB)
- Can be optimized with code splitting (future)
- 4 moderate npm audit vulnerabilities (non-critical)

## Troubleshooting

### Build Fails
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Dev Server Won't Start
```bash
# Check port 5173 is available
netstat -ano | findstr :5173

# Kill process if needed
# Or change port in vite.config.ts
```

### API Connection Fails
```bash
# Verify backend services running
docker-compose ps

# Check service health
curl http://localhost:8099/health  # OMS
curl http://localhost:8103/health  # Risk
curl http://localhost:8080/health  # Gateway
```

## Next Steps

1. **Execute Prompt 03**: Replace Priority 1 mock APIs
   - Connect trading dashboard to OMS
   - Connect risk panel to Risk service
   - Test order submission flow

2. **Execute Prompt 04**: Replace Priority 2 mock APIs
   - Connect market data to Gateway
   - Connect strategies to backend
   - Connect backtesting

3. **Execute Prompt 05**: Setup Nginx reverse proxy
   - Configure routing
   - Handle CORS
   - SSL setup (if needed)

4. **Execute Prompt 06**: Dockerize frontend
   - Create Dockerfile
   - Add to docker-compose
   - Test containerized deployment

5. **Execute Prompt 07**: Integration testing
   - E2E tests
   - API integration tests
   - Performance tests

6. **Execute Prompt 08**: Production polish
   - Error handling
   - Loading states
   - Performance optimization
   - Security hardening

## Support

For issues or questions:
1. Check this README
2. Review Phase 3 prompts in `instructions/`
3. Check backend service logs: `docker-compose logs -f`
4. Review `DOCUMENTATION_INDEX.md` for all docs

---

**Status**: Phase 3 Prompt 02 COMPLETE ✅
**Next**: Execute Prompt 03 (Replace Priority 1 Mock APIs)
**Time to MVP**: ~35 hours remaining
