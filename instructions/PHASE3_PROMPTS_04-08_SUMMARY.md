# Phase 3 - Remaining Prompts Summary (04-08)

**Created**: 2025-10-14  
**Purpose**: Quick implementation guide for Phase 3 Prompts 04-08  
**Note**: Detailed Prompt 03 created separately, use this for 04-08

---

## ✅ COMPLETED PROMPTS

- ✅ Prompt 00: Validation Gate
- ✅ Prompt 01: Survey Frontend
- ✅ Prompt 02: Copy Frontend
- ✅ Prompt 03: Replace Mock APIs P1 (detailed file created)
- ⏸️ Prompts 04-08: Use this guide

---

## 📋 PROMPT 04: Replace Mock APIs - Priority 2 (6-8 hours)

### Services to Integrate

**1. authn (port 8001) - Authentication** (4 hours)
**2. PTRC (port 8109) - P&L and Reports** (3 hours)

### Implementation Guide

#### Authentication Integration

```typescript
// src/api/authApi.ts
const AUTH_URL = import.meta.env.VITE_AUTH_URL || 'http://localhost:8001';

export const login = async (email: string, password: string) => {
  const response = await axios.post(`${AUTH_URL}/login`, { email, password });
  localStorage.setItem('auth_token', response.data.token);
  return response.data;
};

export const logout = () => {
  localStorage.removeItem('auth_token');
};

export const getProfile = async () => {
  const token = localStorage.getItem('auth_token');
  const response = await axios.get(`${AUTH_URL}/profile`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data;
};

export const isAuthenticated = () => {
  return !!localStorage.getItem('auth_token');
};
```

**Update Login Page**:
```typescript
// src/pages/Login.tsx
const handleLogin = async (e) => {
  e.preventDefault();
  try {
    await login(email, password);
    navigate('/dashboard');
  } catch (error) {
    setError('Login failed');
  }
};
```

**Create Auth Context**:
```typescript
// src/contexts/AuthContext.tsx
export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isAuthenticated()) {
      getProfile().then(setUser).finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, setUser, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
```

**Protected Routes**:
```typescript
// src/components/ProtectedRoute.tsx
export const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) return <div>Loading...</div>;
  if (!user) return <Navigate to="/login" />;
  
  return children;
};
```

#### PTRC Integration

```typescript
// src/api/ptrcApi.ts
const PTRC_URL = import.meta.env.VITE_PTRC_URL || 'http://localhost:8109';

export const getPnL = async (account: string) => {
  const response = await axios.get(`${PTRC_URL}/pnl/${account}`);
  return response.data;
};

export const getReport = async (reportType: string, params: any) => {
  const response = await axios.get(`${PTRC_URL}/reports/${reportType}`, { params });
  return response.data;
};

export const getTaxReport = async (account: string, year: number) => {
  const response = await axios.get(`${PTRC_URL}/tax/${account}/${year}`);
  return response.data;
};
```

**Update Analytics Page**:
```typescript
// src/pages/Analytics.tsx
useEffect(() => {
  const loadData = async () => {
    const pnlData = await getPnL('test_account');
    setPnL(pnlData);
  };
  loadData();
}, []);
```

### Testing Checklist

- [ ] Can login with credentials
- [ ] Token stored correctly
- [ ] Protected routes work
- [ ] Can logout
- [ ] P&L displays correctly
- [ ] Reports generate

---

## 📋 PROMPT 05: Setup Nginx Reverse Proxy (4 hours)

### Create Nginx Configuration

```nginx
# config/nginx/nginx.conf
events { worker_connections 1024; }

http {
    # Upstream backends
    upstream oms { server oms:8099; }
    upstream risk { server risk:8103; }
    upstream gateway { server gateway:8080; }
    upstream live-gateway { server live-gateway:8200; }
    upstream ptrc { server ptrc:8109; }
    upstream authn { server authn:8001; }

    server {
        listen 80;
        server_name localhost;

        # Frontend static files
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        # API proxying
        location /api/oms/ {
            proxy_pass http://oms/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /api/risk/ {
            proxy_pass http://risk/;
        }

        location /api/gateway/ {
            proxy_pass http://gateway/;
        }

        location /api/live-gateway/ {
            proxy_pass http://live-gateway/;
        }

        location /api/ptrc/ {
            proxy_pass http://ptrc/;
        }

        location /api/auth/ {
            proxy_pass http://authn/;
        }

        # WebSocket support
        location /ws {
            proxy_pass http://gateway/ws;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

### Update Frontend Environment

```bash
# .env
VITE_API_URL=http://localhost
VITE_OMS_URL=http://localhost/api/oms
VITE_RISK_URL=http://localhost/api/risk
VITE_GATEWAY_URL=http://localhost/api/gateway
VITE_LIVE_GATEWAY_URL=http://localhost/api/live-gateway
VITE_PTRC_URL=http://localhost/api/ptrc
VITE_AUTH_URL=http://localhost/api/auth
```

### Testing

```bash
# Test routing
curl http://localhost/api/oms/health
curl http://localhost/api/risk/health
curl http://localhost/api/gateway/health
```

---

## 📋 PROMPT 06: Build and Containerize Frontend (3 hours)

### Create Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
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
    networks:
      - frontend
      - backend
    depends_on:
      - oms
      - risk
      - gateway
    restart: unless-stopped
```

### Build and Deploy

```bash
cd frontend
docker build -t localhost/frontend:latest .
docker run -d -p 80:80 localhost/frontend:latest
```

---

## 📋 PROMPT 07: Integration Testing (4 hours)

### Test Scenarios

**1. Complete Order Flow** (30 min)
- Login → Submit order → Verify in orders table → Check position

**2. Authentication Flow** (20 min)
- Login → Access protected routes → Logout → Verify redirect

**3. Market Data** (20 min)
- View tickers → Verify refresh → Check chart data

**4. Position Tracking** (20 min)
- Submit orders → Verify positions update → Check P&L

**5. Performance** (30 min)
- Submit 10 orders rapidly → Check response times

**6. Error Handling** (30 min)
- Invalid orders → Network errors → Auth failures

### Automated Tests (Optional)

```typescript
// tests/integration/orderFlow.test.ts
describe('Order Flow', () => {
  it('should submit order successfully', async () => {
    await login('test@example.com', 'password');
    await page.goto('/orders');
    await page.click('[data-testid="new-order"]');
    await page.fill('[name="symbol"]', 'BTCUSDT');
    await page.click('[data-testid="submit"]');
    await expect(page.locator('.success')).toBeVisible();
  });
});
```

---

## 📋 PROMPT 08: Production Polish (4 hours)

### Optimizations

**1. Code Splitting**
```typescript
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Orders = lazy(() => import('./pages/Orders'));
```

**2. API Caching**
```typescript
const cache = new Map();
export const getCachedData = async (key, fetcher, ttl = 60000) => {
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
const [loading, setLoading] = useState(false);

const submitOrder = async () => {
  setLoading(true);
  try {
    await omsApi.submitOrder(order);
    toast.success('Order submitted!');
  } finally {
    setLoading(false);
  }
};
```

**4. Error Boundaries**
```typescript
class ErrorBoundary extends React.Component {
  componentDidCatch(error) {
    console.error('Error:', error);
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
- [ ] Loading states on async operations
- [ ] Toast notifications for feedback
- [ ] Responsive design
- [ ] Browser compatibility
- [ ] No console errors
- [ ] Performance < 3s page load

---

## ✅ PHASE 3 COMPLETE!

### What You Have

**Complete MVP Platform**:
- ✅ React frontend fully integrated
- ✅ All mock APIs replaced
- ✅ Nginx reverse proxy
- ✅ Docker containerization
- ✅ Authentication
- ✅ Order management
- ✅ Position tracking
- ✅ Market data
- ✅ P&L and reports

### Capabilities

- Users can login
- View real-time market data
- Submit orders (paper trading)
- Track positions
- View P&L
- Generate reports

### What's Next

**Option A**: Deploy to production
**Option B**: Phase 4 (ML Library)
**Option C**: Additional polish

---

**Total Phase 3 Time**: 35-40 hours

**Status**: Production-ready platform ✅
