/**
 * Router configuration - defines all application routes
 */

import { createBrowserRouter } from 'react-router-dom';
import { Layout } from './components/layout/Layout';

// Page imports
import { Dashboard } from './pages/Dashboard/Dashboard';
import { Scanner } from './pages/Scanner/Scanner';
import { Trading } from './pages/Trading/Trading';
import { StrategyList } from './pages/Strategies/StrategyList';
import { StrategyDetail } from './pages/Strategies/StrategyDetail';
import { StrategyEditor } from './pages/Strategies/StrategyEditor';
import { BacktestList } from './pages/Backtesting/BacktestList';
import { BacktestReport } from './pages/Backtesting/BacktestReport';
import { AdvancedBacktest } from './pages/Backtesting/AdvancedBacktest';
import { SimulationEngine } from './pages/Backtesting/SimulationEngine';
import { PBOAnalysis } from './pages/Backtesting/PBOAnalysis';
import { StockScreener } from './pages/Scanner/StockScreener';
import CustomScannerBuilder from './pages/Scanning/CustomScannerBuilder';
import RegimeDashboard from './pages/Scanning/RegimeDashboard';
import TimeMachineScanner from './pages/Scanning/TimeMachineScanner';
import CorrelationScanner from './pages/Scanning/CorrelationScanner';
import LiquidityVacuumScanner from './pages/Scanning/LiquidityVacuumScanner';
import SmartMoneyTracker from './pages/Scanning/SmartMoneyTracker';
import SentimentDivergenceScanner from './pages/Scanning/SentimentDivergenceScanner';
import FractalRegimeScanner from './pages/Scanning/FractalRegimeScanner';
import CatalystCalendarScanner from './pages/Scanning/CatalystCalendarScanner';
import IntermarketRelayScanner from './pages/Scanning/IntermarketRelayScanner';
import PairsTradingScanner from './pages/Scanning/PairsTradingScanner';
import ScenarioAnalyzer from './pages/Scanning/ScenarioAnalyzer';
import { Portfolio } from './pages/Portfolio/Portfolio';
import { PortfolioOptimizer } from './pages/Portfolio/PortfolioOptimizer';
import { CovarianceAnalysis } from './pages/Portfolio/CovarianceAnalysis';
import { Risk } from './pages/Risk/Risk';
import { Journal } from './pages/Journal/Journal';
import { JournalDetail } from './pages/Journal/JournalDetail';
import { Alerts } from './pages/Alerts/Alerts';
import { AlertBuilder } from './pages/Alerts/AlertBuilder';
import { AlertDetail } from './pages/Alerts/AlertDetail';
import { Watchlists } from './pages/Watchlists/Watchlists';
import { WatchlistDetail } from './pages/Watchlists/WatchlistDetail';
import { News } from './pages/News/News';
import { AILab } from './pages/AILab/AILab';
import { RLTrading } from './pages/MLInsights/RLTrading';
import { MetaLabeling } from './pages/ML/MetaLabeling';
import { Analytics } from './pages/Analytics/Analytics';
import { FactorAnalysis } from './pages/Analytics/FactorAnalysis';
import { StatisticalTests } from './pages/Analytics/StatisticalTests';
import { MarketRegime } from './pages/Analytics/MarketRegime';
import { Seasonality } from './pages/Analytics/Seasonality';
import { Distribution } from './pages/Analytics/Distribution';
import { HypothesisTesting } from './pages/Analytics/HypothesisTesting';
import { IndicatorBuilder } from './pages/Analytics/IndicatorBuilder';
import { FractionalDiff } from './pages/DataProcessing/FractionalDiff';
import { DataExplorer } from './pages/Database/DataExplorer';
import { HotData } from './pages/Database/HotData';
import { WarmData } from './pages/Database/WarmData';
import { ColdData } from './pages/Database/ColdData';
import MarketData from './pages/MarketData/MarketData';
import { Reports } from './pages/Reports/Reports';
import { ScheduleReports } from './pages/Reports/ScheduleReports';
import { Settings } from './pages/Settings/Settings';
import { NotFound } from './pages/NotFound';
import { ErrorBoundary } from './components/ErrorBoundary';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
      {
        path: 'scanner',
        children: [
          {
            index: true,
            element: <Scanner />,
          },
          {
            path: 'stock-screener',
            element: <StockScreener />,
          },
          {
            path: 'custom-builder',
            element: <CustomScannerBuilder />,
          },
          {
            path: 'regime-dashboard',
            element: <RegimeDashboard />,
          },
          {
            path: 'time-machine',
            element: <TimeMachineScanner />,
          },
          {
            path: 'correlation',
            element: <CorrelationScanner />,
          },
          {
            path: 'liquidity-vacuum',
            element: <LiquidityVacuumScanner />,
          },
          {
            path: 'smart-money',
            element: <SmartMoneyTracker />,
          },
          {
            path: 'sentiment-divergence',
            element: <SentimentDivergenceScanner />,
          },
          {
            path: 'fractal-regime',
            element: <FractalRegimeScanner />,
          },
          {
            path: 'catalyst-calendar',
            element: <CatalystCalendarScanner />,
          },
          {
            path: 'intermarket-relay',
            element: <IntermarketRelayScanner />,
          },
          {
            path: 'pairs-trading',
            element: <PairsTradingScanner />,
          },
          {
            path: 'scenario-analyzer',
            element: <ScenarioAnalyzer />,
          },
        ],
      },
      {
        path: 'trading',
        element: <Trading />,
      },
      {
        path: 'strategies',
        children: [
          {
            index: true,
            element: <StrategyList />,
          },
          {
            path: ':id',
            element: <StrategyDetail />,
          },
          {
            path: 'new',
            element: <StrategyEditor />,
          },
          {
            path: ':id/edit',
            element: <StrategyEditor />,
          },
        ],
      },
      {
        path: 'backtesting',
        children: [
          {
            index: true,
            element: <BacktestList />,
          },
          {
            path: 'report/:id',
            element: <BacktestReport />,
          },
          {
            path: 'advanced',
            element: <AdvancedBacktest />,
          },
          {
            path: 'simulations',
            element: <SimulationEngine />,
          },
          {
            path: 'pbo-analysis',
            element: <PBOAnalysis />,
          },
        ],
      },
      {
        path: 'portfolio',
        children: [
          {
            index: true,
            element: <Portfolio />,
          },
          {
            path: 'optimizer',
            element: <PortfolioOptimizer />,
          },
          {
            path: 'covariance-analysis',
            element: <CovarianceAnalysis />,
          },
        ],
      },
      {
        path: 'risk',
        element: <Risk />,
      },
      {
        path: 'journal',
        children: [
          {
            index: true,
            element: <Journal />,
          },
          {
            path: ':id',
            element: <JournalDetail />,
          },
        ],
      },
      {
        path: 'alerts',
        children: [
          {
            index: true,
            element: <Alerts />,
          },
          {
            path: 'create',
            element: <AlertBuilder />,
          },
          {
            path: ':id',
            element: <AlertDetail />,
          },
        ],
      },
      {
        path: 'watchlists',
        children: [
          {
            index: true,
            element: <Watchlists />,
          },
          {
            path: ':id',
            element: <WatchlistDetail />,
          },
        ],
      },
      {
        path: 'news',
        element: <News />,
      },
      {
        path: 'ai-lab',
        children: [
          {
            index: true,
            element: <AILab />,
          },
          {
            path: 'rl-trading',
            element: <RLTrading />,
          },
          {
            path: 'meta-labeling',
            element: <MetaLabeling />,
          },
        ],
      },
      {
        path: 'analytics',
        children: [
          {
            index: true,
            element: <Analytics />,
          },
          {
            path: 'factors',
            element: <FactorAnalysis />,
          },
          {
            path: 'stats',
            element: <StatisticalTests />,
          },
          {
            path: 'regime',
            element: <MarketRegime />,
          },
          {
            path: 'seasonality',
            element: <Seasonality />,
          },
          {
            path: 'distribution',
            element: <Distribution />,
          },
          {
            path: 'hypothesis',
            element: <HypothesisTesting />,
          },
          {
            path: 'indicators',
            element: <IndicatorBuilder />,
          },
          {
            path: 'fractional-diff',
            element: <FractionalDiff />,
          },
        ],
      },
      {
        path: 'database',
        children: [
          {
            index: true,
            element: <DataExplorer />,
          },
          {
            path: 'hot',
            element: <HotData />,
          },
          {
            path: 'warm',
            element: <WarmData />,
          },
          {
            path: 'cold',
            element: <ColdData />,
          },
        ],
      },
      {
        path: 'market-data',
        element: <MarketData />,
      },
      {
        path: 'reports',
        children: [
          {
            index: true,
            element: <Reports />,
          },
          {
            path: 'schedule',
            element: <ScheduleReports />,
          },
        ],
      },
      {
        path: 'settings',
        element: <Settings />,
      },
      {
        path: '*',
        element: <NotFound />,
      },
    ],
    errorElement: <ErrorBoundary />,
  },
]);
