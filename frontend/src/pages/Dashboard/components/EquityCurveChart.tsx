/**
 * Equity Curve Chart - Shows account value over time using Lightweight Charts
 */

import { useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

interface EquityCurveChartProps {
  data: Array<{ date: string; value: number }>;
}

export function EquityCurveChart({ data }: EquityCurveChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#0f1419' },
        textColor: '#9ca3af',
      },
      grid: {
        vertLines: { color: '#1f2937' },
        horzLines: { color: '#1f2937' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 300,
      timeScale: {
        borderColor: '#1f2937',
      },
      rightPriceScale: {
        borderColor: '#1f2937',
      },
    });

    const lineSeries = chart.addLineSeries({
      color: '#10b981',
      lineWidth: 2,
    });

    // Convert data to chart format
    const chartData = data.map((item) => ({
      time: item.date,
      value: item.value,
    }));

    lineSeries.setData(chartData);

    // Fit content
    chart.timeScale().fitContent();

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
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
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">Equity Curve (30 Days)</h3>
      <div ref={chartContainerRef} />
    </div>
  );
}
