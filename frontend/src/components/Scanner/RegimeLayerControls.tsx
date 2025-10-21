/**
 * Regime Layer Controls Component
 * Toggle UI for each regime layer with weight sliders
 */

import React from 'react';
import type { RegimeLayers } from '../../types/scanner';

interface RegimeLayerControlsProps {
  layers: RegimeLayers;
  onChange: (layers: RegimeLayers) => void;
}

export default function RegimeLayerControls({ layers, onChange }: RegimeLayerControlsProps) {
  const toggleLayer = (layerName: keyof RegimeLayers) => {
    onChange({
      ...layers,
      [layerName]: {
        ...layers[layerName],
        enabled: !layers[layerName].enabled,
      },
    });
  };

  const updateWeight = (layerName: keyof RegimeLayers, weight: number) => {
    onChange({
      ...layers,
      [layerName]: {
        ...layers[layerName],
        weight: weight / 100,
      },
    });
  };

  const updateCriteria = (layerName: keyof RegimeLayers, criteriaKey: string, value: any) => {
    onChange({
      ...layers,
      [layerName]: {
        ...layers[layerName],
        criteria: {
          ...layers[layerName].criteria,
          [criteriaKey]: value,
        },
      },
    });
  };

  const totalWeight = Object.values(layers).reduce((sum, layer) => sum + (layer.enabled ? layer.weight * 100 : 0), 0);

  return (
    <div className="space-y-4 p-4">
      {/* Temporal Regime */}
      <LayerControl
        name="📅 Temporal Regime"
        description="Month, day-of-week, event patterns"
        enabled={layers.temporal.enabled}
        weight={layers.temporal.weight * 100}
        onToggle={() => toggleLayer('temporal')}
        onWeightChange={(w) => updateWeight('temporal', w)}
      >
        <div className="ml-6 mt-2 space-y-2">
          <Checkbox
            label="Month seasonality"
            checked={layers.temporal.criteria.month_seasonality}
            onChange={(checked) => updateCriteria('temporal', 'month_seasonality', checked)}
          />
          <Checkbox
            label="Day-of-week patterns"
            checked={layers.temporal.criteria.day_of_week}
            onChange={(checked) => updateCriteria('temporal', 'day_of_week', checked)}
          />
          <Checkbox
            label="Earnings season context"
            checked={layers.temporal.criteria.earnings_season}
            onChange={(checked) => updateCriteria('temporal', 'earnings_season', checked)}
          />
          <Checkbox
            label="FOMC week"
            checked={layers.temporal.criteria.fomc_week}
            onChange={(checked) => updateCriteria('temporal', 'fomc_week', checked)}
          />
          <Checkbox
            label="OPEX week"
            checked={layers.temporal.criteria.opex_week}
            onChange={(checked) => updateCriteria('temporal', 'opex_week', checked)}
          />
        </div>
      </LayerControl>

      {/* Macro Regime */}
      <LayerControl
        name="🌍 Macro Regime"
        description="Fed policy, inflation, economic cycle"
        enabled={layers.macro.enabled}
        weight={layers.macro.weight * 100}
        onToggle={() => toggleLayer('macro')}
        onWeightChange={(w) => updateWeight('macro', w)}
      >
        <div className="ml-6 mt-2 space-y-2">
          <Checkbox
            label="Fed policy stance"
            checked={layers.macro.criteria.fed_policy}
            onChange={(checked) => updateCriteria('macro', 'fed_policy', checked)}
          />
          <Checkbox
            label="Inflation regime"
            checked={layers.macro.criteria.inflation}
            onChange={(checked) => updateCriteria('macro', 'inflation', checked)}
          />
          <Checkbox
            label="Economic cycle"
            checked={layers.macro.criteria.economic_cycle}
            onChange={(checked) => updateCriteria('macro', 'economic_cycle', checked)}
          />
          <Checkbox
            label="Yield curve shape"
            checked={layers.macro.criteria.yield_curve}
            onChange={(checked) => updateCriteria('macro', 'yield_curve', checked)}
          />
        </div>
      </LayerControl>

      {/* Cross-Asset Regime */}
      <LayerControl
        name="🔗 Cross-Asset Regimes"
        description="Bonds, commodities, currencies, volatility"
        enabled={layers.cross_asset.enabled}
        weight={layers.cross_asset.weight * 100}
        onToggle={() => toggleLayer('cross_asset')}
        onWeightChange={(w) => updateWeight('cross_asset', w)}
      >
        <div className="ml-6 mt-2 space-y-2">
          <Checkbox
            label="Bond market (TLT)"
            checked={layers.cross_asset.criteria.bonds}
            onChange={(checked) => updateCriteria('cross_asset', 'bonds', checked)}
          />
          <Checkbox
            label="Commodities (GLD, USO)"
            checked={layers.cross_asset.criteria.commodities}
            onChange={(checked) => updateCriteria('cross_asset', 'commodities', checked)}
          />
          <Checkbox
            label="Currencies (DXY)"
            checked={layers.cross_asset.criteria.currencies}
            onChange={(checked) => updateCriteria('cross_asset', 'currencies', checked)}
          />
          <Checkbox
            label="Volatility (VIX)"
            checked={layers.cross_asset.criteria.volatility}
            onChange={(checked) => updateCriteria('cross_asset', 'volatility', checked)}
          />
        </div>
      </LayerControl>

      {/* Market Regime */}
      <LayerControl
        name="📊 Market Regime"
        description="Breadth, volatility, market internals"
        enabled={layers.market.enabled}
        weight={layers.market.weight * 100}
        onToggle={() => toggleLayer('market')}
        onWeightChange={(w) => updateWeight('market', w)}
      >
        <div className="ml-6 mt-2 space-y-2">
          <Checkbox
            label="Market breadth"
            checked={layers.market.criteria.breadth}
            onChange={(checked) => updateCriteria('market', 'breadth', checked)}
          />
          <Checkbox
            label="VIX regime"
            checked={layers.market.criteria.vix_regime}
            onChange={(checked) => updateCriteria('market', 'vix_regime', checked)}
          />
          <Checkbox
            label="Advance/decline line"
            checked={layers.market.criteria.advance_decline}
            onChange={(checked) => updateCriteria('market', 'advance_decline', checked)}
          />
          <Checkbox
            label="New highs/lows"
            checked={layers.market.criteria.new_highs_lows}
            onChange={(checked) => updateCriteria('market', 'new_highs_lows', checked)}
          />
        </div>
      </LayerControl>

      {/* Sector Regime */}
      <LayerControl
        name="🏭 Sector Regime"
        description="Sector rotation and leadership"
        enabled={layers.sector.enabled}
        weight={layers.sector.weight * 100}
        onToggle={() => toggleLayer('sector')}
        onWeightChange={(w) => updateWeight('sector', w)}
      >
        <div className="ml-6 mt-2 space-y-2">
          <Checkbox
            label="Sector rotation"
            checked={layers.sector.criteria.rotation}
            onChange={(checked) => updateCriteria('sector', 'rotation', checked)}
          />
          <Checkbox
            label="Sector leadership"
            checked={layers.sector.criteria.leadership}
            onChange={(checked) => updateCriteria('sector', 'leadership', checked)}
          />
          <Checkbox
            label="Cross-sector correlation"
            checked={layers.sector.criteria.correlation}
            onChange={(checked) => updateCriteria('sector', 'correlation', checked)}
          />
        </div>
      </LayerControl>

      {/* Industry Regime */}
      <LayerControl
        name="🔧 Industry Regime"
        description="Industry-level dynamics"
        enabled={layers.industry.enabled}
        weight={layers.industry.weight * 100}
        onToggle={() => toggleLayer('industry')}
        onWeightChange={(w) => updateWeight('industry', w)}
      >
        <div className="ml-6 mt-2 space-y-2">
          <Checkbox
            label="Relative strength"
            checked={layers.industry.criteria.relative_strength}
            onChange={(checked) => updateCriteria('industry', 'relative_strength', checked)}
          />
          <Checkbox
            label="Industry momentum"
            checked={layers.industry.criteria.momentum}
            onChange={(checked) => updateCriteria('industry', 'momentum', checked)}
          />
        </div>
      </LayerControl>

      {/* Stock-Specific Regime */}
      <LayerControl
        name="📈 Stock-Specific Factors"
        description="Earnings, analyst ratings, insider activity"
        enabled={layers.stock_specific.enabled}
        weight={layers.stock_specific.weight * 100}
        onToggle={() => toggleLayer('stock_specific')}
        onWeightChange={(w) => updateWeight('stock_specific', w)}
      >
        <div className="ml-6 mt-2 space-y-2">
          <Checkbox
            label="Earnings quality"
            checked={layers.stock_specific.criteria.earnings}
            onChange={(checked) => updateCriteria('stock_specific', 'earnings', checked)}
          />
          <Checkbox
            label="Analyst ratings"
            checked={layers.stock_specific.criteria.analyst_ratings}
            onChange={(checked) => updateCriteria('stock_specific', 'analyst_ratings', checked)}
          />
          <Checkbox
            label="Insider activity"
            checked={layers.stock_specific.criteria.insider_activity}
            onChange={(checked) => updateCriteria('stock_specific', 'insider_activity', checked)}
          />
          <Checkbox
            label="Short interest"
            checked={layers.stock_specific.criteria.short_interest}
            onChange={(checked) => updateCriteria('stock_specific', 'short_interest', checked)}
          />
        </div>
      </LayerControl>

      {/* Weight Distribution Summary */}
      <div className="mt-6 pt-4 border-t border-gray-700">
        <h4 className="text-sm font-semibold text-gray-400 mb-3">
          Weight Distribution {totalWeight !== 100 && (
            <span className="text-yellow-400 ml-2">({totalWeight.toFixed(0)}% - should be 100%)</span>
          )}
        </h4>
        <WeightDistributionBar layers={layers} />
      </div>
    </div>
  );
}

interface LayerControlProps {
  name: string;
  description: string;
  enabled: boolean;
  weight: number;
  onToggle: () => void;
  onWeightChange: (weight: number) => void;
  children?: React.ReactNode;
}

function LayerControl({
  name,
  description,
  enabled,
  weight,
  onToggle,
  onWeightChange,
  children,
}: LayerControlProps) {
  return (
    <div className={`rounded-lg p-4 transition-colors ${enabled ? 'bg-gray-750 border border-gray-600' : 'bg-gray-800 border border-gray-700'}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <input
            type="checkbox"
            checked={enabled}
            onChange={onToggle}
            className="h-5 w-5 text-blue-600 rounded focus:ring-blue-500 focus:ring-offset-gray-800"
          />
          <div>
            <h3 className="text-white font-medium">{name}</h3>
            <p className="text-sm text-gray-400">{description}</p>
          </div>
        </div>

        {enabled && (
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-400">Weight:</span>
            <input
              type="number"
              value={weight.toFixed(0)}
              onChange={(e) => onWeightChange(Number(e.target.value))}
              min="0"
              max="100"
              step="5"
              className="w-16 bg-gray-700 text-white px-2 py-1 rounded text-center border border-gray-600 focus:outline-none focus:border-blue-500"
            />
            <span className="text-sm text-gray-400">%</span>
          </div>
        )}
      </div>

      {enabled && children}
    </div>
  );
}

interface CheckboxProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

function Checkbox({ label, checked, onChange }: CheckboxProps) {
  return (
    <label className="flex items-center space-x-2 cursor-pointer">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500 focus:ring-offset-gray-800"
      />
      <span className="text-white text-sm">{label}</span>
    </label>
  );
}

function WeightDistributionBar({ layers }: { layers: RegimeLayers }) {
  const weights = Object.entries(layers).map(([name, layer]) => ({
    name,
    weight: layer.enabled ? layer.weight * 100 : 0,
  }));

  const colors = {
    temporal: 'bg-purple-600',
    macro: 'bg-blue-600',
    cross_asset: 'bg-green-600',
    market: 'bg-yellow-600',
    sector: 'bg-orange-600',
    industry: 'bg-red-600',
    stock_specific: 'bg-pink-600',
  };

  return (
    <div className="space-y-2">
      <div className="flex h-4 rounded overflow-hidden">
        {weights.map(({ name, weight }) =>
          weight > 0 ? (
            <div
              key={name}
              className={`${colors[name as keyof typeof colors]} transition-all`}
              style={{ width: `${weight}%` }}
              title={`${name}: ${weight.toFixed(0)}%`}
            />
          ) : null
        )}
      </div>
      <div className="flex flex-wrap gap-2">
        {weights.map(({ name, weight }) =>
          weight > 0 ? (
            <div key={name} className="flex items-center space-x-1">
              <div className={`w-3 h-3 rounded ${colors[name as keyof typeof colors]}`} />
              <span className="text-xs text-gray-400">
                {name.replace('_', ' ')}: {weight.toFixed(0)}%
              </span>
            </div>
          ) : null
        )}
      </div>
    </div>
  );
}
