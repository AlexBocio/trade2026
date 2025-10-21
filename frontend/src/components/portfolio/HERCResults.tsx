/**
 * HERC Results Component
 * Displays HERC portfolio optimization results
 */

import React from 'react';
import Plot from 'react-plotly.js';
import { DendrogramVisualization } from './DendrogramVisualization';
import { RiskContributionChart } from './RiskContributionChart';

interface HERCResultsProps {
  weights: Record<string, number>;
  riskContributions: Record<string, number>;
  portfolioMetrics: {
    volatility: number;
    cvar: number | null;
    diversification_ratio: number;
  };
  clusters: Record<string, string[]>;
  dendrogram: number[][];
}

export const HERCResults: React.FC<HERCResultsProps> = ({
  weights,
  riskContributions,
  portfolioMetrics,
  clusters,
  dendrogram,
}) => {
  const tickers = Object.keys(weights);

  return (
    <div className="space-y-6">
      {/* Portfolio Metrics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Annualized Volatility</div>
          <div className="text-3xl font-bold text-white">
            {(portfolioMetrics.volatility * 100).toFixed(2)}%
          </div>
        </div>
        {portfolioMetrics.cvar && (
          <div className="bg-dark-card border border-dark-border rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">CVaR (95%)</div>
            <div className="text-3xl font-bold text-red-400">
              {(portfolioMetrics.cvar * 100).toFixed(2)}%
            </div>
          </div>
        )}
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Diversification Ratio</div>
          <div className="text-3xl font-bold text-green-400">
            {portfolioMetrics.diversification_ratio.toFixed(2)}
          </div>
          <div className="text-xs text-gray-500 mt-1">Higher is better</div>
        </div>
      </div>

      {/* Weights Bar Chart */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-3">Portfolio Weights</h3>
        <Plot
          data={[
            {
              x: tickers,
              y: tickers.map((t) => weights[t] * 100),
              type: 'bar',
              marker: { color: '#60A5FA' },
            },
          ]}
          layout={{
            paper_bgcolor: '#1a1f2e',
            plot_bgcolor: '#0f1419',
            font: { color: '#E5E7EB' },
            xaxis: { gridcolor: '#374151' },
            yaxis: {
              title: 'Weight (%)',
              gridcolor: '#374151',
            },
            margin: { t: 20, r: 20, b: 60, l: 60 },
          }}
          config={{ displayModeBar: true, displaylogo: false, responsive: true }}
          style={{ width: '100%', height: '300px' }}
        />
      </div>

      {/* Risk Contribution Chart */}
      <RiskContributionChart riskContributions={riskContributions} tickers={tickers} />

      {/* Cluster Dendrogram */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-3">
          Hierarchical Clustering
        </h3>
        <p className="text-sm text-gray-400 mb-4">
          Assets are grouped by correlation. Similar assets are clustered together.
        </p>
        <DendrogramVisualization dendrogram={dendrogram} labels={tickers} />
      </div>

      {/* Cluster Breakdown */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-3">Asset Clusters</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(clusters).map(([clusterId, assets]) => (
            <div key={clusterId} className="bg-dark-bg rounded-lg p-4">
              <div className="text-sm font-medium text-gray-300 mb-2">
                Cluster {clusterId}
              </div>
              <div className="flex flex-wrap gap-2">
                {assets.map((asset) => (
                  <span
                    key={asset}
                    className="bg-blue-600 text-white text-xs px-3 py-1 rounded-full font-mono"
                  >
                    {asset}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
