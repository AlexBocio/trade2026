/**
 * Analytics Store - State management for analytics and research workbench
 */

import { create } from 'zustand';

interface AnalysisRecord {
  id: string;
  type: 'factors' | 'stats' | 'regime' | 'seasonality' | 'distribution' | 'hypothesis' | 'indicators';
  title: string;
  createdAt: string;
  significant: boolean;
  pValue?: number;
}

interface AnalyticsState {
  recentAnalyses: AnalysisRecord[];
  loadRecentAnalyses: () => Promise<void>;
}

export const useAnalyticsStore = create<AnalyticsState>((set) => ({
  recentAnalyses: [],

  loadRecentAnalyses: async () => {
    // Mock recent analyses
    const mockAnalyses: AnalysisRecord[] = [
      {
        id: '1',
        type: 'factors',
        title: 'Factor Analysis: Momentum vs Value',
        createdAt: '2025-10-05T10:00:00Z',
        significant: true,
        pValue: 0.001,
      },
      {
        id: '2',
        type: 'seasonality',
        title: 'Seasonality: Best Days to Trade',
        createdAt: '2025-10-03T14:30:00Z',
        significant: true,
        pValue: 0.012,
      },
      {
        id: '3',
        type: 'distribution',
        title: 'Distribution: Returns Analysis NVAX',
        createdAt: '2025-10-01T09:15:00Z',
        significant: false,
        pValue: 0.234,
      },
      {
        id: '4',
        type: 'regime',
        title: 'Market Regime: Bull/Bear Detection',
        createdAt: '2025-09-28T16:45:00Z',
        significant: true,
        pValue: 0.003,
      },
      {
        id: '5',
        type: 'hypothesis',
        title: 'Hypothesis Test: Strategy A vs B',
        createdAt: '2025-09-25T11:20:00Z',
        significant: false,
        pValue: 0.156,
      },
    ];

    set({ recentAnalyses: mockAnalyses });
  },
}));
