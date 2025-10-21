/**
 * Scanner mock data - 60 small-cap stocks with patterns and catalysts
 */

export interface Stock {
  symbol: string;
  companyName: string;
  price: number;
  prevPrice: number;
  change: number;
  changeDollar: number;
  volume: number;
  avgVolume: number;
  volumeSurge: number;
  marketCap: number;
  momentumScore: number;
  pattern: string;
  patternConfidence: number;
  catalyst: string | null;
  catalystType: string | null;
  liquidity: number;
  breakoutType: string;
  sector: string;
}

export interface ScannerFilters {
  marketCap: string[];
  priceRange: string[];
  volumeSurge: string[];
  pattern: string[];
}

const patterns = ['Cup & Handle', 'Bull Flag', 'Breakout', 'Triangle', 'Ascending Triangle', 'Head & Shoulders'];
const sectors = ['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer', 'Industrial', 'Biotech'];
const catalystTypes = ['earnings', 'news', 'upgrade', 'contract', 'approval', null];
const catalysts = ['Earnings Beat', 'FDA Approval', 'Analyst Upgrade', 'Major Contract', 'Product Launch', null];
const breakoutTypes = ['52w_high', 'resistance', 'consolidation', 'gap_up'];

function generateStock(index: number): Stock {
  const symbolChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const symbol = Array.from({ length: 4 }, () => symbolChars[Math.floor(Math.random() * 26)]).join('');

  const basePrice = 0.5 + Math.random() * 50;
  const changePercent = (Math.random() - 0.3) * 30; // Bias toward positive
  const changeDollar = basePrice * (changePercent / 100);
  const price = basePrice + changeDollar;

  const avgVolume = 200000 + Math.random() * 1000000;
  const surgeFactor = 2 + Math.random() * 4;
  const volume = avgVolume * surgeFactor;

  const marketCap = 75000 + Math.random() * 3675000;

  const momentumScore = 60 + Math.random() * 40;

  const patternIndex = Math.floor(Math.random() * patterns.length);
  const pattern = patterns[patternIndex];
  const patternConfidence = 70 + Math.random() * 25;

  const catalystIndex = Math.floor(Math.random() * catalysts.length);
  const catalyst = catalysts[catalystIndex];
  const catalystType = catalyst ? catalystTypes[catalystIndex] : null;

  const liquidity = 750 + Math.random() * 15000;

  const breakoutType = breakoutTypes[Math.floor(Math.random() * breakoutTypes.length)];

  const sector = sectors[Math.floor(Math.random() * sectors.length)];

  return {
    symbol,
    companyName: `${symbol} ${sector} Inc.`,
    price,
    prevPrice: basePrice,
    change: changePercent,
    changeDollar,
    volume,
    avgVolume,
    volumeSurge: surgeFactor,
    marketCap,
    momentumScore,
    pattern,
    patternConfidence,
    catalyst,
    catalystType,
    liquidity,
    breakoutType,
    sector,
  };
}

// Generate 60 stocks
export const mockScannerStocks: Stock[] = Array.from({ length: 60 }, (_, i) => generateStock(i));

export const scannerFilters: ScannerFilters = {
  marketCap: ['10M-50M', '50M-100M', '100M-500M', 'All'],
  priceRange: ['0.50-5', '5-20', '20-50', 'All'],
  volumeSurge: ['>2x', '>3x', '>5x', 'All'],
  pattern: ['Cup & Handle', 'Bull Flag', 'Breakout', 'Triangle', 'All'],
};

/**
 * Generate intraday candle data for mini chart
 */
export interface Candle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
}

export function generateIntradayData(symbol: string, basePrice: number): Candle[] {
  const candles: Candle[] = [];
  let price = basePrice * 0.98; // Start slightly lower
  const now = Date.now();

  for (let i = 50; i >= 0; i--) {
    const time = now - (i * 3600000); // 1 hour intervals
    const change = (Math.random() - 0.48) * 0.03; // Slight upward bias
    const open = price;
    price = price * (1 + change);
    const close = price;
    const high = Math.max(open, close) * (1 + Math.random() * 0.01);
    const low = Math.min(open, close) * (1 - Math.random() * 0.01);

    candles.push({
      time: Math.floor(time / 1000),
      open,
      high,
      low,
      close
    });
  }

  return candles;
}

/**
 * Simulate price update for live feed
 */
export function simulatePriceUpdate(stock: Stock): Stock {
  const volatility = 0.002; // 0.2% max change per update
  const priceChange = (Math.random() - 0.5) * volatility;
  const newPrice = stock.price * (1 + priceChange);
  const newChange = ((newPrice - stock.prevPrice) / stock.prevPrice) * 100;

  // Update momentum score slightly
  const momentumChange = (Math.random() - 0.5) * 0.5;
  const newMomentum = Math.max(0, Math.min(100, stock.momentumScore + momentumChange));

  return {
    ...stock,
    price: newPrice,
    change: newChange,
    changeDollar: newPrice - stock.prevPrice,
    momentumScore: newMomentum,
  };
}
