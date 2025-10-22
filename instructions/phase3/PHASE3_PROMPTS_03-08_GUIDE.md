# Phase 3 - Prompts 03-08: Quick Implementation Guide

**Purpose**: Concise guide for remaining Phase 3 prompts  
**Prompts Covered**: 03, 04, 05, 06, 07, 08  
**Total Time**: 31-36 hours

---

## 📋 PROMPT 03: Replace Mock APIs - Priority 1 (Core Trading)

**Duration**: 10-12 hours  
**Focus**: Core trading functionality

### Services to Integrate

1. **OMS (port 8099)** - Order Management
2. **Risk (port 8103)** - Risk Checks
3. **Gateway (port 8080)** - Market Data
4. **Live Gateway (port 8200)** - Order Execution

### Implementation Pattern (Apply to Each Service)

```typescript
// BEFORE (Mock)
// src/api/omsApi.ts
export const submitOrder = async (order: Order) => {
  return Promise.resolve({
    success: true,
    orderId: 'mock-123'
  });
};

// AFTER (Real)
import axios from 'axios';

const OMS_URL = import.meta.env.VITE_OMS_URL || 'http://localhost:8099';

export const submitOrder = async (order: Order) => {
  try {
    const response = await axios.post(`${OMS_URL}/orders`, order, {
      timeout: 5000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    return response.data;
  } catch (error) {
    console.error('Order submission failed:', error);
    throw error;
  }
};
```

### Files to Update

**OMS Integration** (~4h):
- `src/api/omsApi.ts` - Order submission, positions, fills
- `src/pages/Orders.tsx` - Display orders
- `src/pages/Positions.tsx` - Display positions
- `src/components/OrderForm.tsx` - Submit orders

**Risk Integration** (~2h):
- `src/api/riskApi.ts` - Risk checks
- `src/components/OrderForm.tsx` - Pre-submission risk check

**Gateway Integration** (~3h):
- `src/api/marketDataApi.ts` - Tickers, candles
- `src/pages/MarketData.tsx` - Display market data
- `src/pages/Dashboard.tsx` - Dashboard widgets

**Live Gateway Integration** (~3h):
- `src/api/liveGatewayApi.ts` - Order routing status
- `src/pages/Orders.tsx` - Order status updates

### Testing Checklist

- [ ] Can submit orders via UI
- [ ] Orders appear in orders page
- [ ] Positions update correctly
- [ ] Market data displays
- [ ] Risk checks execute
- [ ] Error handling works

---

## 📋 PROMPT 04: Replace Mock APIs - Priority 2 (Essential)

**Duration**: 6-8 hours  
**Focus**: Authentication & Reporting

### Services to Integrate

1. **authn (port 8001)** - Authentication
2. **PTRC (port 8109)** - P&L, Reports

### Authentication Integration (~4h)

```typescript
// src/api/authApi.ts
const AUTH_URL = import.meta.env.VITE_AUTH_URL || 'http://localhost:8001';

export const login = async (email: string, password: string) => {
  const response = await axios.post(`${AUTH_URL}/login`, {
    email,
    password
  });
  
  // Store token
  localStorage.setItem('auth_token', response.data.token);
  
  return response.data;
};

export const getProfile = async () => {
  const token = localStorage.getItem('auth_token');
  const response = await axios.get(`${AUTH_URL}/profile`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.data;
};
```

**Files to Update**:
- `src/api/authApi.ts`
- `src/pages/Login.tsx`
- `src/contexts/AuthContext.tsx`
- `src/components/ProtectedRoute.tsx`

### PTRC Integration (~3h)

```typescript
// src/api/ptrcApi.ts
const PTRC_URL = import.meta.env.VITE_PTRC_URL || 'http://localhost:8109';

export const getPnL = async (account: string) => {
  const response = await axios.get(`${PTRC_URL}/pnl/${account}`);
  return response.data;
};

export const getReport = async (reportType: string) => {
  const response = await axios.get(`${PTRC_URL}/reports/${reportType}`);
  return response.data;
};
```

**Files to Update**:
- `src/api/ptrcApi.ts`
- `src/pages/Analytics.tsx`
- `src/pages/Reports.tsx`
- `src/components/PnLDisplay.tsx`

---

## 📋 PROMPT 05: Setup Nginx Reverse Proxy

**Duration**: 4 hours  
**Focus**: Unified API gateway

### Create Nginx Configuration

```nginx
# config/nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream oms {
        server oms:8099;
    }
    
    upstream risk {
        server risk:8103;
    }
    
    upstream gateway {
        server gateway:8080;
    }
    
    upstream live-gateway {
        server live-gateway:8200;
    }
    
    upstream ptrc {
        server ptrc:8109;
    }
    
    upstream authn {
        server authn:8001;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # Frontend static files
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }
        
        # API endpoints
        location /api/oms/ {
            proxy_pass http://oms/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /api/risk/ {
            proxy_pass http://risk/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /api/gateway/ {
            proxy_pass http://gateway/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /api/live-gateway/ {
            proxy_pass http://live-gateway/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /api/ptrc/ {
            proxy_pass http://ptrc/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /api/auth/ {
            proxy_pass http://authn/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # WebSocket support (if needed)
        location /ws {
            proxy_pass http://gateway/ws;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

### Update Frontend .env

```bash
# All APIs now go through Nginx
VITE_API_URL=http://localhost
VITE_OMS_URL=http://localhost/api/oms
VITE_RISK_URL=http://localhost/api/risk
VITE_GATEWAY_URL=http://localhost/api/gateway
VITE_LIVE_GATEWAY_URL=http://localhost/api/live-gateway
VITE_PTRC_URL=http://localhost/api/ptrc
VITE_AUTH_URL=http://localhost/api/auth
```

---

## 📋 PROMPT 06: Build and Containerize Frontend

**Duration**: 3 hours  
**Focus**: Docker containerization

### Create Dockerfile

```dockerfile
# frontend/Dockerfile
# Multi-stage build

# Stage 1: Build
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY . .

# Build production bundle
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Add to docker-compose

```yaml
# infrastructure/docker/docker-compose.frontend.yml
services:
  frontend:
    build:
      context: ../../frontend
      dockerfile: Dockerfile
    container_name: frontend
    ports:
      - "80:80"
      - "443:443"
    networks:
      - frontend
      - backend
    depends_on:
      - oms
      - risk
      - gateway
      - live-gateway
      - ptrc
      - authn
    restart: unless-stopped
    labels:
      - "com.trade2026.service=frontend"
```

### Build and Test

```bash
# Build image
cd frontend
docker build -t localhost/frontend:latest .

# Test container
docker run -d -p 80:80 localhost/frontend:latest

# Open browser to http://localhost
```

---

## 📋 PROMPT 07: Integration Testing

**Duration**: 4 hours  
**Focus**: End-to-end testing

### Test Scenarios

**1. Order Submission Flow** (30 min)
```
1. Login to application
2. Navigate to Orders page
3. Click "New Order"
4. Fill order form (BTCUSDT, Buy, 0.1, Limit, 45000)
5. Submit order
6. Verify risk check passes
7. Verify order appears in orders table
8. Verify order status updates
9. Verify position updates (when filled)
```

**2. Market Data Display** (20 min)
```
1. Navigate to Market Data page
2. Verify tickers loading and updating
3. Select symbol (BTCUSDT)
4. Verify chart displaying
5. Verify data refreshing
```

**3. Position Tracking** (20 min)
```
1. Navigate to Positions page
2. Verify positions loading
3. Verify P&L calculations
4. Verify position updates when orders fill
```

**4. Authentication Flow** (20 min)
```
1. Logout (if logged in)
2. Navigate to login page
3. Enter credentials
4. Submit login
5. Verify token stored
6. Verify redirect to dashboard
7. Verify protected routes work
8. Logout
9. Verify redirect to login
```

**5. Performance Testing** (30 min)
```
1. Submit 10 orders rapidly
2. Monitor response times
3. Check for errors
4. Verify all orders processed
5. Check browser console for errors
6. Monitor network requests
```

**6. Error Handling** (30 min)
```
1. Submit invalid order → Should show error
2. Submit order with insufficient funds → Should show error
3. Try accessing backend with invalid token → Should redirect to login
4. Simulate network failure → Should show error message
```

### Automated Tests (Optional)

```typescript
// tests/integration/orderFlow.test.ts
describe('Order Submission Flow', () => {
  it('should submit order and update UI', async () => {
    // Login
    await login('test@example.com', 'password');
    
    // Navigate to orders
    await page.goto('/orders');
    
    // Click new order
    await page.click('[data-testid="new-order"]');
    
    // Fill form
    await page.fill('[name="symbol"]', 'BTCUSDT');
    await page.select('[name="side"]', 'buy');
    await page.fill('[name="quantity"]', '0.1');
    
    // Submit
    await page.click('[data-testid="submit-order"]');
    
    // Verify success
    await expect(page.locator('.order-success')).toBeVisible();
    
    // Verify order in table
    await expect(page.locator('table tr:has-text("BTCUSDT")')).toBeVisible();
  });
});
```

---

## 📋 PROMPT 08: Production Polish

**Duration**: 4 hours  
**Focus**: Final optimizations

### Performance Optimizations

**1. Code Splitting**
```typescript
// Lazy load pages
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Orders = lazy(() => import('./pages/Orders'));
const Positions = lazy(() => import('./pages/Positions'));

// Wrap in Suspense
<Suspense fallback={<LoadingSpinner />}>
  <Routes>
    <Route path="/" element={<Dashboard />} />
    <Route path="/orders" element={<Orders />} />
    <Route path="/positions" element={<Positions />} />
  </Routes>
</Suspense>
```

**2. API Response Caching**
```typescript
// Simple cache implementation
const cache = new Map();

export const getCachedData = async (key: string, fetcher: () => Promise<any>, ttl = 60000) => {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < ttl) {
    return cached.data;
  }
  
  const data = await fetcher();
  cache.set(key, { data, timestamp: Date.now() });
  return data;
};
```

**3. Loading States**
```typescript
// Add loading indicators
const [loading, setLoading] = useState(false);

const submitOrder = async () => {
  setLoading(true);
  try {
    await omsApi.submitOrder(order);
    toast.success('Order submitted!');
  } catch (error) {
    toast.error('Order failed');
  } finally {
    setLoading(false);
  }
};
```

**4. Error Boundaries**
```typescript
// src/components/ErrorBoundary.tsx
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    console.error('Error caught:', error, errorInfo);
    // Log to monitoring service
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorFallback />;
    }
    return this.props.children;
  }
}
```

### Final Checks

- [ ] All pages load without errors
- [ ] All API integrations working
- [ ] Error handling comprehensive
- [ ] Loading states on all async operations
- [ ] Toast notifications for user feedback
- [ ] Responsive design verified
- [ ] Browser compatibility tested (Chrome, Firefox, Safari)
- [ ] No console errors
- [ ] Performance acceptable (< 3s page load)
- [ ] Production build optimized

---

## ✅ PHASE 3 COMPLETE!

### What You Have

**Complete MVP Platform**:
- ✅ React frontend with all features
- ✅ All mock APIs replaced
- ✅ Real backend integration
- ✅ Nginx reverse proxy
- ✅ Docker containerization
- ✅ Full trading functionality
- ✅ Authentication
- ✅ P&L and reporting
- ✅ Market data display
- ✅ Order management
- ✅ Position tracking

### Capabilities

**Users Can**:
- Login with authentication
- View real-time market data
- Submit orders (paper trading)
- Track positions
- View P&L
- Generate reports
- Manage settings

### What's Next

**Option A**: Deploy to production
**Option B**: Phase 4 (ML Library)
**Option C**: Additional features and polish

---

**Total Phase 3 Time**: 35-40 hours (~5 working days)

**Status**: Complete, production-ready platform ✅
