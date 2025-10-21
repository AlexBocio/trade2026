/**
 * Custom Scanner Builder Page
 * Main page for building custom multi-layer scanners
 */

import React, { useState } from 'react';
import { ArrowLeft, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import ConfigurationPanel from '../../components/Scanner/ConfigurationPanel';
import ScanResults from '../../components/Scanner/ScanResults';
import { scannerApi } from '../../api/scannerApi';
import type { ScannerConfig, ScanResponse } from '../../types/scanner';
import { defaultScannerConfig } from '../../types/scanner';

export default function CustomScannerBuilder() {
  const navigate = useNavigate();
  const [config, setConfig] = useState<ScannerConfig>(defaultScannerConfig);
  const [results, setResults] = useState<ScanResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunScan = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await scannerApi.runCustomScan(config);
      setResults(data);
    } catch (err: any) {
      setError(err.message || 'Scan failed. Make sure backend is running on port 5008.');
      console.error('Scan error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleConfigChange = (newConfig: ScannerConfig) => {
    setConfig(newConfig);
    // Clear old results when config changes significantly
    if (newConfig.mode !== config.mode || newConfig.universe !== config.universe) {
      setResults(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-4">
            <button
              onClick={() => navigate('/scanner')}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-400" />
            </button>
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                🧪 Custom Scanner Builder
              </h1>
              <p className="text-gray-400">
                Configure your own multi-layer scanner with custom regime analysis and technical criteria
              </p>
            </div>
          </div>

          {/* Info Banner */}
          <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <div className="text-blue-400 mt-0.5">
                💡
              </div>
              <div className="flex-1">
                <h3 className="text-blue-400 font-semibold mb-1">How it works</h3>
                <p className="text-sm text-gray-300">
                  1. Select which regime layers to analyze (temporal, macro, market, etc.)
                  <br />
                  2. Choose a scanning mode (alignment, divergence, hybrid, or transition)
                  <br />
                  3. Add technical criteria and filters
                  <br />
                  4. Configure ranking and output options
                  <br />
                  5. Run the scan and export results
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="bg-red-900/30 border border-red-700 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-2 text-red-400">
              <AlertCircle className="w-5 h-5" />
              <span className="font-semibold">{error}</span>
            </div>
            <p className="text-sm text-red-300 mt-2">
              Make sure the scanner backend is running: <code className="bg-red-950 px-2 py-1 rounded">python backend/scanner_service/app.py</code>
            </p>
          </div>
        )}

        {/* Main Layout: Config Panel + Results */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Configuration Panel (2/3 width on large screens) */}
          <div className="lg:col-span-2">
            <ConfigurationPanel
              config={config}
              onChange={handleConfigChange}
              onRun={handleRunScan}
              loading={loading}
            />
          </div>

          {/* Right: Results Preview (1/3 width on large screens) */}
          <div className="lg:col-span-1">
            {loading && <LoadingSpinner />}
            {!loading && results && <ScanResults results={results} />}
            {!loading && !results && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="text-6xl mb-4">📊</div>
                <div className="text-gray-400 text-lg mb-2">No results yet</div>
                <div className="text-gray-500 text-sm">
                  Configure your scan and click <br />"Run Custom Scan" to see results
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer Tips */}
        <div className="mt-8 bg-gray-800 border border-gray-700 rounded-lg p-6">
          <h3 className="text-white font-semibold mb-3">💡 Pro Tips</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-400">
            <div>
              <strong className="text-gray-300">Weight Distribution:</strong> Ensure regime layer weights sum to 100% for optimal scoring
            </div>
            <div>
              <strong className="text-gray-300">Alignment Mode:</strong> Best for trending markets with strong consensus
            </div>
            <div>
              <strong className="text-gray-300">Divergence Mode:</strong> Find contrarian plays when regimes disagree
            </div>
            <div>
              <strong className="text-gray-300">Save Presets:</strong> Save your favorite configurations for quick reuse
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function LoadingSpinner() {
  return (
    <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
      <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
      <div className="text-white text-lg font-semibold mb-2">Scanning...</div>
      <div className="text-gray-400 text-sm">
        Analyzing stocks across multiple regime layers
      </div>
    </div>
  );
}
