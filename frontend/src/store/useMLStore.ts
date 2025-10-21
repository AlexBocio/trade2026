/**
 * ML Store - Manages ML models, training runs, and real-time updates
 */

import { create } from 'zustand';
import type {
  NetworkArchitecture,
  TrainingProgress,
  RLAgentData,
  FeatureImportanceData,
} from '../services/mock-data/ml-model-data';
import {
  mockNeuralNetwork,
  mockTrainingProgress,
  mockRLAgentData,
  mockFeatureImportance,
} from '../services/mock-data/ml-model-data';

interface MLState {
  // Data
  neuralNetwork: NetworkArchitecture | null;
  trainingProgress: TrainingProgress | null;
  rlAgentData: RLAgentData | null;
  featureImportance: FeatureImportanceData | null;
  isLoading: boolean;

  // Actions
  loadMLData: () => Promise<void>;
  updateTrainingProgress: () => void;
  updateRLAgent: () => void;
}

const delay = (ms: number = 500) => new Promise((resolve) => setTimeout(resolve, ms));

export const useMLStore = create<MLState>((set, get) => ({
  neuralNetwork: null,
  trainingProgress: null,
  rlAgentData: null,
  featureImportance: null,
  isLoading: false,

  loadMLData: async () => {
    set({ isLoading: true });
    await delay();
    set({
      neuralNetwork: mockNeuralNetwork,
      trainingProgress: mockTrainingProgress,
      rlAgentData: mockRLAgentData,
      featureImportance: mockFeatureImportance,
      isLoading: false,
    });
  },

  updateTrainingProgress: () => {
    set((state) => {
      if (!state.trainingProgress || state.trainingProgress.status !== 'training') {
        return state;
      }

      const newEpoch = state.trainingProgress.currentEpoch + 1;

      if (newEpoch > state.trainingProgress.totalEpochs) {
        return {
          ...state,
          trainingProgress: {
            ...state.trainingProgress,
            status: 'completed' as const,
          },
        };
      }

      // Calculate new loss values (decreasing with noise)
      const baseTrainLoss = 0.15 + (0.05 * (state.trainingProgress.totalEpochs - newEpoch)) / state.trainingProgress.totalEpochs;
      const baseValLoss = 0.25 + (0.08 * (state.trainingProgress.totalEpochs - newEpoch)) / state.trainingProgress.totalEpochs;
      const trainLoss = Math.max(0.05, baseTrainLoss + (Math.random() - 0.5) * 0.03);
      const valLoss = Math.max(0.15, baseValLoss + (Math.random() - 0.5) * 0.05);

      // Calculate accuracies (increasing with noise)
      const baseTrainAcc = 0.85 + (0.09 * newEpoch) / state.trainingProgress.totalEpochs;
      const baseValAcc = 0.80 + (0.09 * newEpoch) / state.trainingProgress.totalEpochs;
      const trainAcc = Math.min(0.99, baseTrainAcc + (Math.random() - 0.5) * 0.02);
      const valAcc = Math.min(0.95, baseValAcc + (Math.random() - 0.5) * 0.03);

      // Update GPU utilization
      const gpuUtilization = 75 + Math.floor(Math.random() * 20);
      const gpuTemp = 68 + Math.floor(Math.random() * 8);

      return {
        ...state,
        trainingProgress: {
          ...state.trainingProgress,
          currentEpoch: newEpoch,
          metrics: {
            ...state.trainingProgress.metrics,
            trainLoss: [
              ...state.trainingProgress.metrics.trainLoss,
              { epoch: newEpoch, value: trainLoss },
            ],
            valLoss: [
              ...state.trainingProgress.metrics.valLoss,
              { epoch: newEpoch, value: valLoss },
            ],
            trainAccuracy: [
              ...state.trainingProgress.metrics.trainAccuracy,
              { epoch: newEpoch, value: trainAcc },
            ],
            valAccuracy: [
              ...state.trainingProgress.metrics.valAccuracy,
              { epoch: newEpoch, value: valAcc },
            ],
          },
          hardware: {
            ...state.trainingProgress.hardware,
            gpuUtilization,
            gpuTemp,
            gpuMemory: 11.5 + Math.random() * 1.5,
          },
        },
      };
    });
  },

  updateRLAgent: () => {
    set((state) => {
      if (!state.rlAgentData) return state;

      const newEpisode = state.rlAgentData.currentEpisode + 1;
      if (newEpisode > state.rlAgentData.totalEpisodes) {
        return state;
      }

      // Generate new episode reward
      const progress = newEpisode / state.rlAgentData.totalEpisodes;
      const baseReward = -500 + 3000 * progress;
      const noise = (Math.random() - 0.5) * 500;
      const totalReward = baseReward + noise;

      const lastAvg =
        state.rlAgentData.episodes[state.rlAgentData.episodes.length - 1]?.avgReward || -500;
      const avgReward = lastAvg * 0.95 + totalReward * 0.05;

      // Update Q-values slightly
      const qValues = {
        buy: Math.max(0, Math.min(1, state.rlAgentData.qValues.buy + (Math.random() - 0.5) * 0.05)),
        hold: Math.max(0, Math.min(1, state.rlAgentData.qValues.hold + (Math.random() - 0.5) * 0.05)),
        sell: Math.max(0, Math.min(1, state.rlAgentData.qValues.sell + (Math.random() - 0.5) * 0.05)),
      };

      return {
        ...state,
        rlAgentData: {
          ...state.rlAgentData,
          currentEpoch: newEpisode,
          episodes: [
            ...state.rlAgentData.episodes,
            {
              episode: newEpisode,
              totalReward,
              avgReward,
              steps: Math.floor(50 + Math.random() * 100),
            },
          ],
          qValues,
        },
      };
    });
  },
}));
