# optimal_d_finder.py - Find optimal differentiation order d

import numpy as np
import pandas as pd
import logging
from typing import Dict, List
from utils import validate_series
from config import Config
from fractional_diff import fractional_diff_ffd
from stationarity_tests import adf_test, kpss_test, pp_test, combined_stationarity_check
from memory_metrics import memory_retention_score, calculate_autocorrelation

logger = logging.getLogger(__name__)


def find_optimal_d(
    series: pd.Series,
    d_range: tuple = None,
    step: float = None,
    method: str = 'adf',
    alpha: float = None
) -> Dict:
    """
    Find minimum d that achieves stationarity.

    Goal: Find the smallest d value where series becomes stationary.
    Smaller d = more memory retention.

    Args:
        series: Price time series
        d_range: Range to search (min_d, max_d). Default: (0.0, 1.0)
        step: Grid search step size. Default: from config
        method: Stationarity test method:
            'adf': Augmented Dickey-Fuller
            'kpss': Kwiatkowski-Phillips-Schmidt-Shin
            'pp': Phillips-Perron
            'combined': All three tests (consensus)
        alpha: Significance level for stationarity tests

    Returns:
        Dictionary with:
            {
                'optimal_d': float,  # Minimum d that achieves stationarity
                'stationarity_results': [...],  # Results for each d tested
                'memory_retained': float,  # Autocorrelation at optimal d
                'original_memory': float,  # Autocorrelation at d=0
                'search_path': [...],  # All d values tested
                'recommendation': str  # Human-readable recommendation
            }

    Example:
        >>> import yfinance as yf
        >>> price = yf.download('SPY')['Close']
        >>> result = find_optimal_d(price, method='combined')
        >>> print(f"Optimal d: {result['optimal_d']}")
        >>> print(f"Memory retained: {result['memory_retained']:.1%}")
    """
    series = validate_series(series)

    if d_range is None:
        d_range = (Config.MIN_D, Config.MAX_D)

    if step is None:
        step = Config.DEFAULT_D_STEP

    if alpha is None:
        alpha = Config.DEFAULT_ALPHA

    # Generate d values to test
    d_values = np.arange(d_range[0], d_range[1] + step, step)

    logger.info(f"Searching for optimal d in range {d_range} with step {step} "
                f"using {method} test")

    # Store results for each d
    search_results = []
    optimal_d = None

    # Original series memory (for comparison)
    original_memory = calculate_autocorrelation(series, lags=1)[0]

    for d in d_values:
        # Apply fractional differentiation
        if d == 0:
            transformed = series
        else:
            try:
                transformed = fractional_diff_ffd(series, d)
            except Exception as e:
                logger.warning(f"Failed to transform at d={d}: {str(e)}")
                continue

        # Test stationarity
        try:
            if method == 'adf':
                test_result = adf_test(transformed, alpha=alpha)
                is_stationary = test_result['is_stationary']
                p_value = test_result['p_value']

            elif method == 'kpss':
                test_result = kpss_test(transformed, alpha=alpha)
                is_stationary = test_result['is_stationary']
                p_value = test_result['p_value']

            elif method == 'pp':
                test_result = pp_test(transformed, alpha=alpha)
                is_stationary = test_result['is_stationary']
                p_value = test_result['p_value']

            elif method == 'combined':
                test_result = combined_stationarity_check(transformed, alpha=alpha)
                is_stationary = test_result['consensus'] == 'stationary'
                # Use ADF p-value for reporting
                p_value = test_result['adf']['p_value']

            else:
                raise ValueError(f"Unknown test method: {method}")

            # Calculate memory retention
            if len(transformed) > 0:
                memory_score = memory_retention_score(series, transformed, lags=20)
            else:
                memory_score = 0.0

            search_results.append({
                'd': float(d),
                'is_stationary': is_stationary,
                'p_value': float(p_value),
                'memory_retained': float(memory_score),
                'series_length': len(transformed)
            })

            # Check if this is the first stationary result
            if is_stationary and optimal_d is None:
                optimal_d = d
                logger.info(f"Found optimal d={optimal_d} (first stationary point)")

        except Exception as e:
            logger.warning(f"Test failed at d={d}: {str(e)}")
            continue

    # If no stationary point found, use d=1.0 (returns)
    if optimal_d is None:
        logger.warning("No stationary point found in search range, using d=1.0")
        optimal_d = 1.0

    # Get memory retention at optimal d
    optimal_result = next((r for r in search_results if r['d'] == optimal_d), None)

    if optimal_result:
        memory_retained = optimal_result['memory_retained']
    else:
        memory_retained = 0.0

    # Create recommendation
    if optimal_d == 0:
        recommendation = "Series is already stationary (d=0). No fractional differentiation needed."
    elif optimal_d == 1.0:
        recommendation = f"Use standard returns (d=1.0). Series requires full differentiation for stationarity."
    else:
        recommendation = (
            f"Use d={optimal_d:.2f} for stationarity with {memory_retained:.1%} memory retention. "
            f"This balances stationarity and predictive power."
        )

    result = {
        'optimal_d': float(optimal_d),
        'stationarity_results': search_results,
        'memory_retained': float(memory_retained),
        'original_memory': float(original_memory),
        'search_path': d_values.tolist(),
        'method': method,
        'alpha': alpha,
        'recommendation': recommendation
    }

    logger.info(f"Optimal d search complete: d={optimal_d:.2f}, "
                f"memory={memory_retained:.1%}")

    return result


def grid_search_d(
    series: pd.Series,
    d_values: List[float],
    objective: str = 'min_stationary',
    alpha: float = None
) -> Dict:
    """
    Test multiple d values and compare based on objective.

    Objectives:
        'min_stationary': Minimum d that achieves stationarity (max memory)
        'max_memory': Maximum memory retention while stationary
        'balanced': Balance between stationarity strength and memory

    Args:
        series: Price time series
        d_values: List of specific d values to test
        objective: Optimization objective
        alpha: Significance level

    Returns:
        Dictionary with results and best d value
    """
    series = validate_series(series)

    if alpha is None:
        alpha = Config.DEFAULT_ALPHA

    logger.info(f"Grid search with objective: {objective}")

    results = []

    for d in d_values:
        # Transform series
        if d == 0:
            transformed = series
        else:
            try:
                transformed = fractional_diff_ffd(series, d)
            except Exception as e:
                logger.warning(f"Failed at d={d}: {str(e)}")
                continue

        # Test stationarity (using combined for robustness)
        try:
            stationarity_result = combined_stationarity_check(transformed, alpha=alpha)
            is_stationary = stationarity_result['consensus'] == 'stationary'
            confidence = stationarity_result['confidence']

            # Memory retention
            memory_score = memory_retention_score(series, transformed, lags=20)

            # ADF p-value (lower is more stationary)
            adf_p = stationarity_result['adf']['p_value']

            results.append({
                'd': float(d),
                'is_stationary': is_stationary,
                'confidence': confidence,
                'adf_p_value': float(adf_p),
                'memory_retained': float(memory_score),
                'series_length': len(transformed)
            })

        except Exception as e:
            logger.warning(f"Test failed at d={d}: {str(e)}")
            continue

    if not results:
        raise ValueError("No valid results from grid search")

    # Find best d based on objective
    if objective == 'min_stationary':
        # Minimum d that achieves stationarity
        stationary_results = [r for r in results if r['is_stationary']]
        if stationary_results:
            best_result = min(stationary_results, key=lambda x: x['d'])
        else:
            # If none stationary, use one with lowest p-value
            best_result = min(results, key=lambda x: x['adf_p_value'])

    elif objective == 'max_memory':
        # Maximum memory while stationary
        stationary_results = [r for r in results if r['is_stationary']]
        if stationary_results:
            best_result = max(stationary_results, key=lambda x: x['memory_retained'])
        else:
            # If none stationary, use maximum memory
            best_result = max(results, key=lambda x: x['memory_retained'])

    elif objective == 'balanced':
        # Balance stationarity and memory
        # Score = memory_retained if stationary, else 0
        for r in results:
            if r['is_stationary']:
                r['score'] = r['memory_retained']
            else:
                # Penalize non-stationary
                r['score'] = r['memory_retained'] * 0.5

        best_result = max(results, key=lambda x: x['score'])

    else:
        raise ValueError(f"Unknown objective: {objective}")

    return {
        'best_d': best_result['d'],
        'best_result': best_result,
        'all_results': results,
        'objective': objective,
        'n_tested': len(results),
        'n_stationary': sum(r['is_stationary'] for r in results)
    }


def compare_d_values(
    series: pd.Series,
    d_values: List[float] = None
) -> pd.DataFrame:
    """
    Compare multiple d values side-by-side.

    Creates a comprehensive comparison table.

    Args:
        series: Price time series
        d_values: List of d values to compare (default: [0.0, 0.3, 0.5, 0.7, 1.0])

    Returns:
        DataFrame with comparison metrics
    """
    series = validate_series(series)

    if d_values is None:
        d_values = [0.0, 0.3, 0.5, 0.7, 1.0]

    comparison_data = []

    for d in d_values:
        # Transform
        if d == 0:
            transformed = series
            label = "Original (d=0)"
        elif d == 1:
            transformed = series.pct_change().dropna()
            label = "Returns (d=1)"
        else:
            transformed = fractional_diff_ffd(series, d)
            label = f"d={d}"

        # Stationarity
        stationarity = combined_stationarity_check(transformed)

        # Memory
        memory_score = memory_retention_score(series, transformed, lags=20)

        # Statistics
        comparison_data.append({
            'label': label,
            'd': d,
            'is_stationary': stationarity['consensus'] == 'stationary',
            'confidence': stationarity['confidence'],
            'adf_p_value': stationarity['adf']['p_value'],
            'kpss_p_value': stationarity['kpss']['p_value'],
            'memory_retained': memory_score,
            'mean': transformed.mean(),
            'std': transformed.std(),
            'length': len(transformed)
        })

    df = pd.DataFrame(comparison_data)

    logger.info(f"Compared {len(d_values)} d values")

    return df
