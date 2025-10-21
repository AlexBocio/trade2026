/**
 * Similarity Breakdown Component
 * Visual breakdown of pattern matching factors with weighted scores
 */

import React from 'react';

interface MatchingFactor {
  score: number;
  match: boolean;
  details?: string;
}

interface MatchingFactors {
  regime: MatchingFactor;
  volume_pattern: MatchingFactor;
  price_structure: MatchingFactor;
  sector_context: MatchingFactor;
  temporal: MatchingFactor;
}

interface SimilarityBreakdownProps {
  factors: MatchingFactors;
}

interface FactorDefinition {
  key: keyof MatchingFactors;
  label: string;
  weight: number;
}

function calculateWeightedScore(
  factors: MatchingFactors,
  factorList: FactorDefinition[]
): number {
  let totalWeightedScore = 0;
  let totalWeight = 0;

  factorList.forEach((factor) => {
    const data = factors[factor.key];
    if (data) {
      totalWeightedScore += data.score * factor.weight;
      totalWeight += factor.weight;
    }
  });

  return totalWeight > 0 ? totalWeightedScore / totalWeight : 0;
}

export default function SimilarityBreakdown({ factors }: SimilarityBreakdownProps) {
  const factorList: FactorDefinition[] = [
    { key: 'regime', label: 'Regime Match', weight: 30 },
    { key: 'volume_pattern', label: 'Volume Pattern', weight: 25 },
    { key: 'price_structure', label: 'Price Structure', weight: 20 },
    { key: 'sector_context', label: 'Sector Context', weight: 15 },
    { key: 'temporal', label: 'Temporal', weight: 10 },
  ];

  const weightedScore = calculateWeightedScore(factors, factorList);

  return (
    <div className="bg-gray-750 rounded-lg p-4 border border-gray-700">
      <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
        <span>🎯</span>
        <span>Similarity Breakdown</span>
      </h4>

      <div className="space-y-3">
        {factorList.map((factor) => {
          const data = factors[factor.key];
          const score = (data?.score || 0) * 100;

          return (
            <div key={factor.key}>
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-300">{factor.label}</span>
                  {data?.match && <span className="text-green-400 text-xs">✓</span>}
                </div>
                <span className="text-white text-sm font-semibold">{score.toFixed(0)}%</span>
              </div>

              <div className="flex items-center space-x-2">
                <div className="flex-1 bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      score >= 80
                        ? 'bg-green-600'
                        : score >= 60
                        ? 'bg-yellow-600'
                        : 'bg-red-600'
                    }`}
                    style={{ width: `${score}%` }}
                  />
                </div>
                <span className="text-xs text-gray-400 w-12 text-right">{factor.weight}%</span>
              </div>

              {data?.details && (
                <p className="text-xs text-gray-500 mt-1 ml-1">{data.details}</p>
              )}
            </div>
          );
        })}
      </div>

      {/* Overall Weighted Score */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="flex items-center justify-between">
          <span className="text-white font-semibold">Weighted Average:</span>
          <span className="text-blue-400 font-bold text-lg">
            {(weightedScore * 100).toFixed(0)}%
          </span>
        </div>
        <div className="mt-2 bg-gray-700 rounded-full h-3">
          <div
            className="bg-gradient-to-r from-blue-600 to-blue-400 h-3 rounded-full transition-all"
            style={{ width: `${weightedScore * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
}
