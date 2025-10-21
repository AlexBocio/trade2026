/**
 * Database state management using Zustand
 */

import { create } from 'zustand';
import type { DatabaseTable } from '../types/database.types';
import type { DatabaseOverview, TierOverview } from '../services/mock-data/database-data';
import {
  mockDatabaseOverview,
  mockDatabaseTables,
  generateMockTicksData,
  generateMockOHLCVData,
} from '../services/mock-data/database-data';

interface DatabaseState {
  // Data
  overview: DatabaseOverview | null;
  selectedTier: 'hot' | 'warm' | 'cold' | null;
  selectedTable: DatabaseTable | null;
  queryResults: any[] | null;
  isLoading: boolean;

  // Actions
  loadOverview: () => Promise<void>;
  loadTier: (tier: 'hot' | 'warm' | 'cold') => Promise<void>;
  loadTable: (tier: string, tableName: string) => Promise<void>;
  executeQuery: (tier: string, sql: string) => Promise<void>;
}

export const useDatabaseStore = create<DatabaseState>((set, get) => ({
  // Initial state
  overview: null,
  selectedTier: null,
  selectedTable: null,
  queryResults: null,
  isLoading: false,

  // Actions
  loadOverview: async () => {
    set({ isLoading: true });
    try {
      await new Promise((resolve) => setTimeout(resolve, 300));
      set({ overview: mockDatabaseOverview, isLoading: false });
    } catch (error) {
      console.error('Failed to load database overview:', error);
      set({ isLoading: false });
    }
  },

  loadTier: async (tier) => {
    set({ isLoading: true, selectedTier: tier });
    try {
      await new Promise((resolve) => setTimeout(resolve, 200));
      set({ isLoading: false });
    } catch (error) {
      console.error('Failed to load tier:', error);
      set({ isLoading: false });
    }
  },

  loadTable: async (tier, tableName) => {
    set({ isLoading: true });
    try {
      await new Promise((resolve) => setTimeout(resolve, 200));
      const table = mockDatabaseTables.find(
        (t) => t.name === tableName && t.tier.toLowerCase() === tier.toLowerCase()
      );
      set({ selectedTable: table || null, isLoading: false });
    } catch (error) {
      console.error('Failed to load table:', error);
      set({ isLoading: false });
    }
  },

  executeQuery: async (tier, sql) => {
    set({ isLoading: true });
    try {
      // Simulate query execution
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Parse SQL to determine which data to return
      if (sql.toLowerCase().includes('ticks')) {
        const results = generateMockTicksData(100);
        set({ queryResults: results, isLoading: false });
      } else if (sql.toLowerCase().includes('ohlcv')) {
        const results = generateMockOHLCVData(100);
        set({ queryResults: results, isLoading: false });
      } else {
        set({ queryResults: [], isLoading: false });
      }
    } catch (error) {
      console.error('Failed to execute query:', error);
      set({ queryResults: [], isLoading: false });
    }
  },
}));
