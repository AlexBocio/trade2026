/**
 * Market Regime Detection - Identify bull/bear/sideways markets
 */

import { useState } from 'react';
import { ArrowLeft, Play } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Plot from 'react-plotly.js';

export function MarketRegime() {
  const navigate = useNavigate();
  const [config, setConfig] = useState({
    symbol: 'SPY',
    startDate: '2020-01-01',
    endDate: '2024-12-31',
    method: 'hmm',
  });
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleRun = async () => {
    setIsRunning(true);
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Mock results
    const mockResults = {
      currentRegime: 'bull',
      confidence: 0.87,
      regimes: [
        {
          period: 'Jan 2020 - Mar 2020',
          regime: 'bull',
          avgReturn: 1.2,
          volatility: 15.3,
          duration: 90,
        },
        {
          period: 'Mar 2020 - May 2020',
          regime: 'bear',
          avgReturn: -8.5,
          volatility: 45.2,
          duration: 60,
        },
        {
          period: 'May 2020 - Oct 2023',
          regime: 'bull',
          avgReturn: 2.1,
          volatility: 18.7,
          duration: 1260,
        },
        {
          period: 'Oct 2023 - Dec 2023',
          regime: 'sideways',
          avgReturn: 0.3,
          volatility: 12.1,
          duration: 90,
        },
        {
          period: 'Dec 2023 - Present',
          regime: 'bull',
          avgReturn: 1.8,
          volatility: 16.5,
          duration: 300,
        },
      ],
      transitionMatrix: [
        [0.92, 0.05, 0.03], // Bull -> Bull, Bear, Sideways
        [0.15, 0.65, 0.2], // Bear -> Bull, Bear, Sideways
        [0.4, 0.1, 0.5], // Sideways -> Bull, Bear, Sideways
      ],
      timeSeries: generateRegimeTimeSeries(),
    };

    setResults(mockResults);
    setIsRunning(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate('/analytics')}
          className="p-2 hover:bg-dark-border rounded-lg transition"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-white">Market Regime Detection</h1>
          <p className="text-sm text-gray-400">
            Identify bull, bear, and sideways market regimes using HMM and statistical methods
          </p>
        </div>
      </div>

      {/* Configuration */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Configuration</h2>

        <div className="grid grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Symbol</label>
            <select
              value={config.symbol}
              onChange={(e) => setConfig({ ...config, symbol: e.target.value })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            >
              <option value="SPY">SPY (S&P 500)</option>
              <option value="QQQ">QQQ (Nasdaq)</option>
              <option value="IWM">IWM (Russell 2000)</option>
              <option value="NVAX">NVAX</option>
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Detection Method</label>
            <select
              value={config.method}
              onChange={(e) => setConfig({ ...config, method: e.target.value })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            >
              <option value="hmm">Hidden Markov Model (HMM)</option>
              <option value="volatility">Volatility Clustering</option>
              <option value="trend">Trend Analysis</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Start Date</label>
            <input
              type="date"
              value={config.startDate}
              onChange={(e) => setConfig({ ...config, startDate: e.target.value })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">End Date</label>
            <input
              type="date"
              value={config.endDate}
              onChange={(e) => setConfig({ ...config, endDate: e.target.value })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            />
          </div>
        </div>

        <button
          onClick={handleRun}
          disabled={isRunning}
          className="w-full px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg font-semibold flex items-center justify-center gap-2 transition"
        >
          {isRunning ? (
            <>
              <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
              Detecting Regimes...
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              Detect Market Regimes
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {results && (
        <>
          {/* Current Regime */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Current Market Regime</h2>

            <div className="grid grid-cols-2 gap-6 mb-4">
              <div className="bg-dark-bg rounded p-6">
                <div className="text-sm text-gray-400 mb-2">Current Regime</div>
                <div
                  className={`text-4xl font-bold mb-2 ${
                    results.currentRegime === 'bull'
                      ? 'text-green-400'
                      : results.currentRegime === 'bear'
                      ? 'text-red-400'
                      : 'text-yellow-400'
                  }`}
                >
                  {results.currentRegime.toUpperCase()}
                </div>
                <div className="text-sm text-gray-300">
                  Confidence: {(results.confidence * 100).toFixed(1)}%
                </div>
              </div>

              <div className="bg-dark-bg rounded p-6">
                <div className="text-sm text-gray-400 mb-2">Trading Recommendation</div>
                <div className="text-lg font-semibold text-white mb-2">
                  {results.currentRegime === 'bull'
                    ? 'Long Bias'
                    : results.currentRegime === 'bear'
                    ? 'Short Bias / Reduce Exposure'
                    : 'Range Trading / Neutral'}
                </div>
                <div className="text-sm text-gray-400">
                  {results.currentRegime === 'bull'
                    ? 'Momentum strategies work well'
                    : results.currentRegime === 'bear'
                    ? 'Use tight stops, defensive positioning'
                    : 'Mean reversion strategies favored'}
                </div>
              </div>
            </div>
          </div>

          {/* Regime Timeline */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Regime Timeline</h2>
            <RegimeTimelineChart data={results.timeSeries} />
          </div>

          {/* Historical Regimes */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Historical Regimes</h2>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left text-sm text-gray-400 border-b border-dark-border">
                    <th className="pb-3 font-semibold">Period</th>
                    <th className="pb-3 font-semibold">Regime</th>
                    <th className="pb-3 font-semibold text-right">Avg Return</th>
                    <th className="pb-3 font-semibold text-right">Volatility</th>
                    <th className="pb-3 font-semibold text-right">Duration (days)</th>
                  </tr>
                </thead>
                <tbody>
                  {results.regimes.map((regime: any, idx: number) => (
                    <tr key={idx} className="border-b border-dark-border">
                      <td className="py-3 text-white">{regime.period}</td>
                      <td className="py-3">
                        <span
                          className={`px-2 py-1 rounded font-semibold ${
                            regime.regime === 'bull'
                              ? 'bg-green-900/30 text-green-400'
                              : regime.regime === 'bear'
                              ? 'bg-red-900/30 text-red-400'
                              : 'bg-yellow-900/30 text-yellow-400'
                          }`}
                        >
                          {regime.regime.toUpperCase()}
                        </span>
                      </td>
                      <td
                        className={`py-3 text-right font-mono font-bold ${
                          regime.avgReturn > 0 ? 'text-green-400' : 'text-red-400'
                        }`}
                      >
                        {regime.avgReturn > 0 ? '+' : ''}
                        {regime.avgReturn.toFixed(1)}%
                      </td>
                      <td className="py-3 text-right font-mono text-white">
                        {regime.volatility.toFixed(1)}%
                      </td>
                      <td className="py-3 text-right font-mono text-white">{regime.duration}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Transition Matrix */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Regime Transition Matrix</h2>

            <div className="overflow-x-auto mb-4">
              <table className="w-full">
                <thead>
                  <tr className="text-left text-sm text-gray-400">
                    <th className="pb-3 font-semibold">From \ To</th>
                    <th className="pb-3 font-semibold text-right">Bull</th>
                    <th className="pb-3 font-semibold text-right">Bear</th>
                    <th className="pb-3 font-semibold text-right">Sideways</th>
                  </tr>
                </thead>
                <tbody>
                  {['Bull', 'Bear', 'Sideways'].map((from, i) => (
                    <tr key={from} className="border-t border-dark-border">
                      <td className="py-3 font-semibold text-white">{from}</td>
                      {results.transitionMatrix[i].map((prob: number, j: number) => (
                        <td key={j} className="py-3 text-right font-mono text-white">
                          {(prob * 100).toFixed(0)}%
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="p-4 bg-blue-900/20 border border-blue-700 rounded-lg text-sm text-gray-300">
              <div className="font-semibold text-white mb-2">Interpretation:</div>
              Bull markets tend to persist (92% chance), bear markets are unstable (65% chance to
              stay), sideways markets often transition to bull (40%).
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function generateRegimeTimeSeries() {
  const dates = [];
  const prices = [];
  const regimes = [];

  let price = 100;
  let currentRegime = 'bull';
  let regimeDuration = 0;

  for (let i = 0; i < 1200; i++) {
    const date = new Date(2020, 0, 1);
    date.setDate(date.getDate() + i);
    dates.push(date.toISOString().split('T')[0]);

    // Switch regimes periodically
    if (regimeDuration > 90 && Math.random() > 0.95) {
      const rand = Math.random();
      currentRegime = rand < 0.5 ? 'bull' : rand < 0.8 ? 'bear' : 'sideways';
      regimeDuration = 0;
    }
    regimeDuration++;

    // Generate price based on regime
    if (currentRegime === 'bull') {
      price *= 1 + (Math.random() * 0.03 - 0.005); // +1% avg
    } else if (currentRegime === 'bear') {
      price *= 1 + (Math.random() * 0.03 - 0.02); // -0.5% avg
    } else {
      price *= 1 + (Math.random() * 0.02 - 0.01); // 0% avg
    }

    prices.push(price);
    regimes.push(currentRegime);
  }

  return { dates, prices, regimes };
}

function RegimeTimelineChart({ data }: { data: any }) {
  const colors = data.regimes.map((r: string) =>
    r === 'bull' ? '#00ff88' : r === 'bear' ? '#ff4444' : '#ffaa00'
  );

  return (
    <Plot
      data={[
        {
          x: data.dates,
          y: data.prices,
          type: 'scatter',
          mode: 'lines',
          line: { width: 1, color: '#666' },
          name: 'Price',
          showlegend: false,
        },
        {
          x: data.dates,
          y: data.prices,
          type: 'scatter',
          mode: 'markers',
          marker: { size: 4, color: colors },
          name: 'Regime',
          showlegend: false,
        },
      ]}
      layout={{
        paper_bgcolor: '#1a1f2e',
        plot_bgcolor: '#1a1f2e',
        font: { color: '#e0e0e0', family: 'monospace' },
        xaxis: {
          title: 'Date',
          gridcolor: '#2a3142',
          type: 'date',
        },
        yaxis: {
          title: 'Price',
          gridcolor: '#2a3142',
        },
        margin: { l: 60, r: 20, t: 20, b: 60 },
        hovermode: 'x unified',
      }}
      config={{ displayModeBar: false, responsive: true }}
      style={{ width: '100%', height: '400px' }}
    />
  );
}
