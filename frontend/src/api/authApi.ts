/**
 * Authentication API Client
 * Connects to authn service on port 8114
 */

import axios, { AxiosInstance } from 'axios';

// Get Auth URL from environment or use default
const AUTH_URL = import.meta.env.VITE_AUTH_URL || 'http://localhost:8114';

/**
 * Login credentials
 */
export interface LoginRequest {
  email: string;
  password: string;
  username?: string;
}

/**
 * Login response
 */
export interface LoginResponse {
  token: string;
  user: UserProfile;
  expires_at?: string;
}

/**
 * User profile
 */
export interface UserProfile {
  id: string;
  email: string;
  username?: string;
  name?: string;
  role?: string;
  permissions?: string[];
  created_at?: string;
}

/**
 * Token validation response
 */
export interface TokenValidation {
  valid: boolean;
  user?: UserProfile;
  expires_at?: string;
}

/**
 * Register request
 */
export interface RegisterRequest {
  email: string;
  password: string;
  username?: string;
  name?: string;
}

class AuthApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: AUTH_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token && !config.url?.includes('/login') && !config.url?.includes('/register')) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        console.log(`[Auth API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('[Auth API] Request error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log(`[Auth API] Response:`, response.status);
        return response;
      },
      (error) => {
        console.error('[Auth API] Response error:', error.response?.data || error.message);
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.logout();
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Login with email and password
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      const response = await this.client.post<LoginResponse>('/login', credentials);

      // Store token in localStorage
      if (response.data.token) {
        localStorage.setItem('auth_token', response.data.token);
        localStorage.setItem('user_profile', JSON.stringify(response.data.user));
        console.log('[Auth API] Login successful, token stored');
      }

      return response.data;
    } catch (error) {
      console.error('[Auth API] Login failed:', error);
      throw error;
    }
  }

  /**
   * Logout (clear local storage)
   */
  logout(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_profile');
    console.log('[Auth API] Logged out, tokens cleared');
  }

  /**
   * Register new user
   */
  async register(data: RegisterRequest): Promise<LoginResponse> {
    try {
      const response = await this.client.post<LoginResponse>('/register', data);

      // Store token after successful registration
      if (response.data.token) {
        localStorage.setItem('auth_token', response.data.token);
        localStorage.setItem('user_profile', JSON.stringify(response.data.user));
        console.log('[Auth API] Registration successful, token stored');
      }

      return response.data;
    } catch (error) {
      console.error('[Auth API] Registration failed:', error);
      throw error;
    }
  }

  /**
   * Get current user profile
   */
  async getProfile(): Promise<UserProfile> {
    try {
      const response = await this.client.get<UserProfile>('/profile');

      // Update cached profile
      localStorage.setItem('user_profile', JSON.stringify(response.data));

      return response.data;
    } catch (error) {
      console.error('[Auth API] Failed to fetch profile:', error);
      throw error;
    }
  }

  /**
   * Update user profile
   */
  async updateProfile(updates: Partial<UserProfile>): Promise<UserProfile> {
    try {
      const response = await this.client.put<UserProfile>('/profile', updates);

      // Update cached profile
      localStorage.setItem('user_profile', JSON.stringify(response.data));

      return response.data;
    } catch (error) {
      console.error('[Auth API] Failed to update profile:', error);
      throw error;
    }
  }

  /**
   * Validate current token
   */
  async validateToken(): Promise<TokenValidation> {
    try {
      const response = await this.client.get<TokenValidation>('/validate');
      return response.data;
    } catch (error) {
      console.error('[Auth API] Token validation failed:', error);
      return { valid: false };
    }
  }

  /**
   * Change password
   */
  async changePassword(oldPassword: string, newPassword: string): Promise<{ success: boolean }> {
    try {
      const response = await this.client.post('/change-password', {
        old_password: oldPassword,
        new_password: newPassword,
      });
      return response.data;
    } catch (error) {
      console.error('[Auth API] Password change failed:', error);
      throw error;
    }
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(email: string): Promise<{ success: boolean }> {
    try {
      const response = await this.client.post('/reset-password', { email });
      return response.data;
    } catch (error) {
      console.error('[Auth API] Password reset request failed:', error);
      throw error;
    }
  }

  /**
   * Get current auth token
   */
  getToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  /**
   * Get cached user profile
   */
  getCachedProfile(): UserProfile | null {
    const profile = localStorage.getItem('user_profile');
    return profile ? JSON.parse(profile) : null;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; service: string }> {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      console.error('[Auth API] Health check failed:', error);
      throw error;
    }
  }
}

// Export singleton instance
const authApi = new AuthApiClient();
export default authApi;
