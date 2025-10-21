/**
 * Portfolio Store - Manages portfolio data and state
 */

import { create } from 'zustand';
import { mockPortfolioData } from '../services/mock-data/portfolio-risk-data';

interface PortfolioState {
  data: typeof mockPortfolioData | null;
  isLoading: boolean;
  error: string | null;
  loadPortfolio: () => Promise<void>;
  refreshPortfolio: () => Promise<void>;
}

export const usePortfolioStore = create<PortfolioState>((set, get) => ({
  data: null,
  isLoading: false,
  error: null,

  loadPortfolio: async () => {
    set({ isLoading: true, error: null });

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      set({
        data: mockPortfolioData,
        isLoading: false,
      });
    } catch (error) {
      set({
        error: 'Failed to load portfolio data',
        isLoading: false,
      });
    }
  },

  refreshPortfolio: async () => {
    const currentData = get().data;
    if (!currentData) return;

    try {
      // Simulate real-time price updates
      await new Promise((resolve) => setTimeout(resolve, 100));

      const updatedData = { ...currentData };

      // Simulate small price changes
      updatedData.positions = updatedData.positions.map((pos) => {
        if (pos.symbol === 'Cash') return pos;

        const priceChange = (Math.random() - 0.5) * 0.5; // +/- 0.25
        const newPrice = pos.currentPrice + priceChange;
        const newValue = newPrice * pos.quantity;
        const newPnL = (newPrice - pos.entryPrice) * pos.quantity;
        const newPnLPct = ((newPrice - pos.entryPrice) / pos.entryPrice) * 100;

        return {
          ...pos,
          currentPrice: newPrice,
          value: newValue,
          pnl: newPnL,
          pnlPct: newPnLPct,
        };
      });

      // Recalculate account value
      const totalValue = updatedData.positions.reduce((sum, pos) => sum + pos.value, 0);
      const totalPnL = updatedData.positions.reduce((sum, pos) => sum + pos.pnl, 0);

      updatedData.summary.accountValue = totalValue;
      updatedData.summary.totalPnL = totalPnL;
      updatedData.summary.totalPnLPct = (totalPnL / (totalValue - totalPnL)) * 100;

      set({ data: updatedData });
    } catch (error) {
      console.error('Failed to refresh portfolio:', error);
    }
  },
}));
