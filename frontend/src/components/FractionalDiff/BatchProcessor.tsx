/**
 * Batch Processor Component
 * Transform multiple tickers at once
 */

import { useState } from 'react';
import { Loader, Info, Plus, Trash2, Download, CheckCircle, XCircle } from 'lucide-react';
import { fractionalDiffApi, type BatchParams } from '../../api/fractionalDiffApi';

interface BatchResult {
  ticker: string;
  success: boolean;
  error?: string;
  stationarity?: {
    is_stationary: boolean;
    p_value: number;
  };
  memory_retained?: number;
}

interface BatchResults {
  processed: number;
  successful: number;
  failed: number;
  results: BatchResult[];
}

export function BatchProcessor() {
  const [tickers, setTickers] = useState<string[]>(['SPY', 'QQQ', 'IWM']);
  const [newTicker, setNewTicker] = useState('');
  const [dValue, setDValue] = useState(0.5);
  const [startDate, setStartDate] = useState('2020-01-01');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<BatchResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  const addTicker = () => {
    const ticker = newTicker.toUpperCase().trim();
    if (ticker && !tickers.includes(ticker)) {
      setTickers([...tickers, ticker]);
      setNewTicker('');
    }
  };

  const removeTicker = (ticker: string) => {
    setTickers(tickers.filter((t) => t !== ticker));
  };

  const loadFromFile = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const lines = text.split('\n').map((line) => line.trim().toUpperCase()).filter(Boolean);
      const uniqueTickers = [...new Set([...tickers, ...lines])];
      setTickers(uniqueTickers);
    };
    reader.readAsText(file);
  };

  const handleBatchTransform = async () => {
    if (tickers.length === 0) {
      setError('Please add at least one ticker to process');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await fractionalDiffApi.batchTransform({
        tickers,
        d: dValue,
        start_date: startDate,
      });
      setResults(data);
    } catch (err: any) {
      setError(err.message || 'Backend not running! Start: python backend/fracdiff_service/app.py');
    } finally {
      setLoading(false);
    }
  };

  const downloadResults = () => {
    if (!results) return;

    const csvContent = [
      ['Ticker', 'Success', 'Stationary', 'p-value', 'Memory Retained', 'Error'].join(','),
      ...results.results.map((r) =>
        [
          r.ticker,
          r.success,
          r.stationarity?.is_stationary || '',
          r.stationarity?.p_value?.toFixed(4) || '',
          r.memory_retained ? (r.memory_retained * 100).toFixed(1) + '%' : '',
          r.error || '',
        ].join(',')
      ),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `batch_fracdiff_d${dValue.toFixed(2)}_${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Configuration Panel */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h2 className="text-2xl font-semibold text-white mb-4">Batch Processing</h2>

        <p className="text-gray-300 mb-6">
          Transform multiple tickers at once with the same d value. Perfect for portfolio-wide analysis.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* d Value Slider */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Differentiation Order (d): <span className="text-blue-400 font-mono">{dValue.toFixed(2)}</span>
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={dValue}
              onChange={(e) => setDValue(parseFloat(e.target.value))}
              className="w-full h-2 bg-dark-bg rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Start Date */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {/* Tickers Manager */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium text-gray-300">
              Tickers ({tickers.length})
            </label>
            <label className="text-sm text-blue-400 cursor-pointer hover:text-blue-300">
              <input
                type="file"
                accept=".txt,.csv"
                onChange={loadFromFile}
                className="hidden"
              />
              Import from file
            </label>
          </div>

          {/* Current Tickers */}
          <div className="flex flex-wrap gap-2 mb-3 max-h-40 overflow-y-auto">
            {tickers.map((ticker) => (
              <div
                key={ticker}
                className="flex items-center gap-2 bg-blue-900/30 border border-blue-700 rounded-lg px-3 py-1"
              >
                <span className="text-blue-400 font-mono font-semibold">{ticker}</span>
                <button
                  onClick={() => removeTicker(ticker)}
                  className="text-blue-400 hover:text-red-400 transition"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>

          {/* Add New Ticker */}
          <div className="flex gap-2">
            <input
              type="text"
              value={newTicker}
              onChange={(e) => setNewTicker(e.target.value)}
              className="flex-1 px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-blue-500"
              placeholder="Enter ticker symbol"
              onKeyPress={(e) => e.key === 'Enter' && addTicker()}
            />
            <button
              onClick={addTicker}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add
            </button>
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mb-4 bg-red-900/30 border border-red-700 rounded-lg p-4">
            <div className="flex items-center gap-2 text-red-400">
              <Info className="w-5 h-5" />
              <span className="font-semibold">{error}</span>
            </div>
          </div>
        )}

        {/* Action Button */}
        <button
          onClick={handleBatchTransform}
          disabled={loading || tickers.length === 0}
          className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Processing {tickers.length} tickers...
            </>
          ) : (
            <>Process {tickers.length} Tickers</>
          )}
        </button>
      </div>

      {/* Results Display */}
      {results && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Total Processed</div>
              <div className="text-3xl font-bold text-white">{results.processed}</div>
            </div>

            <div className="bg-dark-card border border-green-700 rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Successful</div>
              <div className="text-3xl font-bold text-green-400">{results.successful}</div>
            </div>

            <div className="bg-dark-card border border-red-700 rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Failed</div>
              <div className="text-3xl font-bold text-red-400">{results.failed}</div>
            </div>
          </div>

          {/* Results Table */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-white">Processing Results</h3>
              <button
                onClick={downloadResults}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-medium transition"
              >
                <Download className="w-4 h-4" />
                Download CSV
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-400 border-b border-dark-border">
                    <th className="pb-3">Status</th>
                    <th className="pb-3">Ticker</th>
                    <th className="pb-3 text-right">Stationary</th>
                    <th className="pb-3 text-right">p-value</th>
                    <th className="pb-3 text-right">Memory</th>
                    <th className="pb-3">Message</th>
                  </tr>
                </thead>
                <tbody>
                  {results.results.map((result, index) => (
                    <tr key={index} className="border-b border-dark-border">
                      <td className="py-3">
                        {result.success ? (
                          <CheckCircle className="w-5 h-5 text-green-400" />
                        ) : (
                          <XCircle className="w-5 h-5 text-red-400" />
                        )}
                      </td>
                      <td className="py-3">
                        <span className="text-white font-mono font-semibold">
                          {result.ticker}
                        </span>
                      </td>
                      <td className="py-3 text-right">
                        {result.stationarity && (
                          <span
                            className={`px-2 py-1 rounded text-xs font-semibold ${
                              result.stationarity.is_stationary
                                ? 'bg-green-900/30 text-green-400'
                                : 'bg-red-900/30 text-red-400'
                            }`}
                          >
                            {result.stationarity.is_stationary ? '✓' : '✗'}
                          </span>
                        )}
                      </td>
                      <td className="py-3 text-right text-white font-mono">
                        {result.stationarity?.p_value.toFixed(4) || '-'}
                      </td>
                      <td className="py-3 text-right">
                        {result.memory_retained !== undefined && (
                          <span className="text-green-400 font-mono font-semibold">
                            {(result.memory_retained * 100).toFixed(1)}%
                          </span>
                        )}
                      </td>
                      <td className="py-3 text-gray-400 text-xs">
                        {result.error || 'Success'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Success Rate Summary */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h4 className="text-lg font-medium text-white mb-4">Success Rate</h4>
            <div className="flex items-center gap-4">
              <div className="flex-1 bg-dark-bg rounded-full h-6 overflow-hidden">
                <div
                  className="bg-green-500 h-6 rounded-full transition-all duration-500"
                  style={{ width: `${(results.successful / results.processed) * 100}%` }}
                />
              </div>
              <span className="text-2xl font-bold text-green-400 min-w-[80px] text-right">
                {((results.successful / results.processed) * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          {/* Stationarity Distribution */}
          {results.successful > 0 && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h4 className="text-lg font-medium text-white mb-4">Stationarity Distribution</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-green-900/20 border border-green-700 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">Stationary</div>
                  <div className="text-3xl font-bold text-green-400">
                    {results.results.filter((r) => r.stationarity?.is_stationary).length}
                  </div>
                </div>
                <div className="bg-red-900/20 border border-red-700 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">Non-Stationary</div>
                  <div className="text-3xl font-bold text-red-400">
                    {results.results.filter((r) => r.stationarity && !r.stationarity.is_stationary).length}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
