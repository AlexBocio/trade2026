/**
 * HERC vs HRP Comparison Component
 * Side-by-side comparison of HERC and HRP portfolios
 */

import React from 'react';
import Plot from 'react-plotly.js';

interface HERCvsHRPProps {
  tickers: string[];
  hercWeights: Record<string, number>;
  hrpWeights: Record<string, number>;
  hercRC: Record<string, number>;
  hrpRC: Record<string, number>;
  comparison: {
    herc_vol: number;
    hrp_vol: number;
    herc_cvar: number;
    hrp_cvar: number;
    rc_concentration_herc: number;
    rc_concentration_hrp: number;
    recommendation: string;
    tail_risk_winner: string;
  };
}

export const HERCvsHRP: React.FC<HERCvsHRPProps> = ({
  tickers,
  hercWeights,
  hrpWeights,
  hercRC,
  hrpRC,
  comparison,
}) => {
  return (
    <div className="space-y-6">
      {/* Winner Banner */}
      <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-blue-400 mb-2">Recommendation</h3>
        <p className="text-gray-300">{comparison.recommendation}</p>
        <p className="text-gray-300 mt-1">{comparison.tail_risk_winner}</p>
      </div>

      {/* Metrics Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* HERC Card */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <h3 className="text-xl font-semibold text-white mb-4">HERC Portfolio</h3>
          <div className="space-y-3">
            <div className="flex justify-between p-3 bg-dark-bg rounded-lg">
              <span className="text-gray-400">Volatility</span>
              <span className="text-white font-medium">
                {(comparison.herc_vol * 100).toFixed(2)}%
              </span>
            </div>
            <div className="flex justify-between p-3 bg-dark-bg rounded-lg">
              <span className="text-gray-400">CVaR (95%)</span>
              <span className="text-white font-medium">
                {(comparison.herc_cvar * 100).toFixed(2)}%
              </span>
            </div>
            <div className="flex justify-between p-3 bg-dark-bg rounded-lg">
              <span className="text-gray-400">RC Std Dev</span>
              <span className="text-white font-medium">
                {comparison.rc_concentration_herc.toFixed(2)}
              </span>
            </div>
          </div>
        </div>

        {/* HRP Card */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <h3 className="text-xl font-semibold text-white mb-4">HRP Portfolio</h3>
          <div className="space-y-3">
            <div className="flex justify-between p-3 bg-dark-bg rounded-lg">
              <span className="text-gray-400">Volatility</span>
              <span className="text-white font-medium">
                {(comparison.hrp_vol * 100).toFixed(2)}%
              </span>
            </div>
            <div className="flex justify-between p-3 bg-dark-bg rounded-lg">
              <span className="text-gray-400">CVaR (95%)</span>
              <span className="text-white font-medium">
                {(comparison.hrp_cvar * 100).toFixed(2)}%
              </span>
            </div>
            <div className="flex justify-between p-3 bg-dark-bg rounded-lg">
              <span className="text-gray-400">RC Std Dev</span>
              <span className="text-white font-medium">
                {comparison.rc_concentration_hrp.toFixed(2)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Side-by-Side Weights Comparison */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-4">Weight Comparison</h3>
        <Plot
          data={[
            {
              x: tickers,
              y: tickers.map((t) => hercWeights[t] * 100),
              name: 'HERC',
              type: 'bar',
              marker: { color: '#60A5FA' },
            },
            {
              x: tickers,
              y: tickers.map((t) => hrpWeights[t] * 100),
              name: 'HRP',
              type: 'bar',
              marker: { color: '#34D399' },
            },
          ]}
          layout={{
            paper_bgcolor: '#1a1f2e',
            plot_bgcolor: '#0f1419',
            font: { color: '#E5E7EB' },
            barmode: 'group',
            xaxis: { gridcolor: '#374151' },
            yaxis: {
              title: 'Weight (%)',
              gridcolor: '#374151',
            },
            legend: {
              bgcolor: '#0f1419',
              bordercolor: '#374151',
              borderwidth: 1,
            },
            margin: { t: 20, r: 20, b: 60, l: 60 },
          }}
          config={{ displayModeBar: true, displaylogo: false, responsive: true }}
          style={{ width: '100%', height: '400px' }}
        />
      </div>

      {/* Risk Contribution Comparison */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-4">
          Risk Contribution Comparison
        </h3>
        <Plot
          data={[
            {
              x: tickers,
              y: tickers.map((t) => hercRC[t]),
              name: 'HERC',
              type: 'bar',
              marker: { color: '#60A5FA' },
            },
            {
              x: tickers,
              y: tickers.map((t) => hrpRC[t]),
              name: 'HRP',
              type: 'bar',
              marker: { color: '#34D399' },
            },
            {
              x: [tickers[0], tickers[tickers.length - 1]],
              y: [100 / tickers.length, 100 / tickers.length],
              name: 'Equal RC Target',
              type: 'scatter',
              mode: 'lines',
              line: { color: '#EF4444', dash: 'dash', width: 2 },
            },
          ]}
          layout={{
            paper_bgcolor: '#1a1f2e',
            plot_bgcolor: '#0f1419',
            font: { color: '#E5E7EB' },
            barmode: 'group',
            xaxis: { gridcolor: '#374151' },
            yaxis: {
              title: 'Risk Contribution (%)',
              gridcolor: '#374151',
            },
            legend: {
              bgcolor: '#0f1419',
              bordercolor: '#374151',
              borderwidth: 1,
            },
            margin: { t: 20, r: 20, b: 60, l: 60 },
          }}
          config={{ displayModeBar: true, displaylogo: false, responsive: true }}
          style={{ width: '100%', height: '400px' }}
        />
        <p className="text-sm text-gray-400 mt-4">
          HERC aims to equalize risk contributions (closer to red dashed line = better).
          Lower standard deviation of RC indicates more equal distribution.
        </p>
      </div>
    </div>
  );
};
