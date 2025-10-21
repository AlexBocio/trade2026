/**
 * Factor Correlation Heatmap - Display factor correlations
 */

import Plot from 'react-plotly.js';

export function FactorCorrelationHeatmap({
  factors,
  correlations,
}: {
  factors: string[];
  correlations: number[][];
}) {
  return (
    <Plot
      data={[
        {
          x: factors,
          y: factors,
          z: correlations,
          type: 'heatmap',
          colorscale: [
            [0, '#ff4444'],
            [0.5, '#1a1f2e'],
            [1, '#00ff88'],
          ],
          text: correlations.map((row) => row.map((val) => val.toFixed(2))),
          texttemplate: '%{text}',
          textfont: { size: 12, color: '#fff' },
          hovertemplate: '%{y} vs %{x}: %{z:.3f}<extra></extra>',
          zmid: 0,
          zmin: -1,
          zmax: 1,
        },
      ]}
      layout={{
        paper_bgcolor: '#1a1f2e',
        plot_bgcolor: '#1a1f2e',
        font: { color: '#e0e0e0', family: 'monospace' },
        xaxis: { side: 'bottom' },
        yaxis: { autorange: 'reversed' },
        margin: { l: 100, r: 20, t: 20, b: 80 },
      }}
      config={{ displayModeBar: false, responsive: true }}
      style={{ width: '100%', height: '400px' }}
    />
  );
}
