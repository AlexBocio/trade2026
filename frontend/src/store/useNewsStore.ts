/**
 * News Store - Manage news feed and articles
 */

import { create } from 'zustand';
import type { NewsArticle, NewsStats } from '../services/mock-data/news-data';
import { mockNewsArticles, mockNewsStats } from '../services/mock-data/news-data';

interface NewsState {
  articles: NewsArticle[];
  stats: NewsStats;
  isLoading: boolean;
  filter: 'all' | 'market' | 'stock' | 'earnings' | 'fda' | 'general' | 'crypto' | 'macro';
  sentiment: 'all' | 'positive' | 'negative' | 'neutral';

  // Actions
  loadNews: () => Promise<void>;
  setFilter: (filter: 'all' | 'market' | 'stock' | 'earnings' | 'fda' | 'general' | 'crypto' | 'macro') => void;
  setSentiment: (sentiment: 'all' | 'positive' | 'negative' | 'neutral') => void;
  refreshNews: () => Promise<void>;
}

export const useNewsStore = create<NewsState>((set, get) => ({
  articles: [],
  stats: mockNewsStats,
  isLoading: false,
  filter: 'all',
  sentiment: 'all',

  loadNews: async () => {
    set({ isLoading: true });
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 500));
    set({ articles: mockNewsArticles, isLoading: false });
  },

  setFilter: (filter) => {
    set({ filter });
  },

  setSentiment: (sentiment) => {
    set({ sentiment });
  },

  refreshNews: async () => {
    set({ isLoading: true });
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 300));
    // In a real app, this would fetch new articles
    set({ isLoading: false });
  },
}));
