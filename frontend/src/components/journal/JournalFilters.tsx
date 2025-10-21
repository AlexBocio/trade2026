/**
 * Journal Filters - Filter controls for journal entries
 */

import { Calendar, Tag, Target, Star, X } from 'lucide-react';
import { useState } from 'react';

interface JournalFiltersProps {
  onFilterChange: (filters: {
    dateRange: { start: Date; end: Date } | null;
    tags: string[];
    exitReason: 'target' | 'stop' | 'time' | 'manual' | null;
    minRating: number | null;
  }) => void;
  availableTags: string[];
}

export function JournalFilters({ onFilterChange, availableTags }: JournalFiltersProps) {
  const [dateRange, setDateRange] = useState<{ start: Date; end: Date } | null>(null);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [exitReason, setExitReason] = useState<'target' | 'stop' | 'time' | 'manual' | null>(null);
  const [minRating, setMinRating] = useState<number | null>(null);

  const handleDateRangeChange = (type: 'start' | 'end', value: string) => {
    const newDateRange = dateRange || { start: new Date(), end: new Date() };
    if (type === 'start') {
      newDateRange.start = new Date(value);
    } else {
      newDateRange.end = new Date(value);
    }
    setDateRange(newDateRange);
    onFilterChange({ dateRange: newDateRange, tags: selectedTags, exitReason, minRating });
  };

  const handleTagToggle = (tag: string) => {
    const newTags = selectedTags.includes(tag)
      ? selectedTags.filter((t) => t !== tag)
      : [...selectedTags, tag];
    setSelectedTags(newTags);
    onFilterChange({ dateRange, tags: newTags, exitReason, minRating });
  };

  const handleExitReasonChange = (reason: 'target' | 'stop' | 'time' | 'manual' | null) => {
    setExitReason(reason);
    onFilterChange({ dateRange, tags: selectedTags, exitReason: reason, minRating });
  };

  const handleMinRatingChange = (rating: number | null) => {
    setMinRating(rating);
    onFilterChange({ dateRange, tags: selectedTags, exitReason, minRating: rating });
  };

  const handleReset = () => {
    setDateRange(null);
    setSelectedTags([]);
    setExitReason(null);
    setMinRating(null);
    onFilterChange({ dateRange: null, tags: [], exitReason: null, minRating: null });
  };

  const hasActiveFilters = dateRange || selectedTags.length > 0 || exitReason || minRating;

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-400 flex items-center gap-2">
          <Target className="w-4 h-4" />
          Filters
        </h3>
        {hasActiveFilters && (
          <button
            onClick={handleReset}
            className="text-xs text-gray-400 hover:text-white flex items-center gap-1 transition"
          >
            <X className="w-3 h-3" />
            Clear All
          </button>
        )}
      </div>

      <div className="space-y-4">
        {/* Date Range */}
        <div>
          <label className="text-xs text-gray-400 mb-2 flex items-center gap-2">
            <Calendar className="w-3.5 h-3.5" />
            Date Range
          </label>
          <div className="grid grid-cols-2 gap-2">
            <input
              type="date"
              value={dateRange?.start.toISOString().split('T')[0] || ''}
              onChange={(e) => handleDateRangeChange('start', e.target.value)}
              className="px-3 py-2 bg-dark-bg border border-dark-border rounded text-sm text-white focus:outline-none focus:border-green-600"
            />
            <input
              type="date"
              value={dateRange?.end.toISOString().split('T')[0] || ''}
              onChange={(e) => handleDateRangeChange('end', e.target.value)}
              className="px-3 py-2 bg-dark-bg border border-dark-border rounded text-sm text-white focus:outline-none focus:border-green-600"
            />
          </div>
        </div>

        {/* Tags */}
        <div>
          <label className="text-xs text-gray-400 mb-2 flex items-center gap-2">
            <Tag className="w-3.5 h-3.5" />
            Tags
          </label>
          <div className="flex flex-wrap gap-2">
            {availableTags.map((tag) => (
              <button
                key={tag}
                onClick={() => handleTagToggle(tag)}
                className={`px-2.5 py-1.5 rounded text-xs font-medium transition ${
                  selectedTags.includes(tag)
                    ? 'bg-green-600 text-white'
                    : 'bg-dark-bg text-gray-400 hover:bg-dark-border'
                }`}
              >
                #{tag}
              </button>
            ))}
          </div>
        </div>

        {/* Exit Reason */}
        <div>
          <label className="text-xs text-gray-400 mb-2 flex items-center gap-2">
            <Target className="w-3.5 h-3.5" />
            Exit Reason
          </label>
          <div className="grid grid-cols-4 gap-2">
            {(['target', 'stop', 'time', 'manual'] as const).map((reason) => (
              <button
                key={reason}
                onClick={() => handleExitReasonChange(exitReason === reason ? null : reason)}
                className={`px-3 py-2 rounded text-sm font-medium capitalize transition ${
                  exitReason === reason
                    ? 'bg-green-600 text-white'
                    : 'bg-dark-bg text-gray-400 hover:bg-dark-border'
                }`}
              >
                {reason}
              </button>
            ))}
          </div>
        </div>

        {/* Minimum Rating */}
        <div>
          <label className="text-xs text-gray-400 mb-2 flex items-center gap-2">
            <Star className="w-3.5 h-3.5" />
            Minimum Rating
          </label>
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5].map((rating) => (
              <button
                key={rating}
                onClick={() => handleMinRatingChange(minRating === rating ? null : rating)}
                className={`flex-1 px-3 py-2 rounded text-sm font-medium transition ${
                  minRating === rating
                    ? 'bg-yellow-600 text-white'
                    : 'bg-dark-bg text-gray-400 hover:bg-dark-border'
                }`}
              >
                <div className="flex items-center justify-center gap-1">
                  <Star className={`w-3.5 h-3.5 ${minRating === rating ? 'fill-white' : ''}`} />
                  {rating}+
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
