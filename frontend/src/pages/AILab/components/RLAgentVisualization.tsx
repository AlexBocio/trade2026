/**
 * RL Agent Visualization - Reward curves and episode replay
 */

import { useEffect, useRef } from 'react';
import Plot from 'react-plotly.js';
import type { RLAgentData } from '../../../services/mock-data/ml-model-data';
import { Panel, PanelHeader, PanelContent } from '../../../components/common/Panel';

interface EpisodeReplayCanvasProps {
  episode: RLAgentData['latestEpisode'];
}

function EpisodeReplayCanvas({ episode }: EpisodeReplayCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;

    const width = canvasRef.current.width;
    const height = canvasRef.current.height;

    // Clear canvas
    ctx.fillStyle = '#1a1f2e';
    ctx.fillRect(0, 0, width, height);

    // Draw price chart
    const prices = episode.prices;
    const maxPrice = Math.max(...prices);
    const minPrice = Math.min(...prices);
    const priceRange = maxPrice - minPrice;

    ctx.strokeStyle = '#4a5568';
    ctx.lineWidth = 2;
    ctx.beginPath();

    prices.forEach((price, i) => {
      const x = (i / (prices.length - 1)) * width;
      const y = height - ((price - minPrice) / priceRange) * (height - 20) - 10;

      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    ctx.stroke();

    // Draw agent actions
    episode.actions.forEach((action) => {
      const x = (action.step / (prices.length - 1)) * width;
      const y = height - ((action.price - minPrice) / priceRange) * (height - 20) - 10;

      // Draw action marker
      ctx.beginPath();
      ctx.arc(x, y, 6, 0, Math.PI * 2);

      if (action.action === 'buy') {
        ctx.fillStyle = '#00ff88';
      } else if (action.action === 'sell') {
        ctx.fillStyle = '#ff4444';
      } else {
        ctx.fillStyle = '#ffc800';
      }

      ctx.fill();

      // Draw label
      ctx.fillStyle = '#ffffff';
      ctx.font = '10px monospace';
      ctx.fillText(action.action.toUpperCase(), x - 15, y - 12);
    });

  }, [episode]);

  return (
    <canvas
      ref={canvasRef}
      width={600}
      height={200}
      className="w-full rounded bg-gray-900 border border-gray-700"
    />
  );
}

export function RLAgentVisualization({ data }: { data: RLAgentData }) {
  return (
    <Panel>
      <PanelHeader>
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-semibold">RL Agent Behavior</h3>
            <div className="text-sm text-gray-400">{data.agentName}</div>
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-400">Episode</div>
            <div className="font-mono text-green-400 font-bold">
              {data.currentEpisode}/{data.totalEpisodes}
            </div>
          </div>
        </div>
      </PanelHeader>
      <PanelContent>
        {/* Reward Curve */}
        <Plot
          data={[
            {
              x: data.episodes.map((e) => e.episode),
              y: data.episodes.map((e) => e.totalReward),
              type: 'scatter',
              mode: 'lines',
              name: 'Episode Reward',
              line: { color: '#00ddff', width: 1.5 },
              opacity: 0.6,
            },
            {
              x: data.episodes.map((e) => e.episode),
              y: data.episodes.map((e) => e.avgReward),
              type: 'scatter',
              mode: 'lines',
              name: 'Avg Reward (100 ep)',
              line: { color: '#ffc800', width: 2 },
            },
          ]}
          layout={{
            paper_bgcolor: '#1a1f2e',
            plot_bgcolor: '#1a1f2e',
            font: { color: '#e0e0e0', family: 'monospace', size: 10 },
            xaxis: { title: 'Episode', gridcolor: '#2a3142' },
            yaxis: { title: 'Cumulative Reward', gridcolor: '#2a3142' },
            height: 180,
            margin: { l: 50, r: 20, t: 10, b: 40 },
            legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(0,0,0,0.5)' },
            hovermode: 'x unified',
          }}
          config={{ displayModeBar: false }}
          style={{ width: '100%' }}
        />

        {/* Episode Replay Visualization */}
        <div className="bg-gray-800 rounded p-3 mt-3">
          <div className="text-xs text-gray-400 mb-2">Latest Episode #{data.latestEpisode.episode}</div>

          {/* Render episode as canvas */}
          <EpisodeReplayCanvas episode={data.latestEpisode} />

          <div className="text-xs text-gray-500 mt-2 text-center">
            Green = BUY | Red = SELL | Yellow = HOLD
          </div>
        </div>

        {/* Action Distribution & Q-Values */}
        <div className="grid grid-cols-2 gap-3 mt-3">
          {/* Action Stats */}
          <div className="bg-gray-800 rounded p-2">
            <div className="text-xs text-gray-400 mb-2">Action Distribution</div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm">Buy</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: `${data.actionStats.buy}%` }}
                    />
                  </div>
                  <span className="text-green-400 font-mono text-sm w-10">{data.actionStats.buy}%</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Hold</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-yellow-500 h-2 rounded-full"
                      style={{ width: `${data.actionStats.hold}%` }}
                    />
                  </div>
                  <span className="text-yellow-400 font-mono text-sm w-10">{data.actionStats.hold}%</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Sell</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-red-500 h-2 rounded-full"
                      style={{ width: `${data.actionStats.sell}%` }}
                    />
                  </div>
                  <span className="text-red-400 font-mono text-sm w-10">{data.actionStats.sell}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Q-Values */}
          <div className="bg-gray-800 rounded p-2">
            <div className="text-xs text-gray-400 mb-2">Current Q-Values</div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm">Q(Buy)</span>
                <span className="text-green-400 font-mono text-lg font-bold">
                  {data.qValues.buy.toFixed(3)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Q(Hold)</span>
                <span className="text-yellow-400 font-mono text-lg font-bold">
                  {data.qValues.hold.toFixed(3)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Q(Sell)</span>
                <span className="text-red-400 font-mono text-lg font-bold">
                  {data.qValues.sell.toFixed(3)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </PanelContent>
    </Panel>
  );
}
