/**
 * Trade Setup Card Component
 * Generates and displays trade recommendations based on regime and criteria
 */

import React from 'react';

interface TradeSetup {
  entry: string;
  stop: string;
  target: string;
  rr: number;
  rationale: string;
  positionSize?: string;
  timeframe?: string;
}

interface TradeSetupCardProps {
  stock: any;
}

function generateTradeSetup(stock: any): TradeSetup {
  // Default current price (would be fetched from API)
  const currentPrice = stock.price || 150;

  // Calculate ATR-based stops and targets
  const atr = (stock.criteria_scores?.atr_pct || 0.02) * currentPrice;
  const stopMultiplier = 2;
  const targetMultiplier = 3;

  const entry = currentPrice;
  const stop = currentPrice - stopMultiplier * atr;
  const target = currentPrice + targetMultiplier * atr;
  const rr = targetMultiplier / stopMultiplier;

  // Generate rationale based on regime and alignment
  const regime = stock.regime_hierarchy?.stock?.regime || stock.primary_regime || 'NEUTRAL';
  const alignment = stock.alignment_score || 5;

  let rationale = `${stock.symbol || stock.ticker} is in ${regime.replace(
    '_',
    ' '
  ).toLowerCase()} regime`;

  if (alignment >= 7) {
    rationale += ` with strong alignment (${alignment.toFixed(
      1
    )}/10 across all layers). This setup offers favorable risk/reward`;
  } else if (alignment >= 5) {
    rationale += ` with moderate alignment (${alignment.toFixed(
      1
    )}/10). Consider reducing position size`;
  } else {
    rationale += ` with weak alignment (${alignment.toFixed(
      1
    )}/10). High risk setup, use tight stops`;
  }

  rationale += `. Entry at current levels with ${stopMultiplier} ATR stop ($${stop.toFixed(
    2
  )}) and ${targetMultiplier} ATR target ($${target.toFixed(2)}).`;

  return {
    entry: entry.toFixed(2),
    stop: stop.toFixed(2),
    target: target.toFixed(2),
    rr,
    rationale,
    positionSize: calculatePositionSize(currentPrice, stop, alignment),
    timeframe: determineTimeframe(stock),
  };
}

function calculatePositionSize(entry: number, stop: number, alignment: number): string {
  // Simple position sizing: higher alignment = larger position
  const riskPct = alignment >= 7 ? 2 : alignment >= 5 ? 1 : 0.5;
  const dollarRisk = (entry - stop) * 100; // Assume $10k account
  const shares = Math.floor((100 * riskPct) / (entry - stop));
  return `${shares} shares (~${riskPct}% risk)`;
}

function determineTimeframe(stock: any): string {
  const momentum = stock.criteria_scores?.momentum_20d || 0;
  if (Math.abs(momentum) > 0.15) return 'Swing (1-4 weeks)';
  if (Math.abs(momentum) > 0.08) return 'Position (1-3 months)';
  return 'Short-term (Days)';
}

export default function TradeSetupCard({ stock }: TradeSetupCardProps) {
  const setup = generateTradeSetup(stock);

  return (
    <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-700/50 rounded-lg p-4">
      <div className="flex items-center space-x-2 mb-3">
        <span className="text-2xl">💡</span>
        <h4 className="text-white font-semibold">Suggested Trade Setup</h4>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div>
          <div className="text-xs text-gray-400 mb-1">Entry</div>
          <div className="text-green-400 font-semibold text-lg">${setup.entry}</div>
        </div>

        <div>
          <div className="text-xs text-gray-400 mb-1">Stop Loss</div>
          <div className="text-red-400 font-semibold text-lg">${setup.stop}</div>
        </div>

        <div>
          <div className="text-xs text-gray-400 mb-1">Target</div>
          <div className="text-blue-400 font-semibold text-lg">${setup.target}</div>
        </div>

        <div>
          <div className="text-xs text-gray-400 mb-1">Risk/Reward</div>
          <div className="text-white font-semibold text-lg">{setup.rr.toFixed(1)}:1</div>
        </div>
      </div>

      {setup.positionSize && (
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-gray-800/50 rounded p-2">
            <div className="text-xs text-gray-400 mb-1">Position Size</div>
            <div className="text-white text-sm font-semibold">{setup.positionSize}</div>
          </div>
          <div className="bg-gray-800/50 rounded p-2">
            <div className="text-xs text-gray-400 mb-1">Timeframe</div>
            <div className="text-white text-sm font-semibold">{setup.timeframe}</div>
          </div>
        </div>
      )}

      <div className="pt-3 border-t border-gray-700">
        <div className="text-xs text-gray-400 mb-1">Rationale:</div>
        <p className="text-sm text-gray-300 leading-relaxed">{setup.rationale}</p>
      </div>

      <div className="mt-3 pt-3 border-t border-gray-700 flex items-center justify-between text-xs text-gray-400">
        <span>⚠️ Not financial advice</span>
        <span>Always manage your risk</span>
      </div>
    </div>
  );
}
