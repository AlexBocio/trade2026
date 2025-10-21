/**
 * Configuration Panel Component
 * Multi-step accordion UI for scanner configuration
 */

import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import RegimeLayerControls from './RegimeLayerControls';
import CriteriaControls from './CriteriaControls';
import FilterControls from './FilterControls';
import RankingControls from './RankingControls';
import ScannerPresetManager from './ScannerPresetManager';
import type { ScannerConfig, ScanningMode } from '../../types/scanner';

interface ConfigurationPanelProps {
  config: ScannerConfig;
  onChange: (config: ScannerConfig) => void;
  onRun: () => void;
  loading: boolean;
}

export default function ConfigurationPanel({
  config,
  onChange,
  onRun,
  loading,
}: ConfigurationPanelProps) {
  const [activeStep, setActiveStep] = useState(1);

  return (
    <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      {/* Preset Manager at top */}
      <ScannerPresetManager config={config} onLoad={onChange} />

      {/* Configuration Steps */}
      <div className="divide-y divide-gray-700">
        {/* STEP 1: Regime Layers */}
        <AccordionSection
          stepNumber={1}
          title="Select Regime Layers"
          description="Choose which market regime layers to include"
          icon="📍"
          active={activeStep === 1}
          onToggle={() => setActiveStep(activeStep === 1 ? 0 : 1)}
        >
          <RegimeLayerControls
            layers={config.regime_layers}
            onChange={(layers) => onChange({ ...config, regime_layers: layers })}
          />
        </AccordionSection>

        {/* STEP 2: Scanning Mode */}
        <AccordionSection
          stepNumber={2}
          title="Scanning Mode"
          description="Select how to analyze regime relationships"
          icon="🎯"
          active={activeStep === 2}
          onToggle={() => setActiveStep(activeStep === 2 ? 0 : 2)}
        >
          <ScanningModeSelector
            mode={config.mode}
            universe={config.universe}
            onChange={(mode, universe) => onChange({ ...config, mode, universe })}
          />
        </AccordionSection>

        {/* STEP 3: Technical Criteria */}
        <AccordionSection
          stepNumber={3}
          title="Technical Criteria"
          description="Define technical screening parameters"
          icon="🔬"
          active={activeStep === 3}
          onToggle={() => setActiveStep(activeStep === 3 ? 0 : 3)}
        >
          <CriteriaControls
            criteria={config.technical_criteria}
            onChange={(criteria) => onChange({ ...config, technical_criteria: criteria })}
          />
        </AccordionSection>

        {/* STEP 4: Filters */}
        <AccordionSection
          stepNumber={4}
          title="Filters & Exclusions"
          description="Apply additional filters to results"
          icon="🎲"
          active={activeStep === 4}
          onToggle={() => setActiveStep(activeStep === 4 ? 0 : 4)}
        >
          <FilterControls
            filters={config.filters}
            onChange={(filters) => onChange({ ...config, filters })}
          />
        </AccordionSection>

        {/* STEP 5: Ranking */}
        <AccordionSection
          stepNumber={5}
          title="Ranking & Output"
          description="Configure result ranking and output format"
          icon="📊"
          active={activeStep === 5}
          onToggle={() => setActiveStep(activeStep === 5 ? 0 : 5)}
        >
          <RankingControls
            ranking={config.ranking}
            output={config.output}
            onChange={(ranking, output) => onChange({ ...config, ranking, output })}
          />
        </AccordionSection>
      </div>

      {/* Run Button */}
      <div className="p-6 bg-gray-750">
        <button
          onClick={onRun}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-bold py-4 px-6 rounded-lg transition-colors text-lg"
        >
          {loading ? '🔄 Scanning...' : '🚀 Run Custom Scan'}
        </button>
      </div>
    </div>
  );
}

interface AccordionSectionProps {
  stepNumber: number;
  title: string;
  description: string;
  icon: string;
  active: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

function AccordionSection({
  stepNumber,
  title,
  description,
  icon,
  active,
  onToggle,
  children,
}: AccordionSectionProps) {
  return (
    <div className={`transition-colors ${active ? 'bg-gray-750' : 'bg-gray-800'}`}>
      <button
        onClick={onToggle}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-700 transition-colors"
      >
        <div className="flex items-center gap-4">
          <div className="text-2xl">{icon}</div>
          <div className="text-left">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-blue-400">Step {stepNumber}</span>
              <h3 className="text-white font-semibold text-lg">{title}</h3>
            </div>
            <p className="text-sm text-gray-400">{description}</p>
          </div>
        </div>
        <div className="text-gray-400">
          {active ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </div>
      </button>

      {active && <div className="border-t border-gray-700">{children}</div>}
    </div>
  );
}

interface ScanningModeSelectorProps {
  mode: ScanningMode;
  universe: string;
  onChange: (mode: ScanningMode, universe: string) => void;
}

const UNIVERSES = [
  { value: 'sp500', label: 'S&P 500', description: '500 large-cap stocks' },
  { value: 'nasdaq100', label: 'NASDAQ 100', description: '100 largest non-financial NASDAQ stocks' },
  { value: 'russell2000', label: 'Russell 2000', description: '2000 small-cap stocks' },
  { value: 'djia', label: 'Dow Jones', description: '30 blue-chip stocks' },
  { value: 'all_stocks', label: 'All Stocks', description: 'All publicly traded US stocks' },
];

function ScanningModeSelector({ mode, universe, onChange }: ScanningModeSelectorProps) {
  const modes: Array<{ value: ScanningMode; label: string; description: string; color: string }> = [
    {
      value: 'ALIGNMENT',
      label: 'Alignment Mode',
      description: 'Find stocks where all regime layers agree (strong consensus)',
      color: 'green',
    },
    {
      value: 'DIVERGENCE',
      label: 'Divergence Mode',
      description: 'Find stocks where regime layers disagree (contrarian opportunities)',
      color: 'orange',
    },
    {
      value: 'HYBRID',
      label: 'Hybrid Mode',
      description: 'Balance between alignment and divergence',
      color: 'blue',
    },
    {
      value: 'TRANSITION',
      label: 'Transition Mode',
      description: 'Find stocks in regime transition periods',
      color: 'purple',
    },
  ];

  return (
    <div className="p-4 space-y-6">
      {/* Universe Selection */}
      <div className="bg-gray-750 rounded-lg p-4">
        <h3 className="text-white font-semibold mb-3">🌐 Stock Universe</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {UNIVERSES.map((u) => (
            <button
              key={u.value}
              onClick={() => onChange(mode, u.value)}
              className={`p-3 rounded-lg text-left transition-colors ${
                universe === u.value
                  ? 'bg-blue-600 text-white border-2 border-blue-400'
                  : 'bg-gray-700 text-gray-300 border-2 border-gray-600 hover:bg-gray-600'
              }`}
            >
              <div className="font-semibold">{u.label}</div>
              <div className="text-xs opacity-80">{u.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Mode Selection */}
      <div className="bg-gray-750 rounded-lg p-4">
        <h3 className="text-white font-semibold mb-3">🎯 Scanning Strategy</h3>
        <div className="space-y-2">
          {modes.map((m) => (
            <button
              key={m.value}
              onClick={() => onChange(m.value, universe)}
              className={`w-full p-4 rounded-lg text-left transition-colors border-2 ${
                mode === m.value
                  ? `bg-${m.color}-600 border-${m.color}-400 text-white`
                  : 'bg-gray-700 border-gray-600 text-gray-300 hover:bg-gray-600'
              }`}
            >
              <div className="font-semibold">{m.label}</div>
              <div className="text-sm opacity-90 mt-1">{m.description}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
