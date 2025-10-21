/**
 * Options Flow Card Component
 * Display unusual options activity and large premium trades
 */

import React from 'react';

interface NotableTrade {
  type: 'CALL' | 'PUT';
  strike: number;
  expiry: string;
  premium: number;
  volume: number;
  open_interest: number;
  execution: string;
  moneyness: string;
}

interface OptionsFlowData {
  total_premium: number;
  volume_oi_ratio: number;
  sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  notable_trades: NotableTrade[];
  options_score: number;
}

interface OptionsFlowCardProps {
  data: OptionsFlowData;
}

export default function OptionsFlowCard({ data }: OptionsFlowCardProps) {
  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
        <span>📊</span>
        <span>Unusual Options Flow</span>
      </h4>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div>
          <div className="text-xs text-gray-400 mb-1">Total Premium</div>
          <div className="text-white font-bold text-lg">
            ${(data.total_premium / 1000000).toFixed(1)}M
          </div>
        </div>
        <div>
          <div className="text-xs text-gray-400 mb-1">Vol/OI Ratio</div>
          <div className="text-orange-400 font-bold text-lg">
            {data.volume_oi_ratio.toFixed(1)}x
          </div>
        </div>
        <div>
          <div className="text-xs text-gray-400 mb-1">Sentiment</div>
          <div
            className={`font-bold text-lg ${
              data.sentiment === 'BULLISH'
                ? 'text-green-400'
                : data.sentiment === 'BEARISH'
                ? 'text-red-400'
                : 'text-gray-400'
            }`}
          >
            {data.sentiment}
          </div>
        </div>
      </div>

      {/* Notable Trades */}
      <div>
        <div className="text-xs font-semibold text-gray-400 mb-2">Notable Trades:</div>
        <div className="space-y-2">
          {data.notable_trades.slice(0, 3).map((trade, i) => (
            <div key={i} className="bg-gray-750 rounded p-2 text-xs border border-gray-600">
              <div className="flex items-center justify-between mb-1">
                <span className="text-gray-300">
                  {trade.type} ${trade.strike} exp {trade.expiry}
                </span>
                <span
                  className={`font-semibold ${
                    trade.type === 'CALL' ? 'text-green-400' : 'text-red-400'
                  }`}
                >
                  ${(trade.premium / 1000).toFixed(0)}K
                </span>
              </div>
              <div className="text-gray-400">
                Vol: {trade.volume} | OI: {trade.open_interest} | {trade.execution} |{' '}
                {trade.moneyness}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
