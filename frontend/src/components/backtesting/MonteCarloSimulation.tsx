/**
 * Monte Carlo Simulation - Visualize probabilistic outcomes
 */

import Plot from 'react-plotly.js';

interface MonteCarloProps {
  simulations: Array<{
    simulationId: number;
    equityCurve: number[];
  }>;
  percentiles: {
    p5: number[];
    p25: number[];
    p50: number[];
    p75: number[];
    p95: number[];
  };
}

export function MonteCarloSimulation({ simulations, percentiles }: MonteCarloProps) {
  const dates = simulations[0]?.equityCurve.map((_, i) => i) || [];

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-2">Monte Carlo Simulation (1000 runs)</h3>
      <p className="text-sm text-gray-400 mb-4">
        Shows distribution of possible outcomes by randomly shuffling trade order
      </p>

      <Plot
        data={[
          // All simulation paths (light gray, low opacity)
          ...simulations.slice(0, 100).map((sim) => ({
            x: dates,
            y: sim.equityCurve,
            type: 'scatter' as const,
            mode: 'lines' as const,
            line: { color: '#444', width: 1 },
            opacity: 0.1,
            showlegend: false,
            hoverinfo: 'skip' as const,
          })),

          // Percentile bands
          {
            x: dates,
            y: percentiles.p95,
            type: 'scatter' as const,
            mode: 'lines' as const,
            name: '95th percentile',
            line: { color: '#00ff88', width: 2 },
          },
          {
            x: dates,
            y: percentiles.p75,
            type: 'scatter' as const,
            mode: 'lines' as const,
            name: '75th percentile',
            line: { color: '#00dd77', width: 2 },
            fill: 'tonexty' as const,
            fillcolor: 'rgba(0, 255, 136, 0.1)',
          },
          {
            x: dates,
            y: percentiles.p50,
            type: 'scatter' as const,
            mode: 'lines' as const,
            name: 'Median',
            line: { color: '#ffc800', width: 3 },
          },
          {
            x: dates,
            y: percentiles.p25,
            type: 'scatter' as const,
            mode: 'lines' as const,
            name: '25th percentile',
            line: { color: '#ff8844', width: 2 },
          },
          {
            x: dates,
            y: percentiles.p5,
            type: 'scatter' as const,
            mode: 'lines' as const,
            name: '5th percentile',
            line: { color: '#ff4444', width: 2 },
            fill: 'tonexty' as const,
            fillcolor: 'rgba(255, 68, 68, 0.1)',
          },
        ]}
        layout={{
          paper_bgcolor: '#1a1f2e',
          plot_bgcolor: '#1a1f2e',
          font: { color: '#e0e0e0', family: 'monospace' },
          xaxis: { title: 'Trade Number', gridcolor: '#2a3142' },
          yaxis: { title: 'Portfolio Value ($)', gridcolor: '#2a3142', tickformat: '$,.0f' },
          legend: { x: 0.05, y: 0.95 },
          margin: { l: 60, r: 20, t: 20, b: 50 },
          autosize: true,
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%', height: '500px' }}
      />

      {/* Summary Stats */}
      <div className="grid grid-cols-5 gap-4 mt-6">
        <div className="bg-dark-bg rounded p-3">
          <div className="text-xs text-gray-400 mb-1">95th Percentile</div>
          <div className="text-xl font-bold text-green-400">
            ${percentiles.p95[percentiles.p95.length - 1]?.toLocaleString() || '0'}
          </div>
        </div>
        <div className="bg-dark-bg rounded p-3">
          <div className="text-xs text-gray-400 mb-1">75th Percentile</div>
          <div className="text-xl font-bold text-white">
            ${percentiles.p75[percentiles.p75.length - 1]?.toLocaleString() || '0'}
          </div>
        </div>
        <div className="bg-dark-bg rounded p-3">
          <div className="text-xs text-gray-400 mb-1">Median</div>
          <div className="text-xl font-bold text-yellow-400">
            ${percentiles.p50[percentiles.p50.length - 1]?.toLocaleString() || '0'}
          </div>
        </div>
        <div className="bg-dark-bg rounded p-3">
          <div className="text-xs text-gray-400 mb-1">25th Percentile</div>
          <div className="text-xl font-bold text-white">
            ${percentiles.p25[percentiles.p25.length - 1]?.toLocaleString() || '0'}
          </div>
        </div>
        <div className="bg-dark-bg rounded p-3">
          <div className="text-xs text-gray-400 mb-1">5th Percentile</div>
          <div className="text-xl font-bold text-red-400">
            ${percentiles.p5[percentiles.p5.length - 1]?.toLocaleString() || '0'}
          </div>
        </div>
      </div>
    </div>
  );
}
