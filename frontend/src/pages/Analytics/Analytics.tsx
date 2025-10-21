/**
 * Analytics Dashboard - Main dashboard for analytics and research workbench
 */

import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAnalyticsStore } from '../../store/useAnalyticsStore';
import {
  TrendingUp,
  BarChart3,
  Calendar,
  Activity,
  Target,
  Beaker,
  Code,
  LineChart,
} from 'lucide-react';

const analyticsTools = [
  {
    id: 'factors',
    title: 'Factor Analysis',
    description: 'Test which factors (momentum, value, volatility) drive returns',
    icon: TrendingUp,
    path: '/analytics/factors',
    color: 'from-green-400 to-blue-500',
  },
  {
    id: 'stats',
    title: 'Statistical Tests',
    description: 'Correlation, cointegration, stationarity, autocorrelation',
    icon: BarChart3,
    path: '/analytics/stats',
    color: 'from-blue-400 to-purple-500',
  },
  {
    id: 'regime',
    title: 'Market Regime Detection',
    description: 'Identify bull, bear, and sideways market regimes',
    icon: Activity,
    path: '/analytics/regime',
    color: 'from-purple-400 to-pink-500',
  },
  {
    id: 'seasonality',
    title: 'Seasonality Analysis',
    description: 'Discover day-of-week, month, time-of-day patterns',
    icon: Calendar,
    path: '/analytics/seasonality',
    color: 'from-yellow-400 to-orange-500',
  },
  {
    id: 'distribution',
    title: 'Distribution Analysis',
    description: 'Analyze returns distribution, fat tails, skewness, kurtosis',
    icon: Target,
    path: '/analytics/distribution',
    color: 'from-red-400 to-pink-500',
  },
  {
    id: 'hypothesis',
    title: 'Hypothesis Testing',
    description: 'A/B test strategy variants, statistical significance',
    icon: Beaker,
    path: '/analytics/hypothesis',
    color: 'from-cyan-400 to-blue-500',
  },
  {
    id: 'indicators',
    title: 'Custom Indicator Builder',
    description: 'Create and backtest custom technical indicators',
    icon: Code,
    path: '/analytics/indicators',
    color: 'from-green-400 to-teal-500',
  },
  {
    id: 'fractional-diff',
    title: 'Fractional Differentiation',
    description: 'Transform non-stationary prices to stationary features with memory preservation',
    icon: TrendingUp,
    path: '/analytics/fractional-diff',
    color: 'from-orange-400 to-red-500',
  },
];

export function Analytics() {
  const navigate = useNavigate();
  const { recentAnalyses, loadRecentAnalyses } = useAnalyticsStore();

  useEffect(() => {
    loadRecentAnalyses();
  }, [loadRecentAnalyses]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <LineChart className="w-8 h-8 text-green-400" />
        <div>
          <h1 className="text-2xl font-bold text-white">Analytics & Research Workbench</h1>
          <p className="text-sm text-gray-400">
            Statistical tools for systematic traders. Test hypotheses, discover patterns, validate strategies.
          </p>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-4 gap-6">
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">Total Analyses</div>
          <div className="text-3xl font-bold text-white">42</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">Significant Findings</div>
          <div className="text-3xl font-bold text-green-400">28</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">Best Factor</div>
          <div className="text-lg font-bold text-white">Momentum</div>
          <div className="text-sm text-gray-400">p &lt; 0.001</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">Best Trading Day</div>
          <div className="text-lg font-bold text-white">Tuesday</div>
          <div className="text-sm text-gray-400">+0.8% avg</div>
        </div>
      </div>

      {/* Tool Cards */}
      <div className="grid grid-cols-3 gap-6">
        {analyticsTools.map((tool) => {
          const Icon = tool.icon;
          return (
            <div
              key={tool.id}
              onClick={() => navigate(tool.path)}
              className="bg-dark-card border border-dark-border rounded-lg p-6 hover:border-green-400 cursor-pointer transition group"
            >
              <div
                className={`w-12 h-12 rounded-lg bg-gradient-to-br ${tool.color} flex items-center justify-center mb-4 group-hover:scale-110 transition`}
              >
                <Icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{tool.title}</h3>
              <p className="text-sm text-gray-400 mb-4">{tool.description}</p>
              <button className="px-4 py-2 bg-dark-border hover:bg-dark-border-hover rounded-lg text-sm font-semibold transition">
                Launch Tool
              </button>
            </div>
          );
        })}
      </div>

      {/* Recent Analyses */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Recent Analyses</h2>
        {recentAnalyses.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            No analyses yet. Launch a tool to get started.
          </div>
        ) : (
          <div className="space-y-3">
            {recentAnalyses.map((analysis) => (
              <div
                key={analysis.id}
                onClick={() => navigate(`/analytics/${analysis.type}/${analysis.id}`)}
                className="bg-dark-bg rounded-lg p-4 hover:bg-dark-border cursor-pointer transition"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-white">{analysis.title}</div>
                    <div className="text-sm text-gray-400">
                      {analysis.type} • {new Date(analysis.createdAt).toLocaleDateString()}
                    </div>
                  </div>
                  {analysis.significant && (
                    <span className="px-3 py-1 bg-green-900/30 border border-green-700 text-green-400 rounded text-sm font-semibold">
                      Significant (p &lt; {analysis.pValue})
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
