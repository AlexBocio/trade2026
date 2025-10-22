# stochastic_dominance.py - Stochastic Dominance tests
# Compare two strategies beyond simple metrics like Sharpe ratio

import numpy as np
import pandas as pd
from typing import Dict
import logging

logger = logging.getLogger(__name__)


def stochastic_dominance_test(returns_a: np.ndarray,
                               returns_b: np.ndarray,
                               order: int = 2) -> dict:
    """
    Test if strategy A stochastically dominates strategy B.

    First-order SD: Strategy A dominates if its CDF is always <= B's CDF
    Second-order SD: Accounts for risk aversion (more practical)

    Args:
        returns_a: Returns of strategy A
        returns_b: Returns of strategy B
        order: 1 (first-order) or 2 (second-order)

    Returns:
        {
            'a_dominates_b': Boolean,
            'b_dominates_a': Boolean,
            'max_violation': Maximum CDF difference,
            'dominance_score': Strength of dominance (0 to 1),
            'order': Order of stochastic dominance tested,
            'interpretation': Text interpretation
        }

    Reference:
        Hadar, J., & Russell, W. R. (1969). "Rules for Ordering Uncertain Prospects"
    """
    logger.info(f"Testing {order}-order stochastic dominance")

    # Remove NaN values
    returns_a = returns_a[~np.isnan(returns_a)]
    returns_b = returns_b[~np.isnan(returns_b)]

    # Sort returns
    sorted_a = np.sort(returns_a)
    sorted_b = np.sort(returns_b)

    # Create common grid
    all_returns = np.concatenate([sorted_a, sorted_b])
    grid = np.unique(all_returns)

    # Empirical CDFs
    cdf_a = np.searchsorted(sorted_a, grid, side='right') / len(sorted_a)
    cdf_b = np.searchsorted(sorted_b, grid, side='right') / len(sorted_b)

    if order == 1:
        # First-order SD: CDF_A <= CDF_B for all x
        # (lower CDF means higher probability of higher returns)
        diff = cdf_a - cdf_b
        a_dominates_b = np.all(diff <= 0)
        b_dominates_a = np.all(diff >= 0)
        max_violation = np.max(np.abs(diff))

    else:  # order == 2
        # Second-order SD: Cumulative sum of CDFs
        # Accounts for risk aversion
        cumsum_cdf_a = np.cumsum(cdf_a)
        cumsum_cdf_b = np.cumsum(cdf_b)

        diff = cumsum_cdf_a - cumsum_cdf_b
        a_dominates_b = np.all(diff <= 0)
        b_dominates_a = np.all(diff >= 0)
        max_violation = np.max(np.abs(diff))

    # Dominance score (0 to 1)
    if a_dominates_b:
        dominance_score = 1.0
    elif b_dominates_a:
        dominance_score = 0.0
    else:
        # Partial dominance: fraction of grid where A <= B
        dominance_score = np.mean(diff <= 0)

    # Interpretation
    if a_dominates_b:
        interpretation = f"Strategy A {order}-order stochastically dominates B"
    elif b_dominates_a:
        interpretation = f"Strategy B {order}-order stochastically dominates A"
    else:
        interpretation = f"No clear {order}-order dominance (A wins {dominance_score*100:.1f}% of the time)"

    logger.info(interpretation)

    return {
        'a_dominates_b': bool(a_dominates_b),
        'b_dominates_a': bool(b_dominates_a),
        'max_violation': float(max_violation),
        'dominance_score': float(dominance_score),
        'order': order,
        'interpretation': interpretation,
        'mean_a': float(np.mean(returns_a)),
        'mean_b': float(np.mean(returns_b)),
        'std_a': float(np.std(returns_a)),
        'std_b': float(np.std(returns_b))
    }


def almost_stochastic_dominance(returns_a: np.ndarray,
                                 returns_b: np.ndarray,
                                 epsilon: float = 0.05,
                                 order: int = 2) -> dict:
    """
    Almost Stochastic Dominance (ASD).

    Allows for small violations of strict stochastic dominance.
    Useful when strategies are very similar.

    Args:
        returns_a: Returns of strategy A
        returns_b: Returns of strategy B
        epsilon: Tolerance for violations (default 0.05 = 5%)
        order: 1 or 2

    Returns:
        Similar to stochastic_dominance_test but with epsilon-relaxed conditions
    """
    # Remove NaN values
    returns_a = returns_a[~np.isnan(returns_a)]
    returns_b = returns_b[~np.isnan(returns_b)]

    # Sort returns
    sorted_a = np.sort(returns_a)
    sorted_b = np.sort(returns_b)

    # Create common grid
    all_returns = np.concatenate([sorted_a, sorted_b])
    grid = np.unique(all_returns)

    # Empirical CDFs
    cdf_a = np.searchsorted(sorted_a, grid, side='right') / len(sorted_a)
    cdf_b = np.searchsorted(sorted_b, grid, side='right') / len(sorted_b)

    if order == 1:
        diff = cdf_a - cdf_b
    else:  # order == 2
        cumsum_cdf_a = np.cumsum(cdf_a)
        cumsum_cdf_b = np.cumsum(cdf_b)
        diff = cumsum_cdf_a - cumsum_cdf_b

    # Check epsilon-dominance
    a_almost_dominates_b = np.all(diff <= epsilon)
    b_almost_dominates_a = np.all(diff >= -epsilon)

    max_violation = np.max(np.abs(diff))

    if a_almost_dominates_b:
        interpretation = f"Strategy A epsilon-dominates B (ε={epsilon})"
    elif b_almost_dominates_a:
        interpretation = f"Strategy B epsilon-dominates A (ε={epsilon})"
    else:
        interpretation = f"No epsilon-dominance (max violation = {max_violation:.3f})"

    return {
        'a_almost_dominates_b': bool(a_almost_dominates_b),
        'b_almost_dominates_a': bool(b_almost_dominates_a),
        'max_violation': float(max_violation),
        'epsilon': float(epsilon),
        'order': order,
        'interpretation': interpretation
    }


def kolmogorov_smirnov_test(returns_a: np.ndarray,
                             returns_b: np.ndarray) -> dict:
    """
    Two-sample Kolmogorov-Smirnov test.

    Tests if two return distributions are significantly different.

    Args:
        returns_a: Returns of strategy A
        returns_b: Returns of strategy B

    Returns:
        {
            'ks_statistic': KS test statistic,
            'p_value': P-value,
            'are_different': Boolean (p < 0.05),
            'interpretation': Text interpretation
        }
    """
    from scipy.stats import ks_2samp

    # Remove NaN values
    returns_a = returns_a[~np.isnan(returns_a)]
    returns_b = returns_b[~np.isnan(returns_b)]

    # Perform KS test
    ks_stat, p_value = ks_2samp(returns_a, returns_b)

    are_different = p_value < 0.05

    if are_different:
        interpretation = f"Distributions are significantly different (p={p_value:.4f})"
    else:
        interpretation = f"Distributions are not significantly different (p={p_value:.4f})"

    return {
        'ks_statistic': float(ks_stat),
        'p_value': float(p_value),
        'are_different': bool(are_different),
        'interpretation': interpretation
    }


def compare_strategies(returns_a: np.ndarray,
                       returns_b: np.ndarray,
                       strategy_a_name: str = "Strategy A",
                       strategy_b_name: str = "Strategy B") -> dict:
    """
    Comprehensive comparison of two strategies.

    Combines stochastic dominance, KS test, and summary statistics.

    Args:
        returns_a: Returns of strategy A
        returns_b: Returns of strategy B
        strategy_a_name: Name of strategy A
        strategy_b_name: Name of strategy B

    Returns:
        Comprehensive comparison results
    """
    # Remove NaN values
    returns_a = returns_a[~np.isnan(returns_a)]
    returns_b = returns_b[~np.isnan(returns_b)]

    # Stochastic dominance tests
    sd1 = stochastic_dominance_test(returns_a, returns_b, order=1)
    sd2 = stochastic_dominance_test(returns_a, returns_b, order=2)

    # KS test
    ks = kolmogorov_smirnov_test(returns_a, returns_b)

    # Summary statistics
    stats_a = {
        'mean': float(np.mean(returns_a)),
        'std': float(np.std(returns_a)),
        'sharpe': float(np.mean(returns_a) / np.std(returns_a) * np.sqrt(252)),
        'skewness': float(pd.Series(returns_a).skew()),
        'kurtosis': float(pd.Series(returns_a).kurtosis())
    }

    stats_b = {
        'mean': float(np.mean(returns_b)),
        'std': float(np.std(returns_b)),
        'sharpe': float(np.mean(returns_b) / np.std(returns_b) * np.sqrt(252)),
        'skewness': float(pd.Series(returns_b).skew()),
        'kurtosis': float(pd.Series(returns_b).kurtosis())
    }

    # Overall recommendation
    if sd2['a_dominates_b']:
        recommendation = f"{strategy_a_name} is clearly superior (2nd-order SD)"
    elif sd2['b_dominates_a']:
        recommendation = f"{strategy_b_name} is clearly superior (2nd-order SD)"
    elif stats_a['sharpe'] > stats_b['sharpe'] * 1.2:
        recommendation = f"{strategy_a_name} is likely better (much higher Sharpe)"
    elif stats_b['sharpe'] > stats_a['sharpe'] * 1.2:
        recommendation = f"{strategy_b_name} is likely better (much higher Sharpe)"
    else:
        recommendation = "Strategies are similar in performance - consider other factors"

    return {
        'strategy_a_name': strategy_a_name,
        'strategy_b_name': strategy_b_name,
        'stats_a': stats_a,
        'stats_b': stats_b,
        'first_order_sd': sd1,
        'second_order_sd': sd2,
        'ks_test': ks,
        'recommendation': recommendation
    }
