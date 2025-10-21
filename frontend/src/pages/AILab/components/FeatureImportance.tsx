/**
 * Feature Importance - SHAP values visualization
 */

import Plot from 'react-plotly.js';
import type { FeatureImportanceData } from '../../../services/mock-data/ml-model-data';
import { Panel, PanelHeader, PanelContent } from '../../../components/common/Panel';

export function FeatureImportance({ data }: { data: FeatureImportanceData }) {
  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'technical':
        return '#00ff88';
      case 'fundamental':
        return '#00ddff';
      case 'sentiment':
        return '#ffc800';
      case 'macro':
        return '#ff4444';
      default:
        return '#888888';
    }
  };

  return (
    <Panel>
      <PanelHeader>
        <h3 className="text-lg font-semibold">Feature Importance</h3>
      </PanelHeader>
      <PanelContent>
        {/* SHAP Bar Chart */}
        <Plot
          data={[
            {
              x: data.features.map((f) => f.importance),
              y: data.features.map((f) => f.name),
              type: 'bar',
              orientation: 'h',
              marker: {
                color: data.features.map((f) => (f.importance > 0 ? '#00ff88' : '#ff4444')),
              },
              text: data.features.map((f) => f.importance.toFixed(3)),
              textposition: 'auto',
              hovertemplate: '<b>%{y}</b><br>SHAP: %{x:.3f}<extra></extra>',
            },
          ]}
          layout={{
            paper_bgcolor: '#1a1f2e',
            plot_bgcolor: '#1a1f2e',
            font: { color: '#e0e0e0', family: 'monospace', size: 10 },
            xaxis: { title: 'SHAP Value', gridcolor: '#2a3142', zeroline: true, zerolinecolor: '#555' },
            yaxis: { gridcolor: '#2a3142', automargin: true },
            height: 300,
            margin: { l: 150, r: 20, t: 10, b: 40 },
            showlegend: false,
          }}
          config={{ displayModeBar: false }}
          style={{ width: '100%' }}
        />

        {/* Top Features List */}
        <div className="mt-3 space-y-2">
          <div className="text-xs text-gray-400 mb-2">Top Features:</div>
          {data.features.slice(0, 5).map((feature, i) => (
            <div key={i} className="flex justify-between items-center gap-2 bg-gray-800 rounded p-2">
              <div className="flex items-center gap-2 min-w-0 flex-1">
                <div
                  className="w-2 h-2 rounded-full flex-shrink-0"
                  style={{ backgroundColor: getCategoryColor(feature.category) }}
                />
                <span className="font-mono text-xs truncate">{feature.name}</span>
                <span className="text-xs text-gray-500 uppercase flex-shrink-0">{feature.category}</span>
              </div>
              <span
                className={`font-mono text-xs font-bold flex-shrink-0 ${
                  feature.importance > 0 ? 'text-green-400' : 'text-red-400'
                }`}
              >
                {feature.importance > 0 ? '+' : ''}
                {feature.importance.toFixed(3)}
              </span>
            </div>
          ))}
        </div>

        {/* Category Legend */}
        <div className="mt-3 flex flex-wrap gap-3 text-xs justify-center">
          {['technical', 'fundamental', 'sentiment', 'macro'].map((cat) => (
            <div key={cat} className="flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded" style={{ backgroundColor: getCategoryColor(cat) }} />
              <span className="text-gray-400 capitalize">{cat}</span>
            </div>
          ))}
        </div>
      </PanelContent>
    </Panel>
  );
}
