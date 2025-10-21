/**
 * Journal Card - Displays individual trade review card
 */

import { Star, TrendingUp, TrendingDown, Calendar, Target, StopCircle, Clock, Hand } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import type { JournalEntry } from '../../services/mock-data/journal-data';

interface JournalCardProps {
  entry: JournalEntry;
}

export function JournalCard({ entry }: JournalCardProps) {
  const navigate = useNavigate();
  const isProfit = entry.pnl >= 0;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getExitReasonIcon = () => {
    switch (entry.exitReason) {
      case 'target':
        return <Target className="w-4 h-4" />;
      case 'stop':
        return <StopCircle className="w-4 h-4" />;
      case 'time':
        return <Clock className="w-4 h-4" />;
      case 'manual':
        return <Hand className="w-4 h-4" />;
    }
  };

  const getExitReasonColor = () => {
    switch (entry.exitReason) {
      case 'target':
        return 'bg-green-900/30 text-green-400 border-green-700';
      case 'stop':
        return 'bg-red-900/30 text-red-400 border-red-700';
      case 'time':
        return 'bg-blue-900/30 text-blue-400 border-blue-700';
      case 'manual':
        return 'bg-yellow-900/30 text-yellow-400 border-yellow-700';
    }
  };

  return (
    <div
      onClick={() => navigate(`/journal/${entry.id}`)}
      className="bg-dark-card border border-dark-border rounded-lg p-5 hover:border-dark-border-hover transition cursor-pointer"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-xl font-bold text-white mb-1">{entry.symbol}</h3>
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <Calendar className="w-4 h-4" />
            <span>{formatDate(entry.entryDate)}</span>
            <span>→</span>
            <span>{formatDate(entry.exitDate)}</span>
            <span className="text-gray-500">({entry.holdingDays}d)</span>
          </div>
        </div>

        {/* Exit Reason Badge */}
        <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded border text-xs font-medium ${getExitReasonColor()}`}>
          {getExitReasonIcon()}
          <span className="capitalize">{entry.exitReason}</span>
        </div>
      </div>

      {/* P&L */}
      <div className="mb-3">
        <div className={`flex items-center gap-2 text-2xl font-bold ${isProfit ? 'text-green-400' : 'text-red-400'}`}>
          {isProfit ? <TrendingUp className="w-6 h-6" /> : <TrendingDown className="w-6 h-6" />}
          <span>${Math.abs(entry.pnl).toLocaleString()}</span>
          <span className="text-lg">({entry.pnlPct >= 0 ? '+' : ''}{entry.pnlPct}%)</span>
        </div>
        <div className="text-sm text-gray-400 mt-1">
          R:R {entry.rrRatio.toFixed(1)} • Risk ${entry.riskAmount.toLocaleString()}
        </div>
      </div>

      {/* Rating */}
      <div className="flex items-center gap-3 mb-3 pb-3 border-b border-dark-border">
        <div className="flex items-center gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <Star
              key={star}
              className={`w-4 h-4 ${star <= entry.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-600'}`}
            />
          ))}
        </div>
        <div className="text-xs text-gray-400">
          Setup: {entry.setupQuality}/5 • Execution: {entry.executionQuality}/5
        </div>
      </div>

      {/* Tags */}
      {entry.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {entry.tags.map((tag) => (
            <span
              key={tag}
              className="px-2 py-1 bg-dark-bg rounded text-xs font-medium text-gray-300"
            >
              #{tag}
            </span>
          ))}
        </div>
      )}

      {/* Notes Preview */}
      {entry.notes && (
        <p className="text-sm text-gray-400 line-clamp-2">
          {entry.notes}
        </p>
      )}

      {/* Mistakes/Lessons Indicator */}
      {(entry.mistakes.length > 0 || entry.lessonsLearned.length > 0) && (
        <div className="mt-3 pt-3 border-t border-dark-border flex gap-4 text-xs">
          {entry.mistakes.length > 0 && (
            <span className="text-red-400">
              {entry.mistakes.length} mistake{entry.mistakes.length !== 1 ? 's' : ''}
            </span>
          )}
          {entry.lessonsLearned.length > 0 && (
            <span className="text-blue-400">
              {entry.lessonsLearned.length} lesson{entry.lessonsLearned.length !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
