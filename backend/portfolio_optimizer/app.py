# app.py - API server for portfolio optimization

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.data_fetcher import fetch_prices
from optimizers import PortfolioOptimizer
from covariance import CovarianceEstimator
from covariance_cleaning import detone_covariance, detrend_covariance, detone_and_detrend
from random_matrix_theory import rmt_denoise
from covariance_comparison import compare_covariance_methods
from eigenvalue_analysis import analyze_eigenvalues, eigenvalue_plot_data, compare_before_after_cleaning

# PROMPT 30: HERC imports
from herc import herc_portfolio, herc_from_prices
from hrp import hrp_portfolio, hrp_from_prices
from herc_vs_hrp import compare_herc_hrp, backtest_comparison, weight_stability_analysis
from risk_contribution import calculate_risk_contribution, calculate_cvar_contribution
from tail_risk_metrics import portfolio_tail_risk_analysis

app = Flask(__name__)
CORS(app)

def fetch_price_data(tickers, period='2y'):
    """Fetch historical price data using unified data fetcher (IBKR + yfinance)."""
    data = fetch_prices(tickers, period=period, progress=False)
    if isinstance(data, pd.Series):
        data = data.to_frame()
    return data

@app.route('/api/optimize/mean-variance', methods=['POST'])
def optimize_mean_variance():
    """
    Mean-Variance Optimization endpoint.

    Body:
    {
        "tickers": ["AAPL", "MSFT", "GOOGL"],
        "target_return": 0.15,  // optional
        "risk_free_rate": 0.02
    }
    """
    try:
        data = request.json
        tickers = data['tickers']
        target_return = data.get('target_return')
        risk_free_rate = data.get('risk_free_rate', 0.02)

        # Fetch data
        prices = fetch_price_data(tickers)

        # Optimize
        optimizer = PortfolioOptimizer(prices)
        result = optimizer.mean_variance(
            target_return=target_return,
            risk_free_rate=risk_free_rate
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/optimize/black-litterman', methods=['POST'])
def optimize_black_litterman():
    """
    Black-Litterman optimization endpoint.

    Body:
    {
        "tickers": ["AAPL", "MSFT"],
        "market_caps": {"AAPL": 3000000000000, "MSFT": 2800000000000},
        "views": {"AAPL": 0.15, "MSFT": 0.12},
        "confidence": {"AAPL": 0.8, "MSFT": 0.6}
    }
    """
    try:
        data = request.json
        tickers = data['tickers']
        market_caps = data['market_caps']
        views = data['views']
        confidence = data['confidence']

        prices = fetch_price_data(tickers)
        optimizer = PortfolioOptimizer(prices)

        result = optimizer.black_litterman(
            market_caps=market_caps,
            views_dict=views,
            confidence_dict=confidence
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/optimize/risk-parity', methods=['POST'])
def optimize_risk_parity():
    """
    Risk Parity optimization endpoint.

    Body:
    {
        "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"]
    }
    """
    try:
        data = request.json
        tickers = data['tickers']

        prices = fetch_price_data(tickers)
        optimizer = PortfolioOptimizer(prices)
        result = optimizer.risk_parity()

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/optimize/hrp', methods=['POST'])
def optimize_hrp():
    """Hierarchical Risk Parity optimization."""
    try:
        data = request.json
        tickers = data['tickers']

        prices = fetch_price_data(tickers)
        optimizer = PortfolioOptimizer(prices)
        result = optimizer.hierarchical_risk_parity()

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/optimize/min-variance', methods=['POST'])
def optimize_min_variance():
    """
    Minimum Variance optimization endpoint.

    Body:
    {
        "tickers": ["AAPL", "MSFT", "GOOGL"]
    }
    """
    try:
        data = request.json
        tickers = data['tickers']

        prices = fetch_price_data(tickers)
        optimizer = PortfolioOptimizer(prices)
        result = optimizer.min_variance()

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/optimize/max-diversification', methods=['POST'])
def optimize_max_diversification():
    """
    Maximum Diversification optimization endpoint.

    Body:
    {
        "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"]
    }
    """
    try:
        data = request.json
        tickers = data['tickers']

        prices = fetch_price_data(tickers)
        optimizer = PortfolioOptimizer(prices)
        result = optimizer.max_diversification()

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/optimize/efficient-frontier', methods=['POST'])
def get_efficient_frontier():
    """
    Get the efficient frontier.

    Body:
    {
        "tickers": ["AAPL", "MSFT", "GOOGL"],
        "n_points": 50
    }
    """
    try:
        data = request.json
        tickers = data['tickers']
        n_points = data.get('n_points', 50)

        prices = fetch_price_data(tickers)
        optimizer = PortfolioOptimizer(prices)
        frontier = optimizer.efficient_frontier(n_points)

        return jsonify({'frontier': frontier})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/optimize/transaction-cost', methods=['POST'])
def optimize_transaction_cost():
    """
    Transaction cost-aware optimization endpoint.

    Body:
    {
        "tickers": ["AAPL", "MSFT", "GOOGL"],
        "current_weights": {"AAPL": 0.4, "MSFT": 0.3, "GOOGL": 0.3},
        "target_weights": {"AAPL": 0.5, "MSFT": 0.3, "GOOGL": 0.2},
        "cost_per_trade": 0.001,
        "min_trade_size": 0.01
    }
    """
    try:
        data = request.json
        tickers = data['tickers']
        current_weights = data['current_weights']
        target_weights = data['target_weights']
        cost_per_trade = data.get('cost_per_trade', 0.001)
        min_trade_size = data.get('min_trade_size', 0.01)

        prices = fetch_price_data(tickers)
        optimizer = PortfolioOptimizer(prices)

        result = optimizer.transaction_cost_optimization(
            current_weights=current_weights,
            target_weights=target_weights,
            cost_per_trade=cost_per_trade,
            min_trade_size=min_trade_size
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/covariance/compare', methods=['POST'])
def compare_covariance():
    """
    Compare covariance estimation methods.

    Body:
    {
        "tickers": ["AAPL", "MSFT", "GOOGL"]
    }
    """
    try:
        data = request.json
        tickers = data['tickers']

        prices = fetch_price_data(tickers)
        returns = prices.pct_change().dropna()

        estimator = CovarianceEstimator(returns)
        comparison = estimator.compare_estimators()

        # Convert numpy arrays to lists for JSON
        result = {
            'condition_numbers': comparison['condition_numbers'],
            'methods': list(comparison['estimators'].keys())
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/covariance/ledoit-wolf', methods=['POST'])
def get_ledoit_wolf():
    """
    Get Ledoit-Wolf covariance estimate.

    Body:
    {
        "tickers": ["AAPL", "MSFT", "GOOGL"]
    }
    """
    try:
        data = request.json
        tickers = data['tickers']

        prices = fetch_price_data(tickers)
        returns = prices.pct_change().dropna()

        estimator = CovarianceEstimator(returns)
        result = estimator.ledoit_wolf()

        # Convert numpy array to list for JSON
        result['covariance'] = result['covariance'].tolist()

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/portfolio/covariance/detone', methods=['POST'])
def detone_covariance_endpoint():
    """
    Detone covariance matrix (remove market component).

    Body:
        {
            "tickers": ["SPY", "QQQ", "IWM"],
            "start_date": "2020-01-01",
            "n_components": 1
        }

    Returns:
        Detoned covariance + diagnostics
    """
    try:
        data = request.json
        tickers = data['tickers']
        n_components = data.get('n_components', 1)

        # Fetch data
        prices = fetch_price_data(tickers)
        returns = prices.pct_change().dropna()

        # Calculate raw covariance
        raw_cov = returns.cov().values

        # Detone
        result = detone_covariance(raw_cov, returns, n_components)

        # Convert numpy arrays to lists for JSON
        result['detoned_cov'] = result['detoned_cov'].tolist()
        if 'removed_eigenvectors' in result:
            del result['removed_eigenvectors']  # Too large for JSON

        return jsonify({
            'success': True,
            'result': result,
            'tickers': tickers,
            'n_assets': len(tickers)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/portfolio/covariance/detrend', methods=['POST'])
def detrend_covariance_endpoint():
    """
    Detrend covariance matrix (remove serial correlation).

    Body:
        {
            "tickers": ["SPY", "QQQ", "IWM"],
            "lookback": 20
        }

    Returns:
        Detrended covariance + AR coefficients
    """
    try:
        data = request.json
        tickers = data['tickers']
        lookback = data.get('lookback', 20)

        # Fetch data
        prices = fetch_price_data(tickers)
        returns = prices.pct_change().dropna()

        # Calculate raw covariance
        raw_cov = returns.cov().values

        # Detrend
        result = detrend_covariance(raw_cov, returns, lookback)

        # Convert numpy arrays to lists for JSON
        result['detrended_cov'] = result['detrended_cov'].tolist()
        if 'detrended_returns' in result:
            del result['detrended_returns']  # Too large for JSON

        return jsonify({
            'success': True,
            'result': result,
            'tickers': tickers
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/portfolio/covariance/clean', methods=['POST'])
def clean_covariance_endpoint():
    """
    Apply full cleaning: detrend + detone + RMT.

    Body:
        {
            "tickers": ["SPY", "QQQ", "IWM"],
            "methods": ["detone", "detrend", "rmt"],
            "n_detone": 1,
            "lookback": 20
        }

    Returns:
        Cleaned covariance + comparison to raw
    """
    try:
        data = request.json
        tickers = data['tickers']
        methods = data.get('methods', ['detone', 'detrend'])
        n_detone = data.get('n_detone', 1)
        lookback = data.get('lookback', 20)

        # Fetch data
        prices = fetch_price_data(tickers)
        returns = prices.pct_change().dropna()

        # Calculate raw covariance
        raw_cov = returns.cov().values

        results = {}

        # Apply requested methods
        if 'both' in methods or ('detone' in methods and 'detrend' in methods):
            result = detone_and_detrend(raw_cov, returns, n_detone, lookback)
            results['detone_detrend'] = {
                'final_cov': result['final_cov'].tolist(),
                'improvement_metrics': result['improvement_metrics']
            }
        elif 'detone' in methods:
            result = detone_covariance(raw_cov, returns, n_detone)
            results['detone'] = {
                'detoned_cov': result['detoned_cov'].tolist(),
                'condition_number_after': result['condition_number_after'],
                'variance_explained_removed': result['variance_explained_removed']
            }
        elif 'detrend' in methods:
            result = detrend_covariance(raw_cov, returns, lookback)
            results['detrend'] = {
                'detrended_cov': result['detrended_cov'].tolist(),
                'autocorr_reduction': result['autocorr_before'] - result['autocorr_after']
            }

        if 'rmt' in methods:
            result = rmt_denoise(raw_cov, returns)
            results['rmt'] = {
                'denoised_cov': result['denoised_cov'].tolist(),
                'n_signal_eigenvalues': result['n_signal_eigenvalues'],
                'n_noise_eigenvalues': result['n_noise_eigenvalues']
            }

        return jsonify({
            'success': True,
            'results': results,
            'tickers': tickers,
            'methods_applied': methods
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/portfolio/covariance/compare', methods=['POST'])
def compare_covariance_endpoint():
    """
    Compare portfolio results with different covariance methods.

    Body:
        {
            "tickers": ["SPY", "QQQ", "IWM"],
            "methods": ["raw", "detoned", "detrended", "both", "rmt"]
        }

    Returns:
        Side-by-side comparison of portfolios built with different covariances
    """
    try:
        data = request.json
        tickers = data['tickers']
        methods = data.get('methods', ['raw', 'detoned', 'detrended', 'both', 'rmt'])

        # Fetch data
        prices = fetch_price_data(tickers)
        returns = prices.pct_change().dropna()

        # Compare methods
        comparison = compare_covariance_methods(returns, methods)

        # Convert DataFrames to dicts for JSON
        response = {
            'success': True,
            'metrics': comparison['metrics_df'].to_dict('records'),
            'eigenvalue_comparison': comparison['eigenvalue_comparison'].to_dict('records'),
            'tickers': tickers,
            'methods': methods
        }

        # Add portfolio weights
        response['portfolio_weights'] = {}
        for method, weights in comparison['portfolio_weights'].items():
            response['portfolio_weights'][method] = weights

        return jsonify(response)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/portfolio/covariance/eigenvalue-analysis', methods=['POST'])
def eigenvalue_analysis_endpoint():
    """
    Analyze eigenvalue spectrum and compare to Marchenko-Pastur.

    Body:
        {
            "tickers": ["SPY", "QQQ", "IWM"],
            "method": "raw"  // "raw", "detoned", "detrended", "rmt"
        }

    Returns:
        {
            'eigenvalues': [...],
            'marchenko_pastur_bound': float,
            'n_signal': int,
            'n_noise': int,
            'eigenvalue_plot_data': {...}
        }
    """
    try:
        data = request.json
        tickers = data['tickers']
        method = data.get('method', 'raw')

        # Fetch data
        prices = fetch_price_data(tickers)
        returns = prices.pct_change().dropna()

        # Calculate covariance based on method
        raw_cov = returns.cov().values

        if method == 'raw':
            cov_matrix = raw_cov
        elif method == 'detoned':
            result = detone_covariance(raw_cov, returns)
            cov_matrix = result['detoned_cov']
        elif method == 'detrended':
            result = detrend_covariance(raw_cov, returns)
            cov_matrix = result['detrended_cov']
        elif method == 'rmt':
            result = rmt_denoise(raw_cov, returns)
            cov_matrix = result['denoised_cov']
        else:
            cov_matrix = raw_cov

        # Analyze eigenvalues
        analysis = analyze_eigenvalues(cov_matrix, returns)

        # Get plot data
        plot_data = eigenvalue_plot_data(cov_matrix, returns)

        # Compare to raw if not raw
        comparison = None
        if method != 'raw':
            comparison = compare_before_after_cleaning(raw_cov, cov_matrix, returns)
            # Simplify for JSON
            comparison = {
                'condition_number_reduction': comparison['improvements']['condition_number_reduction'],
                'effective_rank_change': comparison['improvements']['effective_rank_change']
            }

        return jsonify({
            'success': True,
            'analysis': analysis,
            'plot_data': plot_data,
            'comparison': comparison,
            'tickers': tickers,
            'method': method
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================================================
# PROMPT 30: HERC and HRP Endpoints
# ============================================================================

@app.route('/api/portfolio/herc', methods=['POST'])
def herc_optimization_endpoint():
    """
    Optimize portfolio using Hierarchical Equal Risk Contribution.

    Body:
        {
            "tickers": ["SPY", "QQQ", "IWM", "TLT", "GLD"],
            "start_date": "2020-01-01",
            "risk_measure": "volatility" | "cvar",
            "linkage_method": "single" | "complete" | "average" | "ward"
        }

    Returns:
        {
            "weights": {...},
            "risk_contributions": {...},
            "portfolio_metrics": {...},
            "dendrogram": [...],
            "clusters": {...}
        }
    """
    try:
        data = request.json

        tickers = data['tickers']
        risk_measure = data.get('risk_measure', 'volatility')
        linkage_method = data.get('linkage_method', 'single')

        # Fetch data
        prices = fetch_price_data(tickers, period=data.get('period', '2y'))
        returns = prices.pct_change().dropna()

        # Run HERC
        results = herc_portfolio(
            returns,
            risk_measure=risk_measure,
            linkage_method=linkage_method
        )

        # Format weights as dict
        weights_dict = dict(zip(tickers, results['weights'].tolist()))
        rc_dict = dict(zip(tickers, results['risk_contributions'].tolist()))

        return jsonify({
            'success': True,
            'weights': weights_dict,
            'risk_contributions': rc_dict,
            'portfolio_metrics': results['portfolio_metrics'],
            'clusters': results['clusters'],
            'dendrogram': results['dendrogram'].tolist(),
            'risk_measure': results['risk_measure'],
            'method': 'herc'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/portfolio/hrp', methods=['POST'])
def hrp_optimization_endpoint():
    """
    Optimize portfolio using Hierarchical Risk Parity.

    Body:
        {
            "tickers": ["SPY", "QQQ", "IWM", "TLT", "GLD"],
            "linkage_method": "single"
        }

    Returns:
        HRP portfolio weights and metrics
    """
    try:
        data = request.json

        tickers = data['tickers']
        linkage_method = data.get('linkage_method', 'single')

        # Fetch data
        prices = fetch_price_data(tickers, period=data.get('period', '2y'))
        returns = prices.pct_change().dropna()

        # Run HRP
        results = hrp_portfolio(
            returns,
            linkage_method=linkage_method
        )

        # Format weights as dict
        weights_dict = dict(zip(tickers, results['weights'].tolist()))
        rc_dict = dict(zip(tickers, results['risk_contributions'].tolist()))

        return jsonify({
            'success': True,
            'weights': weights_dict,
            'risk_contributions': rc_dict,
            'portfolio_metrics': results['portfolio_metrics'],
            'clusters': results['clusters'],
            'dendrogram': results['dendrogram'].tolist(),
            'method': 'hrp'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/portfolio/herc-vs-hrp', methods=['POST'])
def compare_herc_hrp_endpoint():
    """
    Compare HERC vs HRP portfolios side-by-side.

    Body:
        {
            "tickers": ["SPY", "QQQ", "IWM", "TLT"],
            "linkage_method": "single",
            "risk_measure": "volatility"
        }

    Returns:
        Comprehensive comparison with recommendations
    """
    try:
        data = request.json

        tickers = data['tickers']
        linkage_method = data.get('linkage_method', 'single')
        risk_measure = data.get('risk_measure', 'volatility')

        # Fetch data
        prices = fetch_price_data(tickers, period=data.get('period', '2y'))
        returns = prices.pct_change().dropna()

        # Run comparison
        results = compare_herc_hrp(
            returns,
            linkage_method=linkage_method,
            risk_measure=risk_measure
        )

        # Format response
        response = {
            'success': True,
            'tickers': results['asset_names'],
            'herc': {
                'weights': dict(zip(results['asset_names'], results['herc']['weights'])),
                'risk_contributions': dict(zip(results['asset_names'], results['herc']['risk_contributions'])),
                'portfolio_metrics': results['herc']['portfolio_metrics'],
                'tail_metrics': results['herc']['tail_metrics']
            },
            'hrp': {
                'weights': dict(zip(results['asset_names'], results['hrp']['weights'])),
                'risk_contributions': dict(zip(results['asset_names'], results['hrp']['risk_contributions'])),
                'portfolio_metrics': results['hrp']['portfolio_metrics'],
                'tail_metrics': results['hrp']['tail_metrics']
            },
            'comparison': results['comparison']
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/portfolio/risk-contribution', methods=['POST'])
def risk_contribution_endpoint():
    """
    Calculate risk contribution for given weights.

    Body:
        {
            "tickers": ["SPY", "QQQ", "IWM"],
            "weights": {"SPY": 0.4, "QQQ": 0.3, "IWM": 0.3}
        }

    Returns:
        Risk contribution breakdown (volatility and CVaR)
    """
    try:
        data = request.json

        tickers = data['tickers']
        weights_dict = data['weights']

        # Convert weights to array
        weights = np.array([weights_dict[t] for t in tickers])

        # Fetch data
        prices = fetch_price_data(tickers, period=data.get('period', '2y'))
        returns = prices.pct_change().dropna()
        cov_matrix = returns.cov().values

        # Calculate risk contributions
        rc = calculate_risk_contribution(weights, cov_matrix)
        cvar_rc = calculate_cvar_contribution(weights, returns)

        return jsonify({
            'success': True,
            'tickers': tickers,
            'marginal_rc': dict(zip(tickers, rc['marginal_rc'].tolist())),
            'percentage_rc': dict(zip(tickers, rc['percentage_rc'].tolist())),
            'portfolio_vol': float(rc['portfolio_vol']),
            'cvar': float(cvar_rc['cvar']),
            'percentage_cvar_contribution': dict(zip(tickers, cvar_rc['percentage_cvar_contribution'].tolist()))
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/portfolio/tail-risk', methods=['POST'])
def tail_risk_endpoint():
    """
    Analyze tail risk for a portfolio.

    Body:
        {
            "tickers": ["SPY", "QQQ"],
            "weights": {"SPY": 0.6, "QQQ": 0.4}
        }

    Returns:
        Comprehensive tail risk metrics
    """
    try:
        data = request.json

        tickers = data['tickers']
        weights_dict = data['weights']

        # Convert weights to array
        weights = np.array([weights_dict[t] for t in tickers])

        # Fetch data
        prices = fetch_price_data(tickers, period=data.get('period', '2y'))
        returns = prices.pct_change().dropna()

        # Analyze tail risk
        tail_metrics = portfolio_tail_risk_analysis(weights, returns)

        return jsonify({
            'success': True,
            'tickers': tickers,
            'tail_metrics': tail_metrics
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'portfolio-optimizer',
        'port': 5001
    })

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information."""
    return jsonify({
        'service': 'Trade2025 Portfolio Optimizer',
        'version': '1.2.0',
        'endpoints': {
            'optimization': {
                'mean_variance': '/api/optimize/mean-variance',
                'black_litterman': '/api/optimize/black-litterman',
                'risk_parity': '/api/optimize/risk-parity',
                'hrp': '/api/optimize/hrp',
                'min_variance': '/api/optimize/min-variance',
                'max_diversification': '/api/optimize/max-diversification',
                'efficient_frontier': '/api/optimize/efficient-frontier',
                'transaction_cost': '/api/optimize/transaction-cost'
            },
            'hierarchical_methods_prompt_30': {
                'herc': '/api/portfolio/herc',
                'hrp_new': '/api/portfolio/hrp',
                'herc_vs_hrp': '/api/portfolio/herc-vs-hrp',
                'risk_contribution': '/api/portfolio/risk-contribution',
                'tail_risk': '/api/portfolio/tail-risk'
            },
            'covariance': {
                'compare': '/api/covariance/compare',
                'ledoit_wolf': '/api/covariance/ledoit-wolf'
            },
            'covariance_cleaning': {
                'detone': '/api/portfolio/covariance/detone',
                'detrend': '/api/portfolio/covariance/detrend',
                'clean': '/api/portfolio/covariance/clean',
                'compare_methods': '/api/portfolio/covariance/compare',
                'eigenvalue_analysis': '/api/portfolio/covariance/eigenvalue-analysis'
            },
            'system': {
                'health': '/health'
            }
        }
    })

if __name__ == '__main__':
    print("Starting Trade2025 Portfolio Optimizer v1.2.0")
    print("Server running on http://localhost:5001")
    print("")
    print("EXISTING Endpoints:")
    print("  - Mean-Variance, Black-Litterman, Risk Parity")
    print("  - Covariance Cleaning (Detone, Detrend, RMT)")
    print("")
    print("PROMPT 30 (NEW) Endpoints:")
    print("  - POST /api/portfolio/herc - Hierarchical Equal Risk Contribution")
    print("  - POST /api/portfolio/hrp - Hierarchical Risk Parity")
    print("  - POST /api/portfolio/herc-vs-hrp - Compare HERC vs HRP")
    print("  - POST /api/portfolio/risk-contribution - Risk contribution analysis")
    print("  - POST /api/portfolio/tail-risk - Tail risk metrics")
    print("")
    print("Ready!")
    app.run(host='0.0.0.0', port=5000, debug=True)
