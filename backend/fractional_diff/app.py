# app.py - Flask API for Fractional Differentiation Engine
# Port: 5006

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any
import traceback

# Import core modules
from config import Config
from utils import (
    validate_series,
    validate_d,
    fetch_price_data,
    format_stationarity_result,
    calculate_summary_statistics
)
from fractional_diff import (
    fractional_diff_ffd,
    fractional_diff_standard,
    compare_ffd_vs_standard
)
from stationarity_tests import (
    adf_test,
    kpss_test,
    pp_test,
    combined_stationarity_check
)
from optimal_d_finder import (
    find_optimal_d,
    grid_search_d,
    compare_d_values
)
from memory_metrics import (
    calculate_autocorrelation,
    memory_retention_score,
    hurst_exponent,
    compare_memory_metrics
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


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def parse_series_from_request(data: Dict[str, Any]) -> pd.Series:
    """
    Parse time series from request data.

    Accepts:
    - ticker: Fetch from yfinance
    - values: Array of values (with optional index)
    """
    if 'ticker' in data:
        ticker = data['ticker']
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        column = data.get('column', 'Close')

        series = fetch_price_data(ticker, start_date, end_date, column)
        return series

    elif 'values' in data:
        values = data['values']
        index = data.get('index', None)

        if index:
            series = pd.Series(values, index=pd.to_datetime(index))
        else:
            series = pd.Series(values)

        return series

    else:
        raise ValueError("Must provide either 'ticker' or 'values' in request")


def series_to_json(series: pd.Series) -> Dict[str, Any]:
    """Convert pandas Series to JSON-serializable format."""
    return {
        'values': series.values.tolist(),
        'index': series.index.astype(str).tolist() if hasattr(series.index, 'astype') else list(series.index),
        'length': len(series)
    }


def error_response(message: str, status_code: int = 400) -> tuple:
    """Create error response."""
    return jsonify({
        'success': False,
        'error': message
    }), status_code


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'fractional-diff-engine',
        'port': Config.PORT,
        'version': '1.0.0'
    })


@app.route('/api/fracdiff/transform', methods=['POST'])
def transform_endpoint():
    """
    Apply fractional differentiation to a time series.

    Request body:
    {
        "ticker": "SPY",  // OR "values": [...]
        "d": 0.5,
        "method": "ffd",  // "ffd" or "standard"
        "threshold": 1e-5,
        "start_date": "2020-01-01",  // optional
        "end_date": "2023-01-01"     // optional
    }

    Response:
    {
        "success": true,
        "original": {...},
        "transformed": {...},
        "stationarity": {...},
        "memory": {...},
        "config": {...}
    }
    """
    try:
        data = request.get_json()

        if not data:
            return error_response("No data provided")

        # Parse parameters
        d = float(data.get('d', Config.DEFAULT_D))
        method = data.get('method', 'ffd')
        threshold = float(data.get('threshold', Config.DEFAULT_THRESHOLD))

        # Parse series
        series = parse_series_from_request(data)

        logger.info(f"Transform request: d={d}, method={method}, length={len(series)}")

        # Apply transformation
        if method == 'ffd':
            transformed = fractional_diff_ffd(series, d, thres=threshold)
        elif method == 'standard':
            transformed = fractional_diff_standard(series, d)
        else:
            return error_response(f"Unknown method: {method}. Use 'ffd' or 'standard'")

        # Test stationarity on transformed series
        stationarity = combined_stationarity_check(transformed)

        # Calculate memory retention
        memory_score = memory_retention_score(series, transformed, lags=20)

        # Calculate Hurst exponent
        hurst_original = hurst_exponent(series)
        hurst_transformed = hurst_exponent(transformed)

        # Summary statistics
        original_stats = calculate_summary_statistics(series)
        transformed_stats = calculate_summary_statistics(transformed)

        # Response
        response = {
            'success': True,
            'original': {
                'data': series_to_json(series),
                'statistics': original_stats,
                'hurst_exponent': float(hurst_original)
            },
            'transformed': {
                'data': series_to_json(transformed),
                'statistics': transformed_stats,
                'hurst_exponent': float(hurst_transformed)
            },
            'stationarity': format_stationarity_result(stationarity),
            'memory': {
                'retention_score': float(memory_score),
                'interpretation': 'High' if memory_score > 0.7 else 'Medium' if memory_score > 0.4 else 'Low'
            },
            'config': {
                'd': float(d),
                'method': method,
                'threshold': float(threshold)
            }
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Transform error: {str(e)}\n{traceback.format_exc()}")
        return error_response(str(e), 500)


@app.route('/api/fracdiff/find-optimal-d', methods=['POST'])
def find_optimal_d_endpoint():
    """
    Find optimal d value that achieves stationarity with maximum memory retention.

    Request body:
    {
        "ticker": "SPY",  // OR "values": [...]
        "d_range": [0.0, 1.0],
        "step": 0.05,
        "method": "combined",  // "adf", "kpss", "pp", "combined"
        "alpha": 0.05
    }

    Response:
    {
        "success": true,
        "optimal_d": 0.45,
        "memory_retained": 0.73,
        "stationarity_results": [...],
        "recommendation": "...",
        "visualization_data": {...}
    }
    """
    try:
        data = request.get_json()

        if not data:
            return error_response("No data provided")

        # Parse parameters
        d_range = data.get('d_range', [Config.MIN_D, Config.MAX_D])
        step = float(data.get('step', Config.DEFAULT_D_STEP))
        method = data.get('method', 'combined')
        alpha = float(data.get('alpha', Config.DEFAULT_ALPHA))

        # Parse series
        series = parse_series_from_request(data)

        logger.info(f"Find optimal d: range={d_range}, step={step}, method={method}")

        # Find optimal d
        result = find_optimal_d(
            series,
            d_range=tuple(d_range),
            step=step,
            method=method,
            alpha=alpha
        )

        # Create visualization data
        d_values = result['search_path']
        stationarity_results = result['stationarity_results']

        visualization_data = {
            'd_values': d_values,
            'is_stationary': [r['is_stationary'] for r in stationarity_results],
            'p_values': [r['p_value'] for r in stationarity_results],
            'memory_scores': [r['memory_retained'] for r in stationarity_results]
        }

        # Response
        response = {
            'success': True,
            'optimal_d': result['optimal_d'],
            'memory_retained': result['memory_retained'],
            'original_memory': result['original_memory'],
            'stationarity_results': stationarity_results,
            'method': result['method'],
            'alpha': result['alpha'],
            'recommendation': result['recommendation'],
            'visualization_data': visualization_data
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Find optimal d error: {str(e)}\n{traceback.format_exc()}")
        return error_response(str(e), 500)


@app.route('/api/fracdiff/compare', methods=['POST'])
def compare_endpoint():
    """
    Compare multiple d values side-by-side.

    Request body:
    {
        "ticker": "SPY",  // OR "values": [...]
        "d_values": [0.0, 0.3, 0.5, 0.7, 1.0]
    }

    Response:
    {
        "success": true,
        "comparison": [...],
        "summary": {...}
    }
    """
    try:
        data = request.get_json()

        if not data:
            return error_response("No data provided")

        # Parse parameters
        d_values = data.get('d_values', [0.0, 0.3, 0.5, 0.7, 1.0])

        # Parse series
        series = parse_series_from_request(data)

        logger.info(f"Compare d values: {d_values}")

        # Compare d values
        comparison_df = compare_d_values(series, d_values)

        # Create transformed series dict for memory comparison
        transformed_dict = {}
        for d in d_values:
            if d == 0:
                transformed_dict['d=0'] = series
            elif d == 1:
                transformed_dict['d=1'] = series.pct_change().dropna()
            else:
                transformed_dict[f'd={d}'] = fractional_diff_ffd(series, d)

        # Memory comparison
        memory_df = compare_memory_metrics(series, transformed_dict)

        # Merge dataframes
        comparison_df['d_label'] = comparison_df['label']
        memory_df['d_label'] = memory_df['label']

        # Convert to list of dicts
        comparison_list = comparison_df.to_dict('records')
        memory_list = memory_df.to_dict('records')

        # Create summary
        stationary_count = sum(comparison_df['is_stationary'])
        best_memory = comparison_df[comparison_df['is_stationary']].nsmallest(1, 'd') if stationary_count > 0 else None

        summary = {
            'total_tested': len(d_values),
            'stationary_count': int(stationary_count),
            'best_d_for_memory': float(best_memory['d'].iloc[0]) if best_memory is not None and len(best_memory) > 0 else None
        }

        # Response
        response = {
            'success': True,
            'comparison': comparison_list,
            'memory_comparison': memory_list,
            'summary': summary
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Compare error: {str(e)}\n{traceback.format_exc()}")
        return error_response(str(e), 500)


@app.route('/api/fracdiff/batch', methods=['POST'])
def batch_endpoint():
    """
    Transform multiple tickers in batch.

    Request body:
    {
        "tickers": ["SPY", "QQQ", "IWM"],
        "d": 0.5,
        "method": "ffd",
        "start_date": "2020-01-01",
        "end_date": "2023-01-01"
    }

    Response:
    {
        "success": true,
        "results": {
            "SPY": {...},
            "QQQ": {...},
            "IWM": {...}
        },
        "summary": {...}
    }
    """
    try:
        data = request.get_json()

        if not data:
            return error_response("No data provided")

        # Parse parameters
        tickers = data.get('tickers', [])
        d = float(data.get('d', Config.DEFAULT_D))
        method = data.get('method', 'ffd')
        threshold = float(data.get('threshold', Config.DEFAULT_THRESHOLD))
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        column = data.get('column', 'Close')

        if not tickers:
            return error_response("No tickers provided")

        logger.info(f"Batch transform: tickers={tickers}, d={d}, method={method}")

        results = {}
        success_count = 0
        failure_count = 0

        for ticker in tickers:
            try:
                # Fetch data
                series = fetch_price_data(ticker, start_date, end_date, column)

                # Transform
                if method == 'ffd':
                    transformed = fractional_diff_ffd(series, d, thres=threshold)
                elif method == 'standard':
                    transformed = fractional_diff_standard(series, d)
                else:
                    results[ticker] = {
                        'success': False,
                        'error': f"Unknown method: {method}"
                    }
                    failure_count += 1
                    continue

                # Stationarity test
                stationarity = combined_stationarity_check(transformed)

                # Memory retention
                memory_score = memory_retention_score(series, transformed, lags=20)

                results[ticker] = {
                    'success': True,
                    'original_length': len(series),
                    'transformed_length': len(transformed),
                    'is_stationary': stationarity['consensus'] == 'stationary',
                    'stationarity_confidence': stationarity['confidence'],
                    'memory_retained': float(memory_score),
                    'transformed_data': series_to_json(transformed)
                }

                success_count += 1

            except Exception as e:
                logger.error(f"Error processing {ticker}: {str(e)}")
                results[ticker] = {
                    'success': False,
                    'error': str(e)
                }
                failure_count += 1

        # Summary
        summary = {
            'total': len(tickers),
            'success': success_count,
            'failure': failure_count,
            'config': {
                'd': float(d),
                'method': method,
                'threshold': float(threshold)
            }
        }

        # Response
        response = {
            'success': True,
            'results': results,
            'summary': summary
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Batch error: {str(e)}\n{traceback.format_exc()}")
        return error_response(str(e), 500)


@app.route('/api/fracdiff/stationarity-test', methods=['POST'])
def stationarity_test_endpoint():
    """
    Test stationarity of a time series.

    Request body:
    {
        "ticker": "SPY",  // OR "values": [...]
        "test": "combined",  // "adf", "kpss", "pp", "combined"
        "alpha": 0.05
    }

    Response:
    {
        "success": true,
        "test_results": {...},
        "is_stationary": true,
        "conclusion": "..."
    }
    """
    try:
        data = request.get_json()

        if not data:
            return error_response("No data provided")

        # Parse parameters
        test = data.get('test', 'combined')
        alpha = float(data.get('alpha', Config.DEFAULT_ALPHA))

        # Parse series
        series = parse_series_from_request(data)

        logger.info(f"Stationarity test: test={test}, alpha={alpha}")

        # Run test
        if test == 'adf':
            result = adf_test(series, alpha=alpha)
        elif test == 'kpss':
            result = kpss_test(series, alpha=alpha)
        elif test == 'pp':
            result = pp_test(series, alpha=alpha)
        elif test == 'combined':
            result = combined_stationarity_check(series, alpha=alpha)
        else:
            return error_response(f"Unknown test: {test}. Use 'adf', 'kpss', 'pp', or 'combined'")

        # Response
        response = {
            'success': True,
            'test_results': format_stationarity_result(result),
            'is_stationary': result.get('is_stationary', result.get('consensus') == 'stationary'),
            'conclusion': result.get('conclusion', result.get('summary', ''))
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Stationarity test error: {str(e)}\n{traceback.format_exc()}")
        return error_response(str(e), 500)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    logger.info(f"Starting Fractional Differentiation Engine on port {Config.PORT}")
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=True
    )
