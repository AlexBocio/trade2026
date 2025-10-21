/**
 * Spread Chart Component
 * Visualize spread between two stocks with z-score bands
 */

interface SpreadChartProps {
  data: Array<{ date: string; spread: number; zscore: number }>;
  zscore: number;
}

export default function SpreadChart({ data, zscore }: SpreadChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-48 flex items-center justify-center text-gray-400 text-sm">
        No spread history available
      </div>
    );
  }

  // Calculate chart dimensions and scales
  const width = 100; // percentage
  const height = 192; // pixels (h-48)
  const padding = { top: 10, right: 10, bottom: 20, left: 40 };

  const zscores = data.map((d) => d.zscore);
  const minZ = Math.min(...zscores, -3);
  const maxZ = Math.max(...zscores, 3);

  // Create simple ASCII-style visualization
  const getZscorePosition = (z: number) => {
    return ((z - minZ) / (maxZ - minZ)) * 100;
  };

  const getCurrentIndicator = () => {
    const pos = getZscorePosition(zscore);
    return pos;
  };

  return (
    <div className="relative">
      {/* Chart Container */}
      <div className="relative h-48 bg-gray-800 rounded border border-gray-700 p-2">
        {/* Z-Score Bands */}
        <div className="absolute inset-0 flex flex-col justify-between p-2">
          {/* +3σ */}
          <div className="border-t border-red-500/30 relative">
            <span className="absolute -top-2 left-1 text-[10px] text-red-400">+3σ</span>
          </div>

          {/* +2σ */}
          <div className="border-t border-orange-500/30 relative">
            <span className="absolute -top-2 left-1 text-[10px] text-orange-400">+2σ</span>
          </div>

          {/* +1σ */}
          <div className="border-t border-yellow-500/20 relative">
            <span className="absolute -top-2 left-1 text-[10px] text-yellow-400">+1σ</span>
          </div>

          {/* Mean */}
          <div className="border-t-2 border-blue-500/50 relative">
            <span className="absolute -top-2 left-1 text-[10px] text-blue-400 font-semibold">Mean</span>
          </div>

          {/* -1σ */}
          <div className="border-t border-yellow-500/20 relative">
            <span className="absolute -top-2 left-1 text-[10px] text-yellow-400">-1σ</span>
          </div>

          {/* -2σ */}
          <div className="border-t border-orange-500/30 relative">
            <span className="absolute -top-2 left-1 text-[10px] text-orange-400">-2σ</span>
          </div>

          {/* -3σ */}
          <div className="border-t border-red-500/30 relative">
            <span className="absolute -top-2 left-1 text-[10px] text-red-400">-3σ</span>
          </div>
        </div>

        {/* Spread Line - Simplified visualization */}
        <div className="absolute bottom-4 left-10 right-4 h-32 flex items-center">
          <div className="w-full h-1 bg-gradient-to-r from-blue-600 via-blue-400 to-blue-600 opacity-50 rounded-full" />
        </div>

        {/* Current Position Indicator */}
        <div
          className="absolute w-2 h-2 bg-yellow-400 rounded-full animate-pulse shadow-lg shadow-yellow-400/50"
          style={{
            bottom: `${getCurrentIndicator()}%`,
            left: '90%',
            transform: 'translate(-50%, 50%)',
          }}
        >
          <div className="absolute -right-12 top-1/2 -translate-y-1/2 text-xs text-yellow-400 font-bold whitespace-nowrap">
            {zscore.toFixed(2)}σ
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-2 flex items-center justify-between text-xs text-gray-400">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-blue-500 rounded-full" />
            <span>Spread</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-yellow-400 rounded-full" />
            <span>Current</span>
          </div>
        </div>
        <div className="text-gray-500">
          {data.length} data points
        </div>
      </div>

      {/* Stats */}
      <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
        <div className="bg-gray-750 rounded p-2">
          <div className="text-gray-400 mb-1">Current</div>
          <div className={`font-bold ${
            Math.abs(zscore) >= 2.5 ? 'text-red-400' :
            Math.abs(zscore) >= 2.0 ? 'text-yellow-400' :
            'text-green-400'
          }`}>
            {zscore.toFixed(2)}σ
          </div>
        </div>
        <div className="bg-gray-750 rounded p-2">
          <div className="text-gray-400 mb-1">Min</div>
          <div className="text-white font-bold">
            {Math.min(...zscores).toFixed(2)}σ
          </div>
        </div>
        <div className="bg-gray-750 rounded p-2">
          <div className="text-gray-400 mb-1">Max</div>
          <div className="text-white font-bold">
            {Math.max(...zscores).toFixed(2)}σ
          </div>
        </div>
      </div>
    </div>
  );
}
