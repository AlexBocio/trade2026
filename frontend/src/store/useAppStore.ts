/**
 * Global application state using Zustand
 */

import { create } from 'zustand';

interface AppState {
  // UI state
  sidebarCollapsed: boolean;
  theme: 'dark' | 'light';
  isLoading: boolean;

  // User state
  isAuthenticated: boolean;
  userId?: string;
  userName: string;

  // Connection state
  isConnected: boolean;
  lastUpdate: Date | null;

  // Notifications
  notifications: number;

  // Actions
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setTheme: (theme: 'dark' | 'light') => void;
  setLoading: (loading: boolean) => void;
  setAuthenticated: (authenticated: boolean, userId?: string) => void;
  logout: () => void;
  setConnected: (connected: boolean) => void;
  addNotification: () => void;
  clearNotifications: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Initial state
  sidebarCollapsed: false,
  theme: 'dark',
  isLoading: false,
  isAuthenticated: true,
  userId: 'user-001',
  userName: 'Alex Bocio',
  isConnected: true,
  lastUpdate: null,
  notifications: 3,

  // Actions
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

  setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),

  setTheme: (theme) => {
    set({ theme });
    // Apply theme to document
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  },

  setLoading: (loading) => set({ isLoading: loading }),

  setAuthenticated: (authenticated, userId) => set({ isAuthenticated: authenticated, userId }),

  logout: () => set({ isAuthenticated: false, userId: undefined, userName: '' }),

  setConnected: (connected) => set({ isConnected: connected, lastUpdate: new Date() }),

  addNotification: () => set((state) => ({ notifications: state.notifications + 1 })),

  clearNotifications: () => set({ notifications: 0 }),
}));
