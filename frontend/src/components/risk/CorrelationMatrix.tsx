/**
 * Correlation Matrix - Heatmap showing position correlations
 */

import Plot from 'react-plotly.js';
import { AlertCircle } from 'lucide-react';

interface CorrelationMatrixProps {
  symbols: string[];
  correlations: number[][];
}

export function CorrelationMatrix({ symbols, correlations }: CorrelationMatrixProps) {
  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 mb-6">
      <h3 className="text-lg font-semibold mb-4">Position Correlation Matrix</h3>
      <p className="text-sm text-gray-400 mb-4">Higher correlation = more risk if positions move together</p>

      <Plot
        data={[
          {
            x: symbols,
            y: symbols,
            z: correlations,
            type: 'heatmap',
            colorscale: [
              [0, '#ff4444'],
              [0.5, '#1a1f2e'],
              [1, '#00ff88'],
            ],
            text: correlations.map((row) => row.map((val) => val.toFixed(2))),
            texttemplate: '%{text}',
            textfont: { size: 10, color: '#fff' },
            hovertemplate: '%{y} vs %{x}: %{z:.2f}<extra></extra>',
            zmid: 0,
            zmin: -1,
            zmax: 1,
          },
        ]}
        layout={{
          paper_bgcolor: '#1a1f2e',
          plot_bgcolor: '#1a1f2e',
          font: { color: '#e0e0e0', family: 'monospace', size: 10 },
          xaxis: { side: 'bottom' },
          yaxis: { autorange: 'reversed' },
          margin: { l: 60, r: 20, t: 20, b: 60 },
          annotations: [
            {
              text: '← Negative Correlation | Positive Correlation →',
              xref: 'paper',
              yref: 'paper',
              x: 0.5,
              y: -0.15,
              showarrow: false,
              font: { size: 10, color: '#888' },
            },
          ],
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%', height: '400px' }}
      />

      {/* Risk Warning */}
      <div className="mt-4 bg-yellow-900/20 border border-yellow-700 rounded p-3 flex items-start gap-2">
        <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-yellow-200">
          <strong>High Correlation Detected:</strong> NVAX and SAVA have 0.87 correlation. Consider
          diversifying to reduce portfolio risk.
        </div>
      </div>
    </div>
  );
}
