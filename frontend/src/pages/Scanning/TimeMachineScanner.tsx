/**
 * Time Machine Pattern Scanner Page
 * Find stocks TODAY that look like historical winners BEFORE big moves
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { alphaApi, getUniverseStocks } from '../../api/alphaApi';
import PatternLibrary from '../../components/AlphaScanner/PatternLibrary';
import PatternMatchCard from '../../components/AlphaScanner/PatternMatchCard';

interface Pattern {
  pattern_id: string;
  symbol: string;
  total_return: number;
  start_date: string;
  end_date: string;
  duration_days: number;
  pre_move_characteristics: {
    regime: string;
    catalyst?: string;
  };
}

interface PatternMatchResult {
  reference_pattern: {
    symbol: string;
    id: string;
    return: number;
    duration: number;
  };
  matches: any[];
}

export default function TimeMachineScanner() {
  const navigate = useNavigate();
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [selectedPattern, setSelectedPattern] = useState<string | null>(null);
  const [universe, setUniverse] = useState('sp500');
  const [matchThreshold, setMatchThreshold] = useState(0.8);
  const [matches, setMatches] = useState<PatternMatchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load available patterns
  useEffect(() => {
    const loadPatterns = async () => {
      try {
        const data = await alphaApi.timeMachine.getPatterns();
        setPatterns(data);
        if (data.length > 0) {
          setSelectedPattern(data[0].pattern_id);
        }
      } catch (err) {
        console.error('Failed to load patterns:', err);
        setError('Failed to load pattern library');
      }
    };
    loadPatterns();
  }, []);

  const handleScan = async () => {
    if (!selectedPattern) return;

    setLoading(true);
    setError(null);

    try {
      const universeList = await getUniverseStocks(universe);
      const data = await alphaApi.timeMachine.findMatches(
        selectedPattern,
        universeList,
        matchThreshold
      );
      setMatches(data);
    } catch (err) {
      console.error('Scan failed:', err);
      setError('Scan failed. Please try again.');
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
            <span>🕰️</span>
            <span>Time Machine Pattern Scanner</span>
          </h1>
          <p className="text-gray-400">
            Find stocks TODAY that look like historical winners BEFORE big moves
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Panel: Configuration */}
          <div className="lg:col-span-1 space-y-6">
            {/* Pattern Library */}
            <PatternLibrary
              patterns={patterns}
              selectedPattern={selectedPattern}
              onSelect={setSelectedPattern}
            />

            {/* Scan Configuration */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-white font-semibold mb-4">⚙️ Scan Settings</h3>

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

                {/* Match Threshold */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Match Threshold: {(matchThreshold * 100).toFixed(0)}%
                  </label>
                  <input
                    type="range"
                    min="0.50"
                    max="0.95"
                    step="0.05"
                    value={matchThreshold}
                    onChange={(e) => setMatchThreshold(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Loose (50%)</span>
                    <span>Strict (95%)</span>
                  </div>
                </div>

                {/* Scan Button */}
                <button
                  onClick={handleScan}
                  disabled={!selectedPattern || loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg transition-colors"
                >
                  {loading ? '🔄 Scanning...' : '🔍 Find Pattern Matches'}
                </button>

                {error && (
                  <div className="bg-red-900/20 border border-red-700/50 rounded-lg p-3 text-sm text-red-400">
                    {error}
                  </div>
                )}
              </div>
            </div>

            {/* Create Custom Pattern */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-white font-semibold mb-4">✨ Create Custom Pattern</h3>
              <p className="text-sm text-gray-400 mb-4">
                Define your own historical pattern to match against current market
              </p>
              <button className="w-full bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors">
                + New Pattern
              </button>
            </div>
          </div>

          {/* Right Panel: Results */}
          <div className="lg:col-span-2">
            {!matches && !loading && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="text-6xl mb-4">🔍</div>
                <h3 className="text-white font-semibold mb-2">Select a pattern and run scan</h3>
                <p className="text-gray-400 text-sm">
                  Choose a historical winning pattern from the library, configure your settings,
                  and find similar setups in the current market
                </p>
              </div>
            )}

            {loading && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="animate-spin text-6xl mb-4">🔄</div>
                <h3 className="text-white font-semibold mb-2">Scanning for matches...</h3>
                <p className="text-gray-400 text-sm">
                  Analyzing {universe.toUpperCase()} stocks against reference pattern
                </p>
              </div>
            )}

            {matches && !loading && (
              <div className="space-y-4">
                {/* Reference Pattern Info */}
                <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-700/50 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-white font-bold text-lg">
                        Reference Pattern: {matches.reference_pattern.symbol}
                      </h3>
                      <p className="text-gray-400 text-sm">{matches.reference_pattern.id}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-green-400 font-bold text-2xl">
                        +{(matches.reference_pattern.return * 100).toFixed(0)}%
                      </div>
                      <div className="text-gray-400 text-sm">
                        {matches.reference_pattern.duration} days
                      </div>
                    </div>
                  </div>
                </div>

                {/* Match Results */}
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <h3 className="text-white font-semibold mb-4">
                    Pattern Matches Found: {matches.matches.length}
                  </h3>

                  {matches.matches.length === 0 ? (
                    <div className="text-center py-8 text-gray-400">
                      No matches found with current threshold. Try lowering the match threshold.
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {matches.matches.map((match) => (
                        <PatternMatchCard
                          key={match.symbol}
                          match={match}
                          referencePattern={matches.reference_pattern}
                        />
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
