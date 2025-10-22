# fractional_diff.py - Core fractional differentiation algorithms

import numpy as np
import pandas as pd
import logging
from typing import Tuple
from utils import validate_series, validate_d
from config import Config

logger = logging.getLogger(__name__)


def get_weights_ffd(d: float, thres: float = 1e-5) -> np.ndarray:
    """
    Calculate FFD (Fixed-Width Window) weights for fractional differentiation.

    The weights are derived from the binomial expansion:
    w_k = (-1)^k * binom(d, k)

    Truncation occurs when |w_k| < threshold to create fixed-width window.

    Args:
        d: Differentiation order (0 < d < 1)
        thres: Weight threshold for truncation

    Returns:
        Array of weights for convolution

    Example:
        >>> weights = get_weights_ffd(0.5, thres=0.01)
        >>> len(weights)  # Number of weights before threshold
        15
    """
    d = validate_d(d)

    w = [1.0]
    k = 1

    # Generate weights until they fall below threshold
    while True:
        w_k = -w[-1] / k * (d - k + 1)

        if abs(w_k) < thres:
            break

        w.append(w_k)
        k += 1

    w = np.array(w)

    logger.debug(f"Generated {len(w)} weights for d={d} (threshold={thres})")

    return w


def fractional_diff_ffd(
    series: pd.Series,
    d: float,
    thres: float = None
) -> pd.Series:
    """
    Fractionally differentiate time series using Fixed-Width Window (FFD) method.

    This is the FFD algorithm from "Advances in Financial Machine Learning"
    by Marcos Lopez de Prado. It achieves stationarity while preserving memory.

    Mathematical formulation:
        X̃_t = Σ(k=0 to K) w_k * X_{t-k}
    where w_k are the fractional differentiation weights.

    Args:
        series: Price time series
        d: Differentiation order (0 < d < 1)
            d=0: Original series (non-stationary, full memory)
            d=1: Returns (stationary, no memory)
            d=0.4-0.6: Sweet spot (stationary + memory retention)
        thres: Weight threshold for truncation (default: from config)

    Returns:
        Fractionally differentiated series

    Raises:
        ValueError: If series or d is invalid

    Example:
        >>> import yfinance as yf
        >>> price = yf.download('SPY')['Close']
        >>> stationary_price = fractional_diff_ffd(price, d=0.5)
        >>> # Now stationary_price is stationary but retains autocorrelation
    """
    series = validate_series(series)
    d = validate_d(d)

    if thres is None:
        thres = Config.DEFAULT_THRESHOLD

    # Special cases
    if d == 0:
        logger.info("d=0: Returning original series (no differentiation)")
        return series

    if d == 1:
        logger.info("d=1: Returning standard returns")
        returns = series.pct_change()
        return returns.dropna()

    # Get FFD weights
    w = get_weights_ffd(d, thres)

    # Apply weights via convolution
    width = len(w) - 1
    series_values = series.values

    # Pre-allocate output array
    output = np.zeros(len(series) - width)

    # Convolution: apply weights to create fractionally differentiated series
    for i in range(width, len(series)):
        output[i - width] = np.dot(w, series_values[i - width:i + 1][::-1])

    # Create series with proper index
    result = pd.Series(
        output,
        index=series.index[width:],
        name=f'{series.name}_fracdiff_d{d:.2f}' if series.name else f'fracdiff_d{d:.2f}'
    )

    logger.info(f"Fractional differentiation complete: d={d}, original length={len(series)}, "
                f"result length={len(result)}, weights={len(w)}")

    return result


def fractional_diff_standard(series: pd.Series, d: float) -> pd.Series:
    """
    Standard fractional differentiation (slower, more accurate).

    Uses full binomial expansion without truncation.
    This method is more computationally expensive but doesn't lose observations.

    Args:
        series: Price time series
        d: Differentiation order (0 < d < 1)

    Returns:
        Fractionally differentiated series

    Raises:
        ValueError: If series or d is invalid
    """
    series = validate_series(series)
    d = validate_d(d)

    # Special cases
    if d == 0:
        return series

    if d == 1:
        returns = series.pct_change()
        return returns.dropna()

    # Calculate weights for all lags
    n = len(series)
    w = np.zeros(n)
    w[0] = 1.0

    for k in range(1, n):
        w[k] = -w[k - 1] / k * (d - k + 1)

    # Apply weights
    series_values = series.values
    output = np.zeros(n)

    for i in range(n):
        # Use weights up to current position
        max_lag = min(i + 1, n)
        output[i] = np.dot(w[:max_lag], series_values[i::-1][:max_lag])

    result = pd.Series(
        output,
        index=series.index,
        name=f'{series.name}_fracdiff_std_d{d:.2f}' if series.name else f'fracdiff_std_d{d:.2f}'
    )

    # Remove initial values that are affected by edge effects
    result = result.iloc[int(0.1 * len(result)):]  # Drop first 10%

    logger.info(f"Standard fractional differentiation complete: d={d}, result length={len(result)}")

    return result


def get_weights_expansion(d: float, size: int) -> np.ndarray:
    """
    Get fractional differentiation weights using binomial expansion.

    Args:
        d: Differentiation order
        size: Number of weights to generate

    Returns:
        Array of weights
    """
    d = validate_d(d)

    w = np.zeros(size)
    w[0] = 1.0

    for k in range(1, size):
        w[k] = -w[k - 1] / k * (d - k + 1)

    return w


def plot_weights(d_values: list = None, max_lags: int = 50) -> dict:
    """
    Generate weight series for plotting (useful for visualization).

    Args:
        d_values: List of d values to plot (default: [0.2, 0.4, 0.6, 0.8])
        max_lags: Maximum number of lags to display

    Returns:
        Dictionary of {d_value: weights_array}
    """
    if d_values is None:
        d_values = [0.2, 0.4, 0.6, 0.8]

    weights_dict = {}

    for d in d_values:
        weights = get_weights_expansion(d, max_lags)
        weights_dict[f'd={d}'] = weights

    return weights_dict


def compare_ffd_vs_standard(series: pd.Series, d: float) -> dict:
    """
    Compare FFD and standard fractional differentiation methods.

    Args:
        series: Price time series
        d: Differentiation order

    Returns:
        Dictionary with both results and comparison metrics
    """
    series = validate_series(series)
    d = validate_d(d)

    # Apply both methods
    ffd_result = fractional_diff_ffd(series, d)
    std_result = fractional_diff_standard(series, d)

    # Align series for comparison
    common_index = ffd_result.index.intersection(std_result.index)

    if len(common_index) == 0:
        logger.warning("No common index between FFD and standard methods")
        return {
            'ffd_result': ffd_result,
            'std_result': std_result,
            'comparison': None
        }

    ffd_aligned = ffd_result.loc[common_index]
    std_aligned = std_result.loc[common_index]

    # Calculate comparison metrics
    correlation = ffd_aligned.corr(std_aligned)
    rmse = np.sqrt(np.mean((ffd_aligned - std_aligned) ** 2))
    mae = np.mean(np.abs(ffd_aligned - std_aligned))

    return {
        'ffd_result': ffd_result,
        'std_result': std_result,
        'ffd_length': len(ffd_result),
        'std_length': len(std_result),
        'comparison': {
            'correlation': float(correlation),
            'rmse': float(rmse),
            'mae': float(mae),
            'common_points': len(common_index)
        }
    }
