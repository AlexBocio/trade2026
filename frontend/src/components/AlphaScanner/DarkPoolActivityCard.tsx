/**
 * Dark Pool Activity Card Component
 * Display dark pool trading activity and institutional flow
 */

import React from 'react';

interface DarkPoolData {
  total_blocks: number;
  total_shares: number;
  total_value: number;
  net_direction: 'BUYING' | 'SELLING' | 'NEUTRAL';
  avg_price_impact: number;
  activity_score: number;
}

interface DarkPoolActivityCardProps {
  data: DarkPoolData;
}

export default function DarkPoolActivityCard({ data }: DarkPoolActivityCardProps) {
  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
        <span>🏦</span>
        <span>Dark Pool Activity</span>
      </h4>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div>
          <div className="text-xs text-gray-400 mb-1">Total Blocks</div>
          <div className="text-white font-bold text-lg">{data.total_blocks}</div>
        </div>
        <div>
          <div className="text-xs text-gray-400 mb-1">Total Shares</div>
          <div className="text-white font-bold text-lg">
            {(data.total_shares / 1000).toFixed(0)}K
          </div>
        </div>
        <div>
          <div className="text-xs text-gray-400 mb-1">Total Value</div>
          <div className="text-white font-bold text-lg">
            ${(data.total_value / 1000000).toFixed(1)}M
          </div>
        </div>
        <div>
          <div className="text-xs text-gray-400 mb-1">Direction</div>
          <div
            className={`font-bold text-lg ${
              data.net_direction === 'BUYING'
                ? 'text-green-400'
                : data.net_direction === 'SELLING'
                ? 'text-red-400'
                : 'text-gray-400'
            }`}
          >
            {data.net_direction}
          </div>
        </div>
      </div>

      <div className="bg-gray-750 rounded-lg p-3 border border-gray-600">
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="text-gray-300">Avg Price Impact:</span>
          <span className="text-green-400 font-semibold">
            {(data.avg_price_impact * 100).toFixed(2)}% (stealth)
          </span>
        </div>
        <p className="text-xs text-gray-400">
          Low price impact indicates professional accumulation/distribution
        </p>
      </div>
    </div>
  );
}
