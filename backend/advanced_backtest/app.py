# app.py - Advanced Backtesting API

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.data_fetcher import fetch_prices

from walk_forward import WalkForwardOptimizer, moving_average_crossover_strategy
from cross_validation import CombinatorialPurgedCV
from robustness import RobustnessAnalyzer
from meta_labeling import MetaLabeler

# PROMPT 29: PBO and Advanced Testing modules
from pbo import calculate_pbo, pbo_from_returns
from combinatorial_cv import combinatorial_purged_cv, calculate_sharpe
from deflated_sharpe import deflated_sharpe_ratio, probabilistic_sharpe_ratio, minimum_track_record_length
from stochastic_dominance import stochastic_dominance_test, compare_strategies

app = Flask(__name__)
CORS(app)

# Cache for data
data_cache = {}


def fetch_price_data(ticker, start_date=None, end_date=None):
    """Fetch price data with caching."""
    cache_key = f"{ticker}_{start_date}_{end_date}"

    if cache_key in data_cache:
        return data_cache[cache_key]

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')

    data = fetch_prices(ticker, start=start_date, end=end_date, progress=False)

    # Convert Series to DataFrame if needed
    if isinstance(data, pd.Series):
        data = data.to_frame(name='Close')

    if data.empty:
        raise ValueError(f"No data found for {ticker}")

    # Calculate returns
    data['returns'] = data['Close'].pct_change()
    data = data.dropna()

    data_cache[cache_key] = data

    return data


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Advanced Backtesting Engine',
        'version': '1.0.0'
    })


@app.route('/api/backtest/walk-forward', methods=['POST'])
def walk_forward_backtest():
    """
    Walk-forward optimization endpoint.

    Request body:
    {
        "ticker": "AAPL",
        "strategy": "ma_crossover",  # Currently only MA crossover supported
        "param_grid": {
            "fast": [10, 20, 30],
            "slow": [50, 100, 150]
        },
        "train_period": 252,
        "test_period": 63,
        "start_date": "2020-01-01",  # Optional
        "end_date": "2023-12-31"     # Optional
    }
    """
    try:
        data = request.json

        ticker = data['ticker']
        param_grid = data['param_grid']
        train_period = data.get('train_period', 252)
        test_period = data.get('test_period', 63)
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Fetch data
        price_data = fetch_price_data(ticker, start_date, end_date)

        # Run walk-forward optimization
        optimizer = WalkForwardOptimizer(
            data=price_data,
            strategy_func=moving_average_crossover_strategy,
            param_grid=param_grid,
            train_period=train_period,
            test_period=test_period
        )

        results = optimizer.run()
        summary = optimizer.get_summary()

        # Format results for JSON
        formatted_results = []
        for r in results:
            formatted_results.append({
                'train_start': str(r['train_start']),
                'train_end': str(r['train_end']),
                'test_start': str(r['test_start']),
                'test_end': str(r['test_end']),
                'optimal_params': r['optimal_params'],
                'train_sharpe': float(r['train_sharpe']),
                'test_sharpe': float(r['test_sharpe']),
                'test_return': float(r['test_return'])
            })

        return jsonify({
            'ticker': ticker,
            'results': formatted_results,
            'summary': {
                'num_windows': summary['num_windows'],
                'avg_test_sharpe': float(summary['avg_test_sharpe']),
                'avg_test_return': float(summary['avg_test_return']),
                'total_return': float(summary['total_return']),
                'total_sharpe': float(summary['total_sharpe']),
                'win_rate': float(summary['win_rate']),
                'parameter_stability': float(summary['parameter_stability'])
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/backtest/cross-validation', methods=['POST'])
def cross_validation_backtest():
    """
    Combinatorial Purged Cross-Validation endpoint.

    Request body:
    {
        "ticker": "AAPL",
        "strategy": "ma_crossover",
        "param_grid": {
            "fast": [10, 20, 30],
            "slow": [50, 100, 150]
        },
        "n_splits": 5,
        "purge_pct": 0.05,
        "embargo_pct": 0.01,
        "start_date": "2020-01-01",  # Optional
        "end_date": "2023-12-31"     # Optional
    }
    """
    try:
        data = request.json

        ticker = data['ticker']
        param_grid = data['param_grid']
        n_splits = data.get('n_splits', 5)
        purge_pct = data.get('purge_pct', 0.05)
        embargo_pct = data.get('embargo_pct', 0.01)
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Fetch data
        price_data = fetch_price_data(ticker, start_date, end_date)

        # Run CPCV
        cv = CombinatorialPurgedCV(
            n_splits=n_splits,
            purge_pct=purge_pct,
            embargo_pct=embargo_pct
        )

        results = cv.evaluate_strategy(
            data=price_data,
            strategy_func=moving_average_crossover_strategy,
            param_grid=param_grid
        )

        return jsonify({
            'ticker': ticker,
            'n_splits': n_splits,
            'mean_sharpe': float(results['mean_sharpe']),
            'std_sharpe': float(results['std_sharpe']),
            'mean_return': float(results['mean_return']),
            'probability_of_skill': float(results['probability_of_skill'])
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/backtest/robustness', methods=['POST'])
def robustness_analysis():
    """
    Strategy robustness analysis endpoint.

    Request body:
    {
        "ticker": "AAPL",
        "strategy": "ma_crossover",
        "params": {"fast": 20, "slow": 50},
        "tests": ["monte_carlo", "param_sensitivity", "regime_change"],
        "param_sensitivity": {
            "param_name": "fast",
            "variations": [10, 15, 20, 25, 30]
        },
        "start_date": "2020-01-01",  # Optional
        "end_date": "2023-12-31"     # Optional
    }
    """
    try:
        data = request.json

        ticker = data['ticker']
        params = data['params']
        tests = data.get('tests', ['monte_carlo', 'regime_change'])
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Fetch data
        price_data = fetch_price_data(ticker, start_date, end_date)

        # Create analyzer
        analyzer = RobustnessAnalyzer(
            data=price_data,
            strategy_func=moving_average_crossover_strategy,
            params=params
        )

        results = {}

        # Monte Carlo simulation
        if 'monte_carlo' in tests:
            mc_results = analyzer.monte_carlo_simulation(n_simulations=500)
            results['monte_carlo'] = {
                'baseline_sharpe': float(mc_results['baseline_sharpe']),
                'mean_random_sharpe': float(mc_results['mean_random_sharpe']),
                'p_value': float(mc_results['p_value']),
                'is_significant': bool(mc_results['is_significant'])
            }

        # Parameter sensitivity
        if 'param_sensitivity' in tests:
            sensitivity_config = data.get('param_sensitivity', {})
            param_name = sensitivity_config.get('param_name', 'fast')
            variations = sensitivity_config.get('variations', [10, 15, 20, 25, 30])

            sens_results = analyzer.parameter_sensitivity(param_name, variations)

            results['parameter_sensitivity'] = {
                'param_name': param_name,
                'results': [
                    {
                        'param_value': float(r['param_value']),
                        'sharpe': float(r['sharpe']),
                        'return': float(r['return'])
                    }
                    for r in sens_results['results']
                ],
                'sensitivity_score': float(sens_results['sensitivity_score']),
                'is_robust': bool(sens_results['is_robust'])
            }

        # Complexity analysis
        if 'complexity' in tests:
            complexity_results = analyzer.kolmogorov_complexity()
            results['complexity'] = {
                'n_parameters': int(complexity_results['n_parameters']),
                'n_rules': int(complexity_results['n_rules']),
                'complexity_score': float(complexity_results['complexity_score']),
                'is_simple': bool(complexity_results['is_simple'])
            }

        # Regime change test
        if 'regime_change' in tests:
            regime_results = analyzer.regime_change_test()
            results['regime_change'] = {
                'pre_regime_sharpe': float(regime_results['pre_regime_sharpe']),
                'post_regime_sharpe': float(regime_results['post_regime_sharpe']),
                'stability_score': float(regime_results['stability_score']),
                'is_stable': bool(regime_results['is_stable'])
            }

        return jsonify({
            'ticker': ticker,
            'params': params,
            'tests_run': tests,
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/backtest/comprehensive', methods=['POST'])
def comprehensive_backtest():
    """
    Comprehensive backtesting suite.

    Runs all tests: walk-forward, CPCV, and robustness analysis.

    Request body:
    {
        "ticker": "AAPL",
        "strategy": "ma_crossover",
        "param_grid": {
            "fast": [10, 20, 30],
            "slow": [50, 100, 150]
        },
        "start_date": "2020-01-01",  # Optional
        "end_date": "2023-12-31"     # Optional
    }
    """
    try:
        data = request.json

        ticker = data['ticker']
        param_grid = data['param_grid']
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        price_data = fetch_price_data(ticker, start_date, end_date)

        # 1. Walk-Forward Optimization
        wf_optimizer = WalkForwardOptimizer(
            data=price_data,
            strategy_func=moving_average_crossover_strategy,
            param_grid=param_grid,
            train_period=252,
            test_period=63
        )
        wf_optimizer.run()
        wf_summary = wf_optimizer.get_summary()

        # Get best params from walk-forward
        best_params = wf_optimizer.optimal_params_history[-1]

        # 2. Cross-Validation
        cv = CombinatorialPurgedCV(n_splits=5)
        cv_results = cv.evaluate_strategy(
            data=price_data,
            strategy_func=moving_average_crossover_strategy,
            param_grid=param_grid
        )

        # 3. Robustness Analysis (using best params)
        analyzer = RobustnessAnalyzer(
            data=price_data,
            strategy_func=moving_average_crossover_strategy,
            params=best_params
        )
        robustness = analyzer.comprehensive_report()

        # Compile comprehensive report
        return jsonify({
            'ticker': ticker,
            'best_params': best_params,
            'walk_forward': {
                'num_windows': wf_summary['num_windows'],
                'total_sharpe': float(wf_summary['total_sharpe']),
                'total_return': float(wf_summary['total_return']),
                'win_rate': float(wf_summary['win_rate']),
                'parameter_stability': float(wf_summary['parameter_stability'])
            },
            'cross_validation': {
                'mean_sharpe': float(cv_results['mean_sharpe']),
                'std_sharpe': float(cv_results['std_sharpe']),
                'probability_of_skill': float(cv_results['probability_of_skill'])
            },
            'robustness': {
                'monte_carlo': {
                    'baseline_sharpe': float(robustness['monte_carlo']['baseline_sharpe']),
                    'p_value': float(robustness['monte_carlo']['p_value']),
                    'is_significant': bool(robustness['monte_carlo']['is_significant'])
                },
                'complexity': {
                    'complexity_score': float(robustness['complexity']['complexity_score']),
                    'is_simple': bool(robustness['complexity']['is_simple'])
                },
                'regime_stability': {
                    'stability_score': float(robustness['regime_stability']['stability_score']),
                    'is_stable': bool(robustness['regime_stability']['is_stable'])
                }
            },
            'recommendation': _generate_recommendation(
                wf_summary, cv_results, robustness
            )
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


def _generate_recommendation(wf_summary, cv_results, robustness):
    """Generate trading recommendation based on all tests."""
    score = 0
    reasons = []

    # Walk-forward performance
    if wf_summary['total_sharpe'] > 1.0:
        score += 2
        reasons.append("Strong walk-forward Sharpe ratio")
    elif wf_summary['total_sharpe'] > 0.5:
        score += 1
        reasons.append("Acceptable walk-forward Sharpe ratio")

    # Parameter stability
    if wf_summary['parameter_stability'] > 0.7:
        score += 1
        reasons.append("Parameters are stable across time")

    # Probability of skill
    if cv_results['probability_of_skill'] > 0.95:
        score += 2
        reasons.append("High probability of genuine skill")
    elif cv_results['probability_of_skill'] > 0.8:
        score += 1
        reasons.append("Moderate probability of skill")

    # Monte Carlo significance
    if robustness['monte_carlo']['is_significant']:
        score += 1
        reasons.append("Statistically significant performance")

    # Complexity
    if robustness['complexity']['is_simple']:
        score += 1
        reasons.append("Strategy is simple and generalizable")

    # Regime stability
    if robustness['regime_stability']['is_stable']:
        score += 1
        reasons.append("Stable across market regimes")

    # Final recommendation
    if score >= 6:
        recommendation = "STRONG BUY"
    elif score >= 4:
        recommendation = "BUY"
    elif score >= 2:
        recommendation = "HOLD"
    else:
        recommendation = "AVOID"

    return {
        'recommendation': recommendation,
        'score': score,
        'max_score': 8,
        'reasons': reasons
    }


# ============================================================================
# PROMPT 29: PBO and Advanced Testing Endpoints
# ============================================================================

# Strategy wrapper for CPCV compatibility
def ma_crossover_strategy_wrapper(returns, **kwargs):
    """Wrapper to adapt moving_average_crossover to **kwargs signature."""
    # Convert returns Series to DataFrame with 'Close' column for compatibility
    if isinstance(returns, pd.Series):
        df = pd.DataFrame({'Close': returns})
    else:
        df = returns
    return moving_average_crossover_strategy(df, kwargs)

@app.route('/api/backtest/pbo', methods=['POST'])
def calculate_pbo_endpoint():
    """
    Calculate Probability of Backtest Overfitting.

    Request body:
    {
        "ticker": "SPY",
        "start_date": "2018-01-01",
        "strategy": "ma_crossover",
        "param_grid": {
            "fast": [5, 10, 15, 20],
            "slow": [20, 30, 40, 50]
        },
        "n_splits": 10
    }

    Returns:
        PBO analysis results including overfitting probability
    """
    try:
        data = request.json

        ticker = data['ticker']
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        param_grid = data['param_grid']
        n_splits = data.get('n_splits', 10)

        # Fetch data
        price_data = fetch_price_data(ticker, start_date, end_date)
        returns = price_data['returns']

        # Calculate PBO
        results = pbo_from_returns(
            returns,
            ma_crossover_strategy_wrapper,
            param_grid,
            n_splits=n_splits
        )

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/backtest/deflated-sharpe', methods=['POST'])
def deflated_sharpe_endpoint():
    """
    Calculate Deflated Sharpe Ratio.

    Request body:
    {
        "observed_sharpe": 1.5,
        "n_trials": 100,
        "n_observations": 1000,
        "skewness": -0.5,
        "kurtosis": 4.0
    }

    Returns:
        DSR analysis correcting for multiple testing
    """
    try:
        data = request.json

        results = deflated_sharpe_ratio(
            observed_sharpe=data['observed_sharpe'],
            n_trials=data['n_trials'],
            n_observations=data['n_observations'],
            skewness=data.get('skewness', 0.0),
            kurtosis=data.get('kurtosis', 3.0),
            benchmark_sharpe=data.get('benchmark_sharpe', 0.0)
        )

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/backtest/probabilistic-sharpe', methods=['POST'])
def probabilistic_sharpe_endpoint():
    """
    Calculate Probabilistic Sharpe Ratio.

    Request body:
    {
        "observed_sharpe": 1.2,
        "n_observations": 1000,
        "benchmark_sharpe": 0.5
    }

    Returns:
        PSR = P(Sharpe > benchmark)
    """
    try:
        data = request.json

        results = probabilistic_sharpe_ratio(
            observed_sharpe=data['observed_sharpe'],
            n_observations=data['n_observations'],
            skewness=data.get('skewness', 0.0),
            kurtosis=data.get('kurtosis', 3.0),
            benchmark_sharpe=data.get('benchmark_sharpe', 0.0)
        )

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/backtest/min-track-record', methods=['POST'])
def minimum_track_record_endpoint():
    """
    Calculate Minimum Track Record Length.

    Request body:
    {
        "observed_sharpe": 1.5,
        "benchmark_sharpe": 0.0,
        "confidence_level": 0.95
    }

    Returns:
        Minimum observations needed for statistical significance
    """
    try:
        data = request.json

        results = minimum_track_record_length(
            observed_sharpe=data['observed_sharpe'],
            benchmark_sharpe=data.get('benchmark_sharpe', 0.0),
            skewness=data.get('skewness', 0.0),
            kurtosis=data.get('kurtosis', 3.0),
            confidence_level=data.get('confidence_level', 0.95)
        )

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/backtest/combinatorial-cv', methods=['POST'])
def combinatorial_cv_endpoint():
    """
    Run Combinatorial Purged Cross-Validation.

    Request body:
    {
        "ticker": "SPY",
        "strategy": "ma_crossover",
        "params": {"fast": 10, "slow": 30},
        "n_splits": 10,
        "embargo_pct": 0.01
    }

    Returns:
        Per-fold IS/OOS Sharpe ratios
    """
    try:
        data = request.json

        ticker = data['ticker']
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        params = data['params']
        n_splits = data.get('n_splits', 10)
        embargo_pct = data.get('embargo_pct', 0.01)

        # Fetch data
        price_data = fetch_price_data(ticker, start_date, end_date)
        returns = price_data['returns']

        results = combinatorial_purged_cv(
            returns,
            ma_crossover_strategy_wrapper,
            params,
            n_splits=n_splits,
            embargo_pct=embargo_pct
        )

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/backtest/stochastic-dominance', methods=['POST'])
def stochastic_dominance_endpoint():
    """
    Test if one strategy stochastically dominates another.

    Request body:
    {
        "ticker": "SPY",
        "strategy_a": "ma_crossover",
        "strategy_b": "ma_crossover",
        "params_a": {"fast": 10, "slow": 30},
        "params_b": {"fast": 20, "slow": 50},
        "order": 2
    }

    Returns:
        Stochastic dominance test results
    """
    try:
        data = request.json

        ticker = data['ticker']
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        params_a = data['params_a']
        params_b = data['params_b']
        order = data.get('order', 2)

        # Fetch data
        price_data = fetch_price_data(ticker, start_date, end_date)
        returns = price_data['returns']

        # Run both strategies
        signals_a = ma_crossover_strategy_wrapper(returns, **params_a)
        signals_b = ma_crossover_strategy_wrapper(returns, **params_b)

        returns_a = (returns * signals_a.shift(1)).dropna().values
        returns_b = (returns * signals_b.shift(1)).dropna().values

        results = stochastic_dominance_test(
            returns_a,
            returns_b,
            order=order
        )

        # Add strategy info
        results['strategy_a'] = {'name': 'ma_crossover', 'params': params_a}
        results['strategy_b'] = {'name': 'ma_crossover', 'params': params_b}

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/backtest/compare-strategies', methods=['POST'])
def compare_strategies_endpoint():
    """
    Comprehensive comparison of two strategies.

    Request body:
    {
        "ticker": "SPY",
        "params_a": {"fast": 10, "slow": 30},
        "params_b": {"fast": 20, "slow": 50}
    }

    Returns:
        Comprehensive comparison including SD tests, KS test, and stats
    """
    try:
        data = request.json

        ticker = data['ticker']
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        params_a = data['params_a']
        params_b = data['params_b']

        # Fetch data
        price_data = fetch_price_data(ticker, start_date, end_date)
        returns = price_data['returns']

        # Run both strategies
        signals_a = ma_crossover_strategy_wrapper(returns, **params_a)
        signals_b = ma_crossover_strategy_wrapper(returns, **params_b)

        returns_a = (returns * signals_a.shift(1)).dropna().values
        returns_b = (returns * signals_b.shift(1)).dropna().values

        results = compare_strategies(
            returns_a,
            returns_b,
            strategy_a_name=f"MA({params_a['fast']}/{params_a['slow']})",
            strategy_b_name=f"MA({params_b['fast']}/{params_b['slow']})"
        )

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    print("Starting Advanced Backtesting Engine...")
    print("Available endpoints:")
    print("  EXISTING:")
    print("  - POST /api/backtest/walk-forward")
    print("  - POST /api/backtest/cross-validation")
    print("  - POST /api/backtest/robustness")
    print("  - POST /api/backtest/comprehensive")
    print("\n  PROMPT 29 (PBO & Advanced Testing):")
    print("  - POST /api/backtest/pbo")
    print("  - POST /api/backtest/deflated-sharpe")
    print("  - POST /api/backtest/probabilistic-sharpe")
    print("  - POST /api/backtest/min-track-record")
    print("  - POST /api/backtest/combinatorial-cv")
    print("  - POST /api/backtest/stochastic-dominance")
    print("  - POST /api/backtest/compare-strategies")
    print("\nServer running on http://localhost:5003\n")

    app.run(host='0.0.0.0', port=5003, debug=True)
