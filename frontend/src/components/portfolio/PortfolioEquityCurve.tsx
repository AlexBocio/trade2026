/**
 * Portfolio Equity Curve - 30-day equity chart
 */

import { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';

interface EquityPoint {
  time: string;
  value: number;
}

export function PortfolioEquityCurve({ data }: { data: EquityPoint[] }) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<ReturnType<typeof createChart> | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: '#1a1f2e' },
        textColor: '#888',
      },
      grid: {
        vertLines: { color: '#2a3142' },
        horzLines: { color: '#2a3142' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 300,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    const areaSeries = chart.addAreaSeries({
      lineColor: '#00ff88',
      topColor: 'rgba(0, 255, 136, 0.4)',
      bottomColor: 'rgba(0, 255, 136, 0.0)',
      lineWidth: 2,
    });

    areaSeries.setData(data);

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data]);

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 mb-6">
      <h3 className="text-lg font-semibold mb-4">Equity Curve (30 Days)</h3>
      <div ref={chartContainerRef} />
    </div>
  );
}
