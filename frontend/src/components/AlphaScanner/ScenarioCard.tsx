/**
 * Scenario Card Component
 * Display macro scenario with summary
 */

interface ScenarioCardProps {
  scenario: any;
  onSelect: () => void;
  isSelected: boolean;
}

export default function ScenarioCard({ scenario, onSelect, isSelected }: ScenarioCardProps) {
  const getScenarioIcon = (type: string) => {
    const icons: Record<string, string> = {
      recession: '📉',
      inflation: '💸',
      stagflation: '⚠️',
      boom: '🚀',
      recovery: '📈',
      crisis: '🔥',
      normalization: '⚖️',
      volatility: '⚡',
      default: '💼',
    };
    return icons[type.toLowerCase()] || icons.default;
  };

  return (
    <div
      onClick={onSelect}
      className={`rounded-lg p-4 cursor-pointer transition-all border-2 ${
        isSelected
          ? 'bg-blue-900/30 border-blue-500'
          : 'bg-gray-800 border-gray-700 hover:border-blue-600 hover:bg-gray-750'
      }`}
    >
      <div className="flex items-start space-x-3">
        <div className="text-4xl">{getScenarioIcon(scenario.type)}</div>
        <div className="flex-1">
          <h3 className="text-white font-bold mb-1">{scenario.name}</h3>
          <p className="text-sm text-gray-400 mb-3">{scenario.description}</p>

          {/* Key Characteristics */}
          <div className="space-y-2">
            {scenario.characteristics && scenario.characteristics.slice(0, 3).map((char: string, i: number) => (
              <div key={i} className="flex items-center space-x-2 text-xs">
                <span className="text-blue-400">→</span>
                <span className="text-gray-300">{char}</span>
              </div>
            ))}
          </div>

          {/* Stats */}
          {scenario.historical_frequency && (
            <div className="mt-3 pt-3 border-t border-gray-700 flex items-center justify-between">
              <div>
                <div className="text-xs text-gray-400">Historical Frequency</div>
                <div className="text-sm text-white font-semibold">
                  {(scenario.historical_frequency * 100).toFixed(0)}% of time
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs text-gray-400">Avg Duration</div>
                <div className="text-sm text-white font-semibold">
                  {scenario.avg_duration_months || 'N/A'} mo
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
