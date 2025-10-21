/**
 * Simulation Engine - Advanced simulation and analysis tools
 * Main page with tab-based layout for different simulation methods
 */

import { useState } from 'react';
import { ArrowLeft, Beaker } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { BootstrapSimulation } from '../../components/simulation/BootstrapSimulation';
import { MonteCarloAdvanced } from '../../components/simulation/MonteCarloAdvanced';
import { WalkForwardComparison } from '../../components/simulation/WalkForwardComparison';
import { ScenarioAnalysis } from '../../components/simulation/ScenarioAnalysis';
import { SyntheticDataGenerator } from '../../components/simulation/SyntheticDataGenerator';

type SimulationTab =
  | 'bootstrap'
  | 'monte-carlo'
  | 'walk-forward'
  | 'scenario'
  | 'synthetic';

const TABS = [
  {
    id: 'bootstrap',
    name: 'Bootstrap Resampling',
    description: 'Test return distribution assumptions',
    icon: '🔄',
  },
  {
    id: 'monte-carlo',
    name: 'Advanced Monte Carlo',
    description: 'GARCH, Copula, Jump-Diffusion models',
    icon: '🎲',
  },
  {
    id: 'walk-forward',
    name: 'Walk-Forward Comparison',
    description: 'Compare different WF methods',
    icon: '⏩',
  },
  {
    id: 'scenario',
    name: 'Scenario Analysis',
    description: 'Stress test against crises',
    icon: '⚠️',
  },
  {
    id: 'synthetic',
    name: 'Synthetic Data',
    description: 'GAN/VAE data generation',
    icon: '🤖',
  },
];

export function SimulationEngine() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<SimulationTab>('bootstrap');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'bootstrap':
        return <BootstrapSimulation />;
      case 'monte-carlo':
        return <MonteCarloAdvanced />;
      case 'walk-forward':
        return <WalkForwardComparison />;
      case 'scenario':
        return <ScenarioAnalysis />;
      case 'synthetic':
        return <SyntheticDataGenerator />;
      default:
        return <BootstrapSimulation />;
    }
  };

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
            <div className="flex items-center gap-2">
              <Beaker className="w-6 h-6 text-blue-400" />
              <h1 className="text-2xl font-bold text-white">Simulation Engine</h1>
            </div>
            <p className="text-sm text-gray-400">
              Advanced simulation tools for strategy validation and risk analysis
            </p>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-2">
        <div className="grid grid-cols-5 gap-2">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as SimulationTab)}
              className={`p-4 rounded-lg text-left transition ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-dark-bg text-gray-400 hover:bg-dark-border hover:text-white'
              }`}
            >
              <div className="text-2xl mb-2">{tab.icon}</div>
              <div className="font-semibold text-sm mb-1">{tab.name}</div>
              <div className="text-xs opacity-75">{tab.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="min-h-[600px]">{renderTabContent()}</div>

      {/* Info Footer */}
      <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <div className="text-blue-400 text-2xl">💡</div>
          <div>
            <div className="font-semibold text-white mb-1">About Simulation Engine</div>
            <div className="text-sm text-gray-300 space-y-1">
              <p>
                <strong>Bootstrap Resampling:</strong> Tests if your strategy's performance is robust or
                just lucky by resampling historical returns.
              </p>
              <p>
                <strong>Monte Carlo:</strong> Generates thousands of possible future price paths using
                advanced statistical models (GARCH, copulas, etc.).
              </p>
              <p>
                <strong>Walk-Forward Comparison:</strong> Compares anchored, rolling, and expanding window
                methods to see which is most stable for your strategy.
              </p>
              <p>
                <strong>Scenario Analysis:</strong> Stress tests your portfolio against historical crisis
                events (2008 crash, COVID-19, etc.) to measure downside risk.
              </p>
              <p>
                <strong>Synthetic Data:</strong> Uses deep learning (GAN/VAE) to generate realistic
                synthetic market data for training and testing.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
