/**
 * Trade Journal Store - Manage journal entries and analytics
 */

import { create } from 'zustand';
import type { JournalEntry, JournalStats } from '../services/mock-data/journal-data';
import { mockJournalEntries, mockJournalStats } from '../services/mock-data/journal-data';

interface JournalFilters {
  dateRange: { start: Date; end: Date } | null;
  tags: string[];
  exitReason: 'target' | 'stop' | 'time' | 'manual' | null;
  minRating: number | null;
}

interface JournalState {
  entries: JournalEntry[];
  filters: JournalFilters;
  stats: JournalStats;
  isLoading: boolean;

  // Actions
  loadEntries: () => Promise<void>;
  getEntry: (id: string) => JournalEntry | null;
  createEntry: (tradeId: string, partialEntry: Partial<JournalEntry>) => Promise<void>;
  updateEntry: (id: string, updates: Partial<JournalEntry>) => Promise<void>;
  deleteEntry: (id: string) => Promise<void>;
  setFilters: (filters: Partial<JournalFilters>) => void;
  resetFilters: () => void;
}

export const useJournalStore = create<JournalState>((set, get) => ({
  entries: [],
  filters: {
    dateRange: null,
    tags: [],
    exitReason: null,
    minRating: null,
  },
  stats: mockJournalStats,
  isLoading: false,

  loadEntries: async () => {
    set({ isLoading: true });
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 500));
    set({ entries: mockJournalEntries, isLoading: false });
  },

  getEntry: (id) => {
    return get().entries.find((e) => e.id === id) || null;
  },

  createEntry: async (tradeId, partialEntry) => {
    const newEntry: JournalEntry = {
      id: `journal-${Date.now()}`,
      tradeId,
      symbol: partialEntry.symbol || '',
      entryDate: partialEntry.entryDate || new Date().toISOString(),
      exitDate: partialEntry.exitDate || new Date().toISOString(),
      entryPrice: partialEntry.entryPrice || 0,
      exitPrice: partialEntry.exitPrice || 0,
      stopLoss: partialEntry.stopLoss || 0,
      profitTarget: partialEntry.profitTarget || 0,
      quantity: partialEntry.quantity || 0,
      pnl: partialEntry.pnl || 0,
      pnlPct: partialEntry.pnlPct || 0,
      riskAmount: partialEntry.riskAmount || 0,
      rrRatio: partialEntry.rrRatio || 0,
      holdingDays: partialEntry.holdingDays || 0,
      exitReason: partialEntry.exitReason || 'manual',
      rating: 0,
      setupQuality: 0,
      executionQuality: 0,
      tags: [],
      notes: '',
      mistakes: [],
      lessonsLearned: [],
    };

    set((state) => ({
      entries: [newEntry, ...state.entries],
    }));
  },

  updateEntry: async (id, updates) => {
    await new Promise((resolve) => setTimeout(resolve, 200));
    set((state) => ({
      entries: state.entries.map((e) => (e.id === id ? { ...e, ...updates } : e)),
    }));
  },

  deleteEntry: async (id) => {
    await new Promise((resolve) => setTimeout(resolve, 200));
    set((state) => ({
      entries: state.entries.filter((e) => e.id !== id),
    }));
  },

  setFilters: (filters) => {
    set((state) => ({
      filters: { ...state.filters, ...filters },
    }));
  },

  resetFilters: () => {
    set({
      filters: {
        dateRange: null,
        tags: [],
        exitReason: null,
        minRating: null,
      },
    });
  },
}));
