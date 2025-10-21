/**
 * RL Trading - Reinforcement Learning Trading Agent Training and Backtesting
 */

import { useState } from 'react';
import { Brain, TrendingUp, Play, Loader, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Plot from 'react-plotly.js';

const RL_API = 'http://localhost:5002/api/rl';

export function RLTrading() {
  const navigate = useNavigate();
  const [ticker, setTicker] = useState('AAPL');
  const [episodes, setEpisodes] = useState(100);
  const [agentId, setAgentId] = useState('my_rl_agent');
  const [training, setTraining] = useState(false);
  const [trainResult, setTrainResult] = useState<any>(null);
  const [backtestResult, setBacktestResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTrain = async () => {
    setTraining(true);
    setError(null);

    try {
      const response = await fetch(`${RL_API}/train-dqn`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticker, episodes, agent_id: agentId })
      });

      if (!response.ok) {
        throw new Error('Backend not responding');
      }

      const data = await response.json();
      setTrainResult(data);
    } catch (error) {
      console.error('Training error:', error);
      setError('Backend not running! Start: python backend/rl_trading/app.py');
    } finally {
      setTraining(false);
    }
  };

  const handleBacktest = async () => {
    setError(null);

    try {
      const response = await fetch(`${RL_API}/backtest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_id: agentId, ticker })
      });

      if (!response.ok) {
        throw new Error('Backend not responding');
      }

      const data = await response.json();
      setBacktestResult(data);
    } catch (error) {
      console.error('Backtest error:', error);
      setError('Backend not running! Start: python backend/rl_trading/app.py');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/ai-lab')}
            className="p-2 hover:bg-dark-border rounded-lg transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-white">Reinforcement Learning Trading</h1>
            <p className="text-sm text-gray-400">
              Train and backtest Deep Q-Network trading agents
            </p>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-400">
            <span className="font-semibold">⚠️ {error}</span>
          </div>
        </div>
      )}

      {/* Training Section */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Train RL Agent</h2>

        <div className="grid grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Ticker</label>
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
              placeholder="AAPL"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-2">Episodes</label>
            <input
              type="number"
              value={episodes}
              onChange={(e) => setEpisodes(Number(e.target.value))}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
              min="10"
              max="1000"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-2">Agent ID</label>
            <input
              type="text"
              value={agentId}
              onChange={(e) => setAgentId(e.target.value)}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
              placeholder="my_rl_agent"
            />
          </div>
        </div>

        <div className="flex gap-4">
          <button
            onClick={handleTrain}
            disabled={training}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition disabled:opacity-50 flex items-center gap-2"
          >
            {training ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                Training...
              </>
            ) : (
              <>
                <Brain className="w-5 h-5" />
                Train Agent
              </>
            )}
          </button>

          <button
            onClick={handleBacktest}
            disabled={!agentId || training}
            className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition disabled:opacity-50 flex items-center gap-2"
          >
            <Play className="w-5 h-5" />
            Backtest Agent
          </button>
        </div>
      </div>

      {/* Training Results */}
      {trainResult && (
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Training Results</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-dark-bg rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">Episodes Trained</div>
              <div className="text-2xl font-bold text-white">{trainResult.episodes_trained}</div>
            </div>
            <div className="bg-dark-bg rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">Final Reward</div>
              <div className="text-2xl font-bold text-green-400">
                {trainResult.final_reward?.toFixed(4) || 'N/A'}
              </div>
            </div>
            <div className="bg-dark-bg rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">Avg Reward (last 10)</div>
              <div className="text-2xl font-bold text-blue-400">
                {trainResult.avg_reward?.toFixed(4) || 'N/A'}
              </div>
            </div>
          </div>

          {trainResult.agent_saved && (
            <div className="mt-4 p-3 bg-green-900/30 border border-green-700 rounded-lg text-green-400 text-sm">
              ✓ Agent saved successfully: {agentId}
            </div>
          )}
        </div>
      )}

      {/* Backtest Results */}
      {backtestResult && (
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Backtest Results</h2>

          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-dark-bg rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">Initial Balance</div>
              <div className="text-xl font-bold text-white">
                ${backtestResult.initial_balance?.toLocaleString() || '0'}
              </div>
            </div>
            <div className="bg-dark-bg rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">Final Value</div>
              <div className="text-xl font-bold text-green-400">
                ${backtestResult.final_value?.toLocaleString() || '0'}
              </div>
            </div>
            <div className="bg-dark-bg rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">Total Return</div>
              <div
                className={`text-xl font-bold ${
                  (backtestResult.total_return || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                }`}
              >
                {backtestResult.total_return >= 0 ? '+' : ''}
                {backtestResult.total_return?.toFixed(2) || '0.00'}%
              </div>
            </div>
            <div className="bg-dark-bg rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">Total Trades</div>
              <div className="text-xl font-bold text-white">{backtestResult.num_trades || 0}</div>
            </div>
          </div>

          {/* Portfolio Curve */}
          {backtestResult.portfolio_curve && backtestResult.portfolio_curve.length > 0 && (
            <div className="mt-4">
              <h3 className="text-lg font-semibold text-white mb-3">Portfolio Value Over Time</h3>
              <Plot
                data={[
                  {
                    y: backtestResult.portfolio_curve,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Portfolio Value',
                    line: { color: '#22c55e', width: 2 },
                  },
                ]}
                layout={{
                  paper_bgcolor: '#1a1f2e',
                  plot_bgcolor: '#1a1f2e',
                  font: { color: '#e0e0e0', family: 'monospace' },
                  xaxis: { title: 'Step', gridcolor: '#2a3142' },
                  yaxis: { title: 'Portfolio Value ($)', gridcolor: '#2a3142', tickformat: '$,.0f' },
                  margin: { t: 20, b: 40, l: 60, r: 20 },
                  autosize: true,
                  showlegend: false,
                }}
                config={{ displayModeBar: false, responsive: true }}
                style={{ width: '100%', height: '400px' }}
              />
            </div>
          )}

          {/* Trade Actions */}
          {backtestResult.actions && backtestResult.actions.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-white mb-3">Agent Actions</h3>
              <div className="flex gap-4">
                <div className="flex-1 bg-dark-bg rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">Buy Actions</div>
                  <div className="text-2xl font-bold text-green-400">
                    {backtestResult.actions.filter((a: number) => a === 1).length}
                  </div>
                </div>
                <div className="flex-1 bg-dark-bg rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">Hold Actions</div>
                  <div className="text-2xl font-bold text-gray-400">
                    {backtestResult.actions.filter((a: number) => a === 0).length}
                  </div>
                </div>
                <div className="flex-1 bg-dark-bg rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">Sell Actions</div>
                  <div className="text-2xl font-bold text-red-400">
                    {backtestResult.actions.filter((a: number) => a === 2).length}
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
