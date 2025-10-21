/**
 * Dendrogram Visualization Component
 * Displays hierarchical clustering tree
 */

import React from 'react';

interface DendrogramVisualizationProps {
  dendrogram: number[][];
  labels: string[];
}

export const DendrogramVisualization: React.FC<DendrogramVisualizationProps> = ({
  dendrogram,
  labels,
}) => {
  // Simplified dendrogram display
  // Full implementation would use scipy.cluster.hierarchy.dendrogram logic
  // For now, we'll show a visual representation

  return (
    <div className="bg-dark-bg rounded-lg p-6">
      <div className="text-center">
        <div className="inline-block bg-dark-card border border-dark-border rounded-lg p-8">
          <svg width="600" height="300" className="mx-auto">
            {/* Placeholder for dendrogram visualization */}
            <text
              x="300"
              y="150"
              textAnchor="middle"
              className="fill-gray-400 text-sm"
            >
              Hierarchical Clustering Tree
            </text>
            <text
              x="300"
              y="180"
              textAnchor="middle"
              className="fill-gray-500 text-xs"
            >
              (Assets grouped by correlation similarity)
            </text>
          </svg>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
        {labels.map((label, idx) => (
          <div
            key={label}
            className="bg-dark-card border border-dark-border rounded px-3 py-2 text-center"
          >
            <div className="text-white font-mono font-bold">{label}</div>
            <div className="text-gray-500 text-xs">Node {idx + 1}</div>
          </div>
        ))}
      </div>

      <div className="mt-4 text-xs text-gray-500 text-center">
        Note: Full dendrogram visualization requires D3.js or Plotly implementation
      </div>
    </div>
  );
};
