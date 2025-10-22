# Phase 3 - Prompt 04: Replace Mock APIs - Priority 2 (Essential Features)

**Phase**: 3 - Frontend Integration  
**Prompt**: 04 of 08  
**Purpose**: Replace Priority 2 mock APIs for essential features  
**Duration**: 6-8 hours  
**Status**: ⏸️ Ready after Prompt 03 complete

---

## 🛑 PREREQUISITES

- [ ] Prompt 03 complete (core trading APIs integrated)
- [ ] OMS, Risk, Gateway, Live Gateway APIs working
- [ ] Frontend can submit orders and view market data
- [ ] No critical errors from Prompt 03

---

## 🎯 TASK OVERVIEW

### What This Prompt Does

Integrates Priority 2 services for essential platform features:
1. **Authentication Service** - User login, session management
2. **PTRC Service** - P&L tracking, reports, analytics
3. **Additional Data APIs** - Historical data, analytics queries

---

## 📋 STEP-BY-STEP INSTRUCTIONS

### Step 1: Authentication Service Integration

#### 1.1 Create Auth API Client

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\frontend

# Create authentication API client
cat > src/api/authApi.ts << 'EOF'
import axios, { AxiosError } from 'axios';

const AUTH_URL = import.meta.env.VITE_AUTH_URL || 'http://localhost/api/auth';

// Create axios instance with interceptors
const authClient = axios.create({
  baseURL: AUTH_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
authClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle auth errors globally
authClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: {
    id: string;
    email: string;
    name: string;
    role: string;
    permissions: string[];
  };
  expiresIn: number;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  permissions: string[];
}

// Authentication API functions
export const authApi = {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      const response = await authClient.post<LoginResponse>('/login', credentials);
      
      // Store token and user data
      if (response.data.token) {
        localStorage.setItem('auth_token', response.data.token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      
      return response.data;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  },

  async logout(): Promise<void> {
    try {
      await authClient.post('/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local storage regardless
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
  },

  async getProfile(): Promise<User> {
    try {
      const response = await authClient.get<User>('/profile');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      throw error;
    }
  },

  async refreshToken(): Promise<string> {
    try {
      const response = await authClient.post<{ token: string }>('/refresh');
      
      if (response.data.token) {
        localStorage.setItem('auth_token', response.data.token);
      }
      
      return response.data.token;
    } catch (error) {
      console.error('Token refresh failed:', error);
      throw error;
    }
  },

  async validateToken(): Promise<boolean> {
    try {
      await authClient.get('/validate');
      return true;
    } catch {
      return false;
    }
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
  },

  getStoredUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch {
        return null;
      }
    }
    return null;
  },
};

export default authApi;
EOF
```

#### 1.2 Create Auth Context

```bash
# Create authentication context for React
cat > src/contexts/AuthContext.tsx << 'EOF'
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi, User, LoginRequest } from '../api/authApi';
import { useNavigate } from 'react-router-dom';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is already logged in
    const checkAuth = async () => {
      setIsLoading(true);
      try {
        if (authApi.isAuthenticated()) {
          const isValid = await authApi.validateToken();
          if (isValid) {
            const storedUser = authApi.getStoredUser();
            if (storedUser) {
              setUser(storedUser);
            } else {
              const profile = await authApi.getProfile();
              setUser(profile);
              localStorage.setItem('user', JSON.stringify(profile));
            }
          } else {
            // Token invalid, clear everything
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user');
          }
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (credentials: LoginRequest) => {
    try {
      const response = await authApi.login(credentials);
      setUser(response.user);
      navigate('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
      setUser(null);
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
      // Navigate to login even if logout fails
      navigate('/login');
    }
  };

  const refreshToken = async () => {
    try {
      await authApi.refreshToken();
    } catch (error) {
      console.error('Token refresh failed:', error);
      // If refresh fails, logout
      await logout();
    }
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    refreshToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
EOF
```

#### 1.3 Create Protected Route Component

```bash
# Create protected route wrapper
cat > src/components/ProtectedRoute.tsx << 'EOF'
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermissions?: string[];
}

export function ProtectedRoute({ children, requiredPermissions = [] }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking auth
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check permissions if required
  if (requiredPermissions.length > 0 && user) {
    const hasPermission = requiredPermissions.some(
      permission => user.permissions?.includes(permission)
    );
    
    if (!hasPermission) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return <>{children}</>;
}

export default ProtectedRoute;
EOF
```

#### 1.4 Update Login Page

```bash
# Update or create login page
cat > src/pages/Login.tsx << 'EOF'
import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login({ email, password });
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.response?.data?.message || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h1 className="text-2xl font-bold mb-6 text-center">Trade2026 Login</h1>
        
        <form onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}
          
          <div className="mb-4">
            <label htmlFor="email" className="block text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              required
              disabled={isLoading}
            />
          </div>
          
          <div className="mb-6">
            <label htmlFor="password" className="block text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              required
              disabled={isLoading}
            />
          </div>
          
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <div className="mt-4 text-center text-sm text-gray-600">
          Demo credentials: demo@trade2026.com / demo123
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
EOF
```

---

### Step 2: PTRC (P&L Tracking) Service Integration

#### 2.1 Create PTRC API Client

```bash
# Create PTRC API client
cat > src/api/ptrcApi.ts << 'EOF'
import axios from 'axios';

const PTRC_URL = import.meta.env.VITE_PTRC_URL || 'http://localhost/api/ptrc';

// Create axios instance for PTRC
const ptrcClient = axios.create({
  baseURL: PTRC_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
ptrcClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export interface PnLData {
  account: string;
  timestamp: string;
  realized_pnl: number;
  unrealized_pnl: number;
  total_pnl: number;
  positions: {
    symbol: string;
    quantity: number;
    avg_price: number;
    current_price: number;
    unrealized_pnl: number;
    realized_pnl: number;
  }[];
}

export interface Report {
  id: string;
  type: string;
  account: string;
  start_date: string;
  end_date: string;
  data: any;
  created_at: string;
}

export interface Analytics {
  account: string;
  period: string;
  metrics: {
    total_trades: number;
    winning_trades: number;
    losing_trades: number;
    win_rate: number;
    avg_win: number;
    avg_loss: number;
    profit_factor: number;
    sharpe_ratio: number;
    max_drawdown: number;
    total_pnl: number;
  };
}

// PTRC API functions
export const ptrcApi = {
  async getPnL(account?: string): Promise<PnLData> {
    try {
      const url = account ? `/pnl/${account}` : '/pnl';
      const response = await ptrcClient.get<PnLData>(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch P&L:', error);
      throw error;
    }
  },

  async getPnLHistory(
    account: string,
    startDate: string,
    endDate: string
  ): Promise<PnLData[]> {
    try {
      const response = await ptrcClient.get<PnLData[]>('/pnl/history', {
        params: { account, start_date: startDate, end_date: endDate },
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch P&L history:', error);
      throw error;
    }
  },

  async getReports(account?: string): Promise<Report[]> {
    try {
      const params = account ? { account } : {};
      const response = await ptrcClient.get<Report[]>('/reports', { params });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch reports:', error);
      throw error;
    }
  },

  async generateReport(
    type: string,
    account: string,
    startDate: string,
    endDate: string
  ): Promise<Report> {
    try {
      const response = await ptrcClient.post<Report>('/reports/generate', {
        type,
        account,
        start_date: startDate,
        end_date: endDate,
      });
      return response.data;
    } catch (error) {
      console.error('Failed to generate report:', error);
      throw error;
    }
  },

  async getAnalytics(
    account: string,
    period: 'daily' | 'weekly' | 'monthly' = 'daily'
  ): Promise<Analytics> {
    try {
      const response = await ptrcClient.get<Analytics>('/analytics', {
        params: { account, period },
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      throw error;
    }
  },

  async downloadReport(reportId: string): Promise<Blob> {
    try {
      const response = await ptrcClient.get(`/reports/${reportId}/download`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      console.error('Failed to download report:', error);
      throw error;
    }
  },
};

export default ptrcApi;
EOF
```

#### 2.2 Create P&L Display Component

```bash
# Create P&L display component
cat > src/components/PnLDisplay.tsx << 'EOF'
import React, { useState, useEffect } from 'react';
import { ptrcApi, PnLData } from '../api/ptrcApi';

interface PnLDisplayProps {
  account?: string;
  refreshInterval?: number; // in milliseconds
}

export function PnLDisplay({ 
  account, 
  refreshInterval = 5000 
}: PnLDisplayProps) {
  const [pnlData, setPnlData] = useState<PnLData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPnL = async () => {
      try {
        setLoading(true);
        const data = await ptrcApi.getPnL(account);
        setPnlData(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch P&L:', err);
        setError('Failed to load P&L data');
      } finally {
        setLoading(false);
      }
    };

    fetchPnL();

    // Set up refresh interval
    const interval = setInterval(fetchPnL, refreshInterval);

    return () => clearInterval(interval);
  }, [account, refreshInterval]);

  if (loading && !pnlData) {
    return <div className="animate-pulse bg-gray-200 h-20 rounded"></div>;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  if (!pnlData) {
    return null;
  }

  const formatCurrency = (value: number) => {
    const formatted = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(value);
    
    return value >= 0 ? formatted : formatted;
  };

  const getPnLColor = (value: number) => {
    if (value > 0) return 'text-green-600';
    if (value < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold mb-4">P&L Summary</h3>
      
      <div className="grid grid-cols-3 gap-4">
        <div>
          <p className="text-sm text-gray-500 mb-1">Realized P&L</p>
          <p className={`text-xl font-semibold ${getPnLColor(pnlData.realized_pnl)}`}>
            {formatCurrency(pnlData.realized_pnl)}
          </p>
        </div>
        
        <div>
          <p className="text-sm text-gray-500 mb-1">Unrealized P&L</p>
          <p className={`text-xl font-semibold ${getPnLColor(pnlData.unrealized_pnl)}`}>
            {formatCurrency(pnlData.unrealized_pnl)}
          </p>
        </div>
        
        <div>
          <p className="text-sm text-gray-500 mb-1">Total P&L</p>
          <p className={`text-xl font-semibold ${getPnLColor(pnlData.total_pnl)}`}>
            {formatCurrency(pnlData.total_pnl)}
          </p>
        </div>
      </div>

      {pnlData.positions && pnlData.positions.length > 0 && (
        <div className="mt-4 pt-4 border-t">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">
            Position P&L
          </h4>
          <div className="space-y-2">
            {pnlData.positions.slice(0, 5).map((position) => (
              <div
                key={position.symbol}
                className="flex justify-between items-center text-sm"
              >
                <span className="font-medium">{position.symbol}</span>
                <span className={getPnLColor(position.unrealized_pnl)}>
                  {formatCurrency(position.unrealized_pnl)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="mt-4 text-xs text-gray-400">
        Last updated: {new Date(pnlData.timestamp).toLocaleTimeString()}
      </div>
    </div>
  );
}

export default PnLDisplay;
EOF
```

#### 2.3 Update Analytics Page

```bash
# Update or create Analytics page
cat > src/pages/Analytics.tsx << 'EOF'
import React, { useState, useEffect } from 'react';
import { ptrcApi, Analytics, Report } from '../api/ptrcApi';
import { PnLDisplay } from '../components/PnLDisplay';
import { useAuth } from '../contexts/AuthContext';

export function AnalyticsPage() {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [reports, setReports] = useState<Report[]>([]);
  const [period, setPeriod] = useState<'daily' | 'weekly' | 'monthly'>('daily');
  const [loading, setLoading] = useState(true);
  const [generatingReport, setGeneratingReport] = useState(false);

  useEffect(() => {
    fetchAnalytics();
    fetchReports();
  }, [period]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const data = await ptrcApi.getAnalytics(user?.id || 'default', period);
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchReports = async () => {
    try {
      const data = await ptrcApi.getReports(user?.id);
      setReports(data);
    } catch (error) {
      console.error('Failed to fetch reports:', error);
    }
  };

  const generateReport = async (type: string) => {
    try {
      setGeneratingReport(true);
      const endDate = new Date().toISOString().split('T')[0];
      const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
        .toISOString()
        .split('T')[0];
      
      await ptrcApi.generateReport(
        type,
        user?.id || 'default',
        startDate,
        endDate
      );
      
      // Refresh reports list
      await fetchReports();
    } catch (error) {
      console.error('Failed to generate report:', error);
    } finally {
      setGeneratingReport(false);
    }
  };

  const downloadReport = async (reportId: string, reportType: string) => {
    try {
      const blob = await ptrcApi.downloadReport(reportId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `${reportType}_${reportId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download report:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Trading Analytics</h1>
      
      {/* P&L Display */}
      <div className="mb-8">
        <PnLDisplay account={user?.id} refreshInterval={10000} />
      </div>

      {/* Period Selector */}
      <div className="mb-6">
        <div className="flex space-x-4">
          <button
            onClick={() => setPeriod('daily')}
            className={`px-4 py-2 rounded ${
              period === 'daily'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Daily
          </button>
          <button
            onClick={() => setPeriod('weekly')}
            className={`px-4 py-2 rounded ${
              period === 'weekly'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Weekly
          </button>
          <button
            onClick={() => setPeriod('monthly')}
            className={`px-4 py-2 rounded ${
              period === 'monthly'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Monthly
          </button>
        </div>
      </div>

      {/* Analytics Metrics */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500 mb-1">Total Trades</p>
            <p className="text-2xl font-bold">{analytics.metrics.total_trades}</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500 mb-1">Win Rate</p>
            <p className="text-2xl font-bold">
              {(analytics.metrics.win_rate * 100).toFixed(1)}%
            </p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500 mb-1">Profit Factor</p>
            <p className="text-2xl font-bold">
              {analytics.metrics.profit_factor.toFixed(2)}
            </p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500 mb-1">Sharpe Ratio</p>
            <p className="text-2xl font-bold">
              {analytics.metrics.sharpe_ratio.toFixed(2)}
            </p>
          </div>
        </div>
      )}

      {/* Reports Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Reports</h2>
          <div className="space-x-2">
            <button
              onClick={() => generateReport('daily')}
              disabled={generatingReport}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              Generate Daily Report
            </button>
            <button
              onClick={() => generateReport('monthly')}
              disabled={generatingReport}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            >
              Generate Monthly Report
            </button>
          </div>
        </div>

        {reports.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Type</th>
                  <th className="text-left py-2">Period</th>
                  <th className="text-left py-2">Created</th>
                  <th className="text-left py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((report) => (
                  <tr key={report.id} className="border-b hover:bg-gray-50">
                    <td className="py-2">{report.type}</td>
                    <td className="py-2">
                      {report.start_date} to {report.end_date}
                    </td>
                    <td className="py-2">
                      {new Date(report.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-2">
                      <button
                        onClick={() => downloadReport(report.id, report.type)}
                        className="text-blue-600 hover:underline"
                      >
                        Download
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500">No reports available</p>
        )}
      </div>
    </div>
  );
}

export default AnalyticsPage;
EOF
```

---

### Step 3: Update App Router with Auth

```bash
# Update main App component with auth
cat > src/App.tsx << 'EOF'
import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';

// Lazy load pages for better performance
const LoginPage = lazy(() => import('./pages/Login'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Orders = lazy(() => import('./pages/Orders'));
const Positions = lazy(() => import('./pages/Positions'));
const MarketData = lazy(() => import('./pages/MarketData'));
const Analytics = lazy(() => import('./pages/Analytics'));
const Settings = lazy(() => import('./pages/Settings'));

// Loading component
const LoadingSpinner = () => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
  </div>
);

function App() {
  return (
    <Router>
      <AuthProvider>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            
            {/* Protected routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/orders"
              element={
                <ProtectedRoute>
                  <Orders />
                </ProtectedRoute>
              }
            />
            <Route
              path="/positions"
              element={
                <ProtectedRoute>
                  <Positions />
                </ProtectedRoute>
              }
            />
            <Route
              path="/market-data"
              element={
                <ProtectedRoute>
                  <MarketData />
                </ProtectedRoute>
              }
            />
            <Route
              path="/analytics"
              element={
                <ProtectedRoute>
                  <Analytics />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute requiredPermissions={['settings.view']}>
                  <Settings />
                </ProtectedRoute>
              }
            />
            
            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            
            {/* 404 page */}
            <Route
              path="*"
              element={
                <div className="flex items-center justify-center min-h-screen">
                  <div className="text-center">
                    <h1 className="text-4xl font-bold text-gray-800 mb-4">404</h1>
                    <p className="text-gray-600">Page not found</p>
                  </div>
                </div>
              }
            />
          </Routes>
        </Suspense>
      </AuthProvider>
    </Router>
  );
}

export default App;
EOF
```

---

### Step 4: Add Authentication Headers to All API Clients

```bash
# Update existing API clients to include auth headers

# Create a shared axios instance with auth
cat > src/api/client.ts << 'EOF'
import axios, { AxiosInstance } from 'axios';

// Create base axios instance with auth interceptor
export function createAuthenticatedClient(baseURL: string): AxiosInstance {
  const client = axios.create({
    baseURL,
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor to add auth token
  client.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor to handle auth errors
  client.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return client;
}
EOF
```

Now update each API client to use authenticated client:

```bash
# Example: Update OMS API to use authenticated client
# You'll need to do this for all API files created in Prompt 03

# Update src/api/omsApi.ts
# Add at the top:
# import { createAuthenticatedClient } from './client';
# const omsClient = createAuthenticatedClient(OMS_URL);
# Replace all axios calls with omsClient
```

---

### Step 5: Test Authentication Flow

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\frontend

# Start development server
npm run dev

# Test authentication flow:
# 1. Open http://localhost:5173
# 2. Should redirect to /login
# 3. Enter demo credentials
# 4. Should redirect to /dashboard
# 5. Check localStorage for auth_token
# 6. Try accessing protected pages
# 7. Click logout
# 8. Should redirect to /login
```

**Testing Checklist**:
- [ ] Login page loads
- [ ] Login with valid credentials works
- [ ] Token stored in localStorage
- [ ] Protected routes accessible when logged in
- [ ] Protected routes redirect when logged out
- [ ] Logout clears token and redirects
- [ ] API calls include auth header
- [ ] 401 errors redirect to login

---

### Step 6: Test P&L and Analytics

```bash
# With frontend running, test:

# 1. Navigate to Analytics page
# 2. Verify P&L data loads
# 3. Check period toggles work (daily/weekly/monthly)
# 4. Test report generation
# 5. Test report download
# 6. Verify metrics display correctly
```

**Testing Checklist**:
- [ ] P&L display component loads
- [ ] Real-time P&L updates work
- [ ] Analytics page displays metrics
- [ ] Period selector changes data
- [ ] Report generation works
- [ ] Report download works
- [ ] No console errors

---

## ✅ PROMPT 04 DELIVERABLES

### API Clients Created/Updated

- [ ] `src/api/authApi.ts` - Authentication service client
- [ ] `src/api/ptrcApi.ts` - PTRC service client
- [ ] `src/api/client.ts` - Shared authenticated axios instance

### Components Created

- [ ] `src/contexts/AuthContext.tsx` - Auth provider
- [ ] `src/components/ProtectedRoute.tsx` - Route protection
- [ ] `src/components/PnLDisplay.tsx` - P&L display widget
- [ ] `src/pages/Login.tsx` - Login page
- [ ] `src/pages/Analytics.tsx` - Analytics page

### App Updates

- [ ] `src/App.tsx` - Updated with auth routes
- [ ] All API clients updated with auth headers
- [ ] Protected routes configured

### Testing Complete

- [ ] Authentication flow working
- [ ] P&L data displaying
- [ ] Analytics page functional
- [ ] Reports generation working
- [ ] All API calls authenticated

---

## 🚦 VALIDATION GATE

### Integration Complete?

**Check**:
- [ ] Can login and logout
- [ ] Auth token persists across page refreshes
- [ ] Protected routes work correctly
- [ ] P&L data displays from real backend
- [ ] Analytics metrics load
- [ ] All API calls include auth headers
- [ ] No authentication errors in console

**Decision**:
- ✅ ALL WORKING → Proceed to Prompt 05 (Nginx setup)
- ❌ AUTH ISSUES → Fix authentication first
- ❌ PTRC ISSUES → Debug P&L service integration

---

## 📊 PROMPT 04 COMPLETION CRITERIA

Prompt 04 complete when:

- [ ] Authentication fully integrated
- [ ] Users can login/logout
- [ ] Protected routes working
- [ ] P&L tracking integrated
- [ ] Analytics page functional
- [ ] All Priority 2 APIs replaced
- [ ] No mock data for auth or P&L
- [ ] COMPLETION_TRACKER.md updated

**Next Prompt**: PHASE3_PROMPT05_SETUP_NGINX.md

---

**Prompt Status**: ⏸️ READY (after Prompt 03 complete)

**Estimated Time**: 6-8 hours

**Outcome**: Authentication and P&L tracking fully integrated with real backend
