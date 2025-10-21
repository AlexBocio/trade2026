/**
 * Backtest Report - Detailed backtest analysis with metrics, trades, and Monte Carlo
 */

import { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, TrendingUp, TrendingDown, Activity } from 'lucide-react';
import Plot from 'react-plotly.js';
import { MonteCarloSimulation } from '../../components/backtesting/MonteCarloSimulation';
import { mockBacktestResults, generateMonteCarloData } from '../../services/mock-data/backtest-data';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

export function BacktestReport() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'overview' | 'trades' | 'montecarlo'>('overview');

  // Use mock data for now (would be fetched based on id in real implementation)
  const results = mockBacktestResults;

  // Generate Monte Carlo data from trades
  const monteCarloData = useMemo(() => {
    return generateMonteCarloData(results.trades, 1000);
  }, [results.trades]);

  // Column definitions for trades table
  const columnDefs = [
    {
      field: 'symbol',
      headerName: 'Symbol',
      width: 100,
      cellRenderer: (params: any) => <strong className="font-mono">{params.value}</strong>,
      pinned: 'left' as const,
    },
    {
      field: 'entryDate',
      headerName: 'Entry Date',
      width: 180,
      valueFormatter: (p: any) => new Date(p.value).toLocaleString(),
    },
    {
      field: 'exitDate',
      headerName: 'Exit Date',
      width: 180,
      valueFormatter: (p: any) => new Date(p.value).toLocaleString(),
    },
    {
      field: 'side',
      headerName: 'Side',
      width: 80,
      cellStyle: (params: any) => ({
        color: params.value === 'LONG' ? '#10b981' : '#ef4444',
        fontWeight: 'bold',
      }),
    },
    {
      field: 'entryPrice',
      headerName: 'Entry',
      width: 100,
      valueFormatter: (p: any) => `$${p.value.toFixed(2)}`,
    },
    {
      field: 'exitPrice',
      headerName: 'Exit',
      width: 100,
      valueFormatter: (p: any) => `$${p.value.toFixed(2)}`,
    },
    {
      field: 'quantity',
      headerName: 'Qty',
      width: 80,
    },
    {
      field: 'pnl',
      headerName: 'P&L',
      width: 120,
      cellStyle: (params: any) => ({
        color: params.value >= 0 ? '#10b981' : '#ef4444',
        fontWeight: 'bold',
      }),
      valueFormatter: (p: any) => `${p.value >= 0 ? '+' : ''}$${p.value.toFixed(2)}`,
    },
    {
      field: 'pnlPercent',
      headerName: 'P&L %',
      width: 100,
      cellStyle: (params: any) => ({
        color: params.value >= 0 ? '#10b981' : '#ef4444',
        fontWeight: 'bold',
      }),
      valueFormatter: (p: any) => `${p.value >= 0 ? '+' : ''}${p.value.toFixed(2)}%`,
    },
    {
      field: 'holdingPeriod',
      headerName: 'Hold (days)',
      width: 120,
      valueFormatter: (p: any) => p.value.toFixed(2),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/backtesting')}
            className="p-2 hover:bg-dark-border rounded-lg transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-white">Backtest Report</h1>
            <p className="text-sm text-gray-400">Detailed results and analysis</p>
          </div>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-6 gap-4">
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Total Return</div>
          <div className={`text-2xl font-bold ${results.metrics.totalReturn >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {results.metrics.totalReturn >= 0 ? '+' : ''}${results.metrics.totalReturn.toLocaleString()}
          </div>
          <div className={`text-sm ${results.metrics.annualizedReturn >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {results.metrics.annualizedReturn >= 0 ? '+' : ''}{results.metrics.annualizedReturn.toFixed(2)}%
          </div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Win Rate</div>
          <div className="text-2xl font-bold text-white">{results.metrics.winRate.toFixed(1)}%</div>
          <div className="text-sm text-gray-400">
            {results.metrics.winningTrades}W / {results.metrics.losingTrades}L
          </div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Sharpe Ratio</div>
          <div className="text-2xl font-bold text-white">{results.metrics.sharpeRatio.toFixed(2)}</div>
          <div className="text-sm text-gray-400">Risk-adjusted</div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Max Drawdown</div>
          <div className="text-2xl font-bold text-red-400">
            {results.metrics.maxDrawdownPercent.toFixed(2)}%
          </div>
          <div className="text-sm text-red-400">${results.metrics.maxDrawdown.toLocaleString()}</div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Profit Factor</div>
          <div className="text-2xl font-bold text-white">{results.metrics.profitFactor.toFixed(2)}</div>
          <div className="text-sm text-gray-400">Win/Loss ratio</div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Total Trades</div>
          <div className="text-2xl font-bold text-white">{results.metrics.totalTrades}</div>
          <div className="text-sm text-gray-400">
            Avg ${results.metrics.avgTrade.toFixed(2)}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-dark-border">
        <div className="flex gap-1">
          {[
            { id: 'overview', label: 'Overview', icon: Activity },
            { id: 'trades', label: 'Trade Log', icon: TrendingUp },
            { id: 'montecarlo', label: 'Monte Carlo', icon: TrendingDown },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-3 border-b-2 font-medium transition ${
                  activeTab === tab.id
                    ? 'border-green-400 text-white'
                    : 'border-transparent text-gray-400 hover:text-white hover:border-dark-border'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Equity Curve */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Equity Curve</h3>
            <Plot
              data={[
                {
                  x: results.equityCurve.map((d) => d.date),
                  y: results.equityCurve.map((d) => d.equity),
                  type: 'scatter',
                  mode: 'lines',
                  name: 'Equity',
                  line: { color: '#00ff88', width: 2 },
                },
              ]}
              layout={{
                paper_bgcolor: '#1a1f2e',
                plot_bgcolor: '#1a1f2e',
                font: { color: '#e0e0e0', family: 'monospace' },
                xaxis: { gridcolor: '#2a3142' },
                yaxis: { title: 'Portfolio Value ($)', gridcolor: '#2a3142', tickformat: '$,.0f' },
                margin: { l: 60, r: 20, t: 20, b: 50 },
                autosize: true,
                showlegend: false,
              }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '400px' }}
            />
          </div>

          {/* Monthly Returns */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Monthly Returns</h3>
            <Plot
              data={[
                {
                  x: results.monthlyReturns.map((m) => m.month),
                  y: results.monthlyReturns.map((m) => m.returnPercent),
                  type: 'bar',
                  marker: {
                    color: results.monthlyReturns.map((m) =>
                      m.returnPercent >= 0 ? '#10b981' : '#ef4444'
                    ),
                  },
                },
              ]}
              layout={{
                paper_bgcolor: '#1a1f2e',
                plot_bgcolor: '#1a1f2e',
                font: { color: '#e0e0e0', family: 'monospace' },
                xaxis: { gridcolor: '#2a3142' },
                yaxis: { title: 'Return %', gridcolor: '#2a3142', tickformat: '.2f', zeroline: true },
                margin: { l: 60, r: 20, t: 20, b: 80 },
                autosize: true,
                showlegend: false,
              }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '400px' }}
            />
          </div>

          {/* Additional Metrics Grid */}
          <div className="grid grid-cols-3 gap-6">
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Win/Loss Analysis</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Avg Win</span>
                  <span className="text-green-400 font-semibold">${results.metrics.avgWin.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Avg Loss</span>
                  <span className="text-red-400 font-semibold">${results.metrics.avgLoss.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Best Trade</span>
                  <span className="text-green-400 font-semibold">${results.metrics.bestTrade.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Worst Trade</span>
                  <span className="text-red-400 font-semibold">${results.metrics.worstTrade.toFixed(2)}</span>
                </div>
              </div>
            </div>

            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Risk Metrics</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Sharpe Ratio</span>
                  <span className="text-white font-semibold">{results.metrics.sharpeRatio.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Sortino Ratio</span>
                  <span className="text-white font-semibold">{results.metrics.sortinoRatio.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Calmar Ratio</span>
                  <span className="text-white font-semibold">{results.metrics.calmarRatio.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Volatility</span>
                  <span className="text-white font-semibold">{results.metrics.volatility.toFixed(2)}%</span>
                </div>
              </div>
            </div>

            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Trade Stats</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Avg Holding</span>
                  <span className="text-white font-semibold">{results.metrics.avgHoldingPeriod.toFixed(2)} days</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Commissions</span>
                  <span className="text-white font-semibold">${results.metrics.totalCommissions.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Avg Trade</span>
                  <span className="text-white font-semibold">${results.metrics.avgTrade.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Profit Factor</span>
                  <span className="text-white font-semibold">{results.metrics.profitFactor.toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'trades' && (
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            Trade Log ({results.trades.length} trades)
          </h3>
          <div className="ag-theme-alpine-dark" style={{ height: 600, width: '100%' }}>
            <AgGridReact
              rowData={results.trades}
              columnDefs={columnDefs}
              defaultColDef={{
                sortable: true,
                filter: true,
                resizable: true,
              }}
              rowHeight={50}
              suppressCellFocus={true}
            />
          </div>
        </div>
      )}

      {activeTab === 'montecarlo' && (
        <MonteCarloSimulation
          simulations={monteCarloData.simulations}
          percentiles={monteCarloData.percentiles}
        />
      )}
    </div>
  );
}
