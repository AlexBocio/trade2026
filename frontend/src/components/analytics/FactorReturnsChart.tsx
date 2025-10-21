/**
 * Factor Returns Chart - Display factor returns over time
 */

import Plot from 'react-plotly.js';

export function FactorReturnsChart({ data }: { data: any }) {
  return (
    <Plot
      data={[
        {
          x: data.dates,
          y: data.momentum,
          type: 'scatter',
          mode: 'lines',
          name: 'Momentum',
          line: { color: '#00ff88', width: 2 },
        },
        {
          x: data.dates,
          y: data.value,
          type: 'scatter',
          mode: 'lines',
          name: 'Value',
          line: { color: '#00ddff', width: 2 },
        },
        {
          x: data.dates,
          y: data.volatility,
          type: 'scatter',
          mode: 'lines',
          name: 'Volatility',
          line: { color: '#ff4444', width: 2 },
        },
      ]}
      layout={{
        paper_bgcolor: '#1a1f2e',
        plot_bgcolor: '#1a1f2e',
        font: { color: '#e0e0e0', family: 'monospace' },
        xaxis: {
          title: 'Date',
          gridcolor: '#2a3142',
          type: 'date',
        },
        yaxis: {
          title: 'Cumulative Return (Base = 100)',
          gridcolor: '#2a3142',
        },
        legend: { x: 0.05, y: 0.95 },
        hovermode: 'x unified',
        margin: { l: 60, r: 20, t: 20, b: 50 },
      }}
      config={{ displayModeBar: false, responsive: true }}
      style={{ width: '100%', height: '400px' }}
    />
  );
}
