/**
 * Stock Screener Page
 * Advanced multi-factor stock screening with multi-timeframe prediction heatmap
 * Features: Export, Presets, Real-Time Updates, Comparison
 */

import { useState, useEffect } from 'react';
import { Search, Loader, ArrowLeft, TrendingUp, BarChart3, Save, FolderOpen, RefreshCw, GitCompare } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import io from 'socket.io-client';
import { screenerApi } from '../../api/screenerApi';
import type { ScreenerParams, ScanAndPredictResponse, HeatmapData } from '../../api/screenerApi';
import { StockCard } from '../../components/Screener/StockCard';
import { FactorBreakdown } from '../../components/Screener/FactorBreakdown';
import { ScreenResults } from '../../components/Screener/ScreenResults';
import { DualAxisHeatmap } from '../../components/Heatmap/DualAxisHeatmap';
import { ExportMenu } from '../../components/Screener/ExportMenu';
import { PresetManager } from '../../components/Screener/PresetManager';
import { ComparisonView } from '../../components/Screener/ComparisonView';

export function StockScreener() {
  const navigate = useNavigate();

  // Configuration State
  const [universe, setUniverse] = useState<ScreenerParams['universe']>('small_caps');
  const [timeframe, setTimeframe] = useState<ScreenerParams['timeframe']>('swing');
  const [maxResults, setMaxResults] = useState(50);
  const [minMomentum, setMinMomentum] = useState(10);
  const [maxRsi, setMaxRsi] = useState(30);
  const [minVolumeSurge, setMinVolumeSurge] = useState(1.5);

  // Results State
  const [scanResults, setScanResults] = useState<ScanAndPredictResponse | null>(null);
  const [heatmapData, setHeatmapData] = useState<HeatmapData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<'results' | 'heatmap' | 'compare'>('results');
  const [selectedStock, setSelectedStock] = useState<string | null>(null);

  // Real-Time Updates State
  const [socket, setSocket] = useState<any>(null);
  const [scanId, setScanId] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(5); // minutes
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);

  // Presets State
  const [showPresetManager, setShowPresetManager] = useState(false);
  const [presets, setPresets] = useState<any[]>([]);
  const [presetName, setPresetName] = useState('');
  const [presetDescription, setPresetDescription] = useState('');

  // Comparison State
  const [comparisonMode, setComparisonMode] = useState(false);
  const [scanA, setScanA] = useState<{ name: string; results: any[]; heatmap_data: HeatmapData } | null>(null);
  const [scanB, setScanB] = useState<{ name: string; results: any[]; heatmap_data: HeatmapData } | null>(null);

  // Load presets on mount
  useEffect(() => {
    const loadPresets = async () => {
      try {
        const response = await screenerApi.getPresets();
        setPresets(response.presets);
      } catch (err) {
        console.error('Failed to load presets:', err);
      }
    };
    loadPresets();
  }, []);

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (autoRefresh && scanId) {
      const newSocket = io('http://localhost:5008');

      newSocket.on('connect', () => {
        console.log('✅ Connected to screener WebSocket');
        newSocket.emit('subscribe_scan', { scan_id: scanId });
      });

      newSocket.on('scan_update', (data: ScanAndPredictResponse) => {
        console.log('📊 Received real-time update');
        setScanResults(data);
        setHeatmapData(data.heatmap_data);
        setLastUpdate(new Date().toLocaleTimeString());
      });

      newSocket.on('disconnect', () => {
        console.log('❌ Disconnected from screener WebSocket');
      });

      setSocket(newSocket);

      return () => {
        newSocket.disconnect();
      };
    } else if (socket) {
      socket.disconnect();
      setSocket(null);
    }
  }, [autoRefresh, scanId]);

  const handleScan = async () => {
    setLoading(true);
    setError(null);

    try {
      // ONE API CALL: Scan + Predict + Heatmap
      const response = await screenerApi.scanAndPredict({
        universe,
        timeframe,
        criteria: {
          min_momentum_20d: minMomentum / 100,
          max_rsi: maxRsi,
          min_volume_surge: minVolumeSurge
        },
        max_results: maxResults,
        generate_heatmap: true
      });

      // Results automatically populate
      setScanResults(response);
      setHeatmapData(response.heatmap_data);

      // Handle comparison mode
      if (comparisonMode) {
        if (!scanA) {
          setScanA({
            name: `${universe} - ${timeframe}`,
            results: response.scan_results,
            heatmap_data: response.heatmap_data
          });
        } else {
          setScanB({
            name: `${universe} - ${timeframe}`,
            results: response.scan_results,
            heatmap_data: response.heatmap_data
          });
          setActiveView('compare');
        }
      } else {
        // Auto-switch to heatmap view
        setActiveView('heatmap');
      }

      // Subscribe to real-time updates if enabled
      if (autoRefresh) {
        const subscribeResponse = await screenerApi.subscribeToUpdates({
          scan_config: {
            universe,
            timeframe,
            criteria: {
              min_momentum_20d: minMomentum / 100,
              max_rsi: maxRsi,
              min_volume_surge: minVolumeSurge
            },
            max_results: maxResults
          },
          update_interval_seconds: refreshInterval * 60
        });
        setScanId(subscribeResponse.scan_id);
      }

      console.log(`✅ Loaded ${response.metadata.results_count} stocks into heatmap`);
      setLastUpdate(new Date().toLocaleTimeString());

    } catch (err) {
      console.error('Scan failed:', err);
      setError('Backend not running! Start: python backend/screener_service/app.py');
    } finally {
      setLoading(false);
    }
  };

  const handleSavePreset = async () => {
    if (!presetName.trim()) {
      alert('Please enter a preset name');
      return;
    }

    try {
      await screenerApi.savePreset({
        name: presetName,
        description: presetDescription,
        config: {
          universe,
          timeframe,
          criteria: {
            min_momentum_20d: minMomentum / 100,
            max_rsi: maxRsi,
            min_volume_surge: minVolumeSurge
          },
          max_results: maxResults
        }
      });

      // Reload presets
      const response = await screenerApi.getPresets();
      setPresets(response.presets);

      // Reset form
      setPresetName('');
      setPresetDescription('');

      alert('✅ Preset saved successfully!');
    } catch (err) {
      console.error('Failed to save preset:', err);
      alert('❌ Failed to save preset');
    }
  };

  const handleLoadPreset = async (presetId: string) => {
    setLoading(true);
    try {
      const response = await screenerApi.runPreset(presetId);
      setScanResults(response);
      setHeatmapData(response.heatmap_data);
      setActiveView('heatmap');
      console.log(`✅ Loaded preset: ${presetId}`);
    } catch (err) {
      console.error('Failed to load preset:', err);
      setError('Failed to load preset');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: 'png' | 'csv' | 'html' | 'json') => {
    if (!heatmapData) {
      alert('No heatmap data to export');
      return;
    }

    try {
      const blob = await screenerApi.exportHeatmap(format, {
        heatmap_data: heatmapData,
        scan_config: {
          universe,
          timeframe,
          max_results: maxResults
        }
      });

      // Download file
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `screener_heatmap_${Date.now()}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      console.log(`✅ Exported as ${format.toUpperCase()}`);
    } catch (err) {
      console.error('Export failed:', err);
      alert('❌ Export failed');
    }
  };

  const handleCompare = () => {
    setComparisonMode(!comparisonMode);
    if (!comparisonMode) {
      // Entering comparison mode
      setScanA(null);
      setScanB(null);
      alert('📊 Comparison mode enabled. Run two scans to compare them.');
    } else {
      // Exiting comparison mode
      setScanA(null);
      setScanB(null);
      setActiveView('results');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/scanner')}
            className="p-2 hover:bg-dark-border rounded-lg transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-white">Advanced Stock Screener</h1>
            <p className="text-sm text-gray-400">
              Scan for opportunities → See predictions across all timeframes
            </p>
          </div>
        </div>

        {/* Control Panel - All Features */}
        <div className="flex items-center gap-3">
          {/* Export Menu */}
          {heatmapData && <ExportMenu onExport={handleExport} />}

          {/* Presets */}
          <button
            onClick={() => setShowPresetManager(true)}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
          >
            <FolderOpen className="w-4 h-4" />
            Presets
          </button>

          {/* Auto-Refresh Toggle */}
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 ${
              autoRefresh
                ? 'bg-green-600 hover:bg-green-700 text-white'
                : 'bg-gray-600 hover:bg-gray-500 text-white'
            }`}
          >
            <RefreshCw className={`w-4 h-4 ${autoRefresh ? 'animate-spin' : ''}`} />
            Auto-Refresh {autoRefresh ? 'ON' : 'OFF'}
          </button>

          {/* Compare Toggle */}
          <button
            onClick={handleCompare}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 ${
              comparisonMode
                ? 'bg-orange-600 hover:bg-orange-700 text-white'
                : 'bg-gray-600 hover:bg-gray-500 text-white'
            }`}
          >
            <GitCompare className="w-4 h-4" />
            Compare {comparisonMode ? 'ON' : 'OFF'}
          </button>
        </div>
      </div>

      {/* Status Bar */}
      {(autoRefresh || comparisonMode) && (
        <div className="bg-dark-card border border-dark-border rounded-lg p-3 flex items-center justify-between">
          {autoRefresh && (
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-400">
                Auto-refresh every <strong className="text-white">{refreshInterval} min</strong>
              </span>
              {lastUpdate && (
                <span className="text-xs text-gray-500">
                  Last update: {lastUpdate}
                </span>
              )}
            </div>
          )}
          {comparisonMode && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-orange-400">
                📊 Comparison Mode: {scanA ? '1' : '0'}/2 scans
              </span>
            </div>
          )}
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-400">
            <span className="font-semibold">⚠️ {error}</span>
          </div>
        </div>
      )}

      {/* Configuration Panel */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">
          1. Configure Your Scan
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {/* Universe Selector */}
          <div>
            <label className="text-sm font-medium text-gray-300 mb-2 block">
              Stock Universe
            </label>
            <select
              className="w-full bg-dark-bg text-white border border-dark-border rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
              value={universe}
              onChange={(e) => setUniverse(e.target.value as ScreenerParams['universe'])}
            >
              <option value="sp500">S&P 500 (Large Caps)</option>
              <option value="nasdaq100">NASDAQ 100</option>
              <option value="small_caps">Small Caps ($300M-$2B)</option>
              <option value="mid_caps">Mid Caps ($2B-$10B)</option>
              <option value="micro_caps">Micro Caps ($50M-$300M)</option>
              <option value="all">All Stocks</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">
              {universe === 'sp500' && '500 large-cap stocks'}
              {universe === 'nasdaq100' && '100 largest non-financial NASDAQ stocks'}
              {universe === 'small_caps' && '~2000 small-cap stocks'}
              {universe === 'mid_caps' && '~800 mid-cap stocks'}
              {universe === 'micro_caps' && 'Smallest public companies'}
              {universe === 'all' && 'All publicly traded stocks'}
            </p>
          </div>

          {/* Timeframe Selector */}
          <div>
            <label className="text-sm font-medium text-gray-300 mb-2 block">
              Trading Style
            </label>
            <select
              className="w-full bg-dark-bg text-white border border-dark-border rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value as ScreenerParams['timeframe'])}
            >
              <option value="intraday">Day Trading (Minutes-Hours)</option>
              <option value="swing">Swing Trading (2-10 Days)</option>
              <option value="position">Position Trading (Weeks-Months)</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">
              {timeframe === 'intraday' && 'High liquidity, fast moves'}
              {timeframe === 'swing' && 'Momentum + technical patterns'}
              {timeframe === 'position' && 'Fundamental + growth factors'}
            </p>
          </div>

          {/* Max Results */}
          <div>
            <label className="text-sm font-medium text-gray-300 mb-2 block">
              Max Results
            </label>
            <input
              type="number"
              className="w-full bg-dark-bg text-white border border-dark-border rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
              value={maxResults}
              onChange={(e) => setMaxResults(parseInt(e.target.value))}
              min={10}
              max={200}
            />
            <p className="text-xs text-gray-500 mt-1">
              All results will appear in heatmap (scrollable)
            </p>
          </div>
        </div>

        {/* Screening Criteria */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-300 mb-3">
            Screening Criteria
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-xs text-gray-400 mb-1 block">
                Minimum Momentum (%)
              </label>
              <input
                type="number"
                className="w-full bg-dark-bg text-white border border-dark-border rounded px-3 py-2 focus:outline-none focus:border-blue-500"
                value={minMomentum}
                onChange={(e) => setMinMomentum(parseFloat(e.target.value))}
                step={1}
              />
            </div>

            <div>
              <label className="text-xs text-gray-400 mb-1 block">
                Maximum RSI (Oversold)
              </label>
              <input
                type="number"
                className="w-full bg-dark-bg text-white border border-dark-border rounded px-3 py-2 focus:outline-none focus:border-blue-500"
                value={maxRsi}
                onChange={(e) => setMaxRsi(parseFloat(e.target.value))}
                step={5}
                min={20}
                max={50}
              />
            </div>

            <div>
              <label className="text-xs text-gray-400 mb-1 block">
                Min Volume Surge (x)
              </label>
              <input
                type="number"
                className="w-full bg-dark-bg text-white border border-dark-border rounded px-3 py-2 focus:outline-none focus:border-blue-500"
                value={minVolumeSurge}
                onChange={(e) => setMinVolumeSurge(parseFloat(e.target.value))}
                step={0.1}
                min={1.0}
              />
            </div>
          </div>
        </div>

        {/* Save as Preset Section */}
        <div className="border-t border-dark-border pt-4 mt-4">
          <h3 className="text-sm font-medium text-gray-300 mb-3">Save Current Configuration</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input
              type="text"
              placeholder="Preset name (e.g., 'Small Cap Momentum')"
              value={presetName}
              onChange={(e) => setPresetName(e.target.value)}
              className="bg-dark-bg text-white border border-dark-border rounded px-3 py-2 focus:outline-none focus:border-blue-500"
            />
            <input
              type="text"
              placeholder="Description (optional)"
              value={presetDescription}
              onChange={(e) => setPresetDescription(e.target.value)}
              className="bg-dark-bg text-white border border-dark-border rounded px-3 py-2 focus:outline-none focus:border-blue-500"
            />
            <button
              onClick={handleSavePreset}
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
            >
              <Save className="w-4 h-4" />
              Save as Preset
            </button>
          </div>
        </div>

        {/* Scan Button */}
        <button
          onClick={handleScan}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-8 py-3 rounded-lg font-medium transition-colors flex items-center gap-2 mt-4"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Scanning & Generating Heatmap...
            </>
          ) : (
            <>
              <Search className="w-5 h-5" />
              🔍 Scan & Generate Heatmap
            </>
          )}
        </button>
      </div>

      {/* Results Section */}
      {scanResults && (
        <div className="space-y-6">

          {/* Summary Banner */}
          <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-blue-400">
                  ✓ Scan Complete
                </h3>
                <p className="text-sm text-gray-300">
                  Found <strong>{scanResults.scan_results.length} stocks</strong> matching your criteria
                </p>
              </div>

              {/* View Toggle */}
              <div className="flex space-x-2">
                <button
                  className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                    activeView === 'results'
                      ? 'bg-blue-600 text-white'
                      : 'bg-dark-bg text-gray-300 hover:bg-dark-border'
                  }`}
                  onClick={() => setActiveView('results')}
                >
                  <BarChart3 className="w-4 h-4" />
                  Results Table
                </button>
                <button
                  className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                    activeView === 'heatmap'
                      ? 'bg-blue-600 text-white'
                      : 'bg-dark-bg text-gray-300 hover:bg-dark-border'
                  }`}
                  onClick={() => setActiveView('heatmap')}
                >
                  🔥 Prediction Heatmap
                </button>
                {scanA && scanB && (
                  <button
                    className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                      activeView === 'compare'
                        ? 'bg-blue-600 text-white'
                        : 'bg-dark-bg text-gray-300 hover:bg-dark-border'
                    }`}
                    onClick={() => setActiveView('compare')}
                  >
                    <GitCompare className="w-4 h-4" />
                    Comparison
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Results Table View */}
          {activeView === 'results' && (
            <div className="space-y-6">
              {/* Top Picks Grid */}
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <TrendingUp className="w-6 h-6 text-green-400" />
                  <h2 className="text-2xl font-bold text-white">
                    Top {Math.min(20, scanResults.scan_results.length)} Picks
                  </h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {scanResults.scan_results.slice(0, 20).map((stock) => (
                    <StockCard
                      key={stock.ticker}
                      stock={stock}
                      onViewDetails={setSelectedStock}
                    />
                  ))}
                </div>
              </div>

              {/* Selected Stock Factor Breakdown */}
              {selectedStock && scanResults.scan_results.find(s => s.ticker === selectedStock) && (
                <FactorBreakdown
                  factorScores={scanResults.scan_results.find(s => s.ticker === selectedStock)!.factor_scores}
                />
              )}

              {/* Full Results Table */}
              <div className="bg-dark-card border border-dark-border rounded-lg p-6">
                <h2 className="text-xl font-semibold text-white mb-4">
                  Scan Results ({scanResults.scan_results.length} stocks)
                </h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-dark-bg">
                      <tr>
                        <th className="px-4 py-3 text-left text-gray-300">Rank</th>
                        <th className="px-4 py-3 text-left text-gray-300">Ticker</th>
                        <th className="px-4 py-3 text-right text-gray-300">Score</th>
                        <th className="px-4 py-3 text-right text-gray-300">Momentum</th>
                        <th className="px-4 py-3 text-right text-gray-300">RSI</th>
                        <th className="px-4 py-3 text-right text-gray-300">Volume</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-700">
                      {scanResults.scan_results.map((stock, idx) => (
                        <tr key={stock.ticker} className="hover:bg-dark-bg/50 transition-colors">
                          <td className="px-4 py-3 text-white">{idx + 1}</td>
                          <td className="px-4 py-3 text-white font-mono font-semibold">{stock.ticker}</td>
                          <td className="px-4 py-3 text-right text-blue-400">
                            {stock.composite_score?.toFixed(2) || 'N/A'}
                          </td>
                          <td className="px-4 py-3 text-right text-green-400">
                            {((stock.momentum_20d || 0) * 100).toFixed(1)}%
                          </td>
                          <td className="px-4 py-3 text-right text-yellow-400">
                            {(stock.rsi || 0).toFixed(0)}
                          </td>
                          <td className="px-4 py-3 text-right text-purple-400">
                            {(stock.volume_surge || 0).toFixed(2)}x
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Heatmap View - ALL RESULTS AUTOMATICALLY POPULATE */}
          {activeView === 'heatmap' && heatmapData && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-xl font-semibold text-white">
                  Multi-Timeframe Prediction Heatmap
                </h2>
                <div className="text-sm text-gray-400">
                  Showing all <strong className="text-white">{heatmapData.tickers.length}</strong> stocks × <strong className="text-white">{heatmapData.timeframes.length - 1}</strong> timeframes
                </div>
              </div>

              {/* THE HEATMAP - Automatically shows ALL scan results */}
              <DualAxisHeatmap data={heatmapData} />
            </div>
          )}

          {/* Comparison View */}
          {activeView === 'compare' && scanA && scanB && (
            <ComparisonView scanA={scanA} scanB={scanB} />
          )}
        </div>
      )}

      {/* Empty State */}
      {!scanResults && (
        <div className="bg-dark-card border border-dark-border rounded-lg p-12 text-center">
          <div className="text-gray-500 text-lg mb-2">
            👆 Configure your scan above
          </div>
          <div className="text-gray-400 text-sm">
            Results will automatically populate the heatmap
          </div>
        </div>
      )}

      {/* Preset Manager Modal */}
      {showPresetManager && (
        <PresetManager
          presets={presets}
          onLoad={handleLoadPreset}
          onClose={() => setShowPresetManager(false)}
        />
      )}
    </div>
  );
}
