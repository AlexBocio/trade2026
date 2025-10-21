/**
 * Dashboard state management using Zustand
 */

import { create } from 'zustand';
import { mockDashboardData, type DashboardData } from '../services/mock-data/dashboard-data';

interface DashboardState {
  data: DashboardData | null;
  isLoading: boolean;
  error: string | null;
  loadDashboard: () => Promise<void>;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  data: null,
  isLoading: false,
  error: null,

  loadDashboard: async () => {
    set({ isLoading: true, error: null });
    try {
      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 300));

      // Use mock data
      set({ data: mockDashboardData, isLoading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to load dashboard',
        isLoading: false
      });
    }
  },
}));
