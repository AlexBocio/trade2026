/**
 * Mock data for News Feed
 */

export interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  source: string;
  author?: string;
  url: string;
  publishedAt: string;
  category: 'market' | 'stock' | 'earnings' | 'fda' | 'general' | 'crypto' | 'macro';
  sentiment: 'positive' | 'negative' | 'neutral';
  symbols: string[];
  imageUrl?: string;
  tags: string[];
  isBreaking: boolean;
}

export const mockNewsArticles: NewsArticle[] = [
  {
    id: 'news-001',
    title: 'FDA Approves New Treatment from Novavax',
    summary:
      'The FDA has granted approval for Novavax\'s latest vaccine formulation, marking a significant milestone for the biotech company. Analysts expect this to drive revenue growth in Q4 2025.',
    source: 'BioPharma Today',
    author: 'Dr. Sarah Chen',
    url: 'https://example.com/news/nvax-fda-approval',
    publishedAt: '2025-10-08T08:30:00Z',
    category: 'fda',
    sentiment: 'positive',
    symbols: ['NVAX'],
    imageUrl: 'https://picsum.photos/seed/nvax/400/300',
    tags: ['FDA', 'Approval', 'Vaccine', 'Healthcare'],
    isBreaking: true,
  },
  {
    id: 'news-002',
    title: 'Small-Cap Biotech Stocks Rally on Positive Trial Data',
    summary:
      'Multiple small-cap biotech companies saw significant gains today as positive Phase 3 trial data boosted investor confidence in the sector. Healthcare remains a hot area for momentum traders.',
    source: 'Market Watch',
    author: 'John Martinez',
    url: 'https://example.com/news/biotech-rally',
    publishedAt: '2025-10-08T07:15:00Z',
    category: 'stock',
    sentiment: 'positive',
    symbols: ['SAVA', 'EFGH', 'ABCD'],
    imageUrl: 'https://picsum.photos/seed/biotech/400/300',
    tags: ['Biotech', 'Small-Cap', 'Rally', 'Healthcare'],
    isBreaking: false,
  },
  {
    id: 'news-003',
    title: 'Tech Sector Faces Volatility Amid Fed Rate Decision',
    summary:
      'Technology stocks experienced heightened volatility following the Federal Reserve\'s latest interest rate announcement. Traders are reassessing positions as macro conditions shift.',
    source: 'Financial Times',
    author: 'Emily Thompson',
    url: 'https://example.com/news/tech-volatility',
    publishedAt: '2025-10-08T06:00:00Z',
    category: 'macro',
    sentiment: 'negative',
    symbols: ['MNOP', 'NOPQ', 'RSTU'],
    tags: ['Fed', 'Interest Rates', 'Technology', 'Macro'],
    isBreaking: false,
  },
  {
    id: 'news-004',
    title: 'SAVA Announces Unexpected Leadership Change',
    summary:
      'Cassava Sciences announced today that its CEO will be stepping down effective immediately. The company has named an interim replacement while conducting a search for permanent leadership.',
    source: 'Bloomberg',
    url: 'https://example.com/news/sava-leadership',
    publishedAt: '2025-10-07T16:45:00Z',
    category: 'stock',
    sentiment: 'negative',
    symbols: ['SAVA'],
    tags: ['Leadership', 'Management', 'Biotech'],
    isBreaking: false,
  },
  {
    id: 'news-005',
    title: 'Q3 Earnings Season Kicks Off with Strong Results',
    summary:
      'Major tech companies are reporting better-than-expected Q3 earnings, setting a positive tone for the season. Analysts are optimistic about continued growth in the sector.',
    source: 'CNBC',
    author: 'Mike Roberts',
    url: 'https://example.com/news/q3-earnings',
    publishedAt: '2025-10-07T14:30:00Z',
    category: 'earnings',
    sentiment: 'positive',
    symbols: ['NOPQ', 'RSTU'],
    tags: ['Earnings', 'Q3', 'Technology'],
    isBreaking: false,
  },
  {
    id: 'news-006',
    title: 'Small-Cap Stock EFGH Surges on Merger Announcement',
    summary:
      'BioTech Corp (EFGH) shares jumped 15% after announcing a merger agreement with a larger competitor. The deal is expected to close in Q1 2026 pending regulatory approval.',
    source: 'Reuters',
    url: 'https://example.com/news/efgh-merger',
    publishedAt: '2025-10-07T11:00:00Z',
    category: 'stock',
    sentiment: 'positive',
    symbols: ['EFGH'],
    tags: ['M&A', 'Merger', 'Biotech'],
    isBreaking: false,
  },
  {
    id: 'news-007',
    title: 'Market Volatility Expected as FOMC Meeting Approaches',
    summary:
      'Traders are bracing for increased volatility ahead of next week\'s Federal Open Market Committee meeting. Options activity suggests uncertainty about the Fed\'s next move.',
    source: 'Wall Street Journal',
    author: 'David Kim',
    url: 'https://example.com/news/fomc-volatility',
    publishedAt: '2025-10-07T09:00:00Z',
    category: 'macro',
    sentiment: 'neutral',
    symbols: [],
    tags: ['FOMC', 'Fed', 'Volatility', 'Options'],
    isBreaking: false,
  },
  {
    id: 'news-008',
    title: 'Energy Sector Breaks Out to New Highs',
    summary:
      'Energy stocks are reaching new 52-week highs as oil prices stabilize and demand forecasts improve. Analysts see continued strength in the sector heading into winter.',
    source: 'Energy News',
    url: 'https://example.com/news/energy-breakout',
    publishedAt: '2025-10-06T15:20:00Z',
    category: 'stock',
    sentiment: 'positive',
    symbols: ['JKLM'],
    tags: ['Energy', 'Breakout', 'Oil'],
    isBreaking: false,
  },
  {
    id: 'news-009',
    title: 'FDA Panel to Review Multiple Drug Applications Next Month',
    summary:
      'The FDA has scheduled advisory panel meetings for several biotech companies next month. Traders are closely watching these dates for potential catalysts.',
    source: 'BioPharma Today',
    author: 'Dr. Sarah Chen',
    url: 'https://example.com/news/fda-panel',
    publishedAt: '2025-10-06T12:00:00Z',
    category: 'fda',
    sentiment: 'neutral',
    symbols: ['NVAX', 'ABCD', 'WXYZ'],
    tags: ['FDA', 'Catalyst', 'Advisory Panel'],
    isBreaking: false,
  },
  {
    id: 'news-010',
    title: 'Retail Sector Shows Signs of Weakness in Consumer Spending',
    summary:
      'Recent data suggests consumers are pulling back on discretionary spending, putting pressure on retail stocks. Analysts are watching upcoming earnings reports closely.',
    source: 'Market Insider',
    url: 'https://example.com/news/retail-weakness',
    publishedAt: '2025-10-06T10:00:00Z',
    category: 'market',
    sentiment: 'negative',
    symbols: ['UVWX'],
    tags: ['Retail', 'Consumer', 'Earnings'],
    isBreaking: false,
  },
];

export interface NewsStats {
  totalArticles: number;
  breakingNews: number;
  positiveNews: number;
  negativeNews: number;
  neutralNews: number;
  mostMentionedSymbol: string;
  topCategory: string;
}

export const mockNewsStats: NewsStats = {
  totalArticles: 127,
  breakingNews: 3,
  positiveNews: 68,
  negativeNews: 34,
  neutralNews: 25,
  mostMentionedSymbol: 'NVAX',
  topCategory: 'Stock News',
};
