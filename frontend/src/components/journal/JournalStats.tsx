/**
 * Journal Stats - Displays summary statistics for journal entries
 */

import { TrendingUp, Target, Star, ThumbsUp, ThumbsDown, AlertCircle } from 'lucide-react';
import type { JournalStats as JournalStatsType } from '../../services/mock-data/journal-data';

interface JournalStatsProps {
  stats: JournalStatsType;
}

export function JournalStats({ stats }: JournalStatsProps) {
  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      {/* Main Stats Grid */}
      <div className="grid grid-cols-6 gap-6 mb-6">
        {/* Total Trades */}
        <div className="text-center">
          <div className="text-3xl font-bold text-white mb-1">
            {stats.totalTrades}
          </div>
          <div className="text-sm text-gray-400">Total Trades</div>
        </div>

        {/* Win Rate */}
        <div className="text-center">
          <div className="flex items-center justify-center gap-1 mb-1">
            <Target className="w-5 h-5 text-green-400" />
            <span className="text-3xl font-bold text-green-400">
              {stats.winRate.toFixed(1)}%
            </span>
          </div>
          <div className="text-sm text-gray-400">Win Rate</div>
        </div>

        {/* Avg R:R */}
        <div className="text-center">
          <div className="flex items-center justify-center gap-1 mb-1">
            <TrendingUp className="w-5 h-5 text-blue-400" />
            <span className="text-3xl font-bold text-blue-400">
              {stats.avgRR.toFixed(1)}
            </span>
          </div>
          <div className="text-sm text-gray-400">Avg R:R</div>
        </div>

        {/* Avg Win */}
        <div className="text-center">
          <div className="flex items-center justify-center gap-1 mb-1">
            <ThumbsUp className="w-5 h-5 text-green-400" />
            <span className="text-3xl font-bold text-green-400">
              ${Math.abs(stats.avgWin).toLocaleString()}
            </span>
          </div>
          <div className="text-sm text-gray-400">Avg Win</div>
        </div>

        {/* Avg Loss */}
        <div className="text-center">
          <div className="flex items-center justify-center gap-1 mb-1">
            <ThumbsDown className="w-5 h-5 text-red-400" />
            <span className="text-3xl font-bold text-red-400">
              ${Math.abs(stats.avgLoss).toLocaleString()}
            </span>
          </div>
          <div className="text-sm text-gray-400">Avg Loss</div>
        </div>

        {/* Avg Rating */}
        <div className="text-center">
          <div className="flex items-center justify-center gap-1 mb-1">
            <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />
            <span className="text-3xl font-bold text-yellow-400">
              {stats.avgRating.toFixed(1)}
            </span>
          </div>
          <div className="text-sm text-gray-400">Avg Rating</div>
        </div>
      </div>

      {/* Quality Metrics */}
      <div className="grid grid-cols-2 gap-6 mb-6 pb-6 border-b border-dark-border">
        <div className="flex items-center justify-between px-4 py-3 bg-dark-bg rounded">
          <span className="text-gray-400">Setup Quality</span>
          <div className="flex items-center gap-2">
            <div className="flex gap-0.5">
              {[1, 2, 3, 4, 5].map((star) => (
                <Star
                  key={star}
                  className={`w-3.5 h-3.5 ${
                    star <= Math.round(stats.avgSetupQuality)
                      ? 'fill-yellow-400 text-yellow-400'
                      : 'text-gray-600'
                  }`}
                />
              ))}
            </div>
            <span className="text-white font-semibold">{stats.avgSetupQuality.toFixed(1)}/5</span>
          </div>
        </div>

        <div className="flex items-center justify-between px-4 py-3 bg-dark-bg rounded">
          <span className="text-gray-400">Execution Quality</span>
          <div className="flex items-center gap-2">
            <div className="flex gap-0.5">
              {[1, 2, 3, 4, 5].map((star) => (
                <Star
                  key={star}
                  className={`w-3.5 h-3.5 ${
                    star <= Math.round(stats.avgExecutionQuality)
                      ? 'fill-yellow-400 text-yellow-400'
                      : 'text-gray-600'
                  }`}
                />
              ))}
            </div>
            <span className="text-white font-semibold">{stats.avgExecutionQuality.toFixed(1)}/5</span>
          </div>
        </div>
      </div>

      {/* Top Tags */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-400 mb-3">Top Performing Tags</h3>
        <div className="grid grid-cols-4 gap-3">
          {stats.topTags.map((tag) => (
            <div
              key={tag.tag}
              className="px-3 py-2 bg-dark-bg rounded border border-dark-border"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-white">#{tag.tag}</span>
                <span className="text-xs text-green-400">{tag.winRate.toFixed(1)}%</span>
              </div>
              <div className="text-xs text-gray-400">{tag.count} trades</div>
            </div>
          ))}
        </div>
      </div>

      {/* Common Mistakes */}
      <div>
        <h3 className="text-sm font-semibold text-gray-400 mb-3 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-400" />
          Common Mistakes to Avoid
        </h3>
        <div className="grid grid-cols-3 gap-3">
          {stats.commonMistakes.map((mistake) => (
            <div
              key={mistake.mistake}
              className="px-3 py-2 bg-red-900/10 rounded border border-red-900/30"
            >
              <div className="text-sm font-medium text-red-400 mb-1">
                {mistake.mistake}
              </div>
              <div className="text-xs text-gray-400">{mistake.count} occurrences</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
