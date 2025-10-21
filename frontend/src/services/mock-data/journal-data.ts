/**
 * Mock data for Trade Journal
 */

export interface JournalEntry {
  id: string;
  tradeId: string;
  symbol: string;
  entryDate: string;
  exitDate: string;
  entryPrice: number;
  exitPrice: number;
  stopLoss: number;
  profitTarget: number;
  quantity: number;
  pnl: number;
  pnlPct: number;
  riskAmount: number;
  rrRatio: number;
  holdingDays: number;
  exitReason: 'target' | 'stop' | 'time' | 'manual';
  rating: number; // 1-5 stars
  setupQuality: number; // 1-5
  executionQuality: number; // 1-5
  tags: string[];
  notes: string;
  mistakes: string[];
  lessonsLearned: string[];
}

export const mockJournalEntries: JournalEntry[] = [
  {
    id: 'journal-001',
    tradeId: 'trade-342',
    symbol: 'NVAX',
    entryDate: '2025-10-04T09:35:00Z',
    exitDate: '2025-10-07T15:45:00Z',
    entryPrice: 45.20,
    exitPrice: 49.10,
    stopLoss: 42.04,
    profitTarget: 54.24,
    quantity: 500,
    pnl: 9.75,
    pnlPct: 8.6,
    riskAmount: 7.9,
    rrRatio: 2.8,
    holdingDays: 3,
    exitReason: 'target',
    rating: 5,
    setupQuality: 5,
    executionQuality: 4,
    tags: ['momentum', 'small-cap', 'healthcare', 'catalyst'],
    notes:
      'Perfect setup. FDA catalyst drove momentum. Entry was slightly early but managed risk well. Exited at profit target as planned.',
    mistakes: [],
    lessonsLearned: [
      'Catalyst-driven momentum setups work best with tight stops',
      'Taking profits at predetermined targets removes emotion',
    ],
  },
  {
    id: 'journal-002',
    tradeId: 'trade-341',
    symbol: 'SAVA',
    entryDate: '2025-10-06T10:15:00Z',
    exitDate: '2025-10-07T11:30:00Z',
    entryPrice: 12.80,
    exitPrice: 12.35,
    stopLoss: 11.90,
    profitTarget: 15.36,
    quantity: 800,
    pnl: -1.8,
    pnlPct: -3.5,
    riskAmount: 3.6,
    rrRatio: 2.8,
    holdingDays: 1,
    exitReason: 'manual',
    rating: 3,
    setupQuality: 4,
    executionQuality: 2,
    tags: ['momentum', 'small-cap', 'healthcare'],
    notes:
      "Good setup but exited too early due to fear. Stock bounced back after I sold. Need to trust the plan more.",
    mistakes: [
      "Exited before stop was hit - emotional decision",
      "Didn't wait for confirmed breakdown",
      'Position size was too large, causing anxiety',
    ],
    lessonsLearned: [
      "Don't exit early just because of fear",
      'Size positions to avoid emotional trading',
      "Trust the stop loss - that's why it exists",
    ],
  },
  {
    id: 'journal-003',
    tradeId: 'trade-340',
    symbol: 'EFGH',
    entryDate: '2025-10-03T13:20:00Z',
    exitDate: '2025-10-05T10:15:00Z',
    entryPrice: 8.45,
    exitPrice: 9.73,
    stopLoss: 7.84,
    profitTarget: 10.67,
    quantity: 1000,
    pnl: 6.4,
    pnlPct: 15.2,
    riskAmount: 3.05,
    rrRatio: 3.6,
    holdingDays: 2,
    exitReason: 'target',
    rating: 5,
    setupQuality: 5,
    executionQuality: 5,
    tags: ['catalyst', 'biotech', 'FDA', 'small-cap'],
    notes:
      'Clinical trial data release catalyst. Perfect entry at support. Stock gapped up on news and hit target quickly.',
    mistakes: [],
    lessonsLearned: [
      'Biotech catalysts can create explosive moves',
      'Waiting for support confirmation improves entry',
    ],
  },
  {
    id: 'journal-004',
    tradeId: 'trade-339',
    symbol: 'MNOP',
    entryDate: '2025-10-02T09:45:00Z',
    exitDate: '2025-10-02T14:30:00Z',
    entryPrice: 15.60,
    exitPrice: 14.98,
    stopLoss: 14.50,
    profitTarget: 18.20,
    quantity: 600,
    pnl: -1.86,
    pnlPct: -4.0,
    riskAmount: 3.3,
    rrRatio: 2.4,
    holdingDays: 0,
    exitReason: 'stop',
    rating: 4,
    setupQuality: 3,
    executionQuality: 5,
    tags: ['momentum', 'tech', 'earnings'],
    notes:
      'Earnings play that failed. Setup was mediocre in hindsight. Executed stop loss perfectly without hesitation.',
    mistakes: [
      'Setup quality was not high enough - forced trade',
      'Volume was declining before entry',
    ],
    lessonsLearned: [
      'Only take A+ setups, avoid B setups',
      'Proper stop loss execution prevents larger losses',
    ],
  },
  {
    id: 'journal-005',
    tradeId: 'trade-338',
    symbol: 'QRST',
    entryDate: '2025-09-30T10:00:00Z',
    exitDate: '2025-10-01T15:55:00Z',
    entryPrice: 22.40,
    exitPrice: 24.10,
    stopLoss: 20.84,
    profitTarget: 26.96,
    quantity: 400,
    pnl: 3.4,
    pnlPct: 7.6,
    riskAmount: 3.12,
    rrRatio: 2.9,
    holdingDays: 1,
    exitReason: 'time',
    rating: 4,
    setupQuality: 4,
    executionQuality: 4,
    tags: ['breakout', 'volume', 'tech'],
    notes:
      'Breakout above resistance with volume. Exited after 2 days as momentum faded. Good profit but didnt reach full target.',
    mistakes: [],
    lessonsLearned: [
      'Sometimes taking partial profits is better than holding for full target',
    ],
  },
  {
    id: 'journal-006',
    tradeId: 'trade-337',
    symbol: 'UVWX',
    entryDate: '2025-09-28T11:30:00Z',
    exitDate: '2025-09-29T10:15:00Z',
    entryPrice: 6.80,
    exitPrice: 6.32,
    stopLoss: 6.28,
    profitTarget: 8.16,
    quantity: 1200,
    pnl: -2.88,
    pnlPct: -7.1,
    riskAmount: 3.12,
    rrRatio: 2.6,
    holdingDays: 1,
    exitReason: 'stop',
    rating: 2,
    setupQuality: 2,
    executionQuality: 3,
    tags: ['momentum', 'small-cap'],
    notes:
      'Chased the stock after it was already extended. Poor entry. Stop was hit quickly. Classic FOMO trade.',
    mistakes: [
      'Chased momentum instead of waiting for pullback',
      'Entered without proper catalyst',
      'Ignored technical indicators showing overbought',
    ],
    lessonsLearned: [
      'Never chase - wait for pullbacks',
      'FOMO is the enemy of good trading',
      'Stick to the plan, dont improvise',
    ],
  },
];

export interface JournalStats {
  totalTrades: number;
  winRate: number;
  avgRR: number;
  avgWin: number;
  avgLoss: number;
  avgRating: number;
  avgSetupQuality: number;
  avgExecutionQuality: number;
  topTags: Array<{ tag: string; count: number; winRate: number }>;
  commonMistakes: Array<{ mistake: string; count: number }>;
}

export const mockJournalStats: JournalStats = {
  totalTrades: 342,
  winRate: 54.2,
  avgRR: 2.8,
  avgWin: 6.2,
  avgLoss: -1.9,
  avgRating: 3.8,
  avgSetupQuality: 4.1,
  avgExecutionQuality: 3.9,
  topTags: [
    { tag: 'momentum', count: 187, winRate: 56.1 },
    { tag: 'small-cap', count: 289, winRate: 53.8 },
    { tag: 'catalyst', count: 92, winRate: 61.2 },
    { tag: 'healthcare', count: 156, winRate: 52.3 },
  ],
  commonMistakes: [
    { mistake: 'Exited too early', count: 43 },
    { mistake: 'Position size too large', count: 28 },
    { mistake: 'Entered without catalyst', count: 19 },
  ],
};
