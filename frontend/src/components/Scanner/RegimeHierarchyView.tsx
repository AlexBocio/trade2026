/**
 * Regime Hierarchy View Component
 * Visual tree showing regime cascade from temporal to stock level
 */

import React from 'react';
import RegimeBadge from '../Regime/RegimeBadge';
import RegimeStrengthBar from '../Regime/RegimeStrengthBar';
import { checkAlignment } from '../../utils/formatters';

interface RegimeHierarchyViewProps {
  hierarchy: any;
}

interface RegimeLayer {
  name: string;
  data: any;
  icon: string;
}

export default function RegimeHierarchyView({ hierarchy }: RegimeHierarchyViewProps) {
  if (!hierarchy) {
    return (
      <div className="text-gray-400 text-sm">No hierarchy data available</div>
    );
  }

  const layers: RegimeLayer[] = [
    { name: 'Temporal', data: hierarchy.temporal, icon: '📅' },
    { name: 'Macro', data: hierarchy.macro, icon: '🌍' },
    { name: 'Cross-Asset', data: hierarchy.cross_asset, icon: '🔀' },
    { name: 'Market', data: hierarchy.market, icon: '📈' },
    { name: 'Sector', data: hierarchy.sector, icon: '🏭' },
    { name: 'Industry', data: hierarchy.industry, icon: '🏢' },
    { name: 'Stock', data: hierarchy.stock, icon: '📊' },
  ];

  // Filter out layers with no data
  const validLayers = layers.filter((layer) => layer.data);

  return (
    <div className="space-y-2">
      {validLayers.map((layer, index) => {
        const isAligned =
          index === 0 ||
          (validLayers[index - 1]?.data &&
            checkAlignment(
              getRegimeFromLayer(layer.data),
              getRegimeFromLayer(validLayers[index - 1].data)
            ));

        return (
          <div key={layer.name} className="relative">
            {/* Connector Line */}
            {index > 0 && (
              <div className="absolute left-6 -top-2 w-0.5 h-4 bg-gray-600" />
            )}

            {/* Layer Card */}
            <div
              className={`flex items-center justify-between p-3 rounded-lg transition-colors ${
                isAligned
                  ? 'bg-green-900/20 border border-green-700/50'
                  : 'bg-red-900/20 border border-red-700/50'
              }`}
            >
              <div className="flex items-center space-x-3 flex-1">
                <span className="text-2xl">{layer.icon}</span>
                <div className="flex-1">
                  <div className="text-sm text-gray-400">{layer.name}</div>
                  <div className="flex items-center space-x-2 mt-1">
                    <RegimeBadge regime={getRegimeFromLayer(layer.data) as any} />
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                {layer.data.strength !== undefined && (
                  <div className="text-right">
                    <div className="text-xs text-gray-400">Strength</div>
                    <div className="text-white font-semibold">
                      {layer.data.strength.toFixed(1)}
                    </div>
                  </div>
                )}

                {layer.data.regime_strength !== undefined && (
                  <div className="text-right">
                    <div className="text-xs text-gray-400">Strength</div>
                    <div className="text-white font-semibold">
                      {layer.data.regime_strength.toFixed(1)}
                    </div>
                  </div>
                )}

                <div className="text-xl">
                  {isAligned ? (
                    <span className="text-green-400">✓</span>
                  ) : (
                    <span className="text-red-400">✗</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        );
      })}

      {/* Overall Alignment Score */}
      {hierarchy.alignment_score !== undefined && (
        <div className="mt-4 bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-gray-400 font-semibold">Overall Alignment:</span>
            <div className="flex items-center space-x-3">
              <RegimeStrengthBar
                strength={hierarchy.alignment_score}
                max={10}
                animate={true}
              />
              <span className="text-white font-bold text-lg">
                {hierarchy.alignment_score.toFixed(1)}/10
              </span>
            </div>
          </div>

          {hierarchy.divergence_points && hierarchy.divergence_points.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-700">
              <div className="text-xs text-gray-400 mb-2">Divergence Points:</div>
              <div className="flex flex-wrap gap-2">
                {hierarchy.divergence_points.map((point: string, idx: number) => (
                  <span
                    key={idx}
                    className="text-xs bg-red-800/50 text-red-300 px-2 py-1 rounded"
                  >
                    {point}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * Helper function to extract regime from different layer data structures
 */
function getRegimeFromLayer(layerData: any): string {
  if (!layerData) return 'NEUTRAL';

  // Try different possible property names
  if (layerData.regime) return layerData.regime;
  if (layerData.primary_regime) return layerData.primary_regime;
  if (layerData.overall_macro) return layerData.overall_macro;
  if (layerData.seasonal_regime) return layerData.seasonal_regime;

  return 'NEUTRAL';
}
