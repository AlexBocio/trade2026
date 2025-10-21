/**
 * Risk Store - Manages risk metrics and monitoring
 */

import { create } from 'zustand';
import { mockRiskData } from '../services/mock-data/portfolio-risk-data';

interface RiskState {
  data: typeof mockRiskData | null;
  isLoading: boolean;
  error: string | null;
  hasActiveAlerts: boolean;
  loadRisk: () => Promise<void>;
  checkLimits: () => void;
  updateRiskMetrics: () => void;
}

export const useRiskStore = create<RiskState>((set, get) => ({
  data: null,
  isLoading: false,
  error: null,
  hasActiveAlerts: false,

  loadRisk: async () => {
    set({ isLoading: true, error: null });

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      set({
        data: mockRiskData,
        isLoading: false,
      });

      // Check limits after loading
      get().checkLimits();
    } catch (error) {
      set({
        error: 'Failed to load risk data',
        isLoading: false,
      });
    }
  },

  checkLimits: () => {
    const currentData = get().data;
    if (!currentData) return;

    // Check if any limits are breached or in warning zone
    const breaches = currentData.limits.filter((limit) => {
      const percentage = (Math.abs(limit.current) / Math.abs(limit.limit)) * 100;
      return percentage >= 80; // Warning at 80%
    });

    const hasActiveAlerts = breaches.length > 0;

    if (hasActiveAlerts) {
      console.warn('RISK LIMITS IN WARNING ZONE:', breaches);
    }

    set({ hasActiveAlerts });
  },

  updateRiskMetrics: () => {
    const currentData = get().data;
    if (!currentData) return;

    // Simulate real-time risk metric updates
    const updatedData = { ...currentData };

    // Update VaR with small random changes
    updatedData.metrics.portfolioVaR += (Math.random() - 0.5) * 20;

    // Update volatility
    updatedData.metrics.volatility += (Math.random() - 0.5) * 0.5;

    set({ data: updatedData });
    get().checkLimits();
  },
}));
