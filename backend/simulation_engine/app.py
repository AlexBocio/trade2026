# app.py - Simulation Engine Flask API

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import logging
from config import Config
from utils import fetch_data, validate_simulation_params
import bootstrap
import monte_carlo_advanced
import walk_forward_variants
import scenario_analysis
import synthetic_data
import cross_validation

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': Config.SERVICE_NAME,
        'version': Config.VERSION,
        'port': Config.PORT
    })


@app.route('/api/simulation/bootstrap', methods=['POST'])
def bootstrap_simulation():
    """
    Bootstrap resampling endpoint.

    Request:
    {
        "ticker": "SPY",
        "method": "block",  # standard, block, circular, stationary, wild
        "n_simulations": 1000,
        "block_size": 10  # for block-based methods
    }
    """
    try:
        data = request.json
        ticker = data['ticker']
        method = data.get('method', 'standard')
        n_simulations = data.get('n_simulations', Config.DEFAULT_N_SIMULATIONS)
        block_size = data.get('block_size', Config.DEFAULT_BLOCK_SIZE)

        # Validate params
        params = validate_simulation_params({
            'n_simulations': n_simulations,
            'block_size': block_size
        })

        # Fetch data
        price_data = fetch_data(ticker)
        returns = price_data['returns']

        # Run bootstrap
        if method == 'standard':
            samples = bootstrap.standard_bootstrap(returns, n_simulations)
        elif method == 'block':
            samples = bootstrap.block_bootstrap(returns, block_size, n_simulations)
        elif method == 'circular':
            samples = bootstrap.circular_block_bootstrap(returns, block_size, n_simulations)
        elif method == 'stationary':
            samples = bootstrap.stationary_bootstrap(returns, block_size, n_simulations)
        elif method == 'wild':
            samples = bootstrap.wild_bootstrap(returns, n_simulations)
        else:
            return jsonify({'error': f'Unknown bootstrap method: {method}'}), 400

        # Calculate statistics
        mean_samples = samples.mean(axis=1)
        std_samples = samples.std(axis=1)

        return jsonify({
            'ticker': ticker,
            'method': method,
            'n_simulations': n_simulations,
            'statistics': {
                'mean': {
                    'point_estimate': float(returns.mean()),
                    'bootstrap_mean': float(mean_samples.mean()),
                    'bootstrap_std': float(mean_samples.std()),
                    'ci_lower': float(np.percentile(mean_samples, 2.5)),
                    'ci_upper': float(np.percentile(mean_samples, 97.5))
                },
                'std': {
                    'point_estimate': float(returns.std()),
                    'bootstrap_mean': float(std_samples.mean()),
                    'bootstrap_std': float(std_samples.std()),
                    'ci_lower': float(np.percentile(std_samples, 2.5)),
                    'ci_upper': float(np.percentile(std_samples, 97.5))
                }
            }
        })

    except Exception as e:
        logger.error(f"Error in bootstrap simulation: {str(e)}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/simulation/monte-carlo', methods=['POST'])
def monte_carlo_simulation():
    """
    Advanced Monte Carlo simulation endpoint.

    Request:
    {
        "ticker": "SPY",
        "method": "garch",  # garch, jump_diffusion, regime_switching
        "n_simulations": 1000,
        "forecast_horizon": 252
    }
    """
    try:
        data = request.json
        ticker = data['ticker']
        method = data.get('method', 'garch')
        n_simulations = data.get('n_simulations', Config.DEFAULT_N_SIMULATIONS)
        forecast_horizon = data.get('forecast_horizon')

        # Validate params
        params = validate_simulation_params({'n_simulations': n_simulations})

        # Fetch data
        price_data = fetch_data(ticker)
        returns = price_data['returns']

        # Run simulation
        if method == 'garch':
            result = monte_carlo_advanced.filtered_historical_simulation(
                returns, 'garch', n_simulations, forecast_horizon
            )
        elif method == 'jump_diffusion':
            result = monte_carlo_advanced.jump_diffusion_simulation(
                returns, n_simulations, forecast_horizon
            )
        elif method == 'regime_switching':
            result = monte_carlo_advanced.regime_switching_simulation(
                returns, Config.DEFAULT_N_REGIMES, n_simulations, forecast_horizon
            )
        else:
            return jsonify({'error': f'Unknown Monte Carlo method: {method}'}), 400

        # Convert numpy arrays to lists for JSON serialization
        if 'simulated_paths' in result:
            result['simulated_paths'] = result['simulated_paths'].tolist()
        if 'regime_paths' in result:
            result['regime_paths'] = result['regime_paths'].tolist()

        return jsonify({
            'ticker': ticker,
            'method': method,
            'n_simulations': n_simulations,
            **result
        })

    except Exception as e:
        logger.error(f"Error in Monte Carlo simulation: {str(e)}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/simulation/walk-forward/compare', methods=['POST'])
def compare_walk_forward():
    """
    Compare walk-forward optimization methods.

    Request:
    {
        "ticker": "SPY",
        "strategy_params": {"fast": [10, 20], "slow": [50, 100]},
        "methods": ["anchored", "rolling", "expanding"]
    }
    """
    try:
        data = request.json
        ticker = data['ticker']
        strategy_params = data['strategy_params']
        methods = data.get('methods', ['anchored', 'rolling', 'expanding'])

        # Fetch data
        price_data = fetch_data(ticker)

        # Define simple MA crossover strategy for demo
        def strategy_func(data_df, params):
            fast_ma = data_df['Adj Close'].rolling(params['fast']).mean()
            slow_ma = data_df['Adj Close'].rolling(params['slow']).mean()
            signals = pd.Series(0, index=data_df.index)
            signals[fast_ma > slow_ma] = 1
            signals[fast_ma <= slow_ma] = -1
            return signals

        # Compare methods
        comparison_df = walk_forward_variants.compare_walk_forward_methods(
            price_data, strategy_func, strategy_params, methods
        )

        return jsonify({
            'ticker': ticker,
            'methods_compared': methods,
            'results': comparison_df.to_dict(orient='records')
        })

    except Exception as e:
        logger.error(f"Error in walk-forward comparison: {str(e)}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/simulation/scenario', methods=['POST'])
def scenario_test():
    """
    Historical scenario analysis endpoint.

    Request:
    {
        "portfolio": {"SPY": 0.6, "TLT": 0.4},
        "scenarios": ["2008_crisis", "covid_crash"],
        "benchmark": "SPY"
    }
    """
    try:
        data = request.json
        portfolio = data['portfolio']
        scenarios = data.get('scenarios', ['2008_crisis', 'covid_crash'])
        benchmark = data.get('benchmark', 'SPY')

        # Run scenario comparison
        results_df = scenario_analysis.scenario_comparison(portfolio, scenarios, benchmark)

        return jsonify({
            'portfolio': portfolio,
            'scenarios_tested': scenarios,
            'results': results_df.to_dict(orient='records')
        })

    except Exception as e:
        logger.error(f"Error in scenario analysis: {str(e)}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/simulation/stress-test', methods=['POST'])
def stress_test():
    """
    Custom stress test endpoint.

    Request:
    {
        "portfolio": {"SPY": 0.6, "TLT": 0.4},
        "shocks": {"SPY": -0.20, "TLT": 0.10}
    }
    """
    try:
        data = request.json
        portfolio = data['portfolio']
        shocks = data['shocks']

        # Run stress test
        result = scenario_analysis.custom_stress_test(portfolio, shocks)

        return jsonify({
            'portfolio': portfolio,
            'shocks': shocks,
            **result
        })

    except Exception as e:
        logger.error(f"Error in stress test: {str(e)}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/simulation/synthetic', methods=['POST'])
def generate_synthetic():
    """
    Generate synthetic data endpoint.

    Request:
    {
        "ticker": "SPY",
        "method": "gan",  # gan or vae
        "n_samples": 1000,
        "epochs": 50
    }
    """
    try:
        data = request.json
        ticker = data['ticker']
        method = data.get('method', 'gan')
        n_samples = data.get('n_samples', 1000)
        epochs = data.get('epochs', 50)

        # Fetch data
        price_data = fetch_data(ticker)
        returns = price_data['returns']

        # Generate synthetic data
        if method == 'gan':
            result = synthetic_data.timeseries_gan(returns, n_samples, epochs)
            result['synthetic_data'] = result['synthetic_data'].tolist()

        elif method == 'vae':
            # For VAE, use single asset as DataFrame
            returns_df = pd.DataFrame({ticker: returns})
            result = synthetic_data.vae_market_data(returns_df, n_samples=n_samples, epochs=epochs)
            result['synthetic_data'] = result['synthetic_data'].tolist()

        else:
            return jsonify({'error': f'Unknown synthetic data method: {method}'}), 400

        return jsonify({
            'ticker': ticker,
            'method': method,
            'n_samples': n_samples,
            **result
        })

    except Exception as e:
        logger.error(f"Error in synthetic data generation: {str(e)}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/simulation/cross-validation', methods=['POST'])
def cross_validation_test():
    """
    Advanced cross-validation endpoint.

    Request:
    {
        "ticker": "SPY",
        "strategy_params": {"fast": [10, 20], "slow": [50, 100]},
        "method": "purged_kfold",  # purged_kfold, nested_cv, walk_forward_cv_hybrid
        "n_splits": 5
    }
    """
    try:
        data = request.json
        ticker = data['ticker']
        strategy_params = data['strategy_params']
        method = data.get('method', 'purged_kfold')
        n_splits = data.get('n_splits', 5)

        # Fetch data
        price_data = fetch_data(ticker)

        # Define strategy
        def strategy_func(data_df, params):
            fast_ma = data_df['Adj Close'].rolling(params['fast']).mean()
            slow_ma = data_df['Adj Close'].rolling(params['slow']).mean()
            signals = pd.Series(0, index=data_df.index)
            signals[fast_ma > slow_ma] = 1
            signals[fast_ma <= slow_ma] = -1
            return signals

        # Run cross-validation
        if method == 'purged_kfold':
            result = cross_validation.purged_kfold_cv(
                price_data, strategy_func, strategy_params, n_splits
            )
        elif method == 'nested_cv':
            result = cross_validation.nested_cv(
                price_data, strategy_func, strategy_params, outer_splits=n_splits
            )
        elif method == 'walk_forward_cv_hybrid':
            result = cross_validation.walk_forward_cv_hybrid(
                price_data, strategy_func, strategy_params, n_splits
            )
        else:
            return jsonify({'error': f'Unknown CV method: {method}'}), 400

        return jsonify({
            'ticker': ticker,
            'method': method,
            **result
        })

    except Exception as e:
        logger.error(f"Error in cross-validation: {str(e)}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/simulation/comprehensive', methods=['POST'])
def comprehensive_simulation():
    """
    Comprehensive simulation combining multiple methods.

    Request:
    {
        "ticker": "SPY",
        "include_bootstrap": true,
        "include_monte_carlo": true,
        "include_scenario": false,
        "n_simulations": 1000
    }
    """
    try:
        data = request.json
        ticker = data['ticker']
        include_bootstrap = data.get('include_bootstrap', True)
        include_monte_carlo = data.get('include_monte_carlo', True)
        include_scenario = data.get('include_scenario', False)
        n_simulations = data.get('n_simulations', 1000)

        # Fetch data
        price_data = fetch_data(ticker)
        returns = price_data['returns']

        results = {}

        # Bootstrap
        if include_bootstrap:
            boot_samples = bootstrap.standard_bootstrap(returns, n_simulations)
            mean_samples = boot_samples.mean(axis=1)

            results['bootstrap'] = {
                'mean_ci_lower': float(np.percentile(mean_samples, 2.5)),
                'mean_ci_upper': float(np.percentile(mean_samples, 97.5))
            }

        # Monte Carlo
        if include_monte_carlo:
            mc_result = monte_carlo_advanced.filtered_historical_simulation(
                returns, 'garch', n_simulations, 252
            )
            results['monte_carlo'] = {
                'model_type': mc_result['model_type'],
                'forecast_horizon': mc_result['forecast_horizon'],
                'aic': mc_result['aic'],
                'bic': mc_result['bic']
            }

        # Scenario analysis
        if include_scenario:
            portfolio = {ticker: 1.0}
            scenario_result = scenario_analysis.replay_historical_scenario(
                portfolio, '2008_crisis'
            )
            results['scenario_2008'] = scenario_result['portfolio_metrics']

        return jsonify({
            'ticker': ticker,
            'n_simulations': n_simulations,
            **results
        })

    except Exception as e:
        logger.error(f"Error in comprehensive simulation: {str(e)}")
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    logger.info(f"[START] Starting {Config.SERVICE_NAME} v{Config.VERSION}")
    logger.info(f"[INFO] Available endpoints:")
    logger.info("  - POST /api/simulation/bootstrap")
    logger.info("  - POST /api/simulation/monte-carlo")
    logger.info("  - POST /api/simulation/walk-forward/compare")
    logger.info("  - POST /api/simulation/scenario")
    logger.info("  - POST /api/simulation/stress-test")
    logger.info("  - POST /api/simulation/synthetic")
    logger.info("  - POST /api/simulation/cross-validation")
    logger.info("  - POST /api/simulation/comprehensive")
    logger.info(f"\n[OK] Server running on http://{Config.HOST}:{Config.PORT}\n")

    Config.validate()
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
