# memory_metrics.py - Memory retention and autocorrelation metrics

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import acf, pacf
import logging
from utils import validate_series
from config import Config

logger = logging.getLogger(__name__)


def calculate_autocorrelation(series: pd.Series, lags: int = None) -> np.ndarray:
    """
    Calculate autocorrelation function up to specified lags.

    Args:
        series: Time series data
        lags: Number of lags (default: from config)

    Returns:
        Array of autocorrelation values for each lag

    Example:
        >>> acf_values = calculate_autocorrelation(price_series, lags=20)
        >>> lag1_autocorr = acf_values[0]
    """
    series = validate_series(series)

    if lags is None:
        lags = Config.DEFAULT_LAGS

    # Ensure lags doesn't exceed series length
    lags = min(lags, len(series) - 1)

    try:
        # Calculate ACF
        acf_values = acf(series, nlags=lags, fft=True)

        # Return without lag 0 (which is always 1.0)
        return acf_values[1:]

    except Exception as e:
        logger.error(f"ACF calculation failed: {str(e)}")
        # Fallback to manual calculation
        return _manual_acf(series, lags)


def _manual_acf(series: pd.Series, lags: int) -> np.ndarray:
    """Manual ACF calculation as fallback."""
    series_centered = series - series.mean()
    var = series_centered.var()

    acf_vals = []
    for lag in range(1, lags + 1):
        if lag >= len(series):
            break

        corr = (series_centered[:-lag] * series_centered[lag:]).mean() / var
        acf_vals.append(corr)

    return np.array(acf_vals)


def memory_retention_score(
    original: pd.Series,
    transformed: pd.Series,
    lags: int = None
) -> float:
    """
    Measure how much autocorrelation structure is retained after transformation.

    Returns a score from 0 to 1:
        1.0 = All memory retained (d=0, no transformation)
        0.0 = No memory (d=1, standard returns)

    Args:
        original: Original price series
        transformed: Fractionally differentiated series
        lags: Number of lags to consider (default: from config)

    Returns:
        Memory retention score (0 to 1)

    Example:
        >>> original = price_series
        >>> transformed = fractional_diff_ffd(price_series, d=0.5)
        >>> score = memory_retention_score(original, transformed)
        >>> print(f"Memory retained: {score:.1%}")
    """
    original = validate_series(original)
    transformed = validate_series(transformed)

    if lags is None:
        lags = Config.DEFAULT_LAGS

    try:
        # Calculate ACF for both series
        acf_original = calculate_autocorrelation(original, lags=lags)
        acf_transformed = calculate_autocorrelation(transformed, lags=lags)

        # Handle different lengths
        min_len = min(len(acf_original), len(acf_transformed))
        acf_original = acf_original[:min_len]
        acf_transformed = acf_transformed[:min_len]

        # Calculate retention as correlation between ACFs
        # (how similar is the autocorrelation structure?)
        if len(acf_original) > 0 and np.std(acf_original) > 0:
            retention = np.corrcoef(acf_original, acf_transformed)[0, 1]

            # Ensure it's between 0 and 1
            retention = max(0.0, min(1.0, retention))

            return float(retention)
        else:
            return 0.0

    except Exception as e:
        logger.warning(f"Memory retention calculation failed: {str(e)}")
        return 0.0


def hurst_exponent(series: pd.Series, max_lag: int = 100) -> float:
    """
    Calculate Hurst exponent (measure of long-term memory).

    Hurst Exponent interpretation:
        H = 0.5: Random walk (no memory, geometric Brownian motion)
        H > 0.5: Persistent (trending behavior, positive autocorrelation)
        H < 0.5: Mean-reverting (negative autocorrelation)

    Uses R/S (Rescaled Range) analysis.

    Args:
        series: Time series data
        max_lag: Maximum lag for R/S analysis

    Returns:
        Hurst exponent value

    Example:
        >>> h = hurst_exponent(price_series)
        >>> if h > 0.5:
        >>>     print("Series has positive autocorrelation (persistent)")
        >>> elif h < 0.5:
        >>>     print("Series is mean-reverting")
        >>> else:
        >>>     print("Series is a random walk")
    """
    series = validate_series(series)

    try:
        # Create lag values (powers of 2 for efficiency)
        min_lag = max(2, Config.HURST_LAG_RANGE[0])
        max_lag = min(max_lag, len(series) // 2, Config.HURST_LAG_RANGE[1])

        lags = []
        lag = min_lag
        while lag <= max_lag:
            lags.append(lag)
            lag = int(lag * 1.5)  # Increase by 50% each time

        if len(lags) < 3:
            logger.warning("Too few lags for Hurst calculation")
            return 0.5

        # Calculate R/S for each lag
        rs_values = []

        for lag in lags:
            # Split series into chunks
            n_chunks = len(series) // lag

            if n_chunks == 0:
                continue

            rs_chunk = []

            for i in range(n_chunks):
                chunk = series.iloc[i * lag:(i + 1) * lag].values

                # Mean-adjusted cumulative sum
                mean_chunk = chunk.mean()
                cumsum = np.cumsum(chunk - mean_chunk)

                # Range
                R = cumsum.max() - cumsum.min()

                # Standard deviation
                S = chunk.std(ddof=1)

                if S > 0:
                    rs_chunk.append(R / S)

            if rs_chunk:
                rs_values.append(np.mean(rs_chunk))
            else:
                continue

        if len(rs_values) < 3:
            logger.warning("Insufficient R/S values for Hurst calculation")
            return 0.5

        # Fit log(R/S) = H * log(lag) + constant
        # Hurst exponent is the slope
        log_lags = np.log(lags[:len(rs_values)])
        log_rs = np.log(rs_values)

        # Linear regression
        coeffs = np.polyfit(log_lags, log_rs, 1)
        hurst = coeffs[0]

        # Clamp to reasonable range
        hurst = max(0.0, min(1.0, hurst))

        logger.debug(f"Hurst exponent: {hurst:.3f}")

        return float(hurst)

    except Exception as e:
        logger.error(f"Hurst exponent calculation failed: {str(e)}")
        return 0.5  # Default to random walk


def compare_memory_metrics(
    original: pd.Series,
    transformed_dict: dict
) -> pd.DataFrame:
    """
    Compare memory metrics across multiple d values.

    Args:
        original: Original price series
        transformed_dict: Dictionary of {label: series}
                         e.g., {'d=0.3': series1, 'd=0.5': series2, ...}

    Returns:
        DataFrame with columns: label, autocorr_lag1, autocorr_lag5, hurst, memory_score

    Example:
        >>> transforms = {
        >>>     'd=0.3': fractional_diff_ffd(price, 0.3),
        >>>     'd=0.5': fractional_diff_ffd(price, 0.5),
        >>>     'd=0.7': fractional_diff_ffd(price, 0.7)
        >>> }
        >>> comparison = compare_memory_metrics(price, transforms)
        >>> print(comparison)
    """
    original = validate_series(original)

    comparison_data = []

    # Add original series
    acf_original = calculate_autocorrelation(original, lags=20)
    hurst_original = hurst_exponent(original)

    comparison_data.append({
        'label': 'Original',
        'autocorr_lag1': float(acf_original[0]) if len(acf_original) > 0 else 0.0,
        'autocorr_lag5': float(acf_original[4]) if len(acf_original) > 4 else 0.0,
        'autocorr_lag10': float(acf_original[9]) if len(acf_original) > 9 else 0.0,
        'hurst_exponent': hurst_original,
        'memory_score': 1.0  # Original has 100% memory by definition
    })

    # Add transformed series
    for label, series in transformed_dict.items():
        series = validate_series(series)

        # Calculate metrics
        acf_vals = calculate_autocorrelation(series, lags=20)
        hurst = hurst_exponent(series)
        memory_score = memory_retention_score(original, series, lags=20)

        comparison_data.append({
            'label': label,
            'autocorr_lag1': float(acf_vals[0]) if len(acf_vals) > 0 else 0.0,
            'autocorr_lag5': float(acf_vals[4]) if len(acf_vals) > 4 else 0.0,
            'autocorr_lag10': float(acf_vals[9]) if len(acf_vals) > 9 else 0.0,
            'hurst_exponent': hurst,
            'memory_score': memory_score
        })

    df = pd.DataFrame(comparison_data)

    logger.info(f"Memory comparison complete for {len(transformed_dict)} transformations")

    return df


def calculate_partial_autocorrelation(series: pd.Series, lags: int = None) -> np.ndarray:
    """
    Calculate partial autocorrelation function (PACF).

    PACF removes indirect correlations, showing direct relationship at each lag.

    Args:
        series: Time series data
        lags: Number of lags (default: from config)

    Returns:
        Array of PACF values
    """
    series = validate_series(series)

    if lags is None:
        lags = Config.DEFAULT_LAGS

    lags = min(lags, len(series) - 1)

    try:
        pacf_values = pacf(series, nlags=lags)
        return pacf_values[1:]  # Exclude lag 0

    except Exception as e:
        logger.error(f"PACF calculation failed: {str(e)}")
        return np.zeros(lags)
