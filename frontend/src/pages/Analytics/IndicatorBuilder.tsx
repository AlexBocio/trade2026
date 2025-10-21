/**
 * Custom Indicator Builder - Create and backtest custom indicators
 */

import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function IndicatorBuilder() {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate('/analytics')}
          className="p-2 hover:bg-dark-border rounded-lg transition"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-white">Custom Indicator Builder</h1>
          <p className="text-sm text-gray-400">
            Create and backtest custom technical indicators with code
          </p>
        </div>
      </div>

      <div className="bg-dark-card border border-dark-border rounded-lg p-12 text-center">
        <div className="text-6xl mb-4">⚙️</div>
        <h2 className="text-2xl font-bold text-white mb-2">
          Custom Indicator Builder Coming Soon
        </h2>
        <p className="text-gray-400 mb-6">
          This tool will provide a code editor to create custom indicators using Python/JavaScript,
          backtest them against historical data, and analyze their predictive power.
        </p>
        <button
          onClick={() => navigate('/analytics')}
          className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition"
        >
          Back to Analytics
        </button>
      </div>
    </div>
  );
}
