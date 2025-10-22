# app.py - Flask API for Meta-Labeling System
# Port: 5007

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import logging
import traceback
from datetime import datetime

# Import local modules
from config import Config
from utils import fetch_price_data, series_to_json, dataframe_to_json, calculate_performance_metrics
from primary_models import get_strategy, momentum_strategy, mean_reversion_strategy
from feature_engineering import create_meta_features
from meta_labeler import (
    create_meta_labels,
    train_meta_model,
    apply_meta_sizing,
    predict_meta_probability,
    meta_label_pipeline
)
from backtesting import (
    backtest_with_meta_labeling,
    walk_forward_backtest,
    compare_thresholds
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Store trained models (in-memory for demo)
trained_models = {}


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'meta_labeling',
        'port': Config.PORT,
        'version': '1.0.0'
    })


@app.route('/api/metalabeling/train', methods=['POST'])
def train_meta_model_endpoint():
    """
    Train meta-model on historical data.

    Body:
        {
            "ticker": "SPY",
            "start_date": "2020-01-01",
            "end_date": "2023-01-01",
            "primary_strategy": "momentum",
            "strategy_params": {"fast": 10, "slow": 30},
            "model_type": "random_forest",
            "holding_period": 5
        }

    Returns:
        {
            "model_id": "uuid",
            "train_accuracy": float,
            "test_accuracy": float,
            "precision": float,
            "recall": float,
            "feature_importance": [...]
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        # Parse parameters
        ticker = data.get('ticker')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        primary_strategy_name = data.get('primary_strategy', 'momentum')
        strategy_params = data.get('strategy_params', {})
        model_type = data.get('model_type', 'random_forest')
        holding_period = data.get('holding_period', Config.DEFAULT_HOLDING_PERIOD)

        if not ticker:
            return jsonify({'success': False, 'error': 'ticker is required'}), 400

        logger.info(f"Training meta-model for {ticker}, strategy={primary_strategy_name}")

        # Fetch data
        prices = fetch_price_data(ticker, start_date, end_date)

        # Run complete pipeline
        pipeline_result = meta_label_pipeline(
            prices,
            lambda price: get_strategy(primary_strategy_name, price, **strategy_params),
            holding_period=holding_period,
            model_type=model_type
        )

        # Generate model ID
        model_id = f"{ticker}_{primary_strategy_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Store model
        trained_models[model_id] = {
            'model': pipeline_result['model'],
            'ticker': ticker,
            'strategy': primary_strategy_name,
            'model_type': model_type,
            'trained_at': datetime.now().isoformat()
        }

        # Prepare response
        feature_importance_list = None
        if pipeline_result['feature_importance'] is not None:
            feature_importance_list = pipeline_result['feature_importance'].head(10).to_dict('records')

        response = {
            'success': True,
            'model_id': model_id,
            'train_accuracy': pipeline_result['train_accuracy'],
            'test_accuracy': pipeline_result['test_accuracy'],
            'precision': pipeline_result['precision'],
            'recall': pipeline_result['recall'],
            'feature_importance': feature_importance_list,
            'n_signals': len(pipeline_result['primary_signals']),
            'n_features': len(pipeline_result['features'].columns),
            'ticker': ticker,
            'strategy': primary_strategy_name
        }

        logger.info(f"Model trained successfully: {model_id}, test_acc={pipeline_result['test_accuracy']:.3f}")

        return jsonify(response)

    except Exception as e:
        logger.error(f"Train error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/metalabeling/backtest', methods=['POST'])
def backtest_with_meta_endpoint():
    """
    Backtest strategy with and without meta-labeling.

    Body:
        {
            "ticker": "SPY",
            "start_date": "2020-01-01",
            "end_date": "2023-01-01",
            "primary_strategy": "momentum",
            "strategy_params": {},
            "model_type": "random_forest",
            "threshold": 0.5
        }

    Returns:
        {
            "without_meta": {...},
            "with_meta": {...},
            "improvement": {...}
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        # Parse parameters
        ticker = data.get('ticker')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        primary_strategy_name = data.get('primary_strategy', 'momentum')
        strategy_params = data.get('strategy_params', {})
        model_type = data.get('model_type', 'random_forest')
        threshold = float(data.get('threshold', Config.DEFAULT_CONFIDENCE_THRESHOLD))

        if not ticker:
            return jsonify({'success': False, 'error': 'ticker is required'}), 400

        logger.info(f"Backtesting {ticker}, strategy={primary_strategy_name}, threshold={threshold}")

        # Fetch data
        prices = fetch_price_data(ticker, start_date, end_date)

        # Run pipeline to train model
        pipeline_result = meta_label_pipeline(
            prices,
            lambda price: get_strategy(primary_strategy_name, price, **strategy_params),
            model_type=model_type
        )

        # Backtest
        backtest_result = backtest_with_meta_labeling(
            prices,
            lambda price: get_strategy(primary_strategy_name, price, **strategy_params),
            pipeline_result['model'],
            pipeline_result['features'],
            threshold=threshold
        )

        response = {
            'success': True,
            'without_meta': backtest_result['without_meta'],
            'with_meta': backtest_result['with_meta'],
            'improvement': backtest_result['improvement'],
            'ticker': ticker,
            'strategy': primary_strategy_name,
            'threshold': threshold
        }

        logger.info(f"Backtest complete: Sharpe improvement = {backtest_result['improvement']['sharpe_improvement']:.3f}")

        return jsonify(response)

    except Exception as e:
        logger.error(f"Backtest error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/metalabeling/predict', methods=['POST'])
def predict_meta_label_endpoint():
    """
    Get meta-model prediction for current market conditions.

    Body:
        {
            "model_id": "SPY_momentum_20231201",
            "current_features": {...}
        }

    Returns:
        {
            "primary_signal": 1,
            "meta_probability": 0.75,
            "recommended_size": 0.75,
            "confidence": "high"
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        model_id = data.get('model_id')

        if not model_id or model_id not in trained_models:
            return jsonify({'success': False, 'error': 'model_id not found'}), 404

        # For now, return a placeholder response
        # In production, this would use current market data
        response = {
            'success': True,
            'message': 'Prediction endpoint - requires current market data',
            'model_id': model_id
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Predict error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/metalabeling/walk-forward', methods=['POST'])
def walk_forward_endpoint():
    """
    Run walk-forward backtest.

    Body:
        {
            "ticker": "SPY",
            "primary_strategy": "momentum",
            "train_window": 252,
            "test_window": 63
        }

    Returns:
        Walk-forward backtest results
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        ticker = data.get('ticker')
        primary_strategy_name = data.get('primary_strategy', 'momentum')
        strategy_params = data.get('strategy_params', {})
        train_window = int(data.get('train_window', 252))
        test_window = int(data.get('test_window', 63))

        if not ticker:
            return jsonify({'success': False, 'error': 'ticker is required'}), 400

        logger.info(f"Walk-forward backtest: {ticker}, train={train_window}, test={test_window}")

        # Fetch data
        prices = fetch_price_data(ticker, period='5y')

        # Run walk-forward
        wf_result = walk_forward_backtest(
            prices,
            lambda price: get_strategy(primary_strategy_name, price, **strategy_params),
            train_window=train_window,
            test_window=test_window
        )

        response = {
            'success': True,
            'avg_without_meta': wf_result['avg_without_meta'],
            'avg_with_meta': wf_result['avg_with_meta'],
            'avg_improvement': wf_result['avg_improvement'],
            'n_periods': wf_result['n_periods'],
            'ticker': ticker,
            'strategy': primary_strategy_name
        }

        logger.info(f"Walk-forward complete: {wf_result['n_periods']} periods")

        return jsonify(response)

    except Exception as e:
        logger.error(f"Walk-forward error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/metalabeling/compare-thresholds', methods=['POST'])
def compare_thresholds_endpoint():
    """
    Compare performance at different confidence thresholds.

    Body:
        {
            "ticker": "SPY",
            "primary_strategy": "momentum",
            "thresholds": [0.3, 0.4, 0.5, 0.6, 0.7]
        }

    Returns:
        Performance metrics at each threshold
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        ticker = data.get('ticker')
        primary_strategy_name = data.get('primary_strategy', 'momentum')
        strategy_params = data.get('strategy_params', {})
        thresholds = data.get('thresholds', [0.3, 0.4, 0.5, 0.6, 0.7])

        if not ticker:
            return jsonify({'success': False, 'error': 'ticker is required'}), 400

        logger.info(f"Comparing thresholds for {ticker}")

        # Fetch data
        prices = fetch_price_data(ticker, period='2y')

        # Train model
        pipeline_result = meta_label_pipeline(
            prices,
            lambda price: get_strategy(primary_strategy_name, price, **strategy_params)
        )

        # Compare thresholds
        comparison_df = compare_thresholds(
            prices,
            lambda price: get_strategy(primary_strategy_name, price, **strategy_params),
            pipeline_result['model'],
            pipeline_result['features'],
            thresholds=thresholds
        )

        response = {
            'success': True,
            'comparison': comparison_df.to_dict('records'),
            'best_threshold': float(comparison_df.loc[comparison_df['sharpe_ratio'].idxmax(), 'threshold']),
            'ticker': ticker
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Compare thresholds error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/metalabeling/models', methods=['GET'])
def list_models():
    """List all trained models."""
    models_list = []
    for model_id, info in trained_models.items():
        models_list.append({
            'model_id': model_id,
            'ticker': info['ticker'],
            'strategy': info['strategy'],
            'model_type': info['model_type'],
            'trained_at': info['trained_at']
        })

    return jsonify({
        'success': True,
        'models': models_list,
        'count': len(models_list)
    })


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information."""
    return jsonify({
        'service': 'Trade2025 Meta-Labeling System',
        'version': '1.0.0',
        'port': Config.PORT,
        'endpoints': {
            'train': '/api/metalabeling/train',
            'backtest': '/api/metalabeling/backtest',
            'predict': '/api/metalabeling/predict',
            'walk_forward': '/api/metalabeling/walk-forward',
            'compare_thresholds': '/api/metalabeling/compare-thresholds',
            'list_models': '/api/metalabeling/models',
            'health': '/health'
        }
    })


if __name__ == '__main__':
    logger.info(f"Starting Meta-Labeling System on port {Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
