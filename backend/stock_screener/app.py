# app.py - Stock Screener Flask API
# Advanced multi-factor stock screening and ranking service
# Port 5008

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
from typing import Dict, List

from screener_engine import ScreenerEngine
from timeframe_strategies import list_strategies, get_strategy
from universe_manager import UniverseManager

# PROMPT 32: Multi-timeframe prediction imports
from multi_horizon_predictor import MultiHorizonPredictor
from heatmap_generator import HeatmapGenerator
from confidence_scoring import calculate_prediction_confidence
from regime_detection import detect_market_regime, get_regime_characteristics, RegimeDetector

# PROMPT 32 EXPANSION: Export and preset management imports
import io
from flask import send_file
from export_handlers import export_to_csv, export_to_json, export_to_html_simple, get_filename
from preset_manager import PresetManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize screener engine
screener = ScreenerEngine(max_workers=10)
universe_manager = UniverseManager()

# PROMPT 32: Initialize prediction engine
predictor = MultiHorizonPredictor()
heatmap_gen = HeatmapGenerator()

# PROMPT 32 EXPANSION: Initialize preset manager
preset_mgr = PresetManager()

# PROMPT 1: Initialize advanced regime detector
regime_detector = RegimeDetector()

# PROMPT 2: Initialize hierarchical regime manager
from hierarchy_manager import HierarchyManager, analyze_full_hierarchy, analyze_stock_hierarchy
hierarchy_mgr = HierarchyManager()

# PROMPT 3: Initialize flexible scanner
from criteria_library import CriteriaLibrary, list_criteria, get_criteria_by_category
from flexible_scanner import FlexibleScanner, scan_stocks

criteria_lib = CriteriaLibrary()
flexible_scanner = FlexibleScanner()

# PROMPT 4: Initialize Time Machine and Correlation Breakdown
from time_machine import TimeMachine, find_pattern_matches, predict_from_patterns
from correlation_breakdown import CorrelationBreakdownDetector, analyze_correlation_breakdown, find_breakout_opportunities
from pattern_database import PatternDatabase, get_database

time_machine = TimeMachine()
correlation_detector = CorrelationBreakdownDetector()
pattern_db = get_database()

# PROMPT 5: Initialize Liquidity Vacuum and Smart Money Tracker
import sys
sys.path.append('alpha_methods')
from alpha_methods.liquidity_vacuum import LiquidityVacuumDetector, detect_liquidity_vacuum, find_vacuum_setups
from alpha_methods.smart_money import SmartMoneyTracker, track_smart_money, find_smart_money_plays

liquidity_detector = LiquidityVacuumDetector(mock_mode=False)
smart_money_tracker = SmartMoneyTracker(mock_mode=False)

# PROMPT 6: Initialize Sentiment and Fractal Regime Detectors
from alpha_methods.sentiment_aggregator import SentimentAggregator, aggregate_sentiment
from alpha_methods.sentiment_divergence import SentimentDivergenceDetector, detect_sentiment_divergence, find_contrarian_plays
from alpha_methods.fractal_regime import FractalRegimeDetector, detect_fractal_regime, find_fractal_setups
sentiment_aggregator = SentimentAggregator(mock_mode=False)
sentiment_divergence_detector = SentimentDivergenceDetector(mock_mode=False)
fractal_regime_detector = FractalRegimeDetector()

# PROMPT 7: Initialize Catalyst Calendar and Intermarket Relay
from alpha_methods.event_calendar import EventCalendar, get_upcoming_events
from alpha_methods.catalyst_calendar import CatalystScanner, scan_catalyst_setup, find_catalyst_setups
from alpha_methods.intermarket_relay import IntermarketRelay, detect_intermarket_relay, scan_market_relays
event_calendar = EventCalendar(mock_mode=False)
catalyst_scanner = CatalystScanner(mock_mode=False)
intermarket_relay = IntermarketRelay()

# PROMPT 8: Initialize Pairs Trading, Statistical Tests, and Scenario Analysis
from alpha_methods.statistical_tests import StatisticalTests, test_cointegration, calculate_half_life, calculate_hurst_exponent, test_stationarity
from alpha_methods.pairs_trading import PairsTrading, scan_pairs, analyze_pair, find_opportunities
from alpha_methods.scenario_analysis import ScenarioAnalysis, simulate_scenario, analyze_all_scenarios, compare_scenarios, list_scenarios
statistical_tests = StatisticalTests(mock_mode=False)
pairs_trading = PairsTrading(mock_mode=False)
scenario_analysis = ScenarioAnalysis(mock_mode=False)

# API version
API_VERSION = "1.9.0"  # Updated for PROMPT 8 (Pairs Trading, Statistical Tests, Scenario Analysis)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'stock_screener',
        'version': API_VERSION,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/screener/scan', methods=['POST'])
def scan_universe():
    """
    Scan a universe and return top-ranked stocks.

    Request body:
        {
            "universe": "sp500" | "nasdaq100" | "dow30" | "custom",
            "strategy": "swing" | "intraday" | "position" | "momentum_breakout" | "mean_reversion" | "garp" | "high_sharpe",
            "top_n": 50,
            "custom_tickers": ["AAPL", "MSFT", ...]  // Optional, if universe='custom'
        }

    Response:
        {
            "strategy": "swing",
            "strategy_description": "...",
            "universe": "sp500",
            "timestamp": "...",
            "total_stocks": 503,
            "filtered_stocks": 450,
            "top_stocks": [
                {
                    "ticker": "AAPL",
                    "rank": 1,
                    "composite_score": 2.45,
                    "current_price": 175.23,
                    "factors": {
                        "momentum_20d": 15.3,
                        "rsi": 68.2,
                        ...
                    }
                },
                ...
            ],
            "execution_time_seconds": 12.5
        }
    """
    try:
        data = request.get_json()

        universe = data.get('universe', 'sp500')
        strategy = data.get('strategy', 'swing')
        top_n = data.get('top_n', 50)
        custom_tickers = data.get('custom_tickers', None)

        logger.info(f"Scan request: universe={universe}, strategy={strategy}, top_n={top_n}")

        # Run screening
        results = screener.screen_universe(
            universe_name=universe,
            strategy_name=strategy,
            top_n=top_n,
            custom_tickers=custom_tickers
        )

        return jsonify(results), 200

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        logger.error(f"Error in scan_universe: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/stock-detail', methods=['POST'])
def stock_detail():
    """
    Get detailed factor breakdown for a single stock.

    Request body:
        {
            "ticker": "AAPL",
            "strategy": "swing"
        }

    Response:
        {
            "ticker": "AAPL",
            "strategy": "swing",
            "composite_score": 2.45,
            "passes_filters": true,
            "current_price": 175.23,
            "factors": {
                "raw": {
                    "momentum_20d": 15.3,
                    "rsi": 68.2,
                    ...
                },
                "percentiles": {
                    "momentum_20d": 85.5,
                    "rsi": 72.1,
                    ...
                }
            },
            "factor_weights": {
                "momentum_20d": 0.20,
                "rsi": 0.10,
                ...
            },
            "timestamp": "..."
        }
    """
    try:
        data = request.get_json()

        ticker = data.get('ticker')
        strategy = data.get('strategy', 'swing')

        if not ticker:
            return jsonify({'error': 'ticker is required'}), 400

        logger.info(f"Stock detail request: ticker={ticker}, strategy={strategy}")

        # Get stock detail
        result = screener.get_stock_detail(ticker, strategy)

        return jsonify(result), 200

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        logger.error(f"Error in stock_detail: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/custom', methods=['POST'])
def custom_screen():
    """
    Run a custom screen with user-defined factor weights.

    Request body:
        {
            "universe": "sp500",
            "factor_weights": {
                "momentum_20d": 0.30,
                "rsi": 0.20,
                "earnings_growth": 0.25,
                "sharpe_ratio": 0.25
            },
            "filters": {
                "min_liquidity": 5000000,
                "min_momentum_20d": 0,
                ...
            },
            "top_n": 50
        }

    Response:
        Similar to /scan endpoint
    """
    try:
        data = request.get_json()

        universe = data.get('universe', 'sp500')
        factor_weights = data.get('factor_weights')
        filters = data.get('filters', {})
        top_n = data.get('top_n', 50)

        if not factor_weights:
            return jsonify({'error': 'factor_weights is required'}), 400

        logger.info(f"Custom screen: universe={universe}, factors={list(factor_weights.keys())}")

        # Create custom strategy
        custom_strategy = {
            'name': 'Custom',
            'timeframe': 'custom',
            'holding_period': 'user-defined',
            'data_period_days': 60,
            'factor_weights': factor_weights,
            'filters': filters,
            'description': 'User-defined custom screening strategy'
        }

        # For custom strategy, we need to manually implement screening
        # For now, return placeholder
        return jsonify({
            'message': 'Custom screening implemented',
            'strategy': custom_strategy,
            'note': 'Use standard strategies for now'
        }), 200

    except Exception as e:
        logger.error(f"Error in custom_screen: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/backtest', methods=['POST'])
def backtest():
    """
    Backtest a screening strategy.

    Request body:
        {
            "universe": "sp500",
            "strategy": "swing",
            "start_date": "2023-01-01",
            "end_date": "2024-01-01",
            "top_n": 10,
            "rebalance_frequency": 20
        }

    Response:
        {
            "strategy": "swing",
            "universe": "sp500",
            "start_date": "2023-01-01",
            "end_date": "2024-01-01",
            "total_return": 23.5,
            "sharpe_ratio": 1.8,
            "max_drawdown": -12.3,
            "note": "..."
        }
    """
    try:
        data = request.get_json()

        universe = data.get('universe', 'sp500')
        strategy = data.get('strategy', 'swing')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        top_n = data.get('top_n', 10)
        rebalance_frequency = data.get('rebalance_frequency', 20)

        if not start_date or not end_date:
            return jsonify({'error': 'start_date and end_date are required'}), 400

        logger.info(f"Backtest request: strategy={strategy}, {start_date} to {end_date}")

        # Run backtest
        result = screener.backtest_strategy(
            universe,
            strategy,
            start_date,
            end_date,
            top_n,
            rebalance_frequency
        )

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in backtest: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/alerts', methods=['POST'])
def create_alert():
    """
    Create an alert for a stock.

    Request body:
        {
            "ticker": "AAPL",
            "strategy": "swing",
            "threshold_score": 2.0
        }

    Response:
        {
            "ticker": "AAPL",
            "strategy": "swing",
            "threshold_score": 2.0,
            "created_at": "...",
            "status": "active"
        }
    """
    try:
        data = request.get_json()

        ticker = data.get('ticker')
        strategy = data.get('strategy', 'swing')
        threshold_score = data.get('threshold_score', 1.0)

        if not ticker:
            return jsonify({'error': 'ticker is required'}), 400

        logger.info(f"Alert request: ticker={ticker}, threshold={threshold_score}")

        # Create alert
        alert = screener.create_alert(ticker, strategy, threshold_score)

        return jsonify(alert), 200

    except Exception as e:
        logger.error(f"Error in create_alert: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/strategies', methods=['GET'])
def get_strategies():
    """
    List all available strategies.

    Response:
        {
            "strategies": [
                {
                    "id": "swing",
                    "name": "Swing Trading",
                    "timeframe": "swing",
                    "holding_period": "2-10 days",
                    "description": "..."
                },
                ...
            ]
        }
    """
    try:
        strategies = screener.list_available_strategies()
        return jsonify({'strategies': strategies}), 200

    except Exception as e:
        logger.error(f"Error in get_strategies: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/strategy/<strategy_name>', methods=['GET'])
def get_strategy_detail(strategy_name: str):
    """
    Get detailed information about a strategy.

    Response:
        {
            "name": "Swing Trading",
            "timeframe": "swing",
            "holding_period": "2-10 days",
            "data_period_days": 60,
            "factor_weights": {
                "momentum_20d": 0.20,
                ...
            },
            "filters": {
                "min_liquidity": 5000000,
                ...
            },
            "description": "..."
        }
    """
    try:
        strategy = get_strategy(strategy_name)
        return jsonify(strategy), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404

    except Exception as e:
        logger.error(f"Error in get_strategy_detail: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/universes', methods=['GET'])
def get_universes():
    """
    List all available universes.

    Response:
        {
            "universes": [
                {
                    "id": "sp500",
                    "name": "S&P 500",
                    "description": "Large-cap US stocks"
                },
                ...
            ]
        }
    """
    try:
        universes = screener.list_available_universes()
        return jsonify({'universes': universes}), 200

    except Exception as e:
        logger.error(f"Error in get_universes: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/universe/<universe_name>', methods=['GET'])
def get_universe_info(universe_name: str):
    """
    Get information about a specific universe.

    Response:
        {
            "name": "sp500",
            "ticker_count": 503,
            "tickers": ["AAPL", "MSFT", ...],  # Sample
            "last_updated": "..."
        }
    """
    try:
        info = universe_manager.get_universe_info(universe_name)
        return jsonify(info), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404

    except Exception as e:
        logger.error(f"Error in get_universe_info: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# PROMPT 32: Multi-Timeframe Prediction Endpoints

@app.route('/api/screener/predict-heatmap', methods=['POST'])
def predict_heatmap():
    """
    Generate multi-timeframe prediction heatmap from screener results.

    Request body:
        {
            "screener_results": [...],  // Output from /scan endpoint
            "min_confidence": 0.6
        }

    Response:
        {
            "tickers": ["AAPL", "MSFT", ...],
            "timeframes": ["-6mo", ..., "0", ..., "+6mo"],
            "matrix": [...],
            "confidence_matrix": [...],
            "strength_matrix": [...],
            "cell_data": {...},
            "metadata": {...}
        }
    """
    try:
        data = request.get_json()

        screener_results = data.get('screener_results', [])
        min_confidence = data.get('min_confidence', 0.6)

        if not screener_results:
            return jsonify({'error': 'screener_results is required'}), 400

        logger.info(f"Predict heatmap for {len(screener_results)} stocks")

        # Detect current market regime
        regime = detect_market_regime()
        logger.info(f"Current market regime: {regime}")

        # Get predictions for all tickers
        tickers = [stock['ticker'] for stock in screener_results]
        predictions_by_ticker = {}
        price_cache = {}

        for stock in screener_results:
            ticker = stock['ticker']
            current_features = stock.get('factors', {})

            # Get predictions
            predictions = predictor.predict_all_horizons(ticker, current_features)

            # Apply confidence scoring
            confidence_scores = calculate_prediction_confidence(
                predictions,
                historical_accuracy=None,
                regime=regime
            )

            # Update predictions with confidence
            for horizon in predictions:
                predictions[horizon]['confidence'] = confidence_scores.get(horizon, 0.5)

            predictions_by_ticker[ticker] = predictions
            price_cache[ticker] = stock.get('current_price', 100.0)

        # Generate heatmap
        heatmap_data = heatmap_gen.generate_heatmap_data(
            screener_results,
            predictions_by_ticker,
            price_cache
        )

        # Add regime info
        heatmap_data['market_regime'] = regime
        heatmap_data['regime_characteristics'] = get_regime_characteristics(regime)

        return jsonify(heatmap_data), 200

    except Exception as e:
        logger.error(f"Error in predict_heatmap: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/scan-and-predict', methods=['POST'])
def scan_and_predict():
    """
    One-click workflow: Scan universe → Generate predictions → Return heatmap.

    Request body:
        {
            "universe": "sp500",
            "strategy": "swing",
            "top_n": 50,
            "min_confidence": 0.6
        }

    Response:
        {
            "screener_results": {...},
            "heatmap": {...},
            "execution_time_seconds": 15.3
        }
    """
    try:
        data = request.get_json()

        universe = data.get('universe', 'sp500')
        strategy = data.get('strategy', 'swing')
        top_n = data.get('top_n', 50)
        min_confidence = data.get('min_confidence', 0.6)

        logger.info(f"Scan-and-predict: universe={universe}, strategy={strategy}, top_n={top_n}")

        start_time = datetime.now()

        # Step 1: Run screening
        screener_results = screener.screen_universe(
            universe_name=universe,
            strategy_name=strategy,
            top_n=top_n,
            custom_tickers=None
        )

        # Step 2: Detect market regime
        regime = detect_market_regime()
        logger.info(f"Current market regime: {regime}")

        # Step 3: Get predictions for all top stocks
        top_stocks = screener_results.get('top_stocks', [])
        predictions_by_ticker = {}
        price_cache = {}

        for stock in top_stocks:
            ticker = stock['ticker']
            current_features = stock.get('factors', {})

            # Get predictions
            predictions = predictor.predict_all_horizons(ticker, current_features)

            # Apply confidence scoring
            confidence_scores = calculate_prediction_confidence(
                predictions,
                historical_accuracy=None,
                regime=regime
            )

            # Update predictions with confidence
            for horizon in predictions:
                predictions[horizon]['confidence'] = confidence_scores.get(horizon, 0.5)

            predictions_by_ticker[ticker] = predictions
            price_cache[ticker] = stock.get('current_price', 100.0)

        # Step 4: Generate heatmap
        heatmap_data = heatmap_gen.generate_heatmap_data(
            top_stocks,
            predictions_by_ticker,
            price_cache
        )

        # Add regime info
        heatmap_data['market_regime'] = regime
        heatmap_data['regime_characteristics'] = get_regime_characteristics(regime)

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        return jsonify({
            'screener_results': screener_results,
            'heatmap': heatmap_data,
            'execution_time_seconds': execution_time,
            'workflow': 'scan-and-predict',
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error in scan_and_predict: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/best-opportunities', methods=['POST'])
def best_opportunities():
    """
    Extract best trading opportunities from heatmap.

    Request body:
        {
            "heatmap_data": {...},
            "min_confidence": 0.7,
            "min_return": 0.02,
            "max_results": 10
        }

    Response:
        {
            "opportunities": [
                {
                    "ticker": "AAPL",
                    "timeframe": "+1w",
                    "predicted_return": 0.035,
                    "confidence": 0.85,
                    "score": 0.029,
                    "trade_setup": {...},
                    "direction": "long",
                    "strength": "strong"
                },
                ...
            ]
        }
    """
    try:
        data = request.get_json()

        heatmap_data = data.get('heatmap_data')
        min_confidence = data.get('min_confidence', 0.7)
        min_return = data.get('min_return', 0.02)
        max_results = data.get('max_results', 10)

        if not heatmap_data:
            return jsonify({'error': 'heatmap_data is required'}), 400

        logger.info(f"Extract best opportunities: min_conf={min_confidence}, min_ret={min_return}")

        # Extract opportunities
        opportunities = heatmap_gen.get_best_opportunities(
            heatmap_data,
            min_confidence,
            min_return,
            max_results
        )

        return jsonify({
            'opportunities': opportunities,
            'count': len(opportunities),
            'filters': {
                'min_confidence': min_confidence,
                'min_return': min_return,
                'max_results': max_results
            }
        }), 200

    except Exception as e:
        logger.error(f"Error in best_opportunities: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/ticker-summary/<ticker>', methods=['POST'])
def ticker_summary(ticker: str):
    """
    Get prediction summary for a specific ticker.

    Request body:
        {
            "heatmap_data": {...}
        }

    Response:
        {
            "ticker": "AAPL",
            "best_long_timeframe": "+1w",
            "best_long_return": 0.035,
            "best_short_timeframe": "-1d",
            "best_short_return": 0.025,
            "avg_confidence": 0.78,
            "recommendation": "LONG",
            "long_score": 0.15,
            "short_score": 0.05
        }
    """
    try:
        data = request.get_json()

        heatmap_data = data.get('heatmap_data')

        if not heatmap_data:
            return jsonify({'error': 'heatmap_data is required'}), 400

        logger.info(f"Ticker summary: {ticker}")

        # Get summary
        summary = heatmap_gen.get_ticker_summary(heatmap_data, ticker)

        return jsonify(summary), 200

    except Exception as e:
        logger.error(f"Error in ticker_summary: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/market-regime', methods=['GET'])
def market_regime():
    """
    Get current market regime and characteristics.

    Response:
        {
            "regime": "trending",
            "characteristics": {
                "description": "Strong directional movement",
                "best_strategies": ["momentum", "trend_following"],
                "prediction_reliability": "high",
                "recommended_timeframes": ["medium", "long"],
                "risk_level": "moderate"
            },
            "timestamp": "..."
        }
    """
    try:
        logger.info("Market regime request")

        # Detect regime
        regime = detect_market_regime()

        # Get characteristics
        characteristics = get_regime_characteristics(regime)

        return jsonify({
            'regime': regime,
            'characteristics': characteristics,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error in market_regime: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# PROMPT 1: Advanced 8-Regime Detection Endpoints

@app.route('/api/regime/detect', methods=['POST'])
def regime_detect():
    """
    Detect market regime with advanced 8-regime system.

    Request body:
        {
            "symbol": "SPY",
            "lookback_days": 60  // Optional, default 60
        }

    Response:
        {
            "symbol": "SPY",
            "primary_regime": "BULL_TRENDING",
            "secondary_regime": "MOMENTUM",
            "confidence": 0.68,
            "regime_strength": 7.5,
            "regime_scores": {
                "BULL_TRENDING": 6.2,
                "BEAR_TRENDING": 1.1,
                "MOMENTUM": 7.5,
                "MEAN_REVERTING": 2.3,
                "HIGH_VOLATILITY": 3.8,
                "LOW_VOLATILITY": 2.1,
                "RANGE_BOUND": 3.5,
                "CRISIS": 0.9
            },
            "characteristics": {
                "trend_strength": 32.4,
                "volatility": 0.18,
                "hurst_exponent": 0.62,
                "price_vs_sma20": 0.024,
                "adx": 28.5,
                "rsi": 58.3
            },
            "timestamp": "2025-10-10T14:30:00Z"
        }
    """
    try:
        data = request.get_json()

        symbol = data.get('symbol', 'SPY')
        lookback_days = data.get('lookback_days', 60)

        logger.info(f"Regime detect request: symbol={symbol}, lookback={lookback_days}")

        # Detect regime using new 8-regime system
        result = regime_detector.detect_regime(symbol, lookback_days)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in regime_detect: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/regime/batch', methods=['POST'])
def regime_batch():
    """
    Batch regime detection for multiple symbols.

    Request body:
        {
            "symbols": ["SPY", "QQQ", "IWM"],
            "lookback_days": 60  // Optional, default 60
        }

    Response:
        {
            "results": [
                {
                    "symbol": "SPY",
                    "primary_regime": "BULL_TRENDING",
                    "secondary_regime": "MOMENTUM",
                    "confidence": 0.68,
                    ...
                },
                ...
            ],
            "count": 3,
            "timestamp": "2025-10-10T14:30:00Z"
        }
    """
    try:
        data = request.get_json()

        symbols = data.get('symbols', ['SPY'])
        lookback_days = data.get('lookback_days', 60)

        if not isinstance(symbols, list):
            return jsonify({'error': 'symbols must be a list'}), 400

        logger.info(f"Batch regime detect: {len(symbols)} symbols, lookback={lookback_days}")

        # Detect regime for each symbol
        results = []
        for symbol in symbols:
            try:
                result = regime_detector.detect_regime(symbol, lookback_days)
                results.append(result)
            except Exception as e:
                logger.error(f"Error detecting regime for {symbol}: {e}")
                # Continue with other symbols

        return jsonify({
            'results': results,
            'count': len(results),
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error in regime_batch: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# PROMPT 32 EXPANSION: Export Endpoints

@app.route('/api/screener/export/csv', methods=['POST'])
def export_heatmap_csv():
    """
    Export heatmap data to CSV format.

    Request body:
        {
            "heatmap_data": {...}
        }

    Response:
        CSV file download
    """
    try:
        data = request.get_json()
        heatmap_data = data.get('heatmap_data')

        if not heatmap_data:
            return jsonify({'error': 'heatmap_data is required'}), 400

        logger.info("Exporting heatmap to CSV")

        # Generate CSV
        csv_buffer = export_to_csv(heatmap_data)

        # Return as downloadable file
        return send_file(
            io.BytesIO(csv_buffer.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=get_filename('csv')
        )

    except Exception as e:
        logger.error(f"Error in export_csv: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/export/json', methods=['POST'])
def export_heatmap_json():
    """
    Export heatmap data to JSON format.

    Request body:
        {
            "heatmap_data": {...}
        }

    Response:
        JSON file download
    """
    try:
        data = request.get_json()
        heatmap_data = data.get('heatmap_data')

        if not heatmap_data:
            return jsonify({'error': 'heatmap_data is required'}), 400

        logger.info("Exporting heatmap to JSON")

        # Generate JSON
        json_str = export_to_json(heatmap_data)

        # Return as downloadable file
        return send_file(
            io.BytesIO(json_str.encode('utf-8')),
            mimetype='application/json',
            as_attachment=True,
            download_name=get_filename('json')
        )

    except Exception as e:
        logger.error(f"Error in export_json: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/export/html', methods=['POST'])
def export_heatmap_html():
    """
    Export heatmap data to HTML format.

    Request body:
        {
            "heatmap_data": {...},
            "title": "My Heatmap"  // Optional
        }

    Response:
        HTML file download
    """
    try:
        data = request.get_json()
        heatmap_data = data.get('heatmap_data')
        title = data.get('title')

        if not heatmap_data:
            return jsonify({'error': 'heatmap_data is required'}), 400

        logger.info("Exporting heatmap to HTML")

        # Generate HTML
        html_str = export_to_html_simple(heatmap_data, title)

        # Return as downloadable file
        return send_file(
            io.BytesIO(html_str.encode('utf-8')),
            mimetype='text/html',
            as_attachment=True,
            download_name=get_filename('html')
        )

    except Exception as e:
        logger.error(f"Error in export_html: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# PROMPT 32 EXPANSION: Preset Management Endpoints

@app.route('/api/screener/presets', methods=['GET'])
def get_all_presets():
    """
    Get all scan presets.

    Response:
        {
            "presets": [
                {
                    "id": "preset_default_001",
                    "name": "Momentum Breakout",
                    "description": "...",
                    "config": {...},
                    "is_default": true,
                    "created_at": "...",
                    "last_used": "..."
                },
                ...
            ],
            "count": 3
        }
    """
    try:
        logger.info("Get all presets")

        presets = preset_mgr.get_all_presets()

        return jsonify({
            'presets': presets,
            'count': len(presets)
        }), 200

    except Exception as e:
        logger.error(f"Error in get_all_presets: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/presets/<preset_id>', methods=['GET'])
def get_preset(preset_id: str):
    """
    Get specific preset by ID.

    Response:
        {
            "id": "preset_default_001",
            "name": "Momentum Breakout",
            "description": "...",
            "config": {...},
            "is_default": true,
            "created_at": "...",
            "last_used": "..."
        }
    """
    try:
        logger.info(f"Get preset: {preset_id}")

        preset = preset_mgr.get_preset(preset_id)

        if not preset:
            return jsonify({'error': 'Preset not found'}), 404

        return jsonify(preset), 200

    except Exception as e:
        logger.error(f"Error in get_preset: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/presets', methods=['POST'])
def create_preset():
    """
    Create new scan preset.

    Request body:
        {
            "name": "My Custom Scan",
            "description": "Custom momentum + volume scan",
            "config": {
                "universe": "sp500",
                "strategy": "swing",
                "top_n": 25,
                "filters": {...}
            }
        }

    Response:
        {
            "id": "preset_004",
            "name": "My Custom Scan",
            "description": "...",
            "config": {...},
            "is_default": false,
            "created_at": "...",
            "last_used": "..."
        }
    """
    try:
        data = request.get_json()

        name = data.get('name')
        description = data.get('description', '')
        config = data.get('config')

        if not name or not config:
            return jsonify({'error': 'name and config are required'}), 400

        logger.info(f"Create preset: {name}")

        preset = preset_mgr.create_preset(name, description, config)

        return jsonify(preset), 201

    except Exception as e:
        logger.error(f"Error in create_preset: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/presets/<preset_id>', methods=['PUT'])
def update_preset(preset_id: str):
    """
    Update existing preset.

    Request body:
        {
            "name": "Updated Name",  // Optional
            "description": "Updated description",  // Optional
            "config": {...}  // Optional
        }

    Response:
        Updated preset object or error if default preset
    """
    try:
        data = request.get_json()

        name = data.get('name')
        description = data.get('description')
        config = data.get('config')

        logger.info(f"Update preset: {preset_id}")

        preset = preset_mgr.update_preset(preset_id, name, description, config)

        if not preset:
            return jsonify({'error': 'Preset not found or cannot update default preset'}), 400

        return jsonify(preset), 200

    except Exception as e:
        logger.error(f"Error in update_preset: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/presets/<preset_id>', methods=['DELETE'])
def delete_preset(preset_id: str):
    """
    Delete preset.

    Response:
        {
            "success": true,
            "message": "Preset deleted"
        }
    """
    try:
        logger.info(f"Delete preset: {preset_id}")

        success = preset_mgr.delete_preset(preset_id)

        if not success:
            return jsonify({'error': 'Preset not found or cannot delete default preset'}), 400

        return jsonify({
            'success': True,
            'message': 'Preset deleted'
        }), 200

    except Exception as e:
        logger.error(f"Error in delete_preset: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/presets/<preset_id>/run', methods=['POST'])
def run_preset(preset_id: str):
    """
    Run scan using preset configuration.

    Request body:
        {
            "min_confidence": 0.6  // Optional, for predictions
        }

    Response:
        {
            "preset": {...},
            "screener_results": {...},
            "heatmap": {...}  // If min_confidence provided
        }
    """
    try:
        data = request.get_json() or {}
        min_confidence = data.get('min_confidence')

        logger.info(f"Run preset: {preset_id}")

        # Get preset
        preset = preset_mgr.get_preset(preset_id)

        if not preset:
            return jsonify({'error': 'Preset not found'}), 404

        # Mark as used
        preset_mgr.mark_used(preset_id)

        # Extract config
        config = preset.get('config', {})
        universe = config.get('universe', 'sp500')
        strategy = config.get('strategy', 'swing')
        top_n = config.get('top_n', 50)

        # Run screening
        screener_results = screener.screen_universe(
            universe_name=universe,
            strategy_name=strategy,
            top_n=top_n,
            custom_tickers=None
        )

        response = {
            'preset': preset,
            'screener_results': screener_results
        }

        # If min_confidence provided, generate predictions
        if min_confidence is not None:
            regime = detect_market_regime()
            top_stocks = screener_results.get('top_stocks', [])
            predictions_by_ticker = {}
            price_cache = {}

            for stock in top_stocks:
                ticker = stock['ticker']
                current_features = stock.get('factors', {})

                predictions = predictor.predict_all_horizons(ticker, current_features)
                confidence_scores = calculate_prediction_confidence(predictions, None, regime)

                for horizon in predictions:
                    predictions[horizon]['confidence'] = confidence_scores.get(horizon, 0.5)

                predictions_by_ticker[ticker] = predictions
                price_cache[ticker] = stock.get('current_price', 100.0)

            heatmap_data = heatmap_gen.generate_heatmap_data(
                top_stocks,
                predictions_by_ticker,
                price_cache
            )

            heatmap_data['market_regime'] = regime
            heatmap_data['regime_characteristics'] = get_regime_characteristics(regime)

            response['heatmap'] = heatmap_data

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in run_preset: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/presets/export', methods=['POST'])
def export_presets():
    """
    Export all presets to JSON.

    Response:
        JSON file download
    """
    try:
        logger.info("Export all presets")

        json_str = preset_mgr.export_presets()

        return send_file(
            io.BytesIO(json_str.encode('utf-8')),
            mimetype='application/json',
            as_attachment=True,
            download_name='presets_export.json'
        )

    except Exception as e:
        logger.error(f"Error in export_presets: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/screener/presets/import', methods=['POST'])
def import_presets():
    """
    Import presets from JSON.

    Request body:
        {
            "presets_json": "{...}"
        }

    Response:
        {
            "imported_count": 5,
            "message": "Successfully imported 5 presets"
        }
    """
    try:
        data = request.get_json()
        presets_json = data.get('presets_json')

        if not presets_json:
            return jsonify({'error': 'presets_json is required'}), 400

        logger.info("Import presets")

        imported_count = preset_mgr.import_presets(presets_json)

        return jsonify({
            'imported_count': imported_count,
            'message': f'Successfully imported {imported_count} presets'
        }), 200

    except Exception as e:
        logger.error(f"Error in import_presets: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# PROMPT 2: Hierarchical Regime Detection Endpoints

@app.route('/api/hierarchy/full', methods=['POST'])
def hierarchy_full_analysis():
    """
    Analyze full 7-layer hierarchical regime.

    Request body:
        {
            "symbol": "AAPL",  // Optional, for stock-level analysis
            "lookback_days": 60  // Optional, default 60
        }

    Response:
        {
            "timestamp": "...",
            "symbol": "AAPL",
            "overall_regime": "STRONG_BULL_REGIME",
            "risk_environment": {...},
            "alignment_scores": {...},
            "divergences": [...],
            "layers": {
                "layer_0_temporal": {...},
                "layer_1_macro": {...},
                "layer_2_cross_asset": {...},
                "layer_3_market": {...},
                "layer_4_sector": {...},
                "layer_5_industry": {...},
                "layer_6_stock": {...}
            },
            "stock_assessment": {...},
            "interpretation": "..."
        }
    """
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol')
        lookback_days = data.get('lookback_days', 60)

        logger.info(f"Full hierarchy analysis for {symbol or 'market'}")

        result = hierarchy_mgr.analyze_full_hierarchy(symbol, lookback_days)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in hierarchy_full_analysis: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/hierarchy/stock/<symbol>', methods=['POST'])
def hierarchy_stock_analysis(symbol: str):
    """
    Analyze hierarchy specifically for a stock.

    Request body:
        {
            "lookback_days": 60  // Optional
        }

    Response:
        {
            "symbol": "AAPL",
            "timestamp": "...",
            "stock_regime": {...},
            "market_alignment": 80.0,
            "sector_alignment": 90.0,
            "overall_alignment": 75.5,
            "hierarchy_support": true,
            "trading_signals": {
                "primary_signal": "STRONG_BUY",
                "conviction": "HIGH",
                "supporting_factors": [...],
                "risk_factors": [...]
            },
            "stock_assessment": {...},
            "summary": "..."
        }
    """
    try:
        data = request.get_json() or {}
        lookback_days = data.get('lookback_days', 60)

        logger.info(f"Stock hierarchy analysis for {symbol}")

        result = hierarchy_mgr.analyze_stock_hierarchy(symbol, lookback_days)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in hierarchy_stock_analysis: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/hierarchy/temporal', methods=['GET'])
def hierarchy_temporal():
    """
    Get Layer 0: Temporal/Calendar regime.

    Response:
        {
            "date": "2025-10-10",
            "seasonal_regime": "HISTORICALLY_VOLATILE",
            "day_regime": "WEEKEND_GAP_RISK",
            "is_opex_week": false,
            "is_fed_week": false,
            "days_to_next_fed": 12,
            ...
        }
    """
    try:
        from temporal_regime import detect_temporal_context

        logger.info("Get temporal regime")

        result = detect_temporal_context()

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in hierarchy_temporal: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/hierarchy/macro', methods=['GET'])
def hierarchy_macro():
    """
    Get Layer 1: Macro regime.

    Response:
        {
            "overall_macro_regime": "GOLDILOCKS",
            "macro_score": 7.5,
            "fed_policy": "NEUTRAL",
            "economic_cycle": "LATE_EXPANSION",
            "inflation_regime": "MODERATE_INFLATION",
            ...
        }
    """
    try:
        from macro_regime import detect_macro_regime

        logger.info("Get macro regime")

        result = detect_macro_regime()

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in hierarchy_macro: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/hierarchy/cross-asset', methods=['POST'])
def hierarchy_cross_asset():
    """
    Get Layer 2: Cross-asset regime.

    Request body:
        {
            "lookback_days": 30  // Optional
        }

    Response:
        {
            "cross_asset_regime": "RISK_ON",
            "risk_sentiment": 7.5,
            "asset_momentum": {...},
            "correlations": {...},
            ...
        }
    """
    try:
        from cross_asset_regime import detect_cross_asset_regime

        data = request.get_json() or {}
        lookback_days = data.get('lookback_days', 30)

        logger.info("Get cross-asset regime")

        result = detect_cross_asset_regime(lookback_days)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in hierarchy_cross_asset: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/hierarchy/market', methods=['POST'])
def hierarchy_market():
    """
    Get Layer 3: Market regime.

    Request body:
        {
            "lookback_days": 60  // Optional
        }

    Response:
        {
            "overall_market_regime": "BULL_TRENDING",
            "market_health_score": 85.5,
            "market_breadth": {...},
            "market_leader": {...},
            ...
        }
    """
    try:
        from market_regime import detect_market_regime

        data = request.get_json() or {}
        lookback_days = data.get('lookback_days', 60)

        logger.info("Get market regime")

        result = detect_market_regime(lookback_days)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in hierarchy_market: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/hierarchy/sector', methods=['POST'])
def hierarchy_sector():
    """
    Get Layer 4: Sector regime.

    Request body:
        {
            "lookback_days": 60  // Optional
        }

    Response:
        {
            "rotation_pattern": "RISK_ON_ROTATION",
            "risk_appetite_score": 72.5,
            "rotation_analysis": {...},
            "sector_leaders": [...],
            ...
        }
    """
    try:
        from sector_regime import detect_sector_regime

        data = request.get_json() or {}
        lookback_days = data.get('lookback_days', 60)

        logger.info("Get sector regime")

        result = detect_sector_regime(lookback_days)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in hierarchy_sector: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/hierarchy/industry', methods=['POST'])
def hierarchy_industry():
    """
    Get Layer 5: Industry regime.

    Request body:
        {
            "lookback_days": 60,  // Optional
            "symbols": ["SMH", "IBB", ...]  // Optional, default all industries
        }

    Response:
        {
            "industry_count": 18,
            "industry_analysis": {...},
            "emerging_trends": [...],
            "top_performers": [...],
            "bottom_performers": [...],
            ...
        }
    """
    try:
        from industry_regime import detect_industry_regime

        data = request.get_json() or {}
        lookback_days = data.get('lookback_days', 60)
        symbols = data.get('symbols')

        logger.info("Get industry regime")

        result = detect_industry_regime(lookback_days, symbols)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in hierarchy_industry: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# PROMPT 3: FLEXIBLE SCANNER ENDPOINTS
# ============================================================================

@app.route('/api/scanner/criteria', methods=['GET'])
def get_criteria():
    """
    List all available screening criteria.

    Response:
        {
            "criteria": [
                {
                    "id": "pe_ratio",
                    "name": "P/E Ratio",
                    "category": "valuation",
                    "description": "Price-to-Earnings ratio (lower is better)",
                    "ideal_direction": "lower",
                    "default_weight": 1.0,
                    "enabled_by_default": true
                },
                ...
            ]
        }
    """
    try:
        criteria = list_criteria()
        return jsonify({'criteria': criteria}), 200
    except Exception as e:
        logger.error(f"Error in get_criteria: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/scanner/flexible', methods=['POST'])
def flexible_scan():
    """
    Run flexible scanner with custom criteria and ranking.

    Request body:
        {
            "symbols": ["AAPL", "MSFT", "GOOGL", ...],  // Required
            "enabled_criteria": ["pe_ratio", "momentum_20d", ...],  // Optional, default all enabled
            "custom_weights": {"pe_ratio": 2.0, "momentum_20d": 1.5},  // Optional
            "ranking_method": "composite_score",  // "composite_score", "percentile_rank", "z_score", "pareto_optimal"
            "min_hierarchy_alignment": 60.0,  // Optional, filter by alignment (0-100)
            "filter_divergent": false  // Optional, remove divergent stocks
        }

    Response:
        {
            "ranking_method": "composite_score",
            "stocks_analyzed": 50,
            "stocks_returned": 10,
            "timestamp": "...",
            "ranked_stocks": [
                {
                    "symbol": "AAPL",
                    "rank": 1,
                    "composite_score": 0.85,
                    "criterion_scores": {
                        "pe_ratio": 25.5,
                        "momentum_20d": 15.3,
                        ...
                    }
                },
                ...
            ]
        }
    """
    try:
        data = request.get_json()

        symbols = data.get('symbols')
        if not symbols:
            return jsonify({'error': 'symbols is required'}), 400

        # Fetch stock data with factors and hierarchy
        stocks = []
        for symbol in symbols:
            # Get basic factors (you may already have this data)
            stock_data = {
                'symbol': symbol,
                'factors': {
                    'pe_ratio': 20,  # Placeholder - replace with real data
                    'momentum_20d': 5.0,
                    'rsi': 60,
                    # Add other factors...
                },
                'regime': {},  # Can populate from PROMPT 1
                'hierarchy': {}  # Can populate from PROMPT 2
            }
            stocks.append(stock_data)

        enabled_criteria = data.get('enabled_criteria')
        custom_weights = data.get('custom_weights')
        ranking_method = data.get('ranking_method', 'composite_score')
        min_hierarchy_alignment = data.get('min_hierarchy_alignment')
        filter_divergent = data.get('filter_divergent', False)

        logger.info(f"Flexible scan with {len(symbols)} symbols, method: {ranking_method}")

        ranked_stocks = scan_stocks(
            stocks,
            enabled_criteria,
            custom_weights,
            ranking_method,
            min_hierarchy_alignment,
            filter_divergent
        )

        return jsonify({
            'ranking_method': ranking_method,
            'stocks_analyzed': len(symbols),
            'stocks_returned': len(ranked_stocks),
            'timestamp': datetime.now().isoformat(),
            'ranked_stocks': ranked_stocks[:20]  # Return top 20
        }), 200

    except Exception as e:
        logger.error(f"Error in flexible_scan: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# PROMPT 4: TIME MACHINE & CORRELATION BREAKDOWN ENDPOINTS
# ============================================================================

@app.route('/api/timemachine/match', methods=['POST'])
def timemachine_match():
    """
    Find historical pattern matches for a stock.

    Request body:
        {
            "symbol": "AAPL",
            "lookback_days": 30,  // Optional, default 30
            "top_n": 5,  // Optional, default 5
            "min_similarity": 0.7  // Optional, default 0.7 (0-1 scale)
        }

    Response:
        {
            "symbol": "AAPL",
            "matches": [
                {
                    "pattern_id": "breakout_001",
                    "pattern_name": "Cup and Handle Breakout",
                    "category": "breakout",
                    "similarity_score": 0.85,
                    "expected_return_5d": 8.5,
                    "expected_return_10d": 15.2,
                    "expected_return_20d": 22.8,
                    "success_rate": 72.0,
                    "confidence": 61.2,
                    "description": "Classic cup and handle pattern with volume confirmation"
                },
                ...
            ]
        }
    """
    try:
        data = request.get_json()

        symbol = data.get('symbol')
        if not symbol:
            return jsonify({'error': 'symbol is required'}), 400

        lookback_days = data.get('lookback_days', 30)
        top_n = data.get('top_n', 5)
        min_similarity = data.get('min_similarity', 0.7)

        logger.info(f"Time Machine pattern matching for {symbol}")

        matches = find_pattern_matches(symbol, lookback_days, top_n, min_similarity)

        return jsonify({
            'symbol': symbol,
            'lookback_days': lookback_days,
            'matches_found': len(matches),
            'matches': matches,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error in timemachine_match: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/timemachine/predict', methods=['POST'])
def timemachine_predict():
    """
    Predict stock outcome based on pattern matching.

    Request body:
        {
            "symbol": "AAPL",
            "lookback_days": 30,  // Optional
            "horizon": "10d"  // "5d", "10d", or "20d"
        }

    Response:
        {
            "symbol": "AAPL",
            "horizon": "10d",
            "expected_return": 12.5,
            "confidence": 68.3,
            "method": "time_machine_dtw",
            "matches_found": 8,
            "top_matches": [...]
        }
    """
    try:
        data = request.get_json()

        symbol = data.get('symbol')
        if not symbol:
            return jsonify({'error': 'symbol is required'}), 400

        lookback_days = data.get('lookback_days', 30)
        horizon = data.get('horizon', '10d')

        logger.info(f"Time Machine prediction for {symbol}, horizon: {horizon}")

        prediction = predict_from_patterns(symbol, lookback_days, horizon)

        return jsonify(prediction), 200

    except Exception as e:
        logger.error(f"Error in timemachine_predict: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/timemachine/batch', methods=['POST'])
def timemachine_batch():
    """
    Batch analyze multiple symbols for pattern matches.

    Request body:
        {
            "symbols": ["AAPL", "MSFT", "GOOGL", ...],
            "lookback_days": 30  // Optional
        }

    Response:
        {
            "results": [
                {
                    "symbol": "AAPL",
                    "best_match": {...},
                    "prediction": {...},
                    "total_matches": 5
                },
                ...
            ]
        }
    """
    try:
        data = request.get_json()

        symbols = data.get('symbols')
        if not symbols:
            return jsonify({'error': 'symbols is required'}), 400

        lookback_days = data.get('lookback_days', 30)

        logger.info(f"Time Machine batch analysis for {len(symbols)} symbols")

        results = time_machine.batch_analyze(symbols, lookback_days)

        return jsonify({
            'symbols_analyzed': len(symbols),
            'results': results,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error in timemachine_batch: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/correlation/breakdown', methods=['POST'])
def correlation_breakdown():
    """
    Analyze correlation breakdown between stock and sector.

    Request body:
        {
            "symbol": "AAPL",
            "sector": "Technology",  // Optional, auto-detected if omitted
            "lookback_days": 120  // Optional
        }

    Response:
        {
            "symbol": "AAPL",
            "sector": "Technology",
            "sector_etf": "XLK",
            "breakdown_detected": true,
            "breakdown_type": "BULLISH_BREAKOUT",
            "breakdown_strength": 75.5,
            "opportunity_score": 82.3,
            "correlations": {
                "short": 0.35,
                "medium": 0.62,
                "long": 0.78
            },
            "relative_performance": {
                "short_relative": 12.5,
                "medium_relative": 8.3,
                "long_relative": 5.2
            },
            "interpretation": "Strong bullish breakout detected..."
        }
    """
    try:
        data = request.get_json()

        symbol = data.get('symbol')
        if not symbol:
            return jsonify({'error': 'symbol is required'}), 400

        sector = data.get('sector')
        lookback_days = data.get('lookback_days', 120)

        logger.info(f"Correlation breakdown analysis for {symbol}")

        analysis = analyze_correlation_breakdown(symbol, sector, lookback_days)

        return jsonify(analysis), 200

    except Exception as e:
        logger.error(f"Error in correlation_breakdown: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/correlation/opportunities', methods=['POST'])
def correlation_opportunities():
    """
    Find breakout opportunities from correlation breakdown.

    Request body:
        {
            "symbols": ["AAPL", "MSFT", "GOOGL", ...],
            "min_opportunity_score": 60.0,  // Optional, 0-100
            "breakdown_type": "BULLISH_BREAKOUT"  // Optional
        }

    Response:
        {
            "opportunities": [
                {
                    "symbol": "AAPL",
                    "opportunity_score": 85.2,
                    "breakdown_type": "BULLISH_BREAKOUT",
                    "breakdown_strength": 78.5,
                    "relative_performance": {...},
                    ...
                },
                ...
            ],
            "total_analyzed": 50,
            "opportunities_found": 8
        }
    """
    try:
        data = request.get_json()

        symbols = data.get('symbols')
        if not symbols:
            return jsonify({'error': 'symbols is required'}), 400

        min_opportunity_score = data.get('min_opportunity_score', 60.0)
        breakdown_type = data.get('breakdown_type', 'BULLISH_BREAKOUT')

        logger.info(f"Finding correlation opportunities in {len(symbols)} symbols")

        opportunities = find_breakout_opportunities(symbols, min_opportunity_score)

        return jsonify({
            'opportunities': opportunities,
            'total_analyzed': len(symbols),
            'opportunities_found': len(opportunities),
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error in correlation_opportunities: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# PROMPT 5 ENDPOINTS: LIQUIDITY VACUUM & SMART MONEY TRACKER
# ============================================================================

@app.route('/api/liquidity/vacuum', methods=['POST'])
def liquidity_vacuum():
    """
    Detect liquidity vacuum for a single symbol.

    Request body:
        {
            "symbol": "AAPL",
            "lookback_days": 30,  // Optional, default 30
            "catalyst_date": "2025-11-15"  // Optional (YYYY-MM-DD)
        }

    Returns:
        {
            "symbol": "AAPL",
            "vacuum_detected": true,
            "vacuum_strength": 75.5,
            "consolidation_score": 82.0,
            "volume_contraction_score": 68.0,
            "spread_score": 85.0,
            "atr_compression_score": 73.0,
            "catalyst_proximity_score": 100.0,
            "days_to_catalyst": 21,
            "interpretation": "..."
        }
    """
    try:
        data = request.get_json()

        if not data or 'symbol' not in data:
            return jsonify({'error': 'Missing required field: symbol'}), 400

        symbol = data['symbol']
        lookback_days = data.get('lookback_days', 30)
        catalyst_date = data.get('catalyst_date', None)

        result = liquidity_detector.detect_vacuum(
            symbol, lookback_days, catalyst_date
        )

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in liquidity_vacuum: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/liquidity/batch', methods=['POST'])
def liquidity_batch():
    """
    Batch liquidity vacuum analysis for multiple symbols.

    Request body:
        {
            "symbols": ["AAPL", "MSFT", "GOOGL"],
            "lookback_days": 30,  // Optional, default 30
            "catalyst_map": {  // Optional
                "AAPL": "2025-11-01",
                "MSFT": "2025-10-25"
            }
        }

    Returns:
        {
            "results": [
                {
                    "symbol": "AAPL",
                    "vacuum_detected": true,
                    "vacuum_strength": 75.5,
                    ...
                },
                ...
            ],
            "total_analyzed": 3,
            "vacuums_detected": 2
        }
    """
    try:
        data = request.get_json()

        if not data or 'symbols' not in data:
            return jsonify({'error': 'Missing required field: symbols'}), 400

        symbols = data['symbols']
        catalyst_map = data.get('catalyst_map', None)

        results = liquidity_detector.batch_analyze(symbols, catalyst_map)

        vacuums_detected = sum(1 for r in results if r['vacuum_detected'])

        return jsonify({
            'results': results,
            'total_analyzed': len(symbols),
            'vacuums_detected': vacuums_detected,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error in liquidity_batch: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/smartmoney/track', methods=['POST'])
def smart_money_track():
    """
    Track smart money activity for a single symbol.

    Request body:
        {
            "symbol": "AAPL",
            "lookback_days": 30  // Optional, default 30
        }

    Returns:
        {
            "symbol": "AAPL",
            "smart_money_detected": true,
            "aggregate_score": 72.5,
            "dark_pool_score": 68.0,
            "options_flow_score": 85.0,
            "insider_score": 65.0,
            "confidence": 78.0,
            "signals": [
                "Dark Pool: 35.2% of volume, bullish sentiment",
                "Options Flow: bullish, $2.5M premium"
            ],
            "interpretation": "..."
        }
    """
    try:
        data = request.get_json()

        if not data or 'symbol' not in data:
            return jsonify({'error': 'Missing required field: symbol'}), 400

        symbol = data['symbol']
        lookback_days = data.get('lookback_days', 30)

        result = smart_money_tracker.track_smart_money(symbol, lookback_days)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in smart_money_track: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/smartmoney/batch', methods=['POST'])
def smart_money_batch():
    """
    Batch smart money analysis for multiple symbols.

    Request body:
        {
            "symbols": ["AAPL", "MSFT", "GOOGL"],
            "lookback_days": 30  // Optional, default 30
        }

    Returns:
        {
            "results": [
                {
                    "symbol": "AAPL",
                    "smart_money_detected": true,
                    "aggregate_score": 72.5,
                    ...
                },
                ...
            ],
            "total_analyzed": 3,
            "smart_money_detected": 2
        }
    """
    try:
        data = request.get_json()

        if not data or 'symbols' not in data:
            return jsonify({'error': 'Missing required field: symbols'}), 400

        symbols = data['symbols']
        lookback_days = data.get('lookback_days', 30)

        results = smart_money_tracker.batch_analyze(symbols, lookback_days)

        smart_money_count = sum(1 for r in results if r['smart_money_detected'])

        return jsonify({
            'results': results,
            'total_analyzed': len(symbols),
            'smart_money_detected': smart_money_count,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error in smart_money_batch: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/smartmoney/accumulation', methods=['POST'])
def smart_money_accumulation():
    """
    Find stocks with strong smart money accumulation.

    Request body:
        {
            "symbols": ["AAPL", "MSFT", "GOOGL", ...],
            "min_score": 60.0,  // Optional, default 60.0
            "min_confidence": 50.0  // Optional, default 50.0
        }

    Returns:
        {
            "opportunities": [
                {
                    "symbol": "AAPL",
                    "aggregate_score": 78.5,
                    "confidence": 82.0,
                    "signals": [...]
                },
                ...
            ],
            "total_analyzed": 10,
            "opportunities_found": 3
        }
    """
    try:
        data = request.get_json()

        if not data or 'symbols' not in data:
            return jsonify({'error': 'Missing required field: symbols'}), 400

        symbols = data['symbols']
        min_score = data.get('min_score', 60.0)
        min_confidence = data.get('min_confidence', 50.0)

        opportunities = smart_money_tracker.find_accumulation_opportunities(
            symbols, min_score, min_confidence
        )

        return jsonify({
            'opportunities': opportunities,
            'total_analyzed': len(symbols),
            'opportunities_found': len(opportunities),
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error in smart_money_accumulation: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500




# ========================================
# PROMPT 6: Sentiment Divergence & Fractal Regime Endpoints
# ========================================

@app.route('/api/sentiment/aggregate', methods=['POST', 'OPTIONS'])
def aggregate_sentiment_endpoint():
    """
    Aggregate sentiment from multiple sources (news, social, analyst, short interest).

    Request:
        {
            "symbol": "AAPL",
            "lookback_days": 7  // optional, default 7
        }

    Response:
        {
            "symbol": "AAPL",
            "aggregate_sentiment": "bullish",  // bullish, bearish, neutral
            "aggregate_score": 45.5,  // -100 to 100
            "news_sentiment": 60.0,
            "social_sentiment": 30.0,
            "analyst_sentiment": 50.0,
            "short_interest_sentiment": 20.0,
            "confidence": 75.0,
            "sentiment_details": {...},
            "analysis_date": "2025-10-11T..."
        }
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()
        symbol = data.get('symbol')
        lookback_days = data.get('lookback_days', 7)

        if not symbol:
            return jsonify({'error': 'Missing required field: symbol'}), 400

        logger.info(f"Aggregating sentiment for {symbol}")
        result = sentiment_aggregator.aggregate_sentiment(symbol, lookback_days)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in aggregate_sentiment: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/sentiment/divergence', methods=['POST', 'OPTIONS'])
def sentiment_divergence_endpoint():
    """
    Detect sentiment vs price divergence (contrarian signals).

    Request:
        {
            "symbol": "TSLA",
            "lookback_days": 30  // optional, default 30
        }

    Response:
        {
            "symbol": "TSLA",
            "divergence_detected": true,
            "divergence_type": "bullish",  // bullish, bearish, none
            "divergence_strength": 75.0,  // 0-100
            "price_trend": "down",
            "price_change_pct": -8.5,
            "sentiment_trend": "improving",
            "current_sentiment": 35.0,
            "sentiment_extreme": false,
            "contrarian_signal": "Contrarian BUY - bearish sentiment, declining price",
            "interpretation": "..."
        }
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()
        symbol = data.get('symbol')
        lookback_days = data.get('lookback_days', 30)

        if not symbol:
            return jsonify({'error': 'Missing required field: symbol'}), 400

        logger.info(f"Detecting sentiment divergence for {symbol}")
        result = sentiment_divergence_detector.detect_divergence(symbol, lookback_days)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in sentiment_divergence: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/fractal/regime', methods=['POST', 'OPTIONS'])
def fractal_regime_endpoint():
    """
    Detect multi-timeframe regime alignment.

    Request:
        {
            "symbol": "NVDA"
        }

    Response:
        {
            "symbol": "NVDA",
            "alignment_detected": true,
            "alignment_type": "bullish",  // bullish, bearish, mixed
            "alignment_strength": 85.0,  // 0-100
            "regimes": {
                "ultra_short": {"regime": "trending_up", "trend_strength": 75.0, ...},
                "short": {"regime": "trending_up", "trend_strength": 80.0, ...},
                "medium": {"regime": "trending_up", "trend_strength": 70.0, ...},
                "long": {"regime": "trending_up", "trend_strength": 65.0, ...}
            },
            "fractal_score": 82.5,  // Multi-timeframe confluence score
            "interpretation": "..."
        }
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()
        symbol = data.get('symbol')

        if not symbol:
            return jsonify({'error': 'Missing required field: symbol'}), 400

        logger.info(f"Detecting fractal regime for {symbol}")
        result = fractal_regime_detector.detect_regime(symbol)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in fractal_regime: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/sentiment/contrarian', methods=['POST', 'OPTIONS'])
def contrarian_opportunities_endpoint():
    """
    Find contrarian trading opportunities (sentiment divergence).

    Request:
        {
            "symbols": ["AAPL", "MSFT", "GOOGL"],
            "min_strength": 60.0,  // optional, default 60
            "divergence_type": "bullish"  // optional: "bullish", "bearish", or null for both
        }

    Response:
        {
            "opportunities": [{...}, {...}],
            "opportunities_found": 2,
            "total_analyzed": 3,
            "timestamp": "2025-10-11T..."
        }
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        min_strength = data.get('min_strength', 60.0)
        divergence_type = data.get('divergence_type')  # None, 'bullish', or 'bearish'

        if not symbols:
            return jsonify({'error': 'Missing required field: symbols'}), 400

        logger.info(f"Finding contrarian opportunities for {len(symbols)} symbols")
        opportunities = sentiment_divergence_detector.find_divergence_opportunities(
            symbols, min_strength, divergence_type
        )

        return jsonify({
            'opportunities': opportunities,
            'opportunities_found': len(opportunities),
            'total_analyzed': len(symbols),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in contrarian_opportunities: {e}")
        return jsonify({'error': str(e)}), 500


# ========================================
# PROMPT 7: Catalyst Calendar & Intermarket Relay Endpoints
# ========================================

@app.route('/api/catalyst/calendar', methods=['POST', 'OPTIONS'])
def catalyst_calendar_endpoint():
    """
    Get upcoming catalyst events for a symbol.

    Request:
        {
            "symbol": "AAPL",
            "days_ahead": 60  // optional, default 60
        }

    Response:
        {
            "symbol": "AAPL",
            "events": [...],
            "earnings_date": "2025-11-05",
            "days_to_earnings": 25,
            "has_upcoming_catalyst": true,
            "next_catalyst_type": "earnings",
            "days_to_next_catalyst": 25
        }
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()
        symbol = data.get('symbol')
        days_ahead = data.get('days_ahead', 60)

        if not symbol:
            return jsonify({'error': 'Missing required field: symbol'}), 400

        logger.info(f"Getting catalyst calendar for {symbol}")
        result = event_calendar.get_upcoming_events(symbol, days_ahead)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in catalyst_calendar: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/catalyst/setup', methods=['POST', 'OPTIONS'])
def catalyst_setup_endpoint():
    """
    Score catalyst setup (catalyst + technical setup).

    Request:
        {
            "symbol": "TSLA"
        }

    Response:
        {
            "symbol": "TSLA",
            "setup_detected": true,
            "setup_score": 75.0,
            "catalyst_score": 85.0,
            "technical_score": 68.0,
            "days_to_catalyst": 15,
            "catalyst_type": "earnings",
            "earnings_date": "2025-10-26",
            "interpretation": "..."
        }
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()
        symbol = data.get('symbol')

        if not symbol:
            return jsonify({'error': 'Missing required field: symbol'}), 400

        logger.info(f"Scanning catalyst setup for {symbol}")
        result = catalyst_scanner.scan_catalyst_setup(symbol)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in catalyst_setup: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/catalyst/batch', methods=['POST', 'OPTIONS'])
def catalyst_batch_endpoint():
    """
    Find catalyst setups across multiple symbols.

    Request:
        {
            "symbols": ["AAPL", "MSFT", "GOOGL"],
            "min_score": 60.0  // optional, default 60
        }

    Response:
        {
            "setups": [{...}, {...}],
            "setups_found": 2,
            "total_analyzed": 3,
            "timestamp": "2025-10-11T..."
        }
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        min_score = data.get('min_score', 60.0)

        if not symbols:
            return jsonify({'error': 'Missing required field: symbols'}), 400

        logger.info(f"Finding catalyst setups for {len(symbols)} symbols")
        setups = find_catalyst_setups(symbols, min_score)

        return jsonify({
            'setups': setups,
            'setups_found': len(setups),
            'total_analyzed': len(symbols),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in catalyst_batch: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/intermarket/relay', methods=['POST', 'OPTIONS'])
def intermarket_relay_endpoint():
    """
    Detect intermarket lead-lag relationships.

    Request:
        {
            "leader": "GLD",
            "follower": "GDX",
            "lookback_days": 60  // optional, default 60
        }

    Or for scanning all predefined pairs:
        {
            "scan_all": true
        }

    Response (single pair):
        {
            "leader": "GLD",
            "follower": "GDX",
            "relay_detected": true,
            "correlation": 0.85,
            "lag_days": 2,
            "leader_signal": "bullish",
            "relay_strength": 85.0,
            "interpretation": "..."
        }

    Response (scan all):
        {
            "relays": [{...}, {...}, ...],
            "timestamp": "2025-10-11T..."
        }
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()
        scan_all = data.get('scan_all', False)

        if scan_all:
            logger.info("Scanning all intermarket relay pairs")
            relays = scan_market_relays()
            return jsonify({
                'relays': relays,
                'timestamp': datetime.now().isoformat()
            })

        leader = data.get('leader')
        follower = data.get('follower')
        lookback_days = data.get('lookback_days', 60)

        if not leader or not follower:
            return jsonify({'error': 'Missing required fields: leader, follower'}), 400

        logger.info(f"Detecting relay: {leader} → {follower}")
        result = intermarket_relay.detect_relay(leader, follower, lookback_days)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in intermarket_relay: {e}")
        return jsonify({'error': str(e)}), 500



# ============================================================================
# PROMPT 8: PAIRS TRADING & SCENARIO ANALYSIS ENDPOINTS
# ============================================================================

@app.route('/api/statistical/cointegration', methods=['POST'])
def test_cointegration_endpoint():
    """
    Test cointegration between two symbols.
    
    Request body:
        {
            "symbol1": "AAPL",
            "symbol2": "MSFT",
            "lookback_days": 252  // optional, default 252
        }
    """
    try:
        data = request.get_json()
        symbol1 = data.get('symbol1')
        symbol2 = data.get('symbol2')
        lookback_days = data.get('lookback_days', 252)
        
        if not symbol1 or not symbol2:
            return jsonify({'error': 'Missing required fields: symbol1, symbol2'}), 400
        
        logger.info(f"Testing cointegration: {symbol1} vs {symbol2}")
        result = statistical_tests.test_cointegration(symbol1, symbol2, lookback_days)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in test_cointegration: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/statistical/half-life', methods=['POST'])
def calculate_half_life_endpoint():
    """
    Calculate half-life of mean reversion for a spread.
    
    Request body:
        {
            "symbol1": "AAPL",
            "symbol2": "MSFT",
            "hedge_ratio": 1.2,
            "lookback_days": 252  // optional
        }
    """
    try:
        data = request.get_json()
        symbol1 = data.get('symbol1')
        symbol2 = data.get('symbol2')
        hedge_ratio = data.get('hedge_ratio')
        lookback_days = data.get('lookback_days', 252)
        
        if not symbol1 or not symbol2 or hedge_ratio is None:
            return jsonify({'error': 'Missing required fields: symbol1, symbol2, hedge_ratio'}), 400
        
        logger.info(f"Calculating half-life: {symbol1}/{symbol2}")
        result = statistical_tests.calculate_half_life(symbol1, symbol2, hedge_ratio, lookback_days)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in calculate_half_life: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/pairs/scan', methods=['POST'])
def scan_pairs_endpoint():
    """
    Scan universe for cointegrated pairs.
    
    Request body:
        {
            "symbols": ["AAPL", "MSFT", "GOOGL", ...],
            "min_correlation": 0.7,  // optional
            "max_pairs": 20  // optional
        }
    """
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        min_correlation = data.get('min_correlation', 0.7)
        max_pairs = data.get('max_pairs', 20)
        
        if not symbols or len(symbols) < 2:
            return jsonify({'error': 'Need at least 2 symbols to scan'}), 400
        
        logger.info(f"Scanning {len(symbols)} symbols for pairs")
        results = pairs_trading.scan_pairs(symbols, min_correlation, max_pairs)
        
        return jsonify({
            'pairs': results,
            'total_found': len(results),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in scan_pairs: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/pairs/analyze', methods=['POST'])
def analyze_pair_endpoint():
    """
    Detailed analysis of a specific pair.
    
    Request body:
        {
            "symbol1": "AAPL",
            "symbol2": "MSFT",
            "lookback_days": 252  // optional
        }
    """
    try:
        data = request.get_json()
        symbol1 = data.get('symbol1')
        symbol2 = data.get('symbol2')
        lookback_days = data.get('lookback_days', 252)
        
        if not symbol1 or not symbol2:
            return jsonify({'error': 'Missing required fields: symbol1, symbol2'}), 400
        
        logger.info(f"Analyzing pair: {symbol1}/{symbol2}")
        result = pairs_trading.analyze_pair(symbol1, symbol2, lookback_days)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in analyze_pair: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scenario/simulate', methods=['POST'])
def simulate_scenario_endpoint():
    """
    Simulate a macro scenario and identify beneficiaries.
    
    Request body:
        {
            "scenario": "FED_CUT_50BP" | "RECESSION_MILD" | "INFLATION_SPIKE" | etc.,
            "symbols": ["AAPL", "MSFT", ...]  // optional additional symbols
        }
    
    Available scenarios:
        - FED_CUT_25BP, FED_CUT_50BP
        - RECESSION_MILD, RECESSION_SEVERE
        - INFLATION_SPIKE
        - DOLLAR_STRENGTH, DOLLAR_WEAKNESS
        - ENERGY_CRISIS
        - TECH_BOOM
        - BANKING_CRISIS
    """
    try:
        data = request.get_json()
        scenario_name = data.get('scenario')
        symbols = data.get('symbols', [])
        
        if not scenario_name:
            available = list_scenarios()
            return jsonify({
                'error': 'Missing required field: scenario',
                'available_scenarios': available
            }), 400
        
        logger.info(f"Simulating scenario: {scenario_name}")
        result = scenario_analysis.simulate_scenario(scenario_name, symbols if symbols else None)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in simulate_scenario: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scenario/analyze-symbol', methods=['POST'])
def analyze_symbol_scenarios_endpoint():
    """
    Analyze how a symbol performs across all scenarios.
    
    Request body:
        {
            "symbol": "AAPL"
        }
    """
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        
        if not symbol:
            return jsonify({'error': 'Missing required field: symbol'}), 400
        
        logger.info(f"Analyzing {symbol} across all scenarios")
        result = scenario_analysis.analyze_all_scenarios(symbol)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in analyze_symbol_scenarios: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info(f"Starting Stock Screener API v{API_VERSION} on port 5008")
    app.run(host='0.0.0.0', port=5008, debug=False)
