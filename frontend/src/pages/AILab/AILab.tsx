/**
 * AI Lab - ML/AI Research Dashboard
 * Professional visualization dashboard for neural networks, training, and RL agents
 */

import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Cpu, Zap, Brain, Gamepad2 } from 'lucide-react';
import { useMLStore } from '../../store/useMLStore';
import { NeuralNetworkVisualization } from './components/NeuralNetworkVisualization';
import { TrainingProgressChart } from './components/TrainingProgressChart';
import { RLAgentVisualization } from './components/RLAgentVisualization';
import { FeatureImportance } from './components/FeatureImportance';
import { PanelGrid } from '../../components/common/Panel';

export function AILab() {
  const navigate = useNavigate();
  const {
    neuralNetwork,
    trainingProgress,
    rlAgentData,
    featureImportance,
    isLoading,
    loadMLData,
    updateTrainingProgress,
    updateRLAgent,
  } = useMLStore();

  useEffect(() => {
    // Load initial ML data
    loadMLData();
  }, [loadMLData]);

  useEffect(() => {
    // Simulate real-time training updates every 2 seconds
    const trainingInterval = setInterval(() => {
      if (trainingProgress?.status === 'training') {
        updateTrainingProgress();
      }
    }, 2000);

    return () => clearInterval(trainingInterval);
  }, [trainingProgress, updateTrainingProgress]);

  useEffect(() => {
    // Simulate RL agent updates every 3 seconds
    const rlInterval = setInterval(() => {
      if (rlAgentData) {
        updateRLAgent();
      }
    }, 3000);

    return () => clearInterval(rlInterval);
  }, [rlAgentData, updateRLAgent]);

  if (isLoading || !neuralNetwork || !trainingProgress || !rlAgentData || !featureImportance) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mb-4"></div>
          <p className="text-gray-400">Loading AI Lab...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Status Bar */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">AI Research Lab</h1>
            <p className="text-gray-400 mt-1">
              Deep Learning & Reinforcement Learning Visualization Dashboard
            </p>
          </div>

          <div className="flex gap-6 text-sm">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-green-400" />
              <div>
                <div className="text-gray-400">Active Training Runs</div>
                <div className="font-mono text-xl text-green-400">
                  {trainingProgress.status === 'training' ? '1' : '0'}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Cpu className="w-5 h-5 text-yellow-400" />
              <div>
                <div className="text-gray-400">GPU Utilization</div>
                <div className="font-mono text-xl text-yellow-400">
                  {trainingProgress.hardware.gpuUtilization}%
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-orange-400" />
              <div>
                <div className="text-gray-400">GPU Temperature</div>
                <div className="font-mono text-xl text-orange-400">
                  {trainingProgress.hardware.gpuTemp}°C
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Access Cards */}
      <div className="grid grid-cols-2 gap-6">
        <div
          onClick={() => navigate('/ai-lab/rl-trading')}
          className="bg-dark-card border border-dark-border rounded-lg p-6 hover:border-green-400 cursor-pointer transition group"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center group-hover:scale-110 transition">
              <Gamepad2 className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-white mb-1">RL Trading</h3>
              <p className="text-sm text-gray-400">Train RL agents for automated trading strategies</p>
            </div>
            <button className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-sm font-semibold transition">
              Launch
            </button>
          </div>
        </div>

        <div
          onClick={() => navigate('/ai-lab/meta-labeling')}
          className="bg-dark-card border border-dark-border rounded-lg p-6 hover:border-purple-400 cursor-pointer transition group"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center group-hover:scale-110 transition">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-white mb-1">Meta-Labeling</h3>
              <p className="text-sm text-gray-400">ML-powered bet sizing for primary strategy signals</p>
            </div>
            <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm font-semibold transition">
              Launch
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid - 2x2 Panels */}
      <PanelGrid cols={2} minHeight="650px">
        {/* Panel 1: 3D Neural Network */}
        <NeuralNetworkVisualization architecture={neuralNetwork} />

        {/* Panel 2: Training Progress */}
        <TrainingProgressChart data={trainingProgress} />

        {/* Panel 3: RL Agent */}
        <RLAgentVisualization data={rlAgentData} />

        {/* Panel 4: Feature Importance */}
        <FeatureImportance data={featureImportance} />
      </PanelGrid>

      {/* Bottom Info Bar */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
          <div className="space-y-1">
            <div className="text-xs text-gray-400">Current Model</div>
            <div className="font-semibold text-white truncate">{trainingProgress.modelName}</div>
            <div className="text-xs text-gray-500">
              {trainingProgress.hyperparameters.optimizer} optimizer
            </div>
          </div>
          <div className="space-y-1">
            <div className="text-xs text-gray-400">Training Status</div>
            <div className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full flex-shrink-0 ${
                  trainingProgress.status === 'training'
                    ? 'bg-green-400 animate-pulse'
                    : 'bg-gray-600'
                }`}
              />
              <span className="font-semibold capitalize">{trainingProgress.status}</span>
            </div>
            <div className="text-xs text-gray-500">
              Epoch {trainingProgress.currentEpoch}/{trainingProgress.totalEpochs}
            </div>
          </div>
          <div className="space-y-1">
            <div className="text-xs text-gray-400">RL Agent</div>
            <div className="font-semibold text-white truncate">{rlAgentData.agentName}</div>
            <div className="text-xs text-gray-500">
              Ep {rlAgentData.currentEpisode}/{rlAgentData.totalEpisodes}
            </div>
          </div>
          <div className="space-y-1">
            <div className="text-xs text-gray-400">Hardware</div>
            <div className="font-semibold text-white">{trainingProgress.hardware.gpuModel}</div>
            <div className="text-xs text-gray-500">
              {trainingProgress.hardware.gpuMemory.toFixed(1)}GB VRAM
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
