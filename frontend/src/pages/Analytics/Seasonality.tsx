/**
 * Seasonality Analysis - Day/month/time patterns
 */

import { useState } from 'react';
import { ArrowLeft, Play } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Plot from 'react-plotly.js';

export function Seasonality() {
  const navigate = useNavigate();
  const [config, setConfig] = useState({
    universe: 'small-cap',
    startDate: '2015-01-01',
    endDate: '2024-12-31',
    analysisType: 'all',
  });
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleRun = async () => {
    setIsRunning(true);
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Mock results
    const mockResults = {
      dayOfWeek: [
        {
          day: 'Monday',
          avgReturn: -0.12,
          winRate: 48.2,
          count: 520,
          tStat: -1.23,
          pValue: 0.219,
        },
        {
          day: 'Tuesday',
          avgReturn: 0.78,
          winRate: 54.8,
          count: 520,
          tStat: 3.45,
          pValue: 0.001,
        },
        {
          day: 'Wednesday',
          avgReturn: 0.34,
          winRate: 52.1,
          count: 520,
          tStat: 1.67,
          pValue: 0.095,
        },
        {
          day: 'Thursday',
          avgReturn: 0.15,
          winRate: 50.5,
          count: 520,
          tStat: 0.89,
          pValue: 0.374,
        },
        { day: 'Friday', avgReturn: 0.42, winRate: 53.2, count: 520, tStat: 2.12, pValue: 0.034 },
      ],
      monthOfYear: [
        { month: 'January', avgReturn: 2.45, winRate: 58.3, count: 10, significant: true },
        { month: 'February', avgReturn: 1.12, winRate: 52.1, count: 10, significant: false },
        { month: 'March', avgReturn: 1.89, winRate: 55.4, count: 10, significant: false },
        { month: 'April', avgReturn: 0.87, winRate: 50.8, count: 10, significant: false },
        { month: 'May', avgReturn: -0.34, winRate: 47.2, count: 10, significant: false },
        { month: 'June', avgReturn: 0.56, winRate: 51.3, count: 10, significant: false },
        { month: 'July', avgReturn: 1.78, winRate: 54.6, count: 10, significant: false },
        { month: 'August', avgReturn: -0.92, winRate: 43.8, count: 10, significant: false },
        { month: 'September', avgReturn: -1.23, winRate: 41.2, count: 10, significant: true },
        { month: 'October', avgReturn: 0.23, winRate: 49.5, count: 10, significant: false },
        { month: 'November', avgReturn: 1.92, winRate: 56.7, count: 10, significant: false },
        { month: 'December', avgReturn: 2.12, winRate: 57.9, count: 10, significant: true },
      ],
      timeOfDay: [
        { time: '9:30-10:00', avgReturn: 0.25, volatility: 1.45 },
        { time: '10:00-11:00', avgReturn: 0.12, volatility: 0.89 },
        { time: '11:00-12:00', avgReturn: 0.08, volatility: 0.67 },
        { time: '12:00-13:00', avgReturn: 0.05, volatility: 0.52 },
        { time: '13:00-14:00', avgReturn: 0.11, volatility: 0.73 },
        { time: '14:00-15:00', avgReturn: 0.18, volatility: 0.95 },
        { time: '15:00-16:00', avgReturn: 0.32, volatility: 1.67 },
      ],
    };

    setResults(mockResults);
    setIsRunning(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate('/analytics')}
          className="p-2 hover:bg-dark-border rounded-lg transition"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-white">Seasonality Analysis</h1>
          <p className="text-sm text-gray-400">
            Discover day-of-week, month, and intraday patterns in your trading universe.
          </p>
        </div>
      </div>

      {/* Configuration */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Configuration</h2>

        <div className="grid grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Universe</label>
            <select
              value={config.universe}
              onChange={(e) => setConfig({ ...config, universe: e.target.value })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            >
              <option value="small-cap">Small-Cap Stocks</option>
              <option value="mid-cap">Mid-Cap Stocks</option>
              <option value="large-cap">Large-Cap Stocks</option>
              <option value="all">All Stocks</option>
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Analysis Type</label>
            <select
              value={config.analysisType}
              onChange={(e) => setConfig({ ...config, analysisType: e.target.value })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            >
              <option value="day_of_week">Day of Week</option>
              <option value="month_of_year">Month of Year</option>
              <option value="time_of_day">Time of Day</option>
              <option value="all">All Patterns</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Start Date</label>
            <input
              type="date"
              value={config.startDate}
              onChange={(e) => setConfig({ ...config, startDate: e.target.value })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">End Date</label>
            <input
              type="date"
              value={config.endDate}
              onChange={(e) => setConfig({ ...config, endDate: e.target.value })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            />
          </div>
        </div>

        <button
          onClick={handleRun}
          disabled={isRunning}
          className="w-full px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg font-semibold flex items-center justify-center gap-2 transition"
        >
          {isRunning ? (
            <>
              <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
              Analyzing...
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              Run Seasonality Analysis
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {results && (
        <>
          {/* Day of Week */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Day of Week Analysis</h2>

            <div className="overflow-x-auto mb-6">
              <table className="w-full">
                <thead>
                  <tr className="text-left text-sm text-gray-400 border-b border-dark-border">
                    <th className="pb-3 font-semibold">Day</th>
                    <th className="pb-3 font-semibold text-right">Avg Return</th>
                    <th className="pb-3 font-semibold text-right">Win Rate</th>
                    <th className="pb-3 font-semibold text-right">Count</th>
                    <th className="pb-3 font-semibold text-right">t-Stat</th>
                    <th className="pb-3 font-semibold text-right">p-value</th>
                    <th className="pb-3 font-semibold text-center">Significant?</th>
                  </tr>
                </thead>
                <tbody>
                  {results.dayOfWeek.map((day: any) => (
                    <tr key={day.day} className="border-b border-dark-border">
                      <td className="py-3 font-semibold text-white">{day.day}</td>
                      <td
                        className={`py-3 text-right font-mono font-bold ${
                          day.avgReturn > 0 ? 'text-green-400' : 'text-red-400'
                        }`}
                      >
                        {day.avgReturn > 0 ? '+' : ''}
                        {day.avgReturn.toFixed(2)}%
                      </td>
                      <td className="py-3 text-right font-mono text-white">
                        {day.winRate.toFixed(1)}%
                      </td>
                      <td className="py-3 text-right font-mono text-white">{day.count}</td>
                      <td className="py-3 text-right font-mono text-white">
                        {day.tStat.toFixed(2)}
                      </td>
                      <td
                        className={`py-3 text-right font-mono ${
                          day.pValue < 0.05 ? 'text-green-400 font-bold' : 'text-gray-400'
                        }`}
                      >
                        {day.pValue.toFixed(3)}
                      </td>
                      <td className="py-3 text-center">
                        {day.pValue < 0.05 ? (
                          <span className="text-green-400 font-bold">
                            {day.pValue < 0.001 ? '✓✓✓' : day.pValue < 0.01 ? '✓✓' : '✓'}
                          </span>
                        ) : (
                          <span className="text-red-400">✗</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Bar Chart */}
            <DayOfWeekChart data={results.dayOfWeek} />

            <div className="mt-4 p-4 bg-blue-900/20 border border-blue-700 rounded-lg">
              <div className="font-semibold text-white mb-2">Key Findings:</div>
              <ul className="text-sm text-gray-300 space-y-1">
                <li>
                  • <strong>Tuesday</strong> shows the best average return (+0.78%, p &lt; 0.001)
                  ✓✓✓
                </li>
                <li>
                  • <strong>Friday</strong> also shows positive returns (+0.42%, p &lt; 0.05) ✓
                </li>
                <li>
                  • <strong>Monday</strong> tends to be negative (-0.12%) but not significant
                </li>
                <li>
                  • <strong>Recommendation:</strong> Favor entering positions on Tuesday
                </li>
              </ul>
            </div>
          </div>

          {/* Month of Year */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Month of Year Analysis</h2>

            <MonthOfYearChart data={results.monthOfYear} />

            <div className="mt-4 p-4 bg-blue-900/20 border border-blue-700 rounded-lg">
              <div className="font-semibold text-white mb-2">Key Findings:</div>
              <ul className="text-sm text-gray-300 space-y-1">
                <li>
                  • <strong>January Effect:</strong> Strong positive returns (+2.45%) ✓
                </li>
                <li>
                  • <strong>December:</strong> Santa Claus Rally (+2.12%) ✓
                </li>
                <li>
                  • <strong>September:</strong> Historically weak month (-1.23%) ✓
                </li>
                <li>
                  • <strong>Recommendation:</strong> Increase exposure in Jan/Dec, reduce in Sep
                </li>
              </ul>
            </div>
          </div>

          {/* Time of Day */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">
              Intraday Pattern Analysis
            </h2>

            <TimeOfDayChart data={results.timeOfDay} />

            <div className="mt-4 p-4 bg-blue-900/20 border border-blue-700 rounded-lg">
              <div className="font-semibold text-white mb-2">Key Findings:</div>
              <ul className="text-sm text-gray-300 space-y-1">
                <li>
                  • <strong>Opening 30 minutes:</strong> High volatility and returns (+0.25%)
                </li>
                <li>
                  • <strong>Lunch hour (12-1pm):</strong> Lowest returns and volatility
                </li>
                <li>
                  • <strong>Final hour:</strong> Strong returns (+0.32%) with high volatility
                </li>
                <li>
                  • <strong>Recommendation:</strong> Trade early or late, avoid midday
                </li>
              </ul>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function DayOfWeekChart({ data }: { data: any[] }) {
  return (
    <Plot
      data={[
        {
          x: data.map((d) => d.day),
          y: data.map((d) => d.avgReturn),
          type: 'bar',
          marker: {
            color: data.map((d) => (d.avgReturn > 0 ? '#00ff88' : '#ff4444')),
          },
          text: data.map((d) => `${d.avgReturn > 0 ? '+' : ''}${d.avgReturn.toFixed(2)}%`),
          textposition: 'outside',
        },
      ]}
      layout={{
        paper_bgcolor: '#1a1f2e',
        plot_bgcolor: '#1a1f2e',
        font: { color: '#e0e0e0', family: 'monospace' },
        xaxis: {
          title: 'Day of Week',
          gridcolor: '#2a3142',
        },
        yaxis: {
          title: 'Average Return (%)',
          gridcolor: '#2a3142',
          zeroline: true,
          zerolinecolor: '#555',
        },
        margin: { l: 60, r: 20, t: 20, b: 60 },
        hovermode: 'x',
      }}
      config={{ displayModeBar: false, responsive: true }}
      style={{ width: '100%', height: '300px' }}
    />
  );
}

function MonthOfYearChart({ data }: { data: any[] }) {
  return (
    <Plot
      data={[
        {
          x: data.map((d) => d.month),
          y: data.map((d) => d.avgReturn),
          type: 'bar',
          marker: {
            color: data.map((d) => (d.avgReturn > 0 ? '#00ff88' : '#ff4444')),
          },
          text: data.map((d) => `${d.avgReturn > 0 ? '+' : ''}${d.avgReturn.toFixed(2)}%`),
          textposition: 'outside',
        },
      ]}
      layout={{
        paper_bgcolor: '#1a1f2e',
        plot_bgcolor: '#1a1f2e',
        font: { color: '#e0e0e0', family: 'monospace' },
        xaxis: {
          title: 'Month',
          gridcolor: '#2a3142',
          tickangle: -45,
        },
        yaxis: {
          title: 'Average Return (%)',
          gridcolor: '#2a3142',
          zeroline: true,
          zerolinecolor: '#555',
        },
        margin: { l: 60, r: 20, t: 20, b: 80 },
        hovermode: 'x',
      }}
      config={{ displayModeBar: false, responsive: true }}
      style={{ width: '100%', height: '350px' }}
    />
  );
}

function TimeOfDayChart({ data }: { data: any[] }) {
  return (
    <Plot
      data={[
        {
          x: data.map((d) => d.time),
          y: data.map((d) => d.avgReturn),
          type: 'scatter',
          mode: 'lines+markers',
          name: 'Avg Return',
          yaxis: 'y',
          line: { color: '#00ff88', width: 3 },
          marker: { size: 8 },
        },
        {
          x: data.map((d) => d.time),
          y: data.map((d) => d.volatility),
          type: 'scatter',
          mode: 'lines+markers',
          name: 'Volatility',
          yaxis: 'y2',
          line: { color: '#ff8800', width: 2, dash: 'dash' },
          marker: { size: 6 },
        },
      ]}
      layout={{
        paper_bgcolor: '#1a1f2e',
        plot_bgcolor: '#1a1f2e',
        font: { color: '#e0e0e0', family: 'monospace' },
        xaxis: {
          title: 'Time of Day',
          gridcolor: '#2a3142',
          tickangle: -45,
        },
        yaxis: {
          title: 'Average Return (%)',
          gridcolor: '#2a3142',
          side: 'left',
        },
        yaxis2: {
          title: 'Volatility (%)',
          gridcolor: '#2a3142',
          overlaying: 'y',
          side: 'right',
        },
        legend: { x: 0.05, y: 0.95 },
        margin: { l: 60, r: 60, t: 20, b: 80 },
        hovermode: 'x unified',
      }}
      config={{ displayModeBar: false, responsive: true }}
      style={{ width: '100%', height: '350px' }}
    />
  );
}
