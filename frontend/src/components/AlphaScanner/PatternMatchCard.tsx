/**
 * Pattern Match Card Component
 * Individual match result with similarity breakdown and expected outcomes
 */

import React, { useState } from 'react';
import RegimeBadge from '../Regime/RegimeBadge';
import SimilarityBreakdown from './SimilarityBreakdown';

interface ExpectedOutcome {
  return_estimate: number;
  duration_estimate: number;
  confidence: number;
  historical_success_rate: number;
}

interface PatternMatch {
  symbol: string;
  current_regime: string;
  similarity_score: number;
  matching_factors: any;
  expected_outcome: ExpectedOutcome;
  days_into_pattern: number;
}

interface ReferencePattern {
  symbol: string;
  duration: number;
  return: number;
}

interface PatternMatchCardProps {
  match: PatternMatch;
  referencePattern: ReferencePattern;
}

export default function PatternMatchCard({ match, referencePattern }: PatternMatchCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-gray-750 rounded-lg overflow-hidden border border-gray-700 hover:border-blue-600 transition-all">
      <div
        className="p-4 cursor-pointer hover:bg-gray-700 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          {/* Stock Info */}
          <div className="flex items-center space-x-4">
            <div className="text-white font-bold text-lg">{match.symbol}</div>
            <RegimeBadge regime={match.current_regime as any} />
          </div>

          {/* Similarity Score */}
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-xs text-gray-400">Similarity</div>
              <div className="text-white font-bold text-lg">
                {(match.similarity_score * 100).toFixed(0)}%
              </div>
            </div>

            <div className="text-right">
              <div className="text-xs text-gray-400">Expected Return</div>
              <div className="text-green-400 font-bold">
                +{(match.expected_outcome.return_estimate * 100).toFixed(0)}%
              </div>
            </div>

            <button className="text-gray-400 hover:text-white transition-transform">
              <span
                className={`inline-block transition-transform ${expanded ? 'rotate-90' : ''}`}
              >
                ▶
              </span>
            </button>
          </div>
        </div>
      </div>

      {expanded && (
        <div className="border-t border-gray-700 p-4 bg-gray-800 space-y-4 animate-in slide-in-from-top">
          {/* Similarity Breakdown */}
          <SimilarityBreakdown factors={match.matching_factors} />

          {/* Expected Outcome */}
          <div className="bg-gray-750 rounded-lg p-4 border border-gray-700">
            <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
              <span>📊</span>
              <span>Expected Outcome</span>
            </h4>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <div className="text-xs text-gray-400 mb-1">Est. Return</div>
                <div className="text-green-400 font-bold text-lg">
                  +{(match.expected_outcome.return_estimate * 100).toFixed(0)}%
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-400 mb-1">Est. Duration</div>
                <div className="text-white font-semibold">
                  {match.expected_outcome.duration_estimate} days
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-400 mb-1">Confidence</div>
                <div className="text-blue-400 font-semibold">
                  {(match.expected_outcome.confidence * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          </div>

          {/* Historical Success Rate */}
          <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">Historical Success Rate:</span>
              <span className="text-white font-bold">
                {(match.expected_outcome.historical_success_rate * 100).toFixed(0)}%
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-2">
              Based on{' '}
              {Math.round(match.expected_outcome.historical_success_rate * 30)} of 30 similar
              historical patterns
            </p>
          </div>

          {/* Current Position in Pattern */}
          <div className="bg-gray-750 rounded-lg p-4 border border-gray-700">
            <div className="text-sm text-gray-400 mb-2">Pattern Timeline:</div>
            <div className="flex items-center space-x-2">
              <div className="flex-1 bg-gray-700 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{
                    width: `${(match.days_into_pattern / referencePattern.duration) * 100}%`,
                  }}
                />
              </div>
              <span className="text-white text-sm font-semibold">
                Day {match.days_into_pattern}/{referencePattern.duration}
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-2">
              Reference pattern was at this point {match.days_into_pattern} days before peak
            </p>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-2 gap-3">
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center justify-center space-x-2">
              <span>📊</span>
              <span>View Chart</span>
            </button>
            <button className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center justify-center space-x-2">
              <span>📝</span>
              <span>Add to Watchlist</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
