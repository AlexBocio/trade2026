/**
 * Watchlists Store - Manage watchlists and tracked stocks
 */

import { create } from 'zustand';
import type { Watchlist, WatchlistStock, WatchlistStats } from '../services/mock-data/watchlists-data';
import { mockWatchlists, mockWatchlistStats } from '../services/mock-data/watchlists-data';

interface WatchlistsState {
  watchlists: Watchlist[];
  selectedWatchlist: string | null;
  stats: WatchlistStats;
  isLoading: boolean;

  // Actions
  loadWatchlists: () => Promise<void>;
  getWatchlist: (id: string) => Watchlist | null;
  createWatchlist: (watchlist: Omit<Watchlist, 'id' | 'createdAt' | 'updatedAt' | 'stocks'>) => Promise<void>;
  updateWatchlist: (id: string, updates: Partial<Watchlist>) => Promise<void>;
  deleteWatchlist: (id: string) => Promise<void>;
  selectWatchlist: (id: string | null) => void;

  // Stock actions
  addStock: (watchlistId: string, stock: Omit<WatchlistStock, 'addedAt'>) => Promise<void>;
  removeStock: (watchlistId: string, symbol: string) => Promise<void>;
  updateStockNotes: (watchlistId: string, symbol: string, notes: string) => Promise<void>;
}

export const useWatchlistsStore = create<WatchlistsState>((set, get) => ({
  watchlists: [],
  selectedWatchlist: null,
  stats: mockWatchlistStats,
  isLoading: false,

  loadWatchlists: async () => {
    set({ isLoading: true });
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 500));
    set({
      watchlists: mockWatchlists,
      isLoading: false,
      selectedWatchlist: mockWatchlists[0]?.id || null
    });
  },

  getWatchlist: (id) => {
    return get().watchlists.find((w) => w.id === id) || null;
  },

  createWatchlist: async (watchlistData) => {
    const newWatchlist: Watchlist = {
      id: `watchlist-${Date.now()}`,
      ...watchlistData,
      stocks: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    await new Promise((resolve) => setTimeout(resolve, 200));
    set((state) => ({
      watchlists: [newWatchlist, ...state.watchlists],
      stats: {
        ...state.stats,
        totalWatchlists: state.stats.totalWatchlists + 1,
      },
    }));
  },

  updateWatchlist: async (id, updates) => {
    await new Promise((resolve) => setTimeout(resolve, 200));
    set((state) => ({
      watchlists: state.watchlists.map((w) =>
        w.id === id ? { ...w, ...updates, updatedAt: new Date().toISOString() } : w
      ),
    }));
  },

  deleteWatchlist: async (id) => {
    const watchlist = get().getWatchlist(id);
    if (!watchlist) return;

    await new Promise((resolve) => setTimeout(resolve, 200));
    set((state) => ({
      watchlists: state.watchlists.filter((w) => w.id !== id),
      selectedWatchlist: state.selectedWatchlist === id ? null : state.selectedWatchlist,
      stats: {
        ...state.stats,
        totalWatchlists: state.stats.totalWatchlists - 1,
        totalStocks: state.stats.totalStocks - watchlist.stocks.length,
      },
    }));
  },

  selectWatchlist: (id) => {
    set({ selectedWatchlist: id });
  },

  addStock: async (watchlistId, stockData) => {
    const newStock: WatchlistStock = {
      ...stockData,
      addedAt: new Date().toISOString(),
    };

    await new Promise((resolve) => setTimeout(resolve, 200));
    set((state) => ({
      watchlists: state.watchlists.map((w) =>
        w.id === watchlistId
          ? {
              ...w,
              stocks: [newStock, ...w.stocks],
              updatedAt: new Date().toISOString(),
            }
          : w
      ),
      stats: {
        ...state.stats,
        totalStocks: state.stats.totalStocks + 1,
      },
    }));
  },

  removeStock: async (watchlistId, symbol) => {
    await new Promise((resolve) => setTimeout(resolve, 200));
    set((state) => ({
      watchlists: state.watchlists.map((w) =>
        w.id === watchlistId
          ? {
              ...w,
              stocks: w.stocks.filter((s) => s.symbol !== symbol),
              updatedAt: new Date().toISOString(),
            }
          : w
      ),
      stats: {
        ...state.stats,
        totalStocks: state.stats.totalStocks - 1,
      },
    }));
  },

  updateStockNotes: async (watchlistId, symbol, notes) => {
    await new Promise((resolve) => setTimeout(resolve, 100));
    set((state) => ({
      watchlists: state.watchlists.map((w) =>
        w.id === watchlistId
          ? {
              ...w,
              stocks: w.stocks.map((s) =>
                s.symbol === symbol ? { ...s, notes } : s
              ),
              updatedAt: new Date().toISOString(),
            }
          : w
      ),
    }));
  },
}));
