# covariance_comparison.py - Compare portfolio results with different covariance cleaning methods

import numpy as np
import pandas as pd
from typing import List, Dict
import logging

from covariance_cleaning import detone_covariance, detrend_covariance, detone_and_detrend
from random_matrix_theory import rmt_denoise
from pypfopt import EfficientFrontier, expected_returns

logger = logging.getLogger(__name__)


def optimize_with_covariance(returns: pd.DataFrame,
                             cov_matrix: np.ndarray,
                             method: str = 'max_sharpe',
                             target_return: float = None,
                             risk_free_rate: float = 0.02) -> dict:
    """
    Optimize portfolio using given covariance matrix.

    Args:
        returns: Returns dataframe
        cov_matrix: Covariance matrix to use
        method: 'max_sharpe' or 'efficient_return'
        target_return: Target return (for efficient_return method)
        risk_free_rate: Risk-free rate

    Returns:
        {
            'weights': Portfolio weights,
            'expected_return': Expected annual return,
            'volatility': Expected annual volatility,
            'sharpe_ratio': Sharpe ratio
        }
    """
    # Calculate expected returns
    mu = expected_returns.mean_historical_return(returns)

    # Create EfficientFrontier object
    ef = EfficientFrontier(mu, cov_matrix)

    # Optimize
    if method == 'max_sharpe':
        ef.max_sharpe(risk_free_rate=risk_free_rate)
    elif method == 'efficient_return' and target_return is not None:
        ef.efficient_return(target_return)
    elif method == 'min_volatility':
        ef.min_volatility()
    else:
        ef.max_sharpe(risk_free_rate=risk_free_rate)

    # Get weights and performance
    weights = ef.clean_weights()
    performance = ef.portfolio_performance(verbose=False, risk_free_rate=risk_free_rate)

    # Convert weights dict to array
    weights_array = np.array([weights[ticker] for ticker in returns.columns])

    return {
        'weights': weights,
        'weights_array': weights_array,
        'expected_return': float(performance[0]),
        'volatility': float(performance[1]),
        'sharpe_ratio': float(performance[2])
    }


def compare_covariance_methods(returns: pd.DataFrame,
                               methods: List[str] = ['raw', 'detoned', 'detrended', 'both', 'rmt'],
                               optimization_method: str = 'max_sharpe',
                               risk_free_rate: float = 0.02) -> dict:
    """
    Compare portfolio results using different covariance cleaning methods.

    Args:
        returns: Returns dataframe
        methods: Which methods to compare
        optimization_method: Portfolio optimization method
        risk_free_rate: Risk-free rate

    Returns:
        {
            'covariance_matrices': {...},
            'portfolio_weights': {...},
            'portfolio_metrics': DataFrame,
            'eigenvalue_comparison': DataFrame,
            'condition_numbers': {...}
        }
    """
    logger.info(f"Comparing covariance methods: {methods}")

    results = {
        'covariance_matrices': {},
        'portfolio_weights': {},
        'portfolio_metrics': [],
        'cleaning_diagnostics': {}
    }

    # Raw covariance
    raw_cov = returns.cov().values

    # Process each method
    for method_name in methods:
        try:
            if method_name == 'raw':
                cov_matrix = raw_cov
                diagnostics = {
                    'condition_number': float(np.linalg.cond(raw_cov))
                }

            elif method_name == 'detoned':
                result = detone_covariance(raw_cov, returns, n_components=1)
                cov_matrix = result['detoned_cov']
                diagnostics = {
                    'condition_number': result['condition_number_after'],
                    'variance_removed': result['variance_explained_removed']
                }

            elif method_name == 'detrended':
                result = detrend_covariance(raw_cov, returns)
                cov_matrix = result['detrended_cov']
                diagnostics = {
                    'condition_number': float(np.linalg.cond(cov_matrix)),
                    'autocorr_reduction': result['autocorr_before'] - result['autocorr_after']
                }

            elif method_name == 'both' or method_name == 'detone_detrend':
                result = detone_and_detrend(raw_cov, returns)
                cov_matrix = result['final_cov']
                diagnostics = result['improvement_metrics']

            elif method_name == 'rmt' or method_name == 'rmt_denoised':
                result = rmt_denoise(raw_cov, returns)
                cov_matrix = result['denoised_cov']
                diagnostics = {
                    'condition_number': float(np.linalg.cond(cov_matrix)),
                    'n_signal': result['n_signal_eigenvalues'],
                    'n_noise': result['n_noise_eigenvalues']
                }

            else:
                logger.warning(f"Unknown method: {method_name}, skipping")
                continue

            # Optimize portfolio
            opt_result = optimize_with_covariance(
                returns,
                cov_matrix,
                method=optimization_method,
                risk_free_rate=risk_free_rate
            )

            # Store results
            results['covariance_matrices'][method_name] = cov_matrix
            results['portfolio_weights'][method_name] = opt_result['weights']
            results['cleaning_diagnostics'][method_name] = diagnostics

            # Calculate metrics
            weights_array = opt_result['weights_array']

            results['portfolio_metrics'].append({
                'method': method_name,
                'expected_return': opt_result['expected_return'],
                'volatility': opt_result['volatility'],
                'sharpe_ratio': opt_result['sharpe_ratio'],
                'condition_number': diagnostics.get('condition_number', np.nan),
                'max_weight': float(np.max(weights_array)),
                'min_weight': float(np.min(weights_array)),
                'effective_n': float(1 / np.sum(weights_array**2)),
                'n_non_zero': int(np.sum(weights_array > 1e-4))
            })

        except Exception as e:
            logger.error(f"Error processing method {method_name}: {str(e)}")
            continue

    # Convert metrics to DataFrame
    results['metrics_df'] = pd.DataFrame(results['portfolio_metrics'])

    # Add eigenvalue comparison
    results['eigenvalue_comparison'] = compare_eigenvalues(
        {name: cov for name, cov in results['covariance_matrices'].items()}
    )

    logger.info("Covariance comparison complete")

    return results


def compare_eigenvalues(cov_matrices: Dict[str, np.ndarray]) -> pd.DataFrame:
    """
    Compare eigenvalue spectra of different covariance matrices.

    Args:
        cov_matrices: Dictionary of {method_name: covariance_matrix}

    Returns:
        DataFrame with eigenvalue statistics for each method
    """
    eigenvalue_data = []

    for method_name, cov_matrix in cov_matrices.items():
        # Get eigenvalues
        eigenvalues = np.linalg.eigvalsh(cov_matrix)
        eigenvalues = np.sort(eigenvalues)[::-1]  # Descending order

        # Calculate statistics
        eigenvalue_data.append({
            'method': method_name,
            'max_eigenvalue': float(eigenvalues[0]),
            'min_eigenvalue': float(eigenvalues[-1]),
            'eigenvalue_ratio': float(eigenvalues[0] / eigenvalues[-1]),
            'top_5_sum': float(np.sum(eigenvalues[:5])),
            'total_variance': float(np.sum(eigenvalues)),
            'top_5_pct': float(np.sum(eigenvalues[:5]) / np.sum(eigenvalues)),
            'effective_rank': float(np.sum(eigenvalues)**2 / np.sum(eigenvalues**2))
        })

    return pd.DataFrame(eigenvalue_data)


def backtest_comparison(prices: pd.DataFrame,
                       methods: List[str],
                       rebalance_freq: str = 'M',
                       lookback_days: int = 252) -> dict:
    """
    Backtest portfolios using different covariance methods.

    Args:
        prices: Historical prices
        methods: Covariance methods to compare
        rebalance_freq: Rebalancing frequency ('D', 'W', 'M', 'Q')
        lookback_days: Lookback window for covariance estimation

    Returns:
        {
            'cumulative_returns': DataFrame of cumulative returns for each method,
            'performance_metrics': DataFrame of performance statistics,
            'turnover': DataFrame of turnover for each method
        }
    """
    logger.info(f"Starting backtest comparison with {len(methods)} methods")

    # Resample to rebalancing frequency
    rebalance_dates = prices.resample(rebalance_freq).last().index

    # Initialize results
    portfolio_values = {method: [1.0] for method in methods}
    weights_history = {method: [] for method in methods}

    for i, rebalance_date in enumerate(rebalance_dates[1:], 1):
        # Get lookback window
        lookback_start = prices.index[max(0, prices.index.get_loc(rebalance_date) - lookback_days)]
        lookback_prices = prices.loc[lookback_start:rebalance_date]
        lookback_returns = lookback_prices.pct_change().dropna()

        if len(lookback_returns) < 20:
            continue

        # Compare methods
        try:
            comparison = compare_covariance_methods(
                lookback_returns,
                methods=methods
            )

            # Get next period return
            next_date_idx = rebalance_dates.get_loc(rebalance_date) + 1
            if next_date_idx >= len(rebalance_dates):
                break

            next_date = rebalance_dates[next_date_idx]
            period_returns = prices.loc[rebalance_date:next_date].pct_change().iloc[1:]

            # Calculate portfolio returns for each method
            for method in methods:
                if method in comparison['portfolio_weights']:
                    weights = comparison['portfolio_weights'][method]
                    weights_array = np.array([weights[ticker] for ticker in prices.columns])

                    # Calculate weighted returns
                    period_port_returns = (period_returns * weights_array).sum(axis=1)
                    period_cumret = (1 + period_port_returns).prod()

                    # Update portfolio value
                    portfolio_values[method].append(
                        portfolio_values[method][-1] * period_cumret
                    )

                    weights_history[method].append(weights_array)

        except Exception as e:
            logger.error(f"Error at rebalance date {rebalance_date}: {str(e)}")
            continue

    # Convert to DataFrames
    cumulative_returns_df = pd.DataFrame(portfolio_values)

    # Calculate performance metrics
    performance_metrics = []
    for method in methods:
        returns = pd.Series(portfolio_values[method]).pct_change().dropna()

        if len(returns) > 0:
            total_return = portfolio_values[method][-1] - 1
            annual_return = total_return / (len(returns) / 12)  # Approximate annualization
            annual_vol = returns.std() * np.sqrt(12)
            sharpe = annual_return / annual_vol if annual_vol > 0 else 0

            # Calculate max drawdown
            cumulative = pd.Series(portfolio_values[method])
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()

            performance_metrics.append({
                'method': method,
                'total_return': float(total_return),
                'annual_return': float(annual_return),
                'annual_volatility': float(annual_vol),
                'sharpe_ratio': float(sharpe),
                'max_drawdown': float(max_drawdown),
                'final_value': float(portfolio_values[method][-1])
            })

    performance_df = pd.DataFrame(performance_metrics)

    # Calculate turnover
    turnover_data = []
    for method in methods:
        if len(weights_history[method]) > 1:
            turnovers = []
            for i in range(1, len(weights_history[method])):
                turnover = np.sum(np.abs(
                    weights_history[method][i] - weights_history[method][i-1]
                ))
                turnovers.append(turnover)

            avg_turnover = np.mean(turnovers) if turnovers else 0

            turnover_data.append({
                'method': method,
                'avg_turnover': float(avg_turnover),
                'total_turnover': float(np.sum(turnovers))
            })

    turnover_df = pd.DataFrame(turnover_data)

    return {
        'cumulative_returns': cumulative_returns_df,
        'performance_metrics': performance_df,
        'turnover': turnover_df,
        'rebalance_dates': rebalance_dates.tolist()
    }


def get_best_method(comparison_results: dict, criterion: str = 'sharpe_ratio') -> dict:
    """
    Identify best covariance method based on criterion.

    Args:
        comparison_results: Results from compare_covariance_methods
        criterion: Metric to optimize ('sharpe_ratio', 'volatility', 'effective_n')

    Returns:
        {
            'best_method': Method name,
            'best_value': Best value of criterion,
            'all_values': All values for comparison
        }
    """
    metrics_df = comparison_results['metrics_df']

    if criterion == 'volatility':
        # Lower is better
        best_idx = metrics_df['volatility'].idxmin()
        best_method = metrics_df.loc[best_idx, 'method']
        best_value = metrics_df.loc[best_idx, 'volatility']
    else:
        # Higher is better
        best_idx = metrics_df[criterion].idxmax()
        best_method = metrics_df.loc[best_idx, 'method']
        best_value = metrics_df.loc[best_idx, criterion]

    return {
        'best_method': best_method,
        'best_value': float(best_value),
        'all_values': metrics_df[[' method', criterion]].to_dict('records')
    }
