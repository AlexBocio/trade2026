/**
 * News - Real-time market news and catalysts feed
 */

import { useEffect, useMemo } from 'react';
import { Newspaper, RefreshCw, TrendingUp, TrendingDown, Minus, AlertCircle, ExternalLink } from 'lucide-react';
import { useNewsStore } from '../../store/useNewsStore';
import { EconomicCalendar } from '../../components/news/EconomicCalendar';
import { EarningsCalendar } from '../../components/news/EarningsCalendar';

export function News() {
  const { articles, stats, isLoading, filter, sentiment, loadNews, setFilter, setSentiment, refreshNews } =
    useNewsStore();

  useEffect(() => {
    loadNews();

    // Auto-refresh news every 60 seconds
    const interval = setInterval(() => {
      loadNews();
    }, 60000);

    return () => clearInterval(interval);
  }, [loadNews]);

  // Filter articles
  const filteredArticles = useMemo(() => {
    return articles.filter((article) => {
      if (filter !== 'all' && article.category !== filter) {
        return false;
      }
      if (sentiment !== 'all' && article.sentiment !== sentiment) {
        return false;
      }
      return true;
    });
  }, [articles, filter, sentiment]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

    if (diffHours < 1) {
      const diffMinutes = Math.floor(diffMs / (1000 * 60));
      return `${diffMinutes}m ago`;
    }
    if (diffHours < 24) {
      return `${diffHours}h ago`;
    }
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  const getSentimentIcon = (s: string) => {
    switch (s) {
      case 'positive':
        return <TrendingUp className="w-4 h-4 text-green-400" />;
      case 'negative':
        return <TrendingDown className="w-4 h-4 text-red-400" />;
      default:
        return <Minus className="w-4 h-4 text-gray-400" />;
    }
  };

  const getSentimentColor = (s: string) => {
    switch (s) {
      case 'positive':
        return 'bg-green-900/30 text-green-400 border-green-700';
      case 'negative':
        return 'bg-red-900/30 text-red-400 border-red-700';
      default:
        return 'bg-gray-900/30 text-gray-400 border-gray-700';
    }
  };

  if (isLoading && articles.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading news...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Newspaper className="w-8 h-8 text-green-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">News Feed</h1>
            <p className="text-sm text-gray-400">
              Real-time market news and catalysts • {stats.breakingNews} breaking stories
            </p>
          </div>
        </div>

        <button
          onClick={refreshNews}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition"
        >
          <RefreshCw className="w-5 h-5" />
          Refresh
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-6 gap-4">
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-3xl font-bold text-white mb-1">{stats.totalArticles}</div>
          <div className="text-sm text-gray-400">Articles</div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-1">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <span className="text-3xl font-bold text-red-400">{stats.breakingNews}</span>
          </div>
          <div className="text-sm text-gray-400">Breaking</div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="w-5 h-5 text-green-400" />
            <span className="text-3xl font-bold text-green-400">{stats.positiveNews}</span>
          </div>
          <div className="text-sm text-gray-400">Positive</div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-1">
            <TrendingDown className="w-5 h-5 text-red-400" />
            <span className="text-3xl font-bold text-red-400">{stats.negativeNews}</span>
          </div>
          <div className="text-sm text-gray-400">Negative</div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-1">
            <Minus className="w-5 h-5 text-gray-400" />
            <span className="text-3xl font-bold text-gray-400">{stats.neutralNews}</span>
          </div>
          <div className="text-sm text-gray-400">Neutral</div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-2xl font-bold text-white mb-1">{stats.mostMentionedSymbol}</div>
          <div className="text-sm text-gray-400">Top Symbol</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        {/* Category Filter */}
        <div className="flex gap-2 bg-dark-card border border-dark-border rounded-lg p-2 flex-1">
          {(['all', 'market', 'stock', 'earnings', 'fda', 'macro'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`flex-1 px-3 py-2 rounded font-medium text-sm capitalize transition ${
                filter === f
                  ? 'bg-green-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-dark-border'
              }`}
            >
              {f}
            </button>
          ))}
        </div>

        {/* Sentiment Filter */}
        <div className="flex gap-2 bg-dark-card border border-dark-border rounded-lg p-2">
          {(['all', 'positive', 'negative', 'neutral'] as const).map((s) => (
            <button
              key={s}
              onClick={() => setSentiment(s)}
              className={`px-3 py-2 rounded font-medium text-sm capitalize transition ${
                sentiment === s
                  ? 'bg-green-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-dark-border'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Layout Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* News Articles - Left Side (2 columns) */}
        <div className="col-span-2 space-y-4">
          {filteredArticles.length === 0 ? (
            <div className="bg-dark-card border border-dark-border rounded-lg p-12 text-center">
              <Newspaper className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-400 mb-2">No news articles found</h3>
              <p className="text-gray-500">Try adjusting your filters</p>
            </div>
          ) : (
            <div className="space-y-4">
          {filteredArticles.map((article) => (
            <div
              key={article.id}
              className={`bg-dark-card border rounded-lg p-6 hover:border-dark-border-hover transition ${
                article.isBreaking ? 'border-red-700 bg-red-900/10' : 'border-dark-border'
              }`}
            >
              <div className="flex gap-4">
                {/* Image */}
                {article.imageUrl && (
                  <div className="flex-shrink-0 w-48 h-32 rounded overflow-hidden bg-dark-bg">
                    <img
                      src={article.imageUrl}
                      alt={article.title}
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}

                {/* Content */}
                <div className="flex-1">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      {article.isBreaking && (
                        <span className="px-2 py-1 bg-red-600 text-white rounded text-xs font-bold uppercase">
                          Breaking
                        </span>
                      )}
                      <span className="px-2 py-1 bg-dark-bg rounded text-xs font-medium text-gray-300 capitalize">
                        {article.category}
                      </span>
                      <div className={`flex items-center gap-1 px-2 py-1 rounded border text-xs ${getSentimentColor(article.sentiment)}`}>
                        {getSentimentIcon(article.sentiment)}
                        <span className="capitalize">{article.sentiment}</span>
                      </div>
                    </div>

                    <span className="text-sm text-gray-400">{formatDate(article.publishedAt)}</span>
                  </div>

                  {/* Title */}
                  <h3 className="text-xl font-bold text-white mb-2">{article.title}</h3>

                  {/* Summary */}
                  <p className="text-gray-300 mb-3">{article.summary}</p>

                  {/* Footer */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 text-sm text-gray-400">
                      <span>{article.source}</span>
                      {article.author && <span>• {article.author}</span>}
                      {article.symbols.length > 0 && (
                        <div className="flex gap-1">
                          {article.symbols.map((symbol) => (
                            <span key={symbol} className="px-2 py-0.5 bg-blue-900/30 text-blue-400 rounded text-xs font-semibold">
                              ${symbol}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <a
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 px-3 py-1.5 bg-dark-border hover:bg-dark-border-hover rounded text-sm font-medium transition"
                    >
                      Read More
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>

                  {/* Tags */}
                  {article.tags.length > 0 && (
                    <div className="flex gap-2 mt-3">
                      {article.tags.map((tag) => (
                        <span key={tag} className="px-2 py-0.5 bg-dark-bg rounded text-xs text-gray-400">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
        )}
      </div>

        {/* Right Sidebar - Calendars */}
        <div className="space-y-6">
          <EconomicCalendar />
          <EarningsCalendar />
        </div>
      </div>
    </div>
  );
}
