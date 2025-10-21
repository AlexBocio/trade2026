/**
 * Risk Contribution Chart Component
 * Pie chart showing risk contribution distribution
 */

import React from 'react';
import Plot from 'react-plotly.js';

interface RiskContributionChartProps {
  riskContributions: Record<string, number>;
  tickers: string[];
}

export const RiskContributionChart: React.FC<RiskContributionChartProps> = ({
  riskContributions,
  tickers,
}) => {
  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-semibold text-white mb-3">
        Risk Contribution
        <span className="text-sm text-gray-400 ml-2">(Goal: All slices equal)</span>
      </h3>

      <Plot
        data={[
          {
            labels: tickers,
            values: tickers.map((t) => riskContributions[t]),
            type: 'pie',
            marker: {
              colors: [
                '#60A5FA',
                '#34D399',
                '#F59E0B',
                '#EF4444',
                '#8B5CF6',
                '#EC4899',
                '#10B981',
                '#F97316',
              ],
            },
            textinfo: 'label+percent',
            hovertemplate:
              '<b>%{label}</b><br>Risk Contribution: %{value:.2f}%<extra></extra>',
          },
        ]}
        layout={{
          paper_bgcolor: '#1a1f2e',
          plot_bgcolor: '#1a1f2e',
          font: { color: '#E5E7EB' },
          margin: { t: 20, r: 20, b: 20, l: 20 },
          showlegend: false,
        }}
        config={{ displayModeBar: true, displaylogo: false, responsive: true }}
        style={{ width: '100%', height: '400px' }}
      />

      {/* Risk Contribution Table */}
      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-dark-bg">
            <tr>
              <th className="px-3 py-2 text-left text-gray-300">Asset</th>
              <th className="px-3 py-2 text-right text-gray-300">Risk Contribution</th>
              <th className="px-3 py-2 text-right text-gray-300">Deviation from Equal</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-dark-border">
            {tickers.map((ticker) => {
              const equalRC = 100 / tickers.length;
              const deviation = riskContributions[ticker] - equalRC;
              return (
                <tr key={ticker} className="hover:bg-dark-bg/50">
                  <td className="px-3 py-2 text-white font-medium font-mono">{ticker}</td>
                  <td className="px-3 py-2 text-right text-blue-400 font-medium">
                    {riskContributions[ticker].toFixed(2)}%
                  </td>
                  <td
                    className={`px-3 py-2 text-right font-medium ${
                      Math.abs(deviation) < 2
                        ? 'text-green-400'
                        : Math.abs(deviation) < 5
                        ? 'text-yellow-400'
                        : 'text-red-400'
                    }`}
                  >
                    {deviation > 0 ? '+' : ''}
                    {deviation.toFixed(2)}%
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
