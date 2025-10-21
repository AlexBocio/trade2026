/**
 * Scenario Analyzer Page
 * Analyze stocks for specific macro scenarios
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { alphaApi } from '../../api/alphaApi';
import ScenarioCard from '../../components/AlphaScanner/ScenarioCard';
import StockFitCard from '../../components/AlphaScanner/StockFitCard';

interface AnalysisResult {
  scenario: string;
  analyzed_date: string;
  stocks: any[];
}

export default function ScenarioAnalyzer() {
  const navigate = useNavigate();
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<string>('');
  const [universe, setUniverse] = useState('sp500');
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingScenarios, setLoadingScenarios] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load available scenarios on mount
  useEffect(() => {
    const loadScenarios = async () => {
      try {
        const data = await alphaApi.scenario.list();
        setScenarios(data.scenarios || []);
        if (data.scenarios && data.scenarios.length > 0) {
          setSelectedScenario(data.scenarios[0].id);
        }
      } catch (err) {
        console.error('Failed to load scenarios:', err);
      } finally {
        setLoadingScenarios(false);
      }
    };

    loadScenarios();
  }, []);

  const handleAnalyze = async () => {
    if (!selectedScenario) {
      setError('Please select a scenario');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await alphaApi.scenario.analyze(selectedScenario, universe);
      setResults(data);
    } catch (err) {
      console.error('Analysis failed:', err);
      setError('Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        <button
          onClick={() => navigate('/scanner')}
          className="mb-4 flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Scanner</span>
        </button>

        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center space-x-3">
            <span>🔮</span>
            <span>Scenario Analysis</span>
          </h1>
          <p className="text-gray-400">
            Analyze which stocks are positioned for specific macro scenarios
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Panel: Configuration */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800 rounded-lg p-6 sticky top-6 border border-gray-700">
              <h3 className="text-white font-semibold mb-4">⚙️ Analysis Settings</h3>

              <div className="space-y-4">
                {/* Universe */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Stock Universe</label>
                  <select
                    value={universe}
                    onChange={(e) => setUniverse(e.target.value)}
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                  >
                    <option value="sp500">S&P 500</option>
                    <option value="sp400">S&P 400 MidCap</option>
                    <option value="sp600">S&P 600 SmallCap</option>
                    <option value="nasdaq100">NASDAQ 100</option>
                  </select>
                </div>

                {/* Analyze Button */}
                <button
                  onClick={handleAnalyze}
                  disabled={loading || !selectedScenario}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg transition-colors"
                >
                  {loading ? '🔄 Analyzing...' : '🔍 Analyze Scenario'}
                </button>

                {error && (
                  <div className="bg-red-900/20 border border-red-700/50 rounded-lg p-3 text-sm text-red-400">
                    {error}
                  </div>
                )}
              </div>

              {/* Info Box */}
              <div className="mt-6 bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-xl">💡</span>
                  <span className="text-blue-400 font-semibold text-sm">
                    Scenario Analysis
                  </span>
                </div>
                <p className="text-xs text-gray-300 leading-relaxed">
                  Identify stocks that historically perform well in specific macro
                  environments. Analysis considers:
                  <br />• Historical performance
                  <br />• Business model alignment
                  <br />• Sector positioning
                  <br />• Financial resilience
                </p>
              </div>
            </div>
          </div>

          {/* Right Panel: Scenario Selection & Results */}
          <div className="lg:col-span-3">
            {/* Scenario Selection */}
            <div className="mb-6">
              <h2 className="text-white font-semibold text-lg mb-4">
                📋 Select Macro Scenario
              </h2>

              {loadingScenarios ? (
                <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
                  <div className="animate-spin text-4xl mb-3">🔄</div>
                  <p className="text-gray-400">Loading scenarios...</p>
                </div>
              ) : scenarios.length === 0 ? (
                <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
                  <p className="text-gray-400">No scenarios available</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {scenarios.map((scenario) => (
                    <ScenarioCard
                      key={scenario.id}
                      scenario={scenario}
                      onSelect={() => setSelectedScenario(scenario.id)}
                      isSelected={selectedScenario === scenario.id}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Results */}
            {!results && !loading && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="text-6xl mb-4">🔮</div>
                <h3 className="text-white font-semibold mb-2">
                  Select a scenario and analyze
                </h3>
                <p className="text-gray-400 text-sm">
                  Find stocks positioned for your selected macro environment
                </p>
              </div>
            )}

            {loading && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="animate-spin text-6xl mb-4">🔄</div>
                <h3 className="text-white font-semibold mb-2">
                  Analyzing scenario fit...
                </h3>
                <p className="text-gray-400 text-sm">
                  Evaluating {universe.toUpperCase()} stocks
                </p>
              </div>
            )}

            {results && !loading && (
              <div className="space-y-4">
                {/* Header */}
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-white font-semibold text-lg mb-2">
                        Analysis Results: {results.stocks.length} Stocks
                      </h3>
                      <p className="text-sm text-gray-400">
                        Scenario: {results.scenario} | Date: {results.analyzed_date}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-gray-400 mb-1">Universe</div>
                      <div className="text-white font-semibold">
                        {universe.toUpperCase()}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Stock Results */}
                {results.stocks.length === 0 ? (
                  <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                    <div className="text-gray-400">
                      No stocks found with sufficient fit for this scenario.
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {results.stocks.map((stock) => (
                      <StockFitCard key={stock.symbol} stock={stock} />
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
