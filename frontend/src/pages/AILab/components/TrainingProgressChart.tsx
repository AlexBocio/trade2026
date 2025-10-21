/**
 * Training Progress Chart - Real-time loss and accuracy curves
 */

import Plot from 'react-plotly.js';
import type { TrainingProgress } from '../../../services/mock-data/ml-model-data';
import { TrendingDown, TrendingUp, Zap } from 'lucide-react';
import { Panel, PanelHeader, PanelContent } from '../../../components/common/Panel';

interface MetricCardProps {
  label: string;
  value: string;
  trend: 'up' | 'down';
}

function MetricCard({ label, value, trend }: MetricCardProps) {
  return (
    <div className="bg-gray-800 rounded p-3">
      <div className="text-xs text-gray-400 mb-1">{label}</div>
      <div className="flex items-center justify-between">
        <span className="font-mono text-lg font-bold">{value}</span>
        {trend === 'down' ? (
          <TrendingDown className="w-4 h-4 text-green-400" />
        ) : (
          <TrendingUp className="w-4 h-4 text-green-400" />
        )}
      </div>
    </div>
  );
}

export function TrainingProgressChart({ data }: { data: TrainingProgress }) {
  const currentTrainLoss = data.metrics.trainLoss[data.metrics.trainLoss.length - 1]?.value || 0;
  const currentValLoss = data.metrics.valLoss[data.metrics.valLoss.length - 1]?.value || 0;
  const currentTrainAcc = data.metrics.trainAccuracy[data.metrics.trainAccuracy.length - 1]?.value || 0;
  const currentValAcc = data.metrics.valAccuracy[data.metrics.valAccuracy.length - 1]?.value || 0;

  return (
    <Panel>
      <PanelHeader>
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold">Training Progress</h3>
            <div className="text-sm text-gray-400">{data.modelName}</div>
          </div>
          <div className="flex gap-4 text-sm">
            <div>
              <span className="text-gray-400">Epoch:</span>
              <span className="ml-2 font-mono text-green-400">
                {data.currentEpoch}/{data.totalEpochs}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-yellow-400" />
              <span className="text-gray-400">GPU:</span>
              <span className="ml-1 font-mono text-yellow-400">{data.hardware.gpuUtilization}%</span>
            </div>
            <div>
              <span className="text-gray-400">Temp:</span>
              <span className="ml-1 font-mono text-orange-400">{data.hardware.gpuTemp}°C</span>
            </div>
          </div>
        </div>
      </PanelHeader>
      <PanelContent>
        {/* Loss Curves */}
        <Plot
          data={[
            {
              x: data.metrics.trainLoss.map((d) => d.epoch),
              y: data.metrics.trainLoss.map((d) => d.value),
              type: 'scatter',
              mode: 'lines',
              name: 'Train Loss',
              line: { color: '#00ff88', width: 2 },
            },
            {
              x: data.metrics.valLoss.map((d) => d.epoch),
              y: data.metrics.valLoss.map((d) => d.value),
              type: 'scatter',
              mode: 'lines',
              name: 'Val Loss',
              line: { color: '#ff4444', width: 2 },
            },
          ]}
          layout={{
            paper_bgcolor: '#1a1f2e',
            plot_bgcolor: '#1a1f2e',
            font: { color: '#e0e0e0', family: 'monospace', size: 11 },
            xaxis: {
              title: 'Epoch',
              gridcolor: '#2a3142',
              showgrid: true,
            },
            yaxis: {
              title: 'Loss',
              gridcolor: '#2a3142',
              showgrid: true,
            },
            legend: { x: 0.75, y: 1, bgcolor: 'rgba(0,0,0,0)' },
            margin: { l: 50, r: 20, t: 20, b: 50 },
            hovermode: 'x unified',
          }}
          config={{
            displayModeBar: false,
            responsive: true,
          }}
          style={{ width: '100%', height: '280px' }}
        />

        {/* Metrics Grid */}
        <div className="grid grid-cols-4 gap-3 mt-4">
          <MetricCard label="Train Loss" value={currentTrainLoss.toFixed(4)} trend="down" />
          <MetricCard label="Val Loss" value={currentValLoss.toFixed(4)} trend="down" />
          <MetricCard
            label="Train Acc"
            value={`${(currentTrainAcc * 100).toFixed(1)}%`}
            trend="up"
          />
          <MetricCard label="Val Acc" value={`${(currentValAcc * 100).toFixed(1)}%`} trend="up" />
        </div>

        {/* Hyperparameters */}
        <div className="mt-4 p-3 bg-gray-800 rounded text-xs">
          <div className="grid grid-cols-4 gap-3">
            <div>
              <span className="text-gray-400">LR:</span>
              <span className="ml-2 font-mono">{data.hyperparameters.learningRate}</span>
            </div>
            <div>
              <span className="text-gray-400">Batch:</span>
              <span className="ml-2 font-mono">{data.hyperparameters.batchSize}</span>
            </div>
            <div>
              <span className="text-gray-400">Optimizer:</span>
              <span className="ml-2 font-mono">{data.hyperparameters.optimizer}</span>
            </div>
            <div>
              <span className="text-gray-400">GPU:</span>
              <span className="ml-2 font-mono">{data.hardware.gpuModel}</span>
            </div>
          </div>
        </div>
      </PanelContent>
    </Panel>
  );
}
