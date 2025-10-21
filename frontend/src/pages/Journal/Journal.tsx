/**
 * Journal - Main journal list page
 */

import { useEffect, useMemo } from 'react';
import { BookOpen, Plus } from 'lucide-react';
import { useJournalStore } from '../../store/useJournalStore';
import { JournalCard } from '../../components/journal/JournalCard';
import { JournalStats } from '../../components/journal/JournalStats';
import { JournalFilters } from '../../components/journal/JournalFilters';

export function Journal() {
  const { entries, filters, stats, isLoading, loadEntries, setFilters } = useJournalStore();

  useEffect(() => {
    loadEntries();
  }, [loadEntries]);

  // Get all unique tags from entries
  const availableTags = useMemo(() => {
    const tags = new Set<string>();
    entries.forEach((entry) => {
      entry.tags.forEach((tag) => tags.add(tag));
    });
    return Array.from(tags).sort();
  }, [entries]);

  // Filter entries based on active filters
  const filteredEntries = useMemo(() => {
    return entries.filter((entry) => {
      // Date range filter
      if (filters.dateRange) {
        const entryDate = new Date(entry.entryDate);
        if (entryDate < filters.dateRange.start || entryDate > filters.dateRange.end) {
          return false;
        }
      }

      // Tags filter
      if (filters.tags.length > 0) {
        const hasMatchingTag = filters.tags.some((tag) => entry.tags.includes(tag));
        if (!hasMatchingTag) {
          return false;
        }
      }

      // Exit reason filter
      if (filters.exitReason && entry.exitReason !== filters.exitReason) {
        return false;
      }

      // Minimum rating filter
      if (filters.minRating && entry.rating < filters.minRating) {
        return false;
      }

      return true;
    });
  }, [entries, filters]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading journal entries...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <BookOpen className="w-8 h-8 text-green-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">Trade Journal</h1>
            <p className="text-sm text-gray-400">
              Review and learn from your trades • {filteredEntries.length} of {entries.length} entries
            </p>
          </div>
        </div>

        <button className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition">
          <Plus className="w-5 h-5" />
          New Entry
        </button>
      </div>

      {/* Stats Overview */}
      <JournalStats stats={stats} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-4 gap-6">
        {/* Filters Sidebar */}
        <div className="col-span-1">
          <JournalFilters
            onFilterChange={(newFilters) => setFilters(newFilters)}
            availableTags={availableTags}
          />
        </div>

        {/* Journal Cards Grid */}
        <div className="col-span-3">
          {filteredEntries.length === 0 ? (
            <div className="bg-dark-card border border-dark-border rounded-lg p-12 text-center">
              <BookOpen className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-400 mb-2">No journal entries found</h3>
              <p className="text-gray-500 mb-6">
                {entries.length === 0
                  ? 'Start documenting your trades to build your trading edge'
                  : 'Try adjusting your filters to see more entries'}
              </p>
              <button className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition">
                Create Your First Entry
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {filteredEntries.map((entry) => (
                <JournalCard key={entry.id} entry={entry} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
