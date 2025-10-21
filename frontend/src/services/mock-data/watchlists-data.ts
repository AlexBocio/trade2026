/**
 * Mock data for Watchlists
 */

export interface WatchlistStock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePct: number;
  volume: number;
  marketCap: number;
  sector: string;
  notes?: string;
  addedAt: string;
}

export interface Watchlist {
  id: string;
  name: string;
  description: string;
  color: string;
  stocks: WatchlistStock[];
  createdAt: string;
  updatedAt: string;
  isDefault: boolean;
}

export const mockWatchlists: Watchlist[] = [
  {
    id: 'watchlist-001',
    name: 'Small-Cap Momentum',
    description: 'High-momentum small-cap stocks with strong catalysts',
    color: 'blue',
    isDefault: true,
    createdAt: '2025-09-15T10:00:00Z',
    updatedAt: '2025-10-08T09:30:00Z',
    stocks: [
      {
        symbol: 'NVAX',
        name: 'Novavax Inc',
        price: 49.10,
        change: 3.90,
        changePct: 8.6,
        volume: 12450000,
        marketCap: 31500000,
        sector: 'Healthcare',
        notes: 'FDA catalyst upcoming',
        addedAt: '2025-10-04T09:00:00Z',
      },
      {
        symbol: 'SAVA',
        name: 'Cassava Sciences Inc',
        price: 12.35,
        change: -0.45,
        changePct: -3.5,
        volume: 3200000,
        marketCap: 3900000,
        sector: 'Healthcare',
        notes: 'Watching for support',
        addedAt: '2025-10-06T10:00:00Z',
      },
      {
        symbol: 'EFGH',
        name: 'BioTech Corp',
        price: 9.73,
        change: 1.28,
        changePct: 15.2,
        volume: 5800000,
        marketCap: 6375000,
        sector: 'Healthcare',
        notes: 'Strong breakout',
        addedAt: '2025-10-03T13:00:00Z',
      },
      {
        symbol: 'MNOP',
        name: 'Tech Innovators Inc',
        price: 14.98,
        change: -0.62,
        changePct: -4.0,
        volume: 980000,
        marketCap: 9000000,
        sector: 'Technology',
        addedAt: '2025-10-02T09:00:00Z',
      },
    ],
  },
  {
    id: 'watchlist-002',
    name: 'Biotech Catalysts',
    description: 'Biotech companies with upcoming FDA decisions and trial results',
    color: 'green',
    isDefault: false,
    createdAt: '2025-09-20T14:00:00Z',
    updatedAt: '2025-10-07T11:15:00Z',
    stocks: [
      {
        symbol: 'ABCD',
        name: 'Alpha BioPharm',
        price: 22.40,
        change: 1.70,
        changePct: 7.6,
        volume: 4500000,
        marketCap: 23250000,
        sector: 'Healthcare',
        notes: 'Phase 3 results expected Q4',
        addedAt: '2025-09-30T10:00:00Z',
      },
      {
        symbol: 'WXYZ',
        name: 'Beta Medical',
        price: 18.95,
        change: 0.95,
        changePct: 5.3,
        volume: 2100000,
        marketCap: 13500000,
        sector: 'Healthcare',
        notes: 'FDA approval in 30 days',
        addedAt: '2025-10-01T12:00:00Z',
      },
      {
        symbol: 'QRST',
        name: 'Gamma Therapeutics',
        price: 24.10,
        change: -1.15,
        changePct: -4.5,
        volume: 1650000,
        marketCap: 18000000,
        sector: 'Healthcare',
        notes: 'Watching for entry',
        addedAt: '2025-09-28T15:00:00Z',
      },
    ],
  },
  {
    id: 'watchlist-003',
    name: 'Breakout Candidates',
    description: 'Stocks approaching key resistance levels',
    color: 'purple',
    isDefault: false,
    createdAt: '2025-10-01T09:00:00Z',
    updatedAt: '2025-10-08T08:45:00Z',
    stocks: [
      {
        symbol: 'UVWX',
        name: 'Retail Innovations',
        price: 6.32,
        change: -0.48,
        changePct: -7.1,
        volume: 8900000,
        marketCap: 3375000,
        sector: 'Consumer',
        notes: 'Testing $6.50 resistance',
        addedAt: '2025-09-28T11:00:00Z',
      },
      {
        symbol: 'JKLM',
        name: 'Energy Solutions',
        price: 31.25,
        change: 2.05,
        changePct: 7.0,
        volume: 3400000,
        marketCap: 39000000,
        sector: 'Energy',
        notes: 'Breaking out above $30',
        addedAt: '2025-10-05T14:00:00Z',
      },
    ],
  },
  {
    id: 'watchlist-004',
    name: 'Earnings Plays',
    description: 'Upcoming earnings announcements to watch',
    color: 'yellow',
    isDefault: false,
    createdAt: '2025-10-05T16:00:00Z',
    updatedAt: '2025-10-08T09:00:00Z',
    stocks: [
      {
        symbol: 'NOPQ',
        name: 'Software Giant',
        price: 145.60,
        change: 5.30,
        changePct: 3.8,
        volume: 15600000,
        marketCap: 637500000,
        sector: 'Technology',
        notes: 'Earnings 10/12 after close',
        addedAt: '2025-10-05T16:00:00Z',
      },
      {
        symbol: 'RSTU',
        name: 'Cloud Services Inc',
        price: 78.90,
        change: -2.10,
        changePct: -2.6,
        volume: 7200000,
        marketCap: 135000000,
        sector: 'Technology',
        notes: 'Earnings 10/15 pre-market',
        addedAt: '2025-10-06T09:00:00Z',
      },
    ],
  },
];

export interface WatchlistStats {
  totalWatchlists: number;
  totalStocks: number;
  avgGain: number;
  topGainer: { symbol: string; changePct: number };
  topLoser: { symbol: string; changePct: number };
  mostWatchedSector: string;
}

export const mockWatchlistStats: WatchlistStats = {
  totalWatchlists: 4,
  totalStocks: 11,
  avgGain: 2.4,
  topGainer: { symbol: 'EFGH', changePct: 15.2 },
  topLoser: { symbol: 'UVWX', changePct: -7.1 },
  mostWatchedSector: 'Healthcare',
};
