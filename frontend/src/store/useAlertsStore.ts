/**
 * Alerts Store - Manage alerts and notifications
 */

import { create } from 'zustand';
import type { Alert, AlertHistory, AlertStats } from '../services/mock-data/alerts-data';
import { mockAlerts, mockAlertHistory, mockAlertStats } from '../services/mock-data/alerts-data';

interface AlertsState {
  alerts: Alert[];
  history: AlertHistory[];
  stats: AlertStats;
  isLoading: boolean;
  filter: 'all' | 'active' | 'triggered' | 'expired' | 'disabled';
  notifications: any[];

  // Actions
  loadAlerts: () => Promise<void>;
  loadHistory: () => Promise<void>;
  loadNotifications: () => Promise<void>;
  dismissNotification: (id: string) => void;
  snoozeNotification: (id: string) => void;
  getAlert: (id: string) => Alert | null;
  createAlert: (alert: Omit<Alert, 'id' | 'createdAt' | 'status'>) => Promise<void>;
  updateAlert: (id: string, updates: Partial<Alert>) => Promise<void>;
  deleteAlert: (id: string) => Promise<void>;
  toggleAlert: (id: string) => Promise<void>;
  acknowledgeAlert: (historyId: string) => Promise<void>;
  setFilter: (filter: 'all' | 'active' | 'triggered' | 'expired' | 'disabled') => void;
  testAlert: (id: string) => Promise<void>;
}

export const useAlertsStore = create<AlertsState>((set, get) => ({
  alerts: [],
  history: [],
  stats: mockAlertStats,
  isLoading: false,
  filter: 'all',
  notifications: [],

  loadAlerts: async () => {
    set({ isLoading: true });
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 500));
    set({ alerts: mockAlerts, isLoading: false });
  },

  loadHistory: async () => {
    set({ isLoading: true });
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 300));
    set({ history: mockAlertHistory, isLoading: false });
  },

  getAlert: (id) => {
    return get().alerts.find((a) => a.id === id) || null;
  },

  createAlert: async (alertData) => {
    const newAlert: Alert = {
      id: `alert-${Date.now()}`,
      ...alertData,
      createdAt: new Date().toISOString(),
      status: 'active',
      currentValue: alertData.currentValue || 0,
    };

    await new Promise((resolve) => setTimeout(resolve, 200));
    set((state) => ({
      alerts: [newAlert, ...state.alerts],
      stats: {
        ...state.stats,
        totalAlerts: state.stats.totalAlerts + 1,
        activeAlerts: state.stats.activeAlerts + 1,
      },
    }));
  },

  updateAlert: async (id, updates) => {
    await new Promise((resolve) => setTimeout(resolve, 200));
    set((state) => ({
      alerts: state.alerts.map((a) => (a.id === id ? { ...a, ...updates } : a)),
    }));
  },

  deleteAlert: async (id) => {
    await new Promise((resolve) => setTimeout(resolve, 200));
    set((state) => ({
      alerts: state.alerts.filter((a) => a.id !== id),
      stats: {
        ...state.stats,
        totalAlerts: state.stats.totalAlerts - 1,
      },
    }));
  },

  toggleAlert: async (id) => {
    const alert = get().getAlert(id);
    if (!alert) return;

    const newStatus = alert.status === 'disabled' ? 'active' : 'disabled';
    await get().updateAlert(id, { status: newStatus });
  },

  acknowledgeAlert: async (historyId) => {
    await new Promise((resolve) => setTimeout(resolve, 100));
    set((state) => ({
      history: state.history.map((h) =>
        h.id === historyId ? { ...h, acknowledged: true } : h
      ),
    }));
  },

  setFilter: (filter) => {
    set({ filter });
  },

  testAlert: async (id) => {
    const alert = get().getAlert(id);
    if (!alert) return;

    // Simulate triggering the alert
    await new Promise((resolve) => setTimeout(resolve, 300));

    const newHistoryEntry: AlertHistory = {
      id: `history-${Date.now()}`,
      alertId: id,
      symbol: alert.symbol,
      type: `${alert.type.charAt(0).toUpperCase() + alert.type.slice(1)} Alert`,
      message: `TEST: ${alert.message}`,
      triggeredAt: new Date().toISOString(),
      acknowledged: false,
    };

    set((state) => ({
      history: [newHistoryEntry, ...state.history],
    }));
  },

  loadNotifications: async () => {
    // Simulate loading notifications
    await new Promise((resolve) => setTimeout(resolve, 200));
    set({ notifications: [] });
  },

  dismissNotification: (id) => {
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    }));
  },

  snoozeNotification: (id) => {
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, snoozed: true } : n
      ),
    }));
  },
}));
