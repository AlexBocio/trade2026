/**
 * Journal Detail - Detailed view of a single trade journal entry
 */

import { useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Calendar,
  TrendingUp,
  TrendingDown,
  Target,
  StopCircle,
  Clock,
  Hand,
  Star,
  Edit,
  Trash2,
  AlertCircle,
  Lightbulb,
  Tag,
} from 'lucide-react';
import { createChart } from 'lightweight-charts';
import { useJournalStore } from '../../store/useJournalStore';

export function JournalDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<ReturnType<typeof createChart> | null>(null);

  const { getEntry, deleteEntry } = useJournalStore();
  const entry = getEntry(id || '');

  useEffect(() => {
    if (!entry || !chartContainerRef.current) return;

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: '#1a1a1a' },
        textColor: '#9ca3af',
      },
      grid: {
        vertLines: { color: '#2a2a2a' },
        horzLines: { color: '#2a2a2a' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 400,
    });

    // Generate sample price data for the trade
    const generatePriceData = () => {
      const data = [];
      const entryTime = new Date(entry.entryDate).getTime() / 1000;
      const exitTime = new Date(entry.exitDate).getTime() / 1000;
      const duration = exitTime - entryTime;
      const steps = 100;
      const stepSize = duration / steps;

      for (let i = 0; i <= steps; i++) {
        const time = entryTime + i * stepSize;
        const progress = i / steps;
        const priceChange = entry.exitPrice - entry.entryPrice;
        const volatility = Math.abs(priceChange) * 0.3;
        const randomWalk = Math.sin(progress * Math.PI * 4) * volatility;
        const price = entry.entryPrice + priceChange * progress + randomWalk;

        data.push({
          time: time as any,
          value: price,
        });
      }
      return data;
    };

    const candlestickSeries = chart.addLineSeries({
      color: entry.pnl >= 0 ? '#10b981' : '#ef4444',
      lineWidth: 2,
    });

    candlestickSeries.setData(generatePriceData());

    // Add entry price line
    const entryPriceLine = candlestickSeries.createPriceLine({
      price: entry.entryPrice,
      color: '#3b82f6',
      lineWidth: 2,
      lineStyle: 2, // dashed
      axisLabelVisible: true,
      title: 'Entry',
    });

    // Add exit price line
    const exitPriceLine = candlestickSeries.createPriceLine({
      price: entry.exitPrice,
      color: entry.pnl >= 0 ? '#10b981' : '#ef4444',
      lineWidth: 2,
      lineStyle: 2,
      axisLabelVisible: true,
      title: 'Exit',
    });

    // Add stop loss line
    const stopLossLine = candlestickSeries.createPriceLine({
      price: entry.stopLoss,
      color: '#ef4444',
      lineWidth: 1,
      lineStyle: 3, // dotted
      axisLabelVisible: true,
      title: 'Stop',
    });

    // Add profit target line
    const targetLine = candlestickSeries.createPriceLine({
      price: entry.profitTarget,
      color: '#10b981',
      lineWidth: 1,
      lineStyle: 3,
      axisLabelVisible: true,
      title: 'Target',
    });

    chart.timeScale().fitContent();

    chartRef.current = chart;

    // Cleanup
    return () => {
      chart.remove();
    };
  }, [entry]);

  const handleDelete = async () => {
    if (!entry) return;
    if (confirm(`Delete journal entry for ${entry.symbol}?`)) {
      await deleteEntry(entry.id);
      navigate('/journal');
    }
  };

  if (!entry) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-400 mb-2">Journal entry not found</h2>
          <Link
            to="/journal"
            className="text-green-400 hover:text-green-300 flex items-center gap-2 justify-center"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Journal
          </Link>
        </div>
      </div>
    );
  }

  const isProfit = entry.pnl >= 0;

  const getExitReasonIcon = () => {
    switch (entry.exitReason) {
      case 'target':
        return <Target className="w-5 h-5" />;
      case 'stop':
        return <StopCircle className="w-5 h-5" />;
      case 'time':
        return <Clock className="w-5 h-5" />;
      case 'manual':
        return <Hand className="w-5 h-5" />;
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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            to="/journal"
            className="p-2 hover:bg-dark-border rounded-lg transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-white mb-1">{entry.symbol}</h1>
            <div className="flex items-center gap-3 text-sm text-gray-400">
              <Calendar className="w-4 h-4" />
              <span>
                {new Date(entry.entryDate).toLocaleDateString()} → {new Date(entry.exitDate).toLocaleDateString()}
              </span>
              <span className="text-gray-500">({entry.holdingDays} days)</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-dark-border hover:bg-dark-border-hover rounded-lg transition">
            <Edit className="w-4 h-4" />
            Edit
          </button>
          <button
            onClick={handleDelete}
            className="flex items-center gap-2 px-4 py-2 bg-red-900/30 hover:bg-red-900/50 text-red-400 rounded-lg transition"
          >
            <Trash2 className="w-4 h-4" />
            Delete
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left Column - Chart and Details */}
        <div className="col-span-2 space-y-6">
          {/* P&L Summary */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <div className={`flex items-center gap-3 text-3xl font-bold ${isProfit ? 'text-green-400' : 'text-red-400'}`}>
                {isProfit ? <TrendingUp className="w-8 h-8" /> : <TrendingDown className="w-8 h-8" />}
                <span>${Math.abs(entry.pnl).toLocaleString()}</span>
                <span className="text-xl">({entry.pnlPct >= 0 ? '+' : ''}{entry.pnlPct}%)</span>
              </div>

              <div className={`flex items-center gap-2 px-4 py-2 rounded border ${getExitReasonColor()}`}>
                {getExitReasonIcon()}
                <span className="font-medium capitalize">{entry.exitReason}</span>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-4 text-sm">
              <div>
                <div className="text-gray-400 mb-1">Entry Price</div>
                <div className="text-white font-semibold">${entry.entryPrice.toFixed(2)}</div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Exit Price</div>
                <div className="text-white font-semibold">${entry.exitPrice.toFixed(2)}</div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Stop Loss</div>
                <div className="text-red-400 font-semibold">${entry.stopLoss.toFixed(2)}</div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Target</div>
                <div className="text-green-400 font-semibold">${entry.profitTarget.toFixed(2)}</div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 text-sm mt-4 pt-4 border-t border-dark-border">
              <div>
                <div className="text-gray-400 mb-1">Quantity</div>
                <div className="text-white font-semibold">{entry.quantity.toLocaleString()} shares</div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Risk Amount</div>
                <div className="text-white font-semibold">${entry.riskAmount.toLocaleString()}</div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">R:R Ratio</div>
                <div className="text-blue-400 font-semibold">{entry.rrRatio.toFixed(1)}</div>
              </div>
            </div>
          </div>

          {/* Price Chart */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Price Chart</h2>
            <div ref={chartContainerRef} />
          </div>

          {/* Notes */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-3">Trade Notes</h2>
            <p className="text-gray-300 leading-relaxed">{entry.notes || 'No notes added.'}</p>
          </div>
        </div>

        {/* Right Column - Ratings and Insights */}
        <div className="space-y-6">
          {/* Ratings */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Ratings</h2>

            <div className="space-y-4">
              <div>
                <div className="text-sm text-gray-400 mb-2">Overall Rating</div>
                <div className="flex items-center gap-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star
                      key={star}
                      className={`w-6 h-6 ${
                        star <= entry.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-600'
                      }`}
                    />
                  ))}
                  <span className="text-yellow-400 font-semibold ml-2">{entry.rating}/5</span>
                </div>
              </div>

              <div className="pt-4 border-t border-dark-border">
                <div className="text-sm text-gray-400 mb-2">Setup Quality</div>
                <div className="flex items-center gap-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star
                      key={star}
                      className={`w-5 h-5 ${
                        star <= entry.setupQuality ? 'fill-blue-400 text-blue-400' : 'text-gray-600'
                      }`}
                    />
                  ))}
                  <span className="text-blue-400 font-semibold ml-2">{entry.setupQuality}/5</span>
                </div>
              </div>

              <div>
                <div className="text-sm text-gray-400 mb-2">Execution Quality</div>
                <div className="flex items-center gap-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star
                      key={star}
                      className={`w-5 h-5 ${
                        star <= entry.executionQuality ? 'fill-green-400 text-green-400' : 'text-gray-600'
                      }`}
                    />
                  ))}
                  <span className="text-green-400 font-semibold ml-2">{entry.executionQuality}/5</span>
                </div>
              </div>
            </div>
          </div>

          {/* Tags */}
          {entry.tags.length > 0 && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h2 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <Tag className="w-5 h-5" />
                Tags
              </h2>
              <div className="flex flex-wrap gap-2">
                {entry.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-3 py-1.5 bg-dark-bg rounded-lg text-sm font-medium text-gray-300"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Mistakes */}
          {entry.mistakes.length > 0 && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h2 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-red-400" />
                Mistakes
              </h2>
              <ul className="space-y-2">
                {entry.mistakes.map((mistake, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-red-300">
                    <span className="text-red-500 mt-1">•</span>
                    <span>{mistake}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Lessons Learned */}
          {entry.lessonsLearned.length > 0 && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h2 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-blue-400" />
                Lessons Learned
              </h2>
              <ul className="space-y-2">
                {entry.lessonsLearned.map((lesson, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-blue-300">
                    <span className="text-blue-500 mt-1">•</span>
                    <span>{lesson}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
