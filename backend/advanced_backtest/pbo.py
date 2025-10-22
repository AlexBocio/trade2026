# pbo.py - Probability of Backtest Overfitting calculation
# Implements PBO metric from Bailey et al. (2014)

import numpy as np
import pandas as pd
from scipy.stats import rankdata, pearsonr
from typing import List, Tuple, Dict, Callable
import logging

logger = logging.getLogger(__name__)


def calculate_pbo(in_sample_sharpes: np.ndarray,
                  out_sample_sharpes: np.ndarray,
                  method: str = 'logit') -> dict:
    """
    Calculate Probability of Backtest Overfitting.

    PBO measures the probability that the best-performing in-sample strategy
    will underperform the median out-of-sample strategy. High PBO indicates
    overfitting and lack of robustness.

    Interpretation:
        PBO < 0.5 (50%): Good - Strategy likely robust
        PBO ≈ 0.5 (50%): Neutral - Strategy performance uncertain
        PBO > 0.5 (50%): Bad - Strategy likely overfit
        PBO > 0.7 (70%): Very bad - High probability of overfitting

    Args:
        in_sample_sharpes: Array of in-sample Sharpe ratios from N trials
        out_sample_sharpes: Array of out-of-sample Sharpe ratios (same N trials)
        method: 'logit' (default) or 'frequency'

    Returns:
        {
            'pbo': Probability of backtest overfitting (0 to 1),
            'pbo_percentage': PBO as percentage,
            'is_overfit': Boolean flag (PBO > 0.5),
            'rank_correlation': Spearman correlation of ranks,
            'n_trials': Number of trials,
            'logits': Logit values for each trial (if method='logit'),
            'best_is_sharpe': Best in-sample Sharpe,
            'median_oos_sharpe': Median out-of-sample Sharpe,
            'interpretation': Text interpretation
        }

    Reference:
        Bailey, D.H., Borwein, J., Lopez de Prado, M., & Zhu, Q.J. (2014).
        "The Probability of Backtest Overfitting"
        Journal of Computational Finance
    """
    n = len(in_sample_sharpes)

    if n != len(out_sample_sharpes):
        raise ValueError("in_sample and out_sample must have same length")

    if n < 10:
        raise ValueError("Need at least 10 trials for reliable PBO estimation")

    logger.info(f"Calculating PBO with {n} trials using method='{method}'")

    # Rank strategies by in-sample performance
    ranks_is = rankdata(in_sample_sharpes)
    ranks_oos = rankdata(out_sample_sharpes)

    # Calculate rank correlation
    rank_corr = pearsonr(ranks_is, ranks_oos)[0]

    if method == 'logit':
        # Logit method (more accurate)
        # For each trial, calculate lambda_n = ln(rank_oos / (N+1 - rank_oos))
        logits = np.log(ranks_oos / (n + 1 - ranks_oos))

        # PBO = P(λ_best < 0) where best = highest IS performance
        best_is_idx = np.argmax(in_sample_sharpes)

        # Count how many trials have better OOS rank than the best IS strategy
        w = np.sum(ranks_oos > ranks_oos[best_is_idx]) / n

        pbo = w

    else:  # frequency method
        # Find median OOS Sharpe
        median_oos = np.median(out_sample_sharpes)

        # Find best IS strategy
        best_is_idx = np.argmax(in_sample_sharpes)
        best_is_oos_sharpe = out_sample_sharpes[best_is_idx]

        # PBO = P(best IS strategy < median OOS)
        # More nuanced: use all top quartile IS strategies
        top_quartile_threshold = np.percentile(in_sample_sharpes, 75)
        top_quartile_indices = in_sample_sharpes >= top_quartile_threshold
        top_quartile_oos = out_sample_sharpes[top_quartile_indices]

        # Fraction of top IS strategies that underperform median OOS
        pbo = np.mean(top_quartile_oos < median_oos)

    # Interpretation
    if pbo < 0.3:
        interpretation = "Excellent - Very low probability of overfitting"
    elif pbo < 0.5:
        interpretation = "Good - Strategy appears robust"
    elif pbo < 0.6:
        interpretation = "Marginal - Strategy performance uncertain"
    elif pbo < 0.7:
        interpretation = "Poor - High probability of overfitting"
    else:
        interpretation = "Very Poor - Strategy likely overfit to in-sample data"

    logger.info(f"PBO = {pbo:.2%}, Rank correlation = {rank_corr:.3f}")

    return {
        'pbo': float(pbo),
        'pbo_percentage': float(pbo * 100),
        'is_overfit': bool(pbo > 0.5),
        'rank_correlation': float(rank_corr),
        'n_trials': int(n),
        'logits': logits.tolist() if method == 'logit' else None,
        'best_is_sharpe': float(in_sample_sharpes[best_is_idx]),
        'best_is_oos_sharpe': float(out_sample_sharpes[best_is_idx]),
        'median_oos_sharpe': float(np.median(out_sample_sharpes)),
        'interpretation': interpretation,
        'rank_plot_data': {
            'ranks_is': ranks_is.tolist(),
            'ranks_oos': ranks_oos.tolist(),
            'best_is_idx': int(best_is_idx)
        }
    }


def pbo_from_returns(returns: pd.DataFrame,
                     strategy_func: Callable,
                     param_grid: dict,
                     n_splits: int = 10) -> dict:
    """
    Calculate PBO by running strategy with multiple parameter combinations.

    This is the practical implementation:
    1. Split data into multiple train/test folds (CPCV)
    2. For each parameter combination, calculate IS and OOS Sharpe
    3. Calculate PBO from these results

    Args:
        returns: Returns dataframe or series
        strategy_func: Function that takes (returns, **params) and returns signals
        param_grid: Dict of parameter ranges to test
            Example: {'lookback': [10, 20, 30], 'threshold': [1.5, 2.0, 2.5]}
        n_splits: Number of train/test splits

    Returns:
        PBO results + parameter combination details
    """
    from itertools import product
    from combinatorial_cv import combinatorial_purged_cv

    logger.info(f"Calculating PBO from returns with param_grid={param_grid}")

    # Generate all parameter combinations
    param_names = list(param_grid.keys())
    param_values = list(param_grid.values())
    param_combinations = list(product(*param_values))

    n_params = len(param_combinations)
    logger.info(f"Testing {n_params} parameter combinations")

    # Storage for results
    is_sharpes = np.zeros(n_params)
    oos_sharpes = np.zeros(n_params)
    param_details = []

    # For each parameter combination
    for i, param_tuple in enumerate(param_combinations):
        params = dict(zip(param_names, param_tuple))

        logger.info(f"Testing params {i+1}/{n_params}: {params}")

        # Run CPCV
        cv_results = combinatorial_purged_cv(
            returns,
            strategy_func,
            params,
            n_splits=n_splits
        )

        is_sharpes[i] = cv_results['mean_is_sharpe']
        oos_sharpes[i] = cv_results['mean_oos_sharpe']

        param_details.append({
            'params': params,
            'is_sharpe': float(is_sharpes[i]),
            'oos_sharpe': float(oos_sharpes[i])
        })

    # Calculate PBO
    pbo_results = calculate_pbo(is_sharpes, oos_sharpes)

    # Add parameter details
    pbo_results['parameter_combinations'] = param_details
    pbo_results['best_params'] = param_details[np.argmax(is_sharpes)]['params']
    pbo_results['best_params_oos_sharpe'] = param_details[np.argmax(is_sharpes)]['oos_sharpe']

    return pbo_results


def pbo_test(strategies: List[Callable],
             returns: pd.DataFrame,
             n_splits: int = 10) -> dict:
    """
    Calculate PBO for a list of different strategies.

    Instead of testing parameter combinations of one strategy,
    this tests completely different strategies.

    Args:
        strategies: List of strategy functions
        returns: Returns data
        n_splits: Number of CV splits

    Returns:
        PBO results comparing different strategies
    """
    from combinatorial_cv import combinatorial_purged_cv

    n_strategies = len(strategies)
    logger.info(f"Calculating PBO for {n_strategies} different strategies")

    is_sharpes = np.zeros(n_strategies)
    oos_sharpes = np.zeros(n_strategies)
    strategy_details = []

    for i, strategy_func in enumerate(strategies):
        logger.info(f"Testing strategy {i+1}/{n_strategies}: {strategy_func.__name__}")

        cv_results = combinatorial_purged_cv(
            returns,
            strategy_func,
            {},  # No params
            n_splits=n_splits
        )

        is_sharpes[i] = cv_results['mean_is_sharpe']
        oos_sharpes[i] = cv_results['mean_oos_sharpe']

        strategy_details.append({
            'strategy_name': strategy_func.__name__,
            'is_sharpe': float(is_sharpes[i]),
            'oos_sharpe': float(oos_sharpes[i])
        })

    # Calculate PBO
    pbo_results = calculate_pbo(is_sharpes, oos_sharpes)

    # Add strategy details
    pbo_results['strategies'] = strategy_details
    pbo_results['best_strategy'] = strategy_details[np.argmax(is_sharpes)]['strategy_name']

    return pbo_results
