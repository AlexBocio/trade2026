/**
 * Risk Management page - Monitor portfolio risk, exposures, and compliance limits
 */

import { useEffect } from 'react';
import { useRiskStore } from '../../store/useRiskStore';
import { RiskMetricsCards } from '../../components/risk/RiskMetricsCards';
import { RiskLimitGauges } from '../../components/risk/RiskLimitGauges';
import { ConcentrationRiskTable } from '../../components/risk/ConcentrationRiskTable';
import { CorrelationMatrix } from '../../components/risk/CorrelationMatrix';
import { SectorRiskChart } from '../../components/risk/SectorRiskChart';
import { HistoricalVaRChart } from '../../components/risk/HistoricalVaRChart';
import { RiskEventsLog } from '../../components/risk/RiskEventsLog';
import { AlertTriangle } from 'lucide-react';

export function Risk() {
  const { data, isLoading, error, hasActiveAlerts, loadRisk } = useRiskStore();

  useEffect(() => {
    loadRisk();
  }, [loadRisk]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-400">Loading risk data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card bg-red-900/20 border-red-700">
        <h3 className="text-red-400 font-semibold mb-2">Error Loading Risk Data</h3>
        <p className="text-gray-300">{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="card">
        <p className="text-gray-400">No risk data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Risk Management</h1>
        <p className="text-gray-400 mt-1">Monitor portfolio risk, exposures, and compliance limits</p>
      </div>

      {/* Alert Banner */}
      {hasActiveAlerts && (
        <div className="bg-yellow-900/30 border border-yellow-700 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle className="w-6 h-6 text-yellow-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-yellow-200 font-semibold mb-1">Risk Alerts Active</h3>
            <p className="text-yellow-200/80 text-sm">
              One or more risk limits are approaching or exceeding thresholds. Review limits below.
            </p>
          </div>
        </div>
      )}

      {/* Risk Metrics Cards */}
      <RiskMetricsCards metrics={data.metrics} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left Column (60%) */}
        <div className="col-span-2 space-y-6">
          <RiskLimitGauges limits={data.limits} />
          <ConcentrationRiskTable positions={data.concentrationRisk} />
          <CorrelationMatrix
            symbols={data.correlationMatrix.symbols}
            correlations={data.correlationMatrix.correlations}
          />
        </div>

        {/* Right Column (40%) */}
        <div className="space-y-6">
          <SectorRiskChart data={data.sectorRisk} />
          <HistoricalVaRChart data={data.historicalVaR} />
          <RiskEventsLog events={data.riskEvents} />
        </div>
      </div>
    </div>
  );
}
