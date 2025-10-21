/**
 * Statistical Tests Suite - Correlation, cointegration, stationarity tests
 */

import { useState } from 'react';
import { ArrowLeft, Play } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const availableTests = [
  {
    id: 'correlation',
    name: 'Correlation Test',
    description: 'Pearson, Spearman correlation',
    requiresTwoVars: true,
  },
  {
    id: 'cointegration',
    name: 'Cointegration Test',
    description: 'Engle-Granger test for long-run relationship',
    requiresTwoVars: true,
  },
  {
    id: 'stationarity',
    name: 'Stationarity Test',
    description: 'ADF, KPSS tests',
    requiresTwoVars: false,
  },
  {
    id: 'autocorrelation',
    name: 'Autocorrelation Test',
    description: 'ACF, PACF plots',
    requiresTwoVars: false,
  },
  {
    id: 'normality',
    name: 'Normality Test',
    description: 'Jarque-Bera, Shapiro-Wilk',
    requiresTwoVars: false,
  },
];

export function StatisticalTests() {
  const navigate = useNavigate();
  const [config, setConfig] = useState({
    selectedTests: ['correlation', 'stationarity'],
    variable1: 'NVAX_returns',
    variable2: 'SAVA_returns',
    startDate: '2020-01-01',
    endDate: '2024-12-31',
  });
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleRun = async () => {
    setIsRunning(true);
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Mock results
    const mockResults = {
      correlation: {
        pearson: { value: 0.87, pValue: 0.001, significant: true },
        spearman: { value: 0.82, pValue: 0.002, significant: true },
      },
      stationarity: {
        adf: {
          testStat: -4.23,
          criticalValues: { '1%': -3.43, '5%': -2.86, '10%': -2.57 },
          pValue: 0.001,
          stationary: true,
        },
        kpss: {
          testStat: 0.12,
          criticalValues: { '1%': 0.739, '5%': 0.463, '10%': 0.347 },
          pValue: 0.1,
          stationary: true,
        },
      },
      autocorrelation: {
        acf: [1.0, 0.85, 0.72, 0.58, 0.45, 0.32, 0.21, 0.12, 0.05, -0.02],
        pacf: [1.0, 0.85, 0.02, -0.01, 0.01, 0.0, -0.01, 0.0, 0.01, 0.0],
        ljungBox: { stat: 45.2, pValue: 0.001, significant: true },
      },
      normality: {
        jarqueBera: { stat: 2.34, pValue: 0.31, normal: true },
        shapiroWilk: { stat: 0.98, pValue: 0.42, normal: true },
        skewness: 0.12,
        kurtosis: 3.45,
      },
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
          <h1 className="text-2xl font-bold text-white">Statistical Tests Suite</h1>
          <p className="text-sm text-gray-400">
            Run rigorous statistical tests to validate assumptions and relationships.
          </p>
        </div>
      </div>

      {/* Configuration */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Configuration</h2>

        {/* Test Selection */}
        <div className="mb-6">
          <label className="block text-sm text-gray-400 mb-3">Select Tests</label>
          <div className="space-y-2">
            {availableTests.map((test) => (
              <label
                key={test.id}
                className="flex items-start gap-3 p-3 bg-dark-bg rounded-lg cursor-pointer hover:bg-dark-border transition"
              >
                <input
                  type="checkbox"
                  checked={config.selectedTests.includes(test.id)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setConfig({
                        ...config,
                        selectedTests: [...config.selectedTests, test.id],
                      });
                    } else {
                      setConfig({
                        ...config,
                        selectedTests: config.selectedTests.filter((t) => t !== test.id),
                      });
                    }
                  }}
                  className="mt-1 w-4 h-4"
                />
                <div>
                  <div className="font-semibold text-white">{test.name}</div>
                  <div className="text-xs text-gray-400">{test.description}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Variable Selection */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Variable 1</label>
            <select
              value={config.variable1}
              onChange={(e) => setConfig({ ...config, variable1: e.target.value })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            >
              <option value="NVAX_returns">NVAX Daily Returns</option>
              <option value="SAVA_returns">SAVA Daily Returns</option>
              <option value="SPY_returns">SPY Daily Returns</option>
              <option value="momentum_factor">Momentum Factor</option>
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">
              Variable 2 (for pairwise tests)
            </label>
            <select
              value={config.variable2}
              onChange={(e) => setConfig({ ...config, variable2: e.target.value })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            >
              <option value="SAVA_returns">SAVA Daily Returns</option>
              <option value="NVAX_returns">NVAX Daily Returns</option>
              <option value="SPY_returns">SPY Daily Returns</option>
              <option value="value_factor">Value Factor</option>
            </select>
          </div>
        </div>

        {/* Date Range */}
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

        {/* Run Button */}
        <button
          onClick={handleRun}
          disabled={isRunning || config.selectedTests.length === 0}
          className="w-full px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg font-semibold flex items-center justify-center gap-2 transition"
        >
          {isRunning ? (
            <>
              <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
              Running Tests...
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              Run Statistical Tests
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {results && (
        <>
          {/* Correlation Results */}
          {config.selectedTests.includes('correlation') && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Correlation Test Results</h2>

              <div className="grid grid-cols-2 gap-6 mb-4">
                <div className="bg-dark-bg rounded p-4">
                  <div className="text-sm text-gray-400 mb-2">Pearson Correlation</div>
                  <div className="text-3xl font-bold text-green-400 mb-1">
                    {results.correlation.pearson.value.toFixed(3)}
                  </div>
                  <div className="text-sm text-gray-300">
                    p-value:{' '}
                    <span className="font-mono text-green-400">
                      {results.correlation.pearson.pValue.toFixed(4)}
                    </span>
                  </div>
                  {results.correlation.pearson.significant && (
                    <div className="text-sm text-green-400 font-semibold mt-2">
                      ✓✓✓ Highly Significant
                    </div>
                  )}
                </div>

                <div className="bg-dark-bg rounded p-4">
                  <div className="text-sm text-gray-400 mb-2">Spearman Correlation</div>
                  <div className="text-3xl font-bold text-green-400 mb-1">
                    {results.correlation.spearman.value.toFixed(3)}
                  </div>
                  <div className="text-sm text-gray-300">
                    p-value:{' '}
                    <span className="font-mono text-green-400">
                      {results.correlation.spearman.pValue.toFixed(4)}
                    </span>
                  </div>
                  {results.correlation.spearman.significant && (
                    <div className="text-sm text-green-400 font-semibold mt-2">
                      ✓✓✓ Highly Significant
                    </div>
                  )}
                </div>
              </div>

              <div className="p-4 bg-blue-900/20 border border-blue-700 rounded-lg">
                <div className="font-semibold text-white mb-2">Interpretation:</div>
                <p className="text-sm text-gray-300">
                  Very high positive correlation (0.87) between NVAX and SAVA returns. This means
                  these stocks tend to move together. Consider this when building a diversified
                  portfolio.
                </p>
              </div>
            </div>
          )}

          {/* Stationarity Results */}
          {config.selectedTests.includes('stationarity') && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-4">
                Stationarity Test Results
              </h2>

              <div className="grid grid-cols-2 gap-6 mb-4">
                <div className="bg-dark-bg rounded p-4">
                  <div className="text-sm text-gray-400 mb-2">Augmented Dickey-Fuller (ADF)</div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Test Statistic:</span>
                      <span className="font-mono font-bold text-white">
                        {results.stationarity.adf.testStat.toFixed(3)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Critical Value (5%):</span>
                      <span className="font-mono text-white">
                        {results.stationarity.adf.criticalValues['5%'].toFixed(3)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">p-value:</span>
                      <span className="font-mono text-green-400">
                        {results.stationarity.adf.pValue.toFixed(4)}
                      </span>
                    </div>
                  </div>
                  {results.stationarity.adf.stationary && (
                    <div className="text-sm text-green-400 font-semibold mt-3">
                      ✓ Series is Stationary
                    </div>
                  )}
                </div>

                <div className="bg-dark-bg rounded p-4">
                  <div className="text-sm text-gray-400 mb-2">KPSS Test</div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Test Statistic:</span>
                      <span className="font-mono font-bold text-white">
                        {results.stationarity.kpss.testStat.toFixed(3)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Critical Value (5%):</span>
                      <span className="font-mono text-white">
                        {results.stationarity.kpss.criticalValues['5%'].toFixed(3)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">p-value:</span>
                      <span className="font-mono text-green-400">
                        {results.stationarity.kpss.pValue.toFixed(4)}
                      </span>
                    </div>
                  </div>
                  {results.stationarity.kpss.stationary && (
                    <div className="text-sm text-green-400 font-semibold mt-3">
                      ✓ Series is Stationary
                    </div>
                  )}
                </div>
              </div>

              <div className="p-4 bg-blue-900/20 border border-blue-700 rounded-lg">
                <div className="font-semibold text-white mb-2">Interpretation:</div>
                <p className="text-sm text-gray-300">
                  Both ADF and KPSS tests confirm the series is stationary. This is good for time
                  series modeling - the mean and variance are stable over time.
                </p>
              </div>
            </div>
          )}

          {/* Autocorrelation Results */}
          {config.selectedTests.includes('autocorrelation') && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-4">
                Autocorrelation Test Results
              </h2>

              <div className="grid grid-cols-2 gap-6 mb-4">
                <div>
                  <div className="text-sm text-gray-400 mb-2">ACF (Autocorrelation Function)</div>
                  <div className="bg-dark-bg rounded p-3">
                    {results.autocorrelation.acf.map((value: number, lag: number) => (
                      <div key={lag} className="flex items-center gap-2 mb-1">
                        <span className="text-xs text-gray-500 w-8">Lag {lag}:</span>
                        <div className="flex-1 h-4 bg-gray-800 rounded overflow-hidden">
                          <div
                            className={`h-full ${value > 0 ? 'bg-green-400' : 'bg-red-400'}`}
                            style={{ width: `${Math.abs(value) * 100}%` }}
                          />
                        </div>
                        <span className="text-xs font-mono w-12 text-right text-white">
                          {value.toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="text-sm text-gray-400 mb-2">
                    PACF (Partial Autocorrelation Function)
                  </div>
                  <div className="bg-dark-bg rounded p-3">
                    {results.autocorrelation.pacf.map((value: number, lag: number) => (
                      <div key={lag} className="flex items-center gap-2 mb-1">
                        <span className="text-xs text-gray-500 w-8">Lag {lag}:</span>
                        <div className="flex-1 h-4 bg-gray-800 rounded overflow-hidden">
                          <div
                            className={`h-full ${value > 0 ? 'bg-blue-400' : 'bg-red-400'}`}
                            style={{ width: `${Math.abs(value) * 100}%` }}
                          />
                        </div>
                        <span className="text-xs font-mono w-12 text-right text-white">
                          {value.toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="bg-dark-bg rounded p-4 mb-4">
                <div className="text-sm text-gray-400 mb-2">Ljung-Box Test</div>
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-gray-400">Test Statistic:</span>
                    <span className="ml-2 font-mono font-bold text-white">
                      {results.autocorrelation.ljungBox.stat.toFixed(2)}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">p-value:</span>
                    <span className="ml-2 font-mono text-red-400">
                      {results.autocorrelation.ljungBox.pValue.toFixed(4)}
                    </span>
                  </div>
                  {results.autocorrelation.ljungBox.significant && (
                    <span className="text-red-400 font-semibold">✓ Autocorrelation Present</span>
                  )}
                </div>
              </div>

              <div className="p-4 bg-blue-900/20 border border-blue-700 rounded-lg">
                <div className="font-semibold text-white mb-2">Interpretation:</div>
                <p className="text-sm text-gray-300">
                  Strong autocorrelation detected at multiple lags. This suggests momentum effects
                  - past returns predict future returns. Consider using an AR(1) or ARMA model for
                  time series forecasting.
                </p>
              </div>
            </div>
          )}

          {/* Normality Results */}
          {config.selectedTests.includes('normality') && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Normality Test Results</h2>

              <div className="grid grid-cols-2 gap-6 mb-4">
                <div className="bg-dark-bg rounded p-4">
                  <div className="text-sm text-gray-400 mb-2">Jarque-Bera Test</div>
                  <div className="text-2xl font-bold text-white mb-1">
                    {results.normality.jarqueBera.stat.toFixed(2)}
                  </div>
                  <div className="text-sm text-gray-300">
                    p-value:{' '}
                    <span className="font-mono">
                      {results.normality.jarqueBera.pValue.toFixed(3)}
                    </span>
                  </div>
                  {results.normality.jarqueBera.normal && (
                    <div className="text-sm text-green-400 font-semibold mt-2">
                      ✓ Cannot Reject Normality
                    </div>
                  )}
                </div>

                <div className="bg-dark-bg rounded p-4">
                  <div className="text-sm text-gray-400 mb-2">Shapiro-Wilk Test</div>
                  <div className="text-2xl font-bold text-white mb-1">
                    {results.normality.shapiroWilk.stat.toFixed(3)}
                  </div>
                  <div className="text-sm text-gray-300">
                    p-value:{' '}
                    <span className="font-mono">
                      {results.normality.shapiroWilk.pValue.toFixed(3)}
                    </span>
                  </div>
                  {results.normality.shapiroWilk.normal && (
                    <div className="text-sm text-green-400 font-semibold mt-2">
                      ✓ Cannot Reject Normality
                    </div>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6 mb-4">
                <div className="bg-dark-bg rounded p-4">
                  <div className="text-sm text-gray-400 mb-2">Skewness</div>
                  <div className="text-2xl font-bold text-white">
                    {results.normality.skewness.toFixed(3)}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    {Math.abs(results.normality.skewness) < 0.5 ? 'Nearly Symmetric' : 'Skewed'}
                  </div>
                </div>

                <div className="bg-dark-bg rounded p-4">
                  <div className="text-sm text-gray-400 mb-2">Kurtosis</div>
                  <div className="text-2xl font-bold text-white">
                    {results.normality.kurtosis.toFixed(3)}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    {Math.abs(results.normality.kurtosis - 3) < 0.5 ? 'Normal Tails' : 'Fat Tails'}
                  </div>
                </div>
              </div>

              <div className="p-4 bg-blue-900/20 border border-blue-700 rounded-lg">
                <div className="font-semibold text-white mb-2">Interpretation:</div>
                <p className="text-sm text-gray-300">
                  Returns appear approximately normal (cannot reject normality). Slight positive
                  skewness and kurtosis slightly above 3 indicate mild fat tails. Most statistical
                  methods assuming normality should be valid.
                </p>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
