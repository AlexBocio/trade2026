/**
 * Strategy state management using Zustand
 */

import { create } from 'zustand';
import type { Strategy, Backtest, StrategyTemplate } from '../types/strategy.types';
import { mockStrategies, mockStrategyTrades, type StrategyExtended, type Trade } from '../services/mock-data/strategy-data';

interface StrategyState {
  // Data
  strategies: StrategyExtended[];
  backtests: Backtest[];
  templates: StrategyTemplate[];
  selectedStrategy: StrategyExtended | null;
  selectedBacktest: Backtest | null;
  strategyTrades: Trade[];

  // Filters
  statusFilter: string;
  searchQuery: string;

  // Loading states
  loadingStrategies: boolean;
  loadingBacktests: boolean;
  loadingTemplates: boolean;
  loadingStrategy: boolean;

  // Actions
  fetchStrategies: () => Promise<void>;
  fetchStrategy: (id: string) => Promise<void>;
  fetchStrategyTrades: (id: string) => Promise<void>;
  fetchBacktests: () => Promise<void>;
  fetchTemplates: () => Promise<void>;
  selectStrategy: (strategy: StrategyExtended | null) => void;
  selectBacktest: (backtest: Backtest | null) => void;
  setStatusFilter: (status: string) => void;
  setSearchQuery: (query: string) => void;
  createStrategy: (strategy: Omit<Strategy, 'id' | 'createdAt' | 'updatedAt'>) => Promise<Strategy>;
  updateStrategy: (id: string, updates: Partial<Strategy>) => Promise<void>;
  deleteStrategy: (id: string) => Promise<void>;
  deployStrategy: (id: string) => Promise<void>;
  retireStrategy: (id: string) => Promise<void>;
  createBacktest: (backtest: Omit<Backtest, 'id' | 'createdAt'>) => Promise<Backtest>;
}

export const useStrategyStore = create<StrategyState>((set, get) => ({
  // Initial state
  strategies: [],
  backtests: [],
  templates: [],
  selectedStrategy: null,
  selectedBacktest: null,
  strategyTrades: [],
  statusFilter: 'all',
  searchQuery: '',
  loadingStrategies: false,
  loadingBacktests: false,
  loadingTemplates: false,
  loadingStrategy: false,

  // Actions
  fetchStrategies: async () => {
    set({ loadingStrategies: true });
    try {
      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 300));
      set({ strategies: mockStrategies, loadingStrategies: false });
    } catch (error) {
      console.error('Failed to fetch strategies:', error);
      set({ loadingStrategies: false });
    }
  },

  fetchStrategy: async (id: string) => {
    set({ loadingStrategy: true });
    try {
      await new Promise((resolve) => setTimeout(resolve, 200));
      const strategy = mockStrategies.find((s) => s.id === id);
      set({ selectedStrategy: strategy || null, loadingStrategy: false });
    } catch (error) {
      console.error('Failed to fetch strategy:', error);
      set({ loadingStrategy: false });
    }
  },

  fetchStrategyTrades: async (id: string) => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 200));
      const trades = mockStrategyTrades[id] || [];
      set({ strategyTrades: trades });
    } catch (error) {
      console.error('Failed to fetch strategy trades:', error);
    }
  },

  fetchBacktests: async () => {
    set({ loadingBacktests: true });
    try {
      await new Promise((resolve) => setTimeout(resolve, 300));
      // Would fetch from API
      set({ loadingBacktests: false });
    } catch (error) {
      console.error('Failed to fetch backtests:', error);
      set({ loadingBacktests: false });
    }
  },

  fetchTemplates: async () => {
    set({ loadingTemplates: true });
    try {
      await new Promise((resolve) => setTimeout(resolve, 300));
      // Would fetch from API
      set({ loadingTemplates: false });
    } catch (error) {
      console.error('Failed to fetch templates:', error);
      set({ loadingTemplates: false });
    }
  },

  selectStrategy: (strategy) => set({ selectedStrategy: strategy }),

  selectBacktest: (backtest) => set({ selectedBacktest: backtest }),

  setStatusFilter: (status) => set({ statusFilter: status }),

  setSearchQuery: (query) => set({ searchQuery: query }),

  createStrategy: async (strategy) => {
    try {
      // Would call API
      const newStrategy: any = {
        ...strategy,
        id: `strat-${Date.now()}`,
        version: '1.0.0',
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      set((state) => ({ strategies: [...state.strategies, newStrategy] }));
      return newStrategy;
    } catch (error) {
      console.error('Failed to create strategy:', error);
      throw error;
    }
  },

  updateStrategy: async (id, updates) => {
    try {
      // Would call API
      set((state) => ({
        strategies: state.strategies.map((s) =>
          s.id === id ? { ...s, ...updates, updatedAt: new Date() } : s
        ),
      }));
    } catch (error) {
      console.error('Failed to update strategy:', error);
      throw error;
    }
  },

  deleteStrategy: async (id) => {
    try {
      // Would call API
      set((state) => ({
        strategies: state.strategies.filter((s) => s.id !== id),
        selectedStrategy: state.selectedStrategy?.id === id ? null : state.selectedStrategy,
      }));
    } catch (error) {
      console.error('Failed to delete strategy:', error);
      throw error;
    }
  },

  deployStrategy: async (id) => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 500));
      set((state) => ({
        strategies: state.strategies.map((s) =>
          s.id === id ? { ...s, status: 'LIVE' as const, deployedAt: new Date() } : s
        ),
      }));
    } catch (error) {
      console.error('Failed to deploy strategy:', error);
      throw error;
    }
  },

  retireStrategy: async (id) => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 500));
      set((state) => ({
        strategies: state.strategies.map((s) =>
          s.id === id ? { ...s, status: 'STOPPED' as const } : s
        ),
      }));
    } catch (error) {
      console.error('Failed to retire strategy:', error);
      throw error;
    }
  },

  createBacktest: async (backtest) => {
    try {
      // Would call API
      const newBacktest: any = {
        ...backtest,
        id: `bt-${Date.now()}`,
        createdAt: new Date(),
      };
      set((state) => ({ backtests: [...state.backtests, newBacktest] }));
      return newBacktest;
    } catch (error) {
      console.error('Failed to create backtest:', error);
      throw error;
    }
  },
}));
