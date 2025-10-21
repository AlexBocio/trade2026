/**
 * Formatting utility functions for scanner results
 */

export function formatCriteriaName(key: string): string {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (l) => l.toUpperCase());
}

export function formatCriteriaValue(key: string, value: any): string {
  if (typeof value !== 'number') return String(value);

  if (key.includes('return') || key.includes('momentum') || key.includes('pct')) {
    return `${(value * 100).toFixed(1)}%`;
  }
  if (key.includes('volume') || key.includes('surge')) {
    return `${value.toFixed(1)}x`;
  }
  if (key.includes('rsi') || key.includes('score')) {
    return value.toFixed(1);
  }
  return value.toFixed(2);
}

export function getTopRegime(regimeCounts: Record<string, number>): string {
  if (!regimeCounts || Object.keys(regimeCounts).length === 0) {
    return 'N/A';
  }
  return Object.entries(regimeCounts).sort(([, a], [, b]) => b - a)[0][0];
}

export function exportToCSV(results: any[], filename?: string) {
  const headers = [
    'Rank',
    'Symbol',
    'Score',
    'Regime',
    'Alignment',
    'Momentum 20d',
    'Volume Surge',
    'RSI',
  ];

  const rows = results.map((r) => [
    r.rank || 0,
    r.symbol || r.ticker,
    r.composite_score?.toFixed(2) || 0,
    r.regime_hierarchy?.stock?.regime || r.regime || 'N/A',
    r.alignment_score?.toFixed(2) || 0,
    ((r.criteria_scores?.momentum_20d || 0) * 100).toFixed(1),
    r.criteria_scores?.volume_surge?.toFixed(1) || 0,
    r.criteria_scores?.rsi?.toFixed(0) || 0,
  ]);

  const csv = [headers, ...rows].map((row) => row.join(',')).join('\n');

  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename || `scan-results-${new Date().toISOString().split('T')[0]}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

export function checkAlignment(regime1: string, regime2: string): boolean {
  if (!regime1 || !regime2) return false;

  // Simple alignment check - both should be bullish or both bearish
  const bullishRegimes = ['BULL_TRENDING', 'MOMENTUM', 'EXPANSION'];
  const bearishRegimes = ['BEAR_TRENDING', 'CONTRACTION', 'CRISIS'];

  const r1Bullish = bullishRegimes.includes(regime1);
  const r2Bullish = bullishRegimes.includes(regime2);
  const r1Bearish = bearishRegimes.includes(regime1);
  const r2Bearish = bearishRegimes.includes(regime2);

  return (r1Bullish && r2Bullish) || (r1Bearish && r2Bearish);
}
