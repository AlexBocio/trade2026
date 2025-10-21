/**
 * Scanner state management using Zustand
 */

import { create } from 'zustand';
import type { Stock } from '../services/mock-data/scanner-data';
import { mockScannerStocks, simulatePriceUpdate } from '../services/mock-data/scanner-data';

interface Filters {
  marketCap: string;
  priceRange: string;
  volumeSurge: string;
  pattern: string;
}

interface ScannerState {
  // Data
  stocks: Stock[];
  selectedStock: Stock | null;
  filters: Filters;
  isLoading: boolean;

  // Actions
  loadScanner: () => Promise<void>;
  applyFilters: (filters: Partial<Filters>) => void;
  selectStock: (symbol: string | null) => void;
  updatePrices: () => void;
}

export const useScannerStore = create<ScannerState>((set, get) => ({
  // Initial state
  stocks: [],
  selectedStock: null,
  filters: {
    marketCap: 'All',
    priceRange: 'All',
    volumeSurge: 'All',
    pattern: 'All',
  },
  isLoading: false,

  // Actions
  loadScanner: async () => {
    set({ isLoading: true });
    try {
      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 300));
      set({ stocks: mockScannerStocks, isLoading: false });
    } catch (error) {
      console.error('Failed to load scanner:', error);
      set({ isLoading: false });
    }
  },

  applyFilters: (newFilters) => {
    set((state) => ({
      filters: {
        ...state.filters,
        ...newFilters,
      },
    }));
  },

  selectStock: (symbol) => {
    const stock = symbol ? get().stocks.find((s) => s.symbol === symbol) : null;
    set({ selectedStock: stock || null });
  },

  updatePrices: () => {
    set((state) => ({
      stocks: state.stocks.map((stock) => simulatePriceUpdate(stock)),
    }));
  },
}));
