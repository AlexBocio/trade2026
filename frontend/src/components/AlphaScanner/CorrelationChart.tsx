/**
 * Correlation Chart Component
 * Line chart showing rolling correlation over time
 */

import React, { useEffect, useState } from 'react';
import { alphaApi } from '../../api/alphaApi';

interface KeyEvent {
  date: string;
  description: string;
}

interface CorrelationHistory {
  dates: string[];
  correlations: number[];
  key_events?: KeyEvent[];
}

interface CorrelationChartProps {
  symbol: string;
  sector: string;
}

export default function CorrelationChart({ symbol, sector }: CorrelationChartProps) {
  const [data, setData] = useState<CorrelationHistory | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const history = await alphaApi.correlation.getHistory(symbol, sector, 252);
        setData(history);
      } catch (error) {
        console.error('Failed to fetch correlation history:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [symbol, sector]);

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
        <div className="text-gray-400">Loading chart...</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
        <div className="text-gray-400">No correlation data available</div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <h4 className="text-sm font-semibold text-gray-400 mb-4 flex items-center space-x-2">
        <span>📈</span>
        <span>Rolling 60-Day Correlation: {symbol} vs {sector}</span>
      </h4>

      {/* Placeholder for actual chart - integrate Recharts or Chart.js */}
      <div className="h-64 bg-gray-750 rounded-lg flex flex-col items-center justify-center text-gray-500 border border-gray-600">
        <div className="text-center space-y-2">
          <div className="text-4xl">📊</div>
          <div className="text-sm">Correlation Chart Visualization</div>
          <div className="text-xs">
            (Integrate Recharts/Chart.js for live visualization)
          </div>
        </div>

        {/* Simple data preview */}
        <div className="mt-4 text-xs text-gray-400">
          {data.correlations && data.correlations.length > 0 && (
            <div>
              Latest correlation:{' '}
              <span className="text-white font-semibold">
                {data.correlations[data.correlations.length - 1]?.toFixed(2)}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Key Events */}
      {data.key_events && data.key_events.length > 0 && (
        <div className="mt-4 space-y-2">
          <div className="text-xs font-semibold text-gray-400">Key Events:</div>
          <div className="space-y-1">
            {data.key_events.map((event, i) => (
              <div
                key={i}
                className="text-xs text-gray-300 flex items-start space-x-2 bg-gray-750 rounded p-2"
              >
                <span className="text-blue-400">•</span>
                <div>
                  <span className="text-blue-400 font-semibold">{event.date}:</span>{' '}
                  {event.description}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Correlation Trend Indicator */}
      {data.correlations && data.correlations.length >= 2 && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">Trend:</span>
            <span
              className={`font-semibold ${
                data.correlations[data.correlations.length - 1] >
                data.correlations[data.correlations.length - 10]
                  ? 'text-green-400'
                  : 'text-red-400'
              }`}
            >
              {data.correlations[data.correlations.length - 1] >
              data.correlations[data.correlations.length - 10]
                ? '↗ Strengthening'
                : '↘ Weakening'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
