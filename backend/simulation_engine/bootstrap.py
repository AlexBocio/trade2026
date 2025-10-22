# bootstrap.py - Bootstrap resampling methods

import numpy as np
import pandas as pd
from typing import Callable, Dict, Tuple
import logging
from config import Config
from utils import validate_returns

logger = logging.getLogger(__name__)


def standard_bootstrap(
    returns: pd.Series,
    n_simulations: int = 1000
) -> np.ndarray:
    """
    Standard bootstrap resampling (IID bootstrap).

    Randomly samples returns with replacement. Assumes independence,
    which may not hold for financial time series.

    Args:
        returns: Time series of returns
        n_simulations: Number of bootstrap samples

    Returns:
        Array of shape (n_simulations, len(returns))

    Raises:
        ValueError: If returns is invalid
    """
    returns = validate_returns(returns)
    n = len(returns)

    bootstrap_samples = np.zeros((n_simulations, n))

    for i in range(n_simulations):
        indices = np.random.randint(0, n, size=n)
        bootstrap_samples[i, :] = returns.iloc[indices].values

    logger.info(f"Generated {n_simulations} standard bootstrap samples")
    return bootstrap_samples


def block_bootstrap(
    returns: pd.Series,
    block_size: int = 10,
    n_simulations: int = 1000
) -> np.ndarray:
    """
    Moving block bootstrap (MBB).

    Preserves short-term autocorrelation by sampling consecutive blocks.
    Useful for time series with temporal dependencies.

    Args:
        returns: Time series of returns
        block_size: Size of blocks to resample
        n_simulations: Number of bootstrap samples

    Returns:
        Array of shape (n_simulations, len(returns))

    Raises:
        ValueError: If returns is invalid or block_size is invalid
    """
    returns = validate_returns(returns)
    n = len(returns)

    if block_size < Config.MIN_BLOCK_SIZE or block_size > n:
        raise ValueError(f"block_size must be between {Config.MIN_BLOCK_SIZE} and {n}")

    n_blocks = int(np.ceil(n / block_size))
    bootstrap_samples = np.zeros((n_simulations, n))

    for i in range(n_simulations):
        sample = []

        for _ in range(n_blocks):
            # Random block starting position
            start = np.random.randint(0, n - block_size + 1)
            block = returns.iloc[start:start + block_size].values
            sample.extend(block)

        # Trim to original length
        bootstrap_samples[i, :] = sample[:n]

    logger.info(f"Generated {n_simulations} block bootstrap samples (block_size={block_size})")
    return bootstrap_samples


def circular_block_bootstrap(
    returns: pd.Series,
    block_size: int = 10,
    n_simulations: int = 1000
) -> np.ndarray:
    """
    Circular block bootstrap (CBB).

    Similar to MBB but treats data as circular, allowing blocks to wrap around.
    This increases the number of possible blocks.

    Args:
        returns: Time series of returns
        block_size: Size of blocks to resample
        n_simulations: Number of bootstrap samples

    Returns:
        Array of shape (n_simulations, len(returns))

    Raises:
        ValueError: If returns is invalid or block_size is invalid
    """
    returns = validate_returns(returns)
    n = len(returns)

    if block_size < Config.MIN_BLOCK_SIZE or block_size > n:
        raise ValueError(f"block_size must be between {Config.MIN_BLOCK_SIZE} and {n}")

    # Create circular array
    returns_circular = np.concatenate([returns.values, returns.values[:block_size-1]])

    n_blocks = int(np.ceil(n / block_size))
    bootstrap_samples = np.zeros((n_simulations, n))

    for i in range(n_simulations):
        sample = []

        for _ in range(n_blocks):
            # Random block starting position (can start anywhere due to circularity)
            start = np.random.randint(0, n)
            block = returns_circular[start:start + block_size]
            sample.extend(block)

        # Trim to original length
        bootstrap_samples[i, :] = sample[:n]

    logger.info(f"Generated {n_simulations} circular block bootstrap samples")
    return bootstrap_samples


def stationary_bootstrap(
    returns: pd.Series,
    avg_block_size: int = 10,
    n_simulations: int = 1000
) -> np.ndarray:
    """
    Stationary bootstrap (Politis & Romano, 1994).

    Uses random block lengths with geometric distribution.
    Block lengths vary, preserving stationarity.

    Args:
        returns: Time series of returns
        avg_block_size: Average block size
        n_simulations: Number of bootstrap samples

    Returns:
        Array of shape (n_simulations, len(returns))

    Raises:
        ValueError: If returns is invalid
    """
    returns = validate_returns(returns)
    n = len(returns)

    # Probability of block termination
    p = 1.0 / avg_block_size

    bootstrap_samples = np.zeros((n_simulations, n))

    for i in range(n_simulations):
        sample = []
        idx = 0

        while len(sample) < n:
            # Random starting point
            start = np.random.randint(0, n)

            # Geometric random block length
            block_length = np.random.geometric(p)
            block_length = min(block_length, n - len(sample))

            # Extract block (with wrap-around)
            for j in range(block_length):
                sample.append(returns.iloc[(start + j) % n])

        bootstrap_samples[i, :] = sample[:n]

    logger.info(f"Generated {n_simulations} stationary bootstrap samples")
    return bootstrap_samples


def wild_bootstrap(
    returns: pd.Series,
    n_simulations: int = 1000
) -> np.ndarray:
    """
    Wild bootstrap for heteroskedastic time series.

    Preserves the pattern of heteroskedasticity by multiplying
    residuals by random weights.

    Args:
        returns: Time series of returns
        n_simulations: Number of bootstrap samples

    Returns:
        Array of shape (n_simulations, len(returns))

    Raises:
        ValueError: If returns is invalid
    """
    returns = validate_returns(returns)
    n = len(returns)

    # Estimate conditional mean (simple: rolling mean)
    window = min(20, n // 4)
    conditional_mean = returns.rolling(window, min_periods=1).mean()

    # Residuals
    residuals = returns - conditional_mean

    bootstrap_samples = np.zeros((n_simulations, n))

    for i in range(n_simulations):
        # Rademacher weights: {-1, +1} with equal probability
        weights = np.random.choice([-1, 1], size=n)

        # Wild bootstrap sample
        bootstrap_samples[i, :] = conditional_mean + weights * residuals

    logger.info(f"Generated {n_simulations} wild bootstrap samples")
    return bootstrap_samples


def bootstrap_confidence_interval(
    returns: pd.Series,
    statistic_func: Callable,
    bootstrap_method: str = 'standard',
    alpha: float = 0.05,
    n_simulations: int = 1000,
    **kwargs
) -> Dict[str, float]:
    """
    Calculate bootstrap confidence interval for a statistic.

    Args:
        returns: Time series of returns
        statistic_func: Function to calculate statistic (takes Series, returns float)
        bootstrap_method: Type of bootstrap ('standard', 'block', 'circular', 'stationary', 'wild')
        alpha: Significance level (e.g., 0.05 for 95% CI)
        n_simulations: Number of bootstrap samples
        **kwargs: Additional arguments for bootstrap method (e.g., block_size)

    Returns:
        Dictionary with point estimate, confidence interval, and standard error

    Raises:
        ValueError: If invalid bootstrap method
    """
    # Generate bootstrap samples
    if bootstrap_method == 'standard':
        samples = standard_bootstrap(returns, n_simulations)
    elif bootstrap_method == 'block':
        block_size = kwargs.get('block_size', 10)
        samples = block_bootstrap(returns, block_size, n_simulations)
    elif bootstrap_method == 'circular':
        block_size = kwargs.get('block_size', 10)
        samples = circular_block_bootstrap(returns, block_size, n_simulations)
    elif bootstrap_method == 'stationary':
        avg_block_size = kwargs.get('avg_block_size', 10)
        samples = stationary_bootstrap(returns, avg_block_size, n_simulations)
    elif bootstrap_method == 'wild':
        samples = wild_bootstrap(returns, n_simulations)
    else:
        raise ValueError(f"Unknown bootstrap method: {bootstrap_method}")

    # Calculate statistic for each bootstrap sample
    bootstrap_statistics = np.zeros(n_simulations)

    for i in range(n_simulations):
        sample_series = pd.Series(samples[i, :])
        bootstrap_statistics[i] = statistic_func(sample_series)

    # Point estimate (original data)
    point_estimate = statistic_func(returns)

    # Percentile confidence interval
    lower = np.percentile(bootstrap_statistics, 100 * alpha / 2)
    upper = np.percentile(bootstrap_statistics, 100 * (1 - alpha / 2))

    # Standard error
    standard_error = np.std(bootstrap_statistics)

    return {
        'point_estimate': point_estimate,
        'lower_bound': lower,
        'upper_bound': upper,
        'confidence_level': 1 - alpha,
        'standard_error': standard_error,
        'bootstrap_mean': np.mean(bootstrap_statistics),
        'bootstrap_std': standard_error
    }


def bootstrap_hypothesis_test(
    data1: pd.Series,
    data2: pd.Series,
    statistic_func: Callable,
    n_simulations: int = 1000,
    bootstrap_method: str = 'standard',
    **kwargs
) -> Dict[str, float]:
    """
    Bootstrap hypothesis test for difference in statistics.

    H0: statistic(data1) = statistic(data2)
    H1: statistic(data1) != statistic(data2)

    Args:
        data1: First time series
        data2: Second time series
        statistic_func: Function to calculate statistic
        n_simulations: Number of bootstrap samples
        bootstrap_method: Type of bootstrap
        **kwargs: Additional arguments for bootstrap method

    Returns:
        Dictionary with test statistic, p-value, and conclusion

    Raises:
        ValueError: If data is invalid
    """
    data1 = validate_returns(data1)
    data2 = validate_returns(data2)

    # Observed difference
    stat1 = statistic_func(data1)
    stat2 = statistic_func(data2)
    observed_diff = stat1 - stat2

    # Pooled data under null hypothesis
    pooled = pd.concat([data1, data2])
    n1, n2 = len(data1), len(data2)

    # Bootstrap samples
    bootstrap_diffs = np.zeros(n_simulations)

    for i in range(n_simulations):
        # Resample from pooled data
        if bootstrap_method == 'standard':
            sample = pooled.sample(n=len(pooled), replace=True)
        else:
            # For other methods, use the appropriate bootstrap
            sample_array = standard_bootstrap(pooled, n_simulations=1)[0]
            sample = pd.Series(sample_array)

        # Split into two groups
        sample1 = sample.iloc[:n1]
        sample2 = sample.iloc[n1:n1+n2]

        # Calculate difference
        bootstrap_diffs[i] = statistic_func(sample1) - statistic_func(sample2)

    # P-value (two-tailed)
    p_value = np.mean(np.abs(bootstrap_diffs) >= np.abs(observed_diff))

    return {
        'observed_difference': observed_diff,
        'p_value': p_value,
        'significant_at_0.05': p_value < 0.05,
        'bootstrap_mean_diff': np.mean(bootstrap_diffs),
        'bootstrap_std_diff': np.std(bootstrap_diffs)
    }


def bootstrap_comparison(
    returns: pd.Series,
    statistic_func: Callable,
    methods: list = None,
    n_simulations: int = 1000
) -> pd.DataFrame:
    """
    Compare different bootstrap methods for a statistic.

    Args:
        returns: Time series of returns
        statistic_func: Function to calculate statistic
        methods: List of bootstrap methods to compare (None = all methods)
        n_simulations: Number of bootstrap samples

    Returns:
        DataFrame comparing bootstrap methods
    """
    if methods is None:
        methods = ['standard', 'block', 'circular', 'stationary', 'wild']

    results = []

    for method in methods:
        try:
            ci = bootstrap_confidence_interval(
                returns,
                statistic_func,
                bootstrap_method=method,
                n_simulations=n_simulations
            )

            results.append({
                'method': method,
                'point_estimate': ci['point_estimate'],
                'lower_bound': ci['lower_bound'],
                'upper_bound': ci['upper_bound'],
                'ci_width': ci['upper_bound'] - ci['lower_bound'],
                'standard_error': ci['standard_error']
            })
        except Exception as e:
            logger.error(f"Error in {method} bootstrap: {str(e)}")

    return pd.DataFrame(results)
