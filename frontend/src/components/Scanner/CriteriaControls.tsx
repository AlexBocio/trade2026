/**
 * Criteria Controls Component
 * Technical criteria with min/max inputs
 */

import React from 'react';
import type { TechnicalCriteria } from '../../types/scanner';

interface CriteriaControlsProps {
  criteria: TechnicalCriteria;
  onChange: (criteria: TechnicalCriteria) => void;
}

export default function CriteriaControls({ criteria, onChange }: CriteriaControlsProps) {
  const updateCriteria = (
    category: keyof TechnicalCriteria,
    field: string,
    key: 'enabled' | 'min' | 'max',
    value: boolean | number
  ) => {
    onChange({
      ...criteria,
      [category]: {
        ...criteria[category],
        [field]: {
          ...(criteria[category] as any)[field],
          [key]: value,
        },
      },
    });
  };

  return (
    <div className="p-4 space-y-6">
      {/* Momentum Criteria */}
      <CriteriaSection title="🚀 Momentum Criteria">
        <CriteriaRow
          label="20-day return"
          enabled={criteria.momentum.return_20d.enabled}
          min={criteria.momentum.return_20d.min}
          max={criteria.momentum.return_20d.max}
          onToggle={(enabled) => updateCriteria('momentum', 'return_20d', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('momentum', 'return_20d', 'min', val)}
          onMaxChange={(val) => updateCriteria('momentum', 'return_20d', 'max', val)}
          unit="%"
          step={1}
        />

        <CriteriaRow
          label="60-day return"
          enabled={criteria.momentum.return_60d.enabled}
          min={criteria.momentum.return_60d.min}
          max={criteria.momentum.return_60d.max}
          onToggle={(enabled) => updateCriteria('momentum', 'return_60d', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('momentum', 'return_60d', 'min', val)}
          onMaxChange={(val) => updateCriteria('momentum', 'return_60d', 'max', val)}
          unit="%"
          step={1}
        />

        <CriteriaRow
          label="252-day return (1Y)"
          enabled={criteria.momentum.return_252d.enabled}
          min={criteria.momentum.return_252d.min}
          max={criteria.momentum.return_252d.max}
          onToggle={(enabled) => updateCriteria('momentum', 'return_252d', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('momentum', 'return_252d', 'min', val)}
          onMaxChange={(val) => updateCriteria('momentum', 'return_252d', 'max', val)}
          unit="%"
          step={5}
        />

        <CriteriaRow
          label="Hurst exponent"
          enabled={criteria.momentum.hurst.enabled}
          min={criteria.momentum.hurst.min}
          max={criteria.momentum.hurst.max}
          onToggle={(enabled) => updateCriteria('momentum', 'hurst', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('momentum', 'hurst', 'min', val)}
          onMaxChange={(val) => updateCriteria('momentum', 'hurst', 'max', val)}
          step={0.05}
          description="0.5=random, >0.5=trending, <0.5=mean-reverting"
        />

        <CriteriaRow
          label="Autocorrelation"
          enabled={criteria.momentum.autocorr.enabled}
          min={criteria.momentum.autocorr.min}
          max={criteria.momentum.autocorr.max}
          onToggle={(enabled) => updateCriteria('momentum', 'autocorr', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('momentum', 'autocorr', 'min', val)}
          onMaxChange={(val) => updateCriteria('momentum', 'autocorr', 'max', val)}
          step={0.1}
        />
      </CriteriaSection>

      {/* Mean Reversion Criteria */}
      <CriteriaSection title="↩️ Mean Reversion Criteria">
        <CriteriaRow
          label="Z-score"
          enabled={criteria.mean_reversion.zscore.enabled}
          min={criteria.mean_reversion.zscore.min}
          max={criteria.mean_reversion.zscore.max}
          onToggle={(enabled) => updateCriteria('mean_reversion', 'zscore', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('mean_reversion', 'zscore', 'min', val)}
          onMaxChange={(val) => updateCriteria('mean_reversion', 'zscore', 'max', val)}
          step={0.5}
          description="Standard deviations from mean"
        />

        <CriteriaRow
          label="RSI (Relative Strength Index)"
          enabled={criteria.mean_reversion.rsi.enabled}
          min={criteria.mean_reversion.rsi.min}
          max={criteria.mean_reversion.rsi.max}
          onToggle={(enabled) => updateCriteria('mean_reversion', 'rsi', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('mean_reversion', 'rsi', 'min', val)}
          onMaxChange={(val) => updateCriteria('mean_reversion', 'rsi', 'max', val)}
          step={5}
          description="<30=oversold, >70=overbought"
        />

        <CriteriaRow
          label="Bollinger Band position"
          enabled={criteria.mean_reversion.bollinger_position.enabled}
          min={criteria.mean_reversion.bollinger_position.min}
          max={criteria.mean_reversion.bollinger_position.max}
          onToggle={(enabled) => updateCriteria('mean_reversion', 'bollinger_position', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('mean_reversion', 'bollinger_position', 'min', val)}
          onMaxChange={(val) => updateCriteria('mean_reversion', 'bollinger_position', 'max', val)}
          step={0.1}
          description="0=bottom band, 1=top band"
        />

        <CriteriaRow
          label="Mean reversion speed"
          enabled={criteria.mean_reversion.mean_reversion_speed.enabled}
          min={criteria.mean_reversion.mean_reversion_speed.min}
          max={criteria.mean_reversion.mean_reversion_speed.max}
          onToggle={(enabled) => updateCriteria('mean_reversion', 'mean_reversion_speed', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('mean_reversion', 'mean_reversion_speed', 'min', val)}
          onMaxChange={(val) => updateCriteria('mean_reversion', 'mean_reversion_speed', 'max', val)}
          step={0.05}
          description="Half-life of reversion"
        />
      </CriteriaSection>

      {/* Volatility Criteria */}
      <CriteriaSection title="📉 Volatility Criteria">
        <CriteriaRow
          label="ATR percentile"
          enabled={criteria.volatility.atr_percentile.enabled}
          min={criteria.volatility.atr_percentile.min}
          max={criteria.volatility.atr_percentile.max}
          onToggle={(enabled) => updateCriteria('volatility', 'atr_percentile', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('volatility', 'atr_percentile', 'min', val)}
          onMaxChange={(val) => updateCriteria('volatility', 'atr_percentile', 'max', val)}
          unit="%"
          step={5}
          description="ATR relative to 1-year history"
        />

        <CriteriaRow
          label="Volume surge"
          enabled={criteria.volatility.volume_surge.enabled}
          min={criteria.volatility.volume_surge.min}
          max={criteria.volatility.volume_surge.max}
          onToggle={(enabled) => updateCriteria('volatility', 'volume_surge', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('volatility', 'volume_surge', 'min', val)}
          onMaxChange={(val) => updateCriteria('volatility', 'volume_surge', 'max', val)}
          unit="x"
          step={0.5}
          description="Volume relative to 20-day avg"
        />

        <CriteriaRow
          label="GARCH volatility"
          enabled={criteria.volatility.garch_vol.enabled}
          min={criteria.volatility.garch_vol.min}
          max={criteria.volatility.garch_vol.max}
          onToggle={(enabled) => updateCriteria('volatility', 'garch_vol', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('volatility', 'garch_vol', 'min', val)}
          onMaxChange={(val) => updateCriteria('volatility', 'garch_vol', 'max', val)}
          unit="%"
          step={5}
          description="GARCH(1,1) predicted vol"
        />

        <CriteriaRow
          label="Implied volatility"
          enabled={criteria.volatility.implied_vol.enabled}
          min={criteria.volatility.implied_vol.min}
          max={criteria.volatility.implied_vol.max}
          onToggle={(enabled) => updateCriteria('volatility', 'implied_vol', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('volatility', 'implied_vol', 'min', val)}
          onMaxChange={(val) => updateCriteria('volatility', 'implied_vol', 'max', val)}
          unit="%"
          step={5}
          description="Options implied volatility"
        />
      </CriteriaSection>

      {/* Trend Criteria */}
      <CriteriaSection title="📈 Trend Criteria">
        <CriteriaRow
          label="Price vs SMA(50)"
          enabled={criteria.trend.price_vs_sma50.enabled}
          min={criteria.trend.price_vs_sma50.min}
          max={criteria.trend.price_vs_sma50.max}
          onToggle={(enabled) => updateCriteria('trend', 'price_vs_sma50', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('trend', 'price_vs_sma50', 'min', val)}
          onMaxChange={(val) => updateCriteria('trend', 'price_vs_sma50', 'max', val)}
          unit="%"
          step={1}
          description="Distance from 50-day moving average"
        />

        <CriteriaRow
          label="Price vs SMA(200)"
          enabled={criteria.trend.price_vs_sma200.enabled}
          min={criteria.trend.price_vs_sma200.min}
          max={criteria.trend.price_vs_sma200.max}
          onToggle={(enabled) => updateCriteria('trend', 'price_vs_sma200', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('trend', 'price_vs_sma200', 'min', val)}
          onMaxChange={(val) => updateCriteria('trend', 'price_vs_sma200', 'max', val)}
          unit="%"
          step={1}
          description="Distance from 200-day moving average"
        />

        <CriteriaRow
          label="SMA slope"
          enabled={criteria.trend.sma_slope.enabled}
          min={criteria.trend.sma_slope.min}
          max={criteria.trend.sma_slope.max}
          onToggle={(enabled) => updateCriteria('trend', 'sma_slope', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('trend', 'sma_slope', 'min', val)}
          onMaxChange={(val) => updateCriteria('trend', 'sma_slope', 'max', val)}
          unit="°"
          step={0.5}
          description="Angle of SMA(50) slope"
        />

        <CriteriaRow
          label="ADX (Trend Strength)"
          enabled={criteria.trend.adx.enabled}
          min={criteria.trend.adx.min}
          max={criteria.trend.adx.max}
          onToggle={(enabled) => updateCriteria('trend', 'adx', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('trend', 'adx', 'min', val)}
          onMaxChange={(val) => updateCriteria('trend', 'adx', 'max', val)}
          step={5}
          description="<20=weak, >40=strong trend"
        />
      </CriteriaSection>

      {/* Liquidity Criteria */}
      <CriteriaSection title="💧 Liquidity Criteria">
        <CriteriaRow
          label="Average volume"
          enabled={criteria.liquidity.avg_volume.enabled}
          min={criteria.liquidity.avg_volume.min}
          max={criteria.liquidity.avg_volume.max}
          onToggle={(enabled) => updateCriteria('liquidity', 'avg_volume', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('liquidity', 'avg_volume', 'min', val)}
          onMaxChange={(val) => updateCriteria('liquidity', 'avg_volume', 'max', val)}
          step={100000}
          description="20-day average volume"
        />

        <CriteriaRow
          label="Dollar volume"
          enabled={criteria.liquidity.dollar_volume.enabled}
          min={criteria.liquidity.dollar_volume.min}
          max={criteria.liquidity.dollar_volume.max}
          onToggle={(enabled) => updateCriteria('liquidity', 'dollar_volume', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('liquidity', 'dollar_volume', 'min', val)}
          onMaxChange={(val) => updateCriteria('liquidity', 'dollar_volume', 'max', val)}
          step={1000000}
          description="Average daily dollar volume"
        />

        <CriteriaRow
          label="Bid-ask spread"
          enabled={criteria.liquidity.spread.enabled}
          min={criteria.liquidity.spread.min}
          max={criteria.liquidity.spread.max}
          onToggle={(enabled) => updateCriteria('liquidity', 'spread', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('liquidity', 'spread', 'min', val)}
          onMaxChange={(val) => updateCriteria('liquidity', 'spread', 'max', val)}
          unit="%"
          step={0.01}
          description="Relative spread"
        />

        <CriteriaRow
          label="Float shares"
          enabled={criteria.liquidity.float.enabled}
          min={criteria.liquidity.float.min}
          max={criteria.liquidity.float.max}
          onToggle={(enabled) => updateCriteria('liquidity', 'float', 'enabled', enabled)}
          onMinChange={(val) => updateCriteria('liquidity', 'float', 'min', val)}
          onMaxChange={(val) => updateCriteria('liquidity', 'float', 'max', val)}
          step={1000000}
          description="Publicly tradable shares"
        />
      </CriteriaSection>
    </div>
  );
}

interface CriteriaSectionProps {
  title: string;
  children: React.ReactNode;
}

function CriteriaSection({ title, children }: CriteriaSectionProps) {
  return (
    <div className="bg-gray-750 rounded-lg p-4">
      <h3 className="text-white font-semibold mb-4">{title}</h3>
      <div className="space-y-3">{children}</div>
    </div>
  );
}

interface CriteriaRowProps {
  label: string;
  enabled: boolean;
  min: number;
  max: number;
  onToggle: (enabled: boolean) => void;
  onMinChange: (val: number) => void;
  onMaxChange: (val: number) => void;
  unit?: string;
  step?: number;
  description?: string;
}

function CriteriaRow({
  label,
  enabled,
  min,
  max,
  onToggle,
  onMinChange,
  onMaxChange,
  unit = '',
  step = 1,
  description,
}: CriteriaRowProps) {
  return (
    <div className="py-2">
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center space-x-3 flex-1">
          <input
            type="checkbox"
            checked={enabled}
            onChange={(e) => onToggle(e.target.checked)}
            className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500 focus:ring-offset-gray-800"
          />
          <label className="text-white text-sm font-medium">{label}</label>
        </div>

        {enabled && (
          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-400">Min:</span>
            <input
              type="number"
              value={min}
              onChange={(e) => onMinChange(Number(e.target.value))}
              step={step}
              className="w-24 bg-gray-700 text-white px-2 py-1 rounded text-sm text-center border border-gray-600 focus:outline-none focus:border-blue-500"
            />
            <span className="text-xs text-gray-400">Max:</span>
            <input
              type="number"
              value={max}
              onChange={(e) => onMaxChange(Number(e.target.value))}
              step={step}
              className="w-24 bg-gray-700 text-white px-2 py-1 rounded text-sm text-center border border-gray-600 focus:outline-none focus:border-blue-500"
            />
            {unit && <span className="text-xs text-gray-400">{unit}</span>}
          </div>
        )}
      </div>
      {description && enabled && (
        <div className="ml-7 text-xs text-gray-500">{description}</div>
      )}
    </div>
  );
}
