/**
 * Mock ML/AI Model Data - Neural networks, training runs, RL agents
 */

export interface NetworkArchitecture {
  layers: Array<{
    name: string;
    neurons: number;
    activationFunction: string;
  }>;
  weights: number[][][]; // [layer][from][to]
  biases: number[][];
}

export interface TrainingProgress {
  runId: string;
  modelName: string;
  status: 'training' | 'completed' | 'failed' | 'paused';
  startTime: string;
  currentEpoch: number;
  totalEpochs: number;
  metrics: {
    trainLoss: Array<{ epoch: number; value: number }>;
    valLoss: Array<{ epoch: number; value: number }>;
    trainAccuracy: Array<{ epoch: number; value: number }>;
    valAccuracy: Array<{ epoch: number; value: number }>;
  };
  hyperparameters: {
    learningRate: number;
    batchSize: number;
    optimizer: string;
    lossFunction: string;
  };
  hardware: {
    gpuModel: string;
    gpuUtilization: number;
    gpuMemory: number;
    gpuTemp: number;
  };
}

export interface RLAgentData {
  agentId: string;
  agentName: string;
  currentEpisode: number;
  totalEpisodes: number;
  episodes: Array<{
    episode: number;
    totalReward: number;
    avgReward: number;
    steps: number;
  }>;
  latestEpisode: {
    episode: number;
    prices: number[];
    actions: Array<{ step: number; action: 'buy' | 'sell' | 'hold'; price: number }>;
    rewards: number[];
  };
  actionStats: {
    buy: number;
    hold: number;
    sell: number;
  };
  qValues: {
    buy: number;
    hold: number;
    sell: number;
  };
}

export interface FeatureImportanceData {
  modelId: string;
  features: Array<{
    name: string;
    importance: number;
    category: 'technical' | 'fundamental' | 'sentiment' | 'macro';
  }>;
}

// Helper functions
function generateRandomWeights(layerSizes: number[]): number[][][] {
  const weights: number[][][] = [];
  for (let i = 0; i < layerSizes.length - 1; i++) {
    const layerWeights: number[][] = [];
    for (let j = 0; j < layerSizes[i]; j++) {
      const neuronWeights: number[] = [];
      for (let k = 0; k < layerSizes[i + 1]; k++) {
        neuronWeights.push((Math.random() - 0.5) * 2); // -1 to 1
      }
      layerWeights.push(neuronWeights);
    }
    weights.push(layerWeights);
  }
  return weights;
}

function generateRandomBiases(layerSizes: number[]): number[][] {
  return layerSizes.map((size) => Array.from({ length: size }, () => (Math.random() - 0.5) * 0.5));
}

function generateTrainingCurve(startLoss: number, endLoss: number, epochs: number): Array<{ epoch: number; value: number }> {
  const curve: Array<{ epoch: number; value: number }> = [];
  for (let i = 0; i <= epochs; i++) {
    const progress = i / epochs;
    const noise = (Math.random() - 0.5) * 0.1;
    const value = startLoss + (endLoss - startLoss) * progress + noise * (1 - progress);
    curve.push({ epoch: i, value: Math.max(0, value) });
  }
  return curve;
}

// Mock Neural Network
export const mockNeuralNetwork: NetworkArchitecture = {
  layers: [
    { name: 'Input', neurons: 64, activationFunction: 'none' },
    { name: 'Hidden 1', neurons: 128, activationFunction: 'ReLU' },
    { name: 'Hidden 2', neurons: 256, activationFunction: 'ReLU' },
    { name: 'Hidden 3', neurons: 128, activationFunction: 'ReLU' },
    { name: 'Output', neurons: 3, activationFunction: 'Softmax' },
  ],
  weights: generateRandomWeights([64, 128, 256, 128, 3]),
  biases: generateRandomBiases([128, 256, 128, 3]),
};

// Mock Training Progress
export const mockTrainingProgress: TrainingProgress = {
  runId: 'train-20251007-143000',
  modelName: 'Momentum Predictor v2.0',
  status: 'training',
  startTime: '2025-10-07T14:30:00Z',
  currentEpoch: 45,
  totalEpochs: 100,
  metrics: {
    trainLoss: generateTrainingCurve(2.45, 0.15, 45),
    valLoss: generateTrainingCurve(2.51, 0.25, 45),
    trainAccuracy: generateTrainingCurve(0.33, 0.94, 45).map((d) => ({
      epoch: d.epoch,
      value: Math.min(1, d.value),
    })),
    valAccuracy: generateTrainingCurve(0.31, 0.89, 45).map((d) => ({
      epoch: d.epoch,
      value: Math.min(1, d.value),
    })),
  },
  hyperparameters: {
    learningRate: 0.001,
    batchSize: 32,
    optimizer: 'Adam',
    lossFunction: 'CrossEntropy',
  },
  hardware: {
    gpuModel: 'RTX 5080',
    gpuUtilization: 87,
    gpuMemory: 12.3,
    gpuTemp: 72,
  },
};

// Mock RL Agent Data
function generateEpisodeRewards(numEpisodes: number): Array<{ episode: number; totalReward: number; avgReward: number; steps: number }> {
  const episodes: Array<{ episode: number; totalReward: number; avgReward: number; steps: number }> = [];
  let runningAvg = -500;

  for (let i = 0; i < numEpisodes; i++) {
    const progress = i / numEpisodes;
    const baseReward = -500 + 3000 * progress; // Improve over time
    const noise = (Math.random() - 0.5) * 500;
    const totalReward = baseReward + noise;

    runningAvg = runningAvg * 0.95 + totalReward * 0.05;

    episodes.push({
      episode: i,
      totalReward,
      avgReward: runningAvg,
      steps: Math.floor(50 + Math.random() * 100),
    });
  }

  return episodes;
}

export const mockRLAgentData: RLAgentData = {
  agentId: 'rl-agent-001',
  agentName: 'DQN Trader v1.0',
  currentEpisode: 250,
  totalEpisodes: 500,
  episodes: generateEpisodeRewards(250),
  latestEpisode: {
    episode: 250,
    prices: Array.from({ length: 100 }, (_, i) => 100 + Math.sin(i * 0.1) * 10 + (Math.random() - 0.5) * 5),
    actions: [
      { step: 10, action: 'buy', price: 105.2 },
      { step: 45, action: 'sell', price: 112.8 },
      { step: 70, action: 'buy', price: 98.5 },
      { step: 95, action: 'sell', price: 108.3 },
    ],
    rewards: Array.from({ length: 100 }, () => Math.random() * 20 - 5),
  },
  actionStats: {
    buy: 42,
    hold: 40,
    sell: 18,
  },
  qValues: {
    buy: 0.85,
    hold: 0.62,
    sell: 0.43,
  },
};

// Mock Feature Importance
export const mockFeatureImportance: FeatureImportanceData = {
  modelId: 'model-001',
  features: [
    { name: 'momentum_score', importance: 0.34, category: 'technical' },
    { name: 'volume_surge', importance: 0.28, category: 'technical' },
    { name: 'rsi_14', importance: 0.19, category: 'technical' },
    { name: 'macd_signal', importance: 0.15, category: 'technical' },
    { name: 'sentiment_score', importance: 0.12, category: 'sentiment' },
    { name: 'price_volatility', importance: 0.11, category: 'technical' },
    { name: 'market_cap', importance: 0.09, category: 'fundamental' },
    { name: 'relative_strength', importance: 0.08, category: 'technical' },
    { name: 'trend_strength', importance: 0.07, category: 'technical' },
    { name: 'liquidity_ratio', importance: 0.06, category: 'fundamental' },
    { name: 'sector_correlation', importance: -0.04, category: 'macro' },
    { name: 'pe_ratio', importance: -0.05, category: 'fundamental' },
    { name: 'beta', importance: -0.08, category: 'technical' },
  ].sort((a, b) => Math.abs(b.importance) - Math.abs(a.importance)),
};

export function calculateTotalParams(architecture: NetworkArchitecture): string {
  let total = 0;
  for (let i = 0; i < architecture.layers.length - 1; i++) {
    const inputSize = architecture.layers[i].neurons;
    const outputSize = architecture.layers[i + 1].neurons;
    total += inputSize * outputSize + outputSize; // weights + biases
  }
  return total >= 1000000 ? `${(total / 1000000).toFixed(1)}M` : `${(total / 1000).toFixed(1)}K`;
}
