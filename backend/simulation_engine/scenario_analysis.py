# scenario_analysis.py - Historical scenarios and stress tests

import numpy as np
import pandas as pd
from typing import Dict, List
import logging
import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.data_fetcher import fetch_prices
from config import Config
from utils import calculate_metrics, fetch_data

logger = logging.getLogger(__name__)


def replay_historical_scenario(
    portfolio: Dict[str, float],
    scenario_name: str,
    benchmark: str = 'SPY'
) -> Dict:
    """
    Replay historical crisis scenario on portfolio.

    Tests how portfolio would have performed during historical events.

    Args:
        portfolio: Dictionary of {ticker: weight}
        scenario_name: Name of scenario (e.g., '2008_crisis', 'covid_crash')
        benchmark: Benchmark ticker for comparison

    Returns:
        Dictionary with scenario analysis results

    Raises:
        ValueError: If scenario name is invalid
    """
    if scenario_name not in Config.SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario_name}. Available: {list(Config.SCENARIOS.keys())}")

    scenario = Config.SCENARIOS[scenario_name]
    start_date = scenario['start']
    end_date = scenario['end']
    scenario_description = scenario['name']

    logger.info(f"Replaying scenario: {scenario_description}")

    # Fetch data for portfolio assets
    portfolio_returns = None
    asset_returns_dict = {}

    for ticker, weight in portfolio.items():
        try:
            data = fetch_data(ticker, start_date, end_date)
            asset_returns = data['returns']
            asset_returns_dict[ticker] = asset_returns

            if portfolio_returns is None:
                portfolio_returns = weight * asset_returns
            else:
                # Align indices
                common_idx = portfolio_returns.index.intersection(asset_returns.index)
                portfolio_returns = portfolio_returns.loc[common_idx] + weight * asset_returns.loc[common_idx]

        except Exception as e:
            logger.warning(f"Could not fetch data for {ticker}: {str(e)}")
            continue

    if portfolio_returns is None or len(portfolio_returns) == 0:
        raise ValueError("Could not calculate portfolio returns")

    # Fetch benchmark data
    try:
        benchmark_data = fetch_data(benchmark, start_date, end_date)
        benchmark_returns = benchmark_data['returns']

        # Align indices
        common_idx = portfolio_returns.index.intersection(benchmark_returns.index)
        portfolio_returns = portfolio_returns.loc[common_idx]
        benchmark_returns = benchmark_returns.loc[common_idx]
    except Exception as e:
        logger.warning(f"Could not fetch benchmark data: {str(e)}")
        benchmark_returns = None

    # Calculate metrics
    portfolio_metrics = calculate_metrics(portfolio_returns)

    if benchmark_returns is not None:
        benchmark_metrics = calculate_metrics(benchmark_returns)
        relative_performance = {
            'return_diff': portfolio_metrics['total_return'] - benchmark_metrics['total_return'],
            'sharpe_diff': portfolio_metrics['sharpe_ratio'] - benchmark_metrics['sharpe_ratio'],
            'drawdown_diff': portfolio_metrics['max_drawdown'] - benchmark_metrics['max_drawdown']
        }
    else:
        benchmark_metrics = None
        relative_performance = None

    # Asset-level performance
    asset_performance = {}
    for ticker, returns in asset_returns_dict.items():
        aligned_returns = returns.loc[common_idx]
        asset_performance[ticker] = calculate_metrics(aligned_returns)

    logger.info(f"Scenario analysis completed: {scenario_description}")

    return {
        'scenario': scenario_name,
        'scenario_description': scenario_description,
        'period': {'start': start_date, 'end': end_date},
        'portfolio_metrics': portfolio_metrics,
        'benchmark_metrics': benchmark_metrics,
        'relative_performance': relative_performance,
        'asset_performance': asset_performance
    }


def custom_stress_test(
    portfolio: Dict[str, float],
    shocks: Dict[str, float]
) -> Dict:
    """
    Apply custom shocks to portfolio assets.

    Args:
        portfolio: Dictionary of {ticker: weight}
        shocks: Dictionary of {ticker: shock_percentage}
                e.g., {'SPY': -0.20, 'TLT': 0.10}

    Returns:
        Dictionary with stress test results
    """
    logger.info("Running custom stress test")

    # Portfolio value before shock (normalized to 100)
    initial_value = 100.0

    # Calculate post-shock value
    post_shock_value = 0.0
    asset_impacts = {}

    for ticker, weight in portfolio.items():
        shock = shocks.get(ticker, 0)  # Default to 0 if no shock specified

        # Asset value after shock
        asset_initial = initial_value * weight
        asset_final = asset_initial * (1 + shock)
        asset_impact = asset_final - asset_initial

        asset_impacts[ticker] = {
            'weight': weight,
            'shock': shock,
            'initial_value': asset_initial,
            'final_value': asset_final,
            'impact': asset_impact
        }

        post_shock_value += asset_final

    # Portfolio-level impact
    total_impact = post_shock_value - initial_value
    total_return = total_impact / initial_value

    logger.info(f"Stress test completed: {total_return:.2%} impact")

    return {
        'initial_value': initial_value,
        'post_shock_value': post_shock_value,
        'total_impact': total_impact,
        'total_return': total_return,
        'asset_impacts': asset_impacts
    }


def multi_factor_stress(
    portfolio: Dict[str, float],
    factors: List[str] = None,
    factor_shocks: Dict[str, float] = None
) -> Dict:
    """
    Multi-factor stress test.

    Args:
        portfolio: Dictionary of {ticker: weight}
        factors: List of risk factors (e.g., ['interest_rate', 'volatility', 'equity'])
        factor_shocks: Dictionary of {factor: shock_size}

    Returns:
        Dictionary with multi-factor stress results
    """
    if factors is None:
        factors = ['equity', 'interest_rate', 'volatility']

    if factor_shocks is None:
        # Default shocks
        factor_shocks = {
            'equity': -0.10,        # -10% equity shock
            'interest_rate': 0.01,  # +1% rate shock
            'volatility': 0.50      # +50% vol shock
        }

    logger.info(f"Running multi-factor stress test: {factors}")

    # Define factor sensitivities (simplified assumptions)
    # In practice, these would come from a factor model
    factor_sensitivities = {
        'equity': {
            'SPY': 1.0, 'QQQ': 1.2, 'AAPL': 1.3, 'MSFT': 1.1,
            'GOOGL': 1.2, 'AMZN': 1.4, 'TLT': -0.2, 'GLD': 0.3
        },
        'interest_rate': {
            'SPY': -0.3, 'QQQ': -0.2, 'AAPL': -0.1, 'MSFT': -0.1,
            'GOOGL': -0.1, 'AMZN': -0.1, 'TLT': -5.0, 'GLD': 0.5
        },
        'volatility': {
            'SPY': -0.5, 'QQQ': -0.6, 'AAPL': -0.7, 'MSFT': -0.6,
            'GOOGL': -0.7, 'AMZN': -0.8, 'TLT': 0.2, 'GLD': 0.3
        }
    }

    # Calculate impact for each asset
    asset_impacts = {}
    total_impact = 0.0

    for ticker, weight in portfolio.items():
        asset_impact = 0.0

        for factor in factors:
            if factor in factor_sensitivities and ticker in factor_sensitivities[factor]:
                sensitivity = factor_sensitivities[factor][ticker]
                shock = factor_shocks.get(factor, 0)

                factor_impact = sensitivity * shock
                asset_impact += factor_impact

        # Total asset impact weighted by portfolio weight
        weighted_impact = asset_impact * weight
        total_impact += weighted_impact

        asset_impacts[ticker] = {
            'weight': weight,
            'total_impact': asset_impact,
            'weighted_impact': weighted_impact
        }

    logger.info(f"Multi-factor stress completed: {total_impact:.2%} impact")

    return {
        'factors': factors,
        'factor_shocks': factor_shocks,
        'total_impact': total_impact,
        'asset_impacts': asset_impacts
    }


def scenario_comparison(
    portfolio: Dict[str, float],
    scenarios: List[str] = None,
    benchmark: str = 'SPY'
) -> pd.DataFrame:
    """
    Compare portfolio performance across multiple scenarios.

    Args:
        portfolio: Dictionary of {ticker: weight}
        scenarios: List of scenario names (None = all scenarios)
        benchmark: Benchmark ticker

    Returns:
        DataFrame comparing scenarios
    """
    if scenarios is None:
        scenarios = list(Config.SCENARIOS.keys())

    results = []

    for scenario_name in scenarios:
        try:
            result = replay_historical_scenario(portfolio, scenario_name, benchmark)

            portfolio_metrics = result['portfolio_metrics']
            benchmark_metrics = result['benchmark_metrics']
            relative_perf = result['relative_performance']

            results.append({
                'scenario': scenario_name,
                'description': result['scenario_description'],
                'portfolio_return': portfolio_metrics['total_return'],
                'portfolio_sharpe': portfolio_metrics['sharpe_ratio'],
                'portfolio_drawdown': portfolio_metrics['max_drawdown'],
                'benchmark_return': benchmark_metrics['total_return'] if benchmark_metrics else None,
                'benchmark_sharpe': benchmark_metrics['sharpe_ratio'] if benchmark_metrics else None,
                'benchmark_drawdown': benchmark_metrics['max_drawdown'] if benchmark_metrics else None,
                'relative_return': relative_perf['return_diff'] if relative_perf else None,
                'relative_sharpe': relative_perf['sharpe_diff'] if relative_perf else None
            })

        except Exception as e:
            logger.error(f"Error analyzing scenario {scenario_name}: {str(e)}")
            continue

    return pd.DataFrame(results)


def worst_case_scenario(
    portfolio: Dict[str, float],
    lookback_period: str = '10y',
    percentile: float = 0.05
) -> Dict:
    """
    Identify worst-case historical scenario for portfolio.

    Args:
        portfolio: Dictionary of {ticker: weight}
        lookback_period: Historical lookback period (e.g., '5y', '10y')
        percentile: Percentile for worst-case (default: 0.05 for 5th percentile)

    Returns:
        Dictionary with worst-case scenario analysis
    """
    logger.info(f"Calculating worst-case scenario (lookback={lookback_period})")

    # Fetch historical data for portfolio assets
    portfolio_returns = None

    for ticker, weight in portfolio.items():
        try:
            prices = fetch_prices(ticker, period=lookback_period, progress=False)

            # Convert Series to DataFrame if needed
            if isinstance(prices, pd.Series):
                data = prices.to_frame(name='Close')
            else:
                data = prices

            if data.empty:
                continue

            data['returns'] = data['Close'].pct_change()
            asset_returns = data['returns'].dropna()

            if portfolio_returns is None:
                portfolio_returns = weight * asset_returns
            else:
                common_idx = portfolio_returns.index.intersection(asset_returns.index)
                portfolio_returns = portfolio_returns.loc[common_idx] + weight * asset_returns.loc[common_idx]

        except Exception as e:
            logger.warning(f"Could not fetch data for {ticker}: {str(e)}")
            continue

    if portfolio_returns is None or len(portfolio_returns) == 0:
        raise ValueError("Could not calculate portfolio returns")

    # Calculate rolling worst-case
    window_sizes = [1, 5, 21, 63]  # 1 day, 1 week, 1 month, 3 months
    worst_cases = {}

    for window in window_sizes:
        rolling_returns = portfolio_returns.rolling(window).sum()
        worst_return = rolling_returns.quantile(percentile)
        worst_date = rolling_returns.idxmin()

        worst_cases[f'{window}d'] = {
            'worst_return': worst_return,
            'worst_date': str(worst_date),
            'window_days': window
        }

    # Overall statistics
    overall_worst = portfolio_returns.min()
    overall_worst_date = portfolio_returns.idxmin()

    logger.info("Worst-case scenario analysis completed")

    return {
        'lookback_period': lookback_period,
        'percentile': percentile,
        'worst_cases_by_window': worst_cases,
        'overall_worst_return': overall_worst,
        'overall_worst_date': str(overall_worst_date)
    }


def reverse_stress_test(
    portfolio: Dict[str, float],
    loss_threshold: float = -0.20
) -> Dict:
    """
    Reverse stress test: What scenarios would cause a specific loss?

    Args:
        portfolio: Dictionary of {ticker: weight}
        loss_threshold: Target loss level (e.g., -0.20 for -20%)

    Returns:
        Dictionary with scenarios that would cause the target loss
    """
    logger.info(f"Running reverse stress test (threshold={loss_threshold:.1%})")

    scenarios_to_loss = []

    # Test individual asset shocks
    for ticker, weight in portfolio.items():
        # Calculate required shock to reach loss threshold
        # Portfolio loss = weight * shock
        required_shock = loss_threshold / weight if weight != 0 else 0

        scenarios_to_loss.append({
            'scenario': f'{ticker} shock',
            'description': f'{ticker} drops {required_shock:.1%}',
            'asset': ticker,
            'required_shock': required_shock,
            'weight': weight
        })

    # Test market-wide shock
    market_shock = loss_threshold  # All assets drop equally

    scenarios_to_loss.append({
        'scenario': 'Market-wide shock',
        'description': f'All assets drop {market_shock:.1%}',
        'asset': 'All',
        'required_shock': market_shock,
        'weight': 1.0
    })

    logger.info(f"Reverse stress test completed: {len(scenarios_to_loss)} scenarios identified")

    return {
        'loss_threshold': loss_threshold,
        'scenarios': scenarios_to_loss,
        'n_scenarios': len(scenarios_to_loss)
    }
