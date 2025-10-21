/**
 * Timeframe Regime Row Component
 * Display regime analysis for a specific timeframe
 */

import RegimeBadge from './RegimeBadge';

interface TimeframeData {
  regime: string;
  strength: number;
  direction: string;
  return: number;
}

interface TimeframeInfo {
  name: string;
  key: string;
  label: string;
}

interface TimeframeRegimeRowProps {
  timeframe: TimeframeInfo;
  data: TimeframeData;
}

export default function TimeframeRegimeRow({ timeframe, data }: TimeframeRegimeRowProps) {
  return (
    <div className="bg-gray-750 rounded-lg p-3 border border-gray-600 hover:border-gray-500 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <div>
          <div className="text-white font-semibold text-sm">
            {timeframe.name}{' '}
            <span className="text-gray-400 text-xs">({timeframe.label})</span>
          </div>
        </div>
        <RegimeBadge regime={data.regime} size="sm" />
      </div>

      <div className="grid grid-cols-3 gap-3 text-xs">
        <div>
          <div className="text-gray-400 mb-1">Strength:</div>
          <div className="text-white font-semibold">{data.strength.toFixed(1)}</div>
        </div>
        <div>
          <div className="text-gray-400 mb-1">Direction:</div>
          <div
            className={`font-semibold ${
              data.direction === 'UP' ? 'text-green-400' : 'text-red-400'
            }`}
          >
            {data.direction}
          </div>
        </div>
        <div>
          <div className="text-gray-400 mb-1">Return:</div>
          <div
            className={`font-semibold ${data.return > 0 ? 'text-green-400' : 'text-red-400'}`}
          >
            {(data.return * 100).toFixed(1)}%
          </div>
        </div>
      </div>
    </div>
  );
}
