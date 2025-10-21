/**
 * Top Winners & Losers - Display best and worst performing positions
 */

import { TrendingUp, TrendingDown } from 'lucide-react';

interface PositionSummary {
  symbol: string;
  pnl: number;
  pnlPct: number;
  quantity: number;
}

export function TopWinnersLosers({
  winners,
  losers,
}: {
  winners: PositionSummary[];
  losers: PositionSummary[];
}) {
  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <h3 className="text-lg font-semibold mb-4">Top Winners & Losers</h3>

      {/* Winners */}
      <div className="mb-4">
        <div className="flex items-center gap-2 text-sm text-green-400 mb-2">
          <TrendingUp className="w-4 h-4" />
          <span className="font-semibold">Top Winners</span>
        </div>
        <div className="space-y-2">
          {winners.slice(0, 5).map((position, index) => (
            <div key={index} className="flex justify-between items-center">
              <div>
                <div className="font-semibold">{position.symbol}</div>
                <div className="text-xs text-gray-400">{position.quantity} shares</div>
              </div>
              <div className="text-right">
                <div className="text-green-400 font-mono">+${position.pnl.toLocaleString()}</div>
                <div className="text-xs text-green-400">+{position.pnlPct.toFixed(1)}%</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Losers */}
      <div>
        <div className="flex items-center gap-2 text-sm text-red-400 mb-2">
          <TrendingDown className="w-4 h-4" />
          <span className="font-semibold">Top Losers</span>
        </div>
        <div className="space-y-2">
          {losers.slice(0, 5).map((position, index) => (
            <div key={index} className="flex justify-between items-center">
              <div>
                <div className="font-semibold">{position.symbol}</div>
                <div className="text-xs text-gray-400">{position.quantity} shares</div>
              </div>
              <div className="text-right">
                <div className="text-red-400 font-mono">${position.pnl.toLocaleString()}</div>
                <div className="text-xs text-red-400">{position.pnlPct.toFixed(1)}%</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
