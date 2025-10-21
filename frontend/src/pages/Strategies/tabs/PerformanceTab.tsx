/**
 * Performance Tab - Charts and performance analysis
 */

import { useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';
import type { IChartApi, ISeriesApi } from 'lightweight-charts';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import type { StrategyExtended } from '../../../services/mock-data/strategy-data';
import { formatCurrency } from '../../../utils/helpers';

interface PerformanceTabProps {
  strategy: StrategyExtended;
}

export function PerformanceTab({ strategy }: PerformanceTabProps) {
  const equityChartRef = useRef<HTMLDivElement>(null);
  const drawdownChartRef = useRef<HTMLDivElement>(null);

  // Mock equity curve data
  const equityData = Array.from({ length: 90 }, (_, i) => {
    const baseValue = 100000;
    const trend = i * 500;
    const volatility = Math.sin(i / 10) * 2000;
    return {
      time: new Date(Date.now() - (90 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      value: baseValue + trend + volatility + Math.random() * 1000,
    };
  });

  // Mock drawdown data
  const drawdownData = Array.from({ length: 90 }, (_, i) => ({
    time: new Date(Date.now() - (90 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    value: -Math.random() * strategy.performance.maxDrawdown * 0.8,
  }));

  // Mock returns distribution
  const returnsDistribution = [
    { range: '-10%', count: 2 },
    { range: '-8%', count: 4 },
    { range: '-6%', count: 8 },
    { range: '-4%', count: 12 },
    { range: '-2%', count: 18 },
    { range: '0%', count: 25 },
    { range: '2%', count: 22 },
    { range: '4%', count: 16 },
    { range: '6%', count: 10 },
    { range: '8%', count: 6 },
    { range: '10%', count: 3 },
  ];

  // Monthly returns heatmap data
  const monthlyReturns = [
    { month: 'Jan', return: 2.3 },
    { month: 'Feb', return: -1.2 },
    { month: 'Mar', return: 4.5 },
    { month: 'Apr', return: 3.1 },
    { month: 'May', return: -0.8 },
    { month: 'Jun', return: 5.2 },
    { month: 'Jul', return: 1.9 },
    { month: 'Aug', return: -2.1 },
    { month: 'Sep', return: 3.8 },
    { month: 'Oct', return: 2.7 },
    { month: 'Nov', return: 4.3 },
    { month: 'Dec', return: 1.5 },
  ];

  // Equity curve chart
  useEffect(() => {
    if (!equityChartRef.current) return;

    const chart: IChartApi = createChart(equityChartRef.current, {
      width: equityChartRef.current.clientWidth,
      height: 300,
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#9CA3AF',
      },
      grid: {
        vertLines: { color: '#374151' },
        horzLines: { color: '#374151' },
      },
      rightPriceScale: {
        borderColor: '#374151',
      },
      timeScale: {
        borderColor: '#374151',
        timeVisible: true,
      },
    });

    const lineSeries: ISeriesApi<'Area'> = chart.addAreaSeries({
      lineColor: '#10B981',
      topColor: 'rgba(16, 185, 129, 0.4)',
      bottomColor: 'rgba(16, 185, 129, 0.0)',
      lineWidth: 2,
    });

    lineSeries.setData(equityData as any);

    const handleResize = () => {
      if (equityChartRef.current) {
        chart.applyOptions({ width: equityChartRef.current.clientWidth });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  // Drawdown chart
  useEffect(() => {
    if (!drawdownChartRef.current) return;

    const chart: IChartApi = createChart(drawdownChartRef.current, {
      width: drawdownChartRef.current.clientWidth,
      height: 200,
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#9CA3AF',
      },
      grid: {
        vertLines: { color: '#374151' },
        horzLines: { color: '#374151' },
      },
      rightPriceScale: {
        borderColor: '#374151',
      },
      timeScale: {
        borderColor: '#374151',
        timeVisible: true,
      },
    });

    const areaSeries: ISeriesApi<'Area'> = chart.addAreaSeries({
      lineColor: '#EF4444',
      topColor: 'rgba(239, 68, 68, 0.4)',
      bottomColor: 'rgba(239, 68, 68, 0.0)',
      lineWidth: 2,
    });

    areaSeries.setData(drawdownData as any);

    const handleResize = () => {
      if (drawdownChartRef.current) {
        chart.applyOptions({ width: drawdownChartRef.current.clientWidth });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  const getReturnColor = (returnValue: number) => {
    if (returnValue > 3) return 'bg-green-600';
    if (returnValue > 1) return 'bg-green-700';
    if (returnValue > 0) return 'bg-green-800';
    if (returnValue > -1) return 'bg-gray-700';
    if (returnValue > -3) return 'bg-red-800';
    return 'bg-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Equity Curve */}
      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-4">Equity Curve</h2>
        <div ref={equityChartRef} className="w-full" />
      </div>

      {/* Monthly Returns Heatmap */}
      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-4">Monthly Returns</h2>
        <div className="grid grid-cols-6 md:grid-cols-12 gap-2">
          {monthlyReturns.map((item) => (
            <div key={item.month} className="text-center">
              <div className="text-xs text-gray-500 mb-1">{item.month}</div>
              <div
                className={`p-3 rounded ${getReturnColor(item.return)} flex items-center justify-center`}
                title={`${item.month}: ${item.return > 0 ? '+' : ''}${item.return}%`}
              >
                <span className="text-xs font-semibold text-white">
                  {item.return > 0 ? '+' : ''}
                  {item.return}%
                </span>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 flex items-center justify-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-red-600 rounded"></div>
            <span className="text-gray-400">Large Loss</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-gray-700 rounded"></div>
            <span className="text-gray-400">Neutral</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-green-600 rounded"></div>
            <span className="text-gray-400">Large Gain</span>
          </div>
        </div>
      </div>

      {/* Distribution and Drawdown Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribution of Returns */}
        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Distribution of Returns</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={returnsDistribution}>
              <XAxis dataKey="range" stroke="#9CA3AF" style={{ fontSize: '12px' }} />
              <YAxis stroke="#9CA3AF" style={{ fontSize: '12px' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: '1px solid #374151',
                  borderRadius: '6px',
                }}
                labelStyle={{ color: '#F3F4F6' }}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {returnsDistribution.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={
                      entry.range.includes('-')
                        ? '#EF4444'
                        : entry.range === '0%'
                        ? '#6B7280'
                        : '#10B981'
                    }
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Drawdown Chart */}
        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Drawdown</h2>
          <div ref={drawdownChartRef} className="w-full" />
          <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-gray-500">Max Drawdown</div>
              <div className="text-red-400 font-semibold">
                {strategy.performance.maxDrawdown.toFixed(2)}%
              </div>
            </div>
            <div>
              <div className="text-gray-500">Current Drawdown</div>
              <div className="text-red-400 font-semibold">
                {(drawdownData[drawdownData.length - 1].value).toFixed(2)}%
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-4">Performance Summary</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div>
            <div className="text-sm text-gray-500 mb-1">Total Return</div>
            <div className="text-2xl font-bold text-green-400">
              +{((strategy.performance.totalPnL / 100000) * 100).toFixed(2)}%
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500 mb-1">Sharpe Ratio</div>
            <div className="text-2xl font-bold text-white">
              {strategy.performance.sharpeRatio.toFixed(2)}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500 mb-1">Win Rate</div>
            <div className="text-2xl font-bold text-white">
              {strategy.performance.winRate.toFixed(1)}%
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500 mb-1">Total Trades</div>
            <div className="text-2xl font-bold text-white">{strategy.performance.totalTrades}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
