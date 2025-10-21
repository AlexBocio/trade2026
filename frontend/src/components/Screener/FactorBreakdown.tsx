/**
 * Factor Breakdown Component
 * Visualizes factor scores with radar chart
 */

import React from 'react';
import Plot from 'react-plotly.js';

interface FactorBreakdownProps {
  factorScores: Record<string, number>;
}

export const FactorBreakdown: React.FC<FactorBreakdownProps> = ({ factorScores }) => {
  const factors = Object.keys(factorScores);
  const scores = Object.values(factorScores);

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-semibold text-white mb-4">Factor Analysis</h3>

      {/* Radar Chart */}
      <Plot
        data={[
          {
            type: 'scatterpolar',
            r: scores,
            theta: factors.map(f => f.charAt(0).toUpperCase() + f.slice(1)),
            fill: 'toself',
            fillcolor: 'rgba(96, 165, 250, 0.2)',
            line: {
              color: '#60A5FA',
              width: 2,
            },
            marker: {
              color: '#60A5FA',
              size: 8,
            },
          },
        ]}
        layout={{
          polar: {
            radialaxis: {
              visible: true,
              range: [0, 100],
              gridcolor: '#374151',
              tickfont: { color: '#9CA3AF' },
            },
            angularaxis: {
              gridcolor: '#374151',
              tickfont: { color: '#E5E7EB', size: 12 },
            },
            bgcolor: '#1a1f2e',
          },
          paper_bgcolor: '#1a1f2e',
          plot_bgcolor: '#1a1f2e',
          font: { color: '#E5E7EB' },
          showlegend: false,
          margin: { t: 40, r: 40, b: 40, l: 40 },
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%', height: '350px' }}
      />

      {/* Factor Score Bars */}
      <div className="mt-6 space-y-3">
        {factors.map(factor => {
          const score = factorScores[factor];
          return (
            <div key={factor}>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-gray-300 capitalize">{factor}</span>
                <span className="text-white font-bold">{score}/100</span>
              </div>
              <div className="w-full bg-dark-bg rounded-full h-3">
                <div
                  className={`h-3 rounded-full transition-all ${
                    score >= 80 ? 'bg-green-500' :
                    score >= 60 ? 'bg-blue-500' :
                    score >= 40 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${score}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Factor Interpretation */}
      <div className="mt-6 p-4 bg-blue-900/20 border border-blue-700 rounded-lg">
        <h4 className="text-sm font-semibold text-blue-400 mb-2">Factor Guide</h4>
        <ul className="text-xs text-gray-300 space-y-1">
          <li><strong>Momentum:</strong> Price trend strength and direction</li>
          <li><strong>Value:</strong> Fundamental valuation metrics (P/E, P/B)</li>
          <li><strong>Quality:</strong> Balance sheet health and profitability</li>
          <li><strong>Growth:</strong> Revenue and earnings growth rates</li>
          <li><strong>Volatility:</strong> Price stability (lower = better)</li>
          <li><strong>Liquidity:</strong> Trading volume and spread</li>
        </ul>
      </div>
    </div>
  );
};
