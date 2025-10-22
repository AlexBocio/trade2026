# stationarity_tests.py - Stationarity testing methods

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.stattools import acf
import logging
from utils import validate_series
from config import Config

logger = logging.getLogger(__name__)


def adf_test(series: pd.Series, alpha: float = None, **kwargs) -> dict:
    """
    Augmented Dickey-Fuller test for stationarity.

    Null hypothesis (H0): Series has a unit root (non-stationary)
    Alternative (H1): Series is stationary

    If p-value < alpha: Reject H0 → Series is stationary

    Args:
        series: Time series to test
        alpha: Significance level (default: from config)
        **kwargs: Additional arguments for adfuller()
            regression: 'c' (default), 'ct', 'ctt', 'nc'
            maxlag: Maximum lag to use (default: auto)

    Returns:
        Dictionary with test results:
            {
                'test': 'ADF',
                'statistic': float,
                'p_value': float,
                'critical_values': {'1%': ..., '5%': ..., '10%': ...},
                'used_lag': int,
                'n_obs': int,
                'is_stationary': bool,
                'conclusion': str
            }

    Example:
        >>> result = adf_test(price_series)
        >>> if result['is_stationary']:
        >>>     print("Series is stationary!")
    """
    series = validate_series(series)

    if alpha is None:
        alpha = Config.DEFAULT_ALPHA

    # Set defaults from config if not provided
    regression = kwargs.pop('regression', Config.ADF_REGRESSION)
    maxlag = kwargs.pop('maxlag', Config.ADF_MAXLAG)

    try:
        # Perform ADF test
        adf_result = adfuller(series, regression=regression, maxlag=maxlag, **kwargs)

        statistic, p_value, used_lag, n_obs, critical_values, icbest = adf_result

        # Determine if stationary
        is_stationary = p_value < alpha

        # Create detailed conclusion
        if is_stationary:
            conclusion = f"Series is stationary (p={p_value:.4f} < {alpha})"
        else:
            conclusion = f"Series is non-stationary (p={p_value:.4f} >= {alpha})"

        result = {
            'test': 'ADF',
            'statistic': float(statistic),
            'p_value': float(p_value),
            'critical_values': {k: float(v) for k, v in critical_values.items()},
            'used_lag': int(used_lag),
            'n_obs': int(n_obs),
            'alpha': alpha,
            'is_stationary': is_stationary,
            'conclusion': conclusion,
            'regression': regression
        }

        logger.debug(f"ADF test: statistic={statistic:.4f}, p-value={p_value:.4f}, "
                    f"stationary={is_stationary}")

        return result

    except Exception as e:
        logger.error(f"ADF test failed: {str(e)}")
        raise ValueError(f"ADF test failed: {str(e)}")


def kpss_test(series: pd.Series, alpha: float = None, **kwargs) -> dict:
    """
    Kwiatkowski-Phillips-Schmidt-Shin test for stationarity.

    Null hypothesis (H0): Series IS stationary (opposite of ADF!)
    Alternative (H1): Series is non-stationary

    If p-value < alpha: Reject H0 → Series is non-stationary
    If p-value >= alpha: Fail to reject H0 → Series is stationary

    Args:
        series: Time series to test
        alpha: Significance level (default: from config)
        **kwargs: Additional arguments for kpss()
            regression: 'c' (default), 'ct'
            nlags: Number of lags (default: 'auto')

    Returns:
        Dictionary with test results

    Example:
        >>> result = kpss_test(price_series)
        >>> # Note: KPSS has opposite interpretation from ADF!
        >>> if result['is_stationary']:
        >>>     print("Series is stationary!")
    """
    series = validate_series(series)

    if alpha is None:
        alpha = Config.DEFAULT_ALPHA

    regression = kwargs.pop('regression', Config.KPSS_REGRESSION)
    nlags = kwargs.pop('nlags', Config.KPSS_NLAGS)

    try:
        # Perform KPSS test
        kpss_result = kpss(series, regression=regression, nlags=nlags, **kwargs)

        statistic, p_value, n_lags, critical_values = kpss_result

        # KPSS: H0 is stationarity, so opposite interpretation!
        # If p-value < alpha: reject H0 → non-stationary
        # If p-value >= alpha: fail to reject H0 → stationary
        is_stationary = p_value >= alpha

        if is_stationary:
            conclusion = f"Series is stationary (p={p_value:.4f} >= {alpha}, fail to reject H0)"
        else:
            conclusion = f"Series is non-stationary (p={p_value:.4f} < {alpha}, reject H0)"

        result = {
            'test': 'KPSS',
            'statistic': float(statistic),
            'p_value': float(p_value),
            'critical_values': {k: float(v) for k, v in critical_values.items()},
            'used_lag': int(n_lags),
            'n_obs': len(series),
            'alpha': alpha,
            'is_stationary': is_stationary,
            'conclusion': conclusion,
            'regression': regression,
            'note': 'KPSS H0: series IS stationary (opposite of ADF)'
        }

        logger.debug(f"KPSS test: statistic={statistic:.4f}, p-value={p_value:.4f}, "
                    f"stationary={is_stationary}")

        return result

    except Exception as e:
        logger.error(f"KPSS test failed: {str(e)}")
        raise ValueError(f"KPSS test failed: {str(e)}")


def pp_test(series: pd.Series, alpha: float = None, **kwargs) -> dict:
    """
    Phillips-Perron test for stationarity.

    Similar to ADF but more robust to heteroskedasticity and serial correlation.

    Null hypothesis (H0): Series has a unit root (non-stationary)
    Alternative (H1): Series is stationary

    Args:
        series: Time series to test
        alpha: Significance level (default: from config)
        **kwargs: Additional arguments

    Returns:
        Dictionary with test results

    Note:
        statsmodels doesn't have built-in PP test, so we use ADF
        with a modified lag structure as approximation.
    """
    series = validate_series(series)

    if alpha is None:
        alpha = Config.DEFAULT_ALPHA

    try:
        # PP test is similar to ADF but handles heteroskedasticity better
        # We approximate using ADF with specific settings
        # In production, you might want to implement the full PP test

        regression = kwargs.pop('regression', 'c')

        # Use ADF as approximation (PP test is not in statsmodels)
        # Proper PP test would use Newey-West variance estimator
        adf_result = adfuller(series, regression=regression, autolag='AIC')

        statistic, p_value, used_lag, n_obs, critical_values, icbest = adf_result

        is_stationary = p_value < alpha

        if is_stationary:
            conclusion = f"Series is stationary (p={p_value:.4f} < {alpha})"
        else:
            conclusion = f"Series is non-stationary (p={p_value:.4f} >= {alpha})"

        result = {
            'test': 'PP',
            'statistic': float(statistic),
            'p_value': float(p_value),
            'critical_values': {k: float(v) for k, v in critical_values.items()},
            'used_lag': int(used_lag),
            'n_obs': int(n_obs),
            'alpha': alpha,
            'is_stationary': is_stationary,
            'conclusion': conclusion,
            'regression': regression,
            'note': 'Approximated using ADF with AIC lag selection'
        }

        logger.debug(f"PP test: statistic={statistic:.4f}, p-value={p_value:.4f}, "
                    f"stationary={is_stationary}")

        return result

    except Exception as e:
        logger.error(f"PP test failed: {str(e)}")
        raise ValueError(f"PP test failed: {str(e)}")


def combined_stationarity_check(series: pd.Series, alpha: float = None) -> dict:
    """
    Run all three stationarity tests and provide consensus.

    Uses ADF, KPSS, and PP tests to determine stationarity with higher confidence.

    Args:
        series: Time series to test
        alpha: Significance level (default: from config)

    Returns:
        Dictionary with all test results and consensus:
            {
                'adf': {...},
                'kpss': {...},
                'pp': {...},
                'consensus': 'stationary' | 'non-stationary' | 'inconclusive',
                'confidence': 'high' | 'medium' | 'low',
                'summary': str
            }

    Consensus Logic:
        - All 3 agree: High confidence
        - 2 out of 3 agree: Medium confidence
        - No agreement: Inconclusive (low confidence)

    Example:
        >>> result = combined_stationarity_check(price_series)
        >>> print(result['consensus'])  # 'stationary' or 'non-stationary'
        >>> print(result['summary'])    # Human-readable summary
    """
    series = validate_series(series)

    if alpha is None:
        alpha = Config.DEFAULT_ALPHA

    # Run all three tests
    adf_result = adf_test(series, alpha=alpha)
    kpss_result = kpss_test(series, alpha=alpha)
    pp_result = pp_test(series, alpha=alpha)

    # Collect votes
    votes = {
        'ADF': adf_result['is_stationary'],
        'KPSS': kpss_result['is_stationary'],
        'PP': pp_result['is_stationary']
    }

    stationary_votes = sum(votes.values())
    total_votes = len(votes)

    # Determine consensus
    if stationary_votes == total_votes:
        consensus = 'stationary'
        confidence = 'high'
        summary = f"All {total_votes} tests indicate stationarity"
    elif stationary_votes == 0:
        consensus = 'non-stationary'
        confidence = 'high'
        summary = f"All {total_votes} tests indicate non-stationarity"
    elif stationary_votes >= total_votes / 2:
        consensus = 'stationary'
        confidence = 'medium'
        summary = f"{stationary_votes}/{total_votes} tests indicate stationarity"
    else:
        consensus = 'non-stationary'
        confidence = 'medium'
        summary = f"{total_votes - stationary_votes}/{total_votes} tests indicate non-stationarity"

    # Special case: ADF and KPSS disagree (common scenario)
    if adf_result['is_stationary'] != kpss_result['is_stationary']:
        confidence = 'low'
        summary += " (ADF and KPSS disagree - inconclusive)"

    result = {
        'adf': adf_result,
        'kpss': kpss_result,
        'pp': pp_result,
        'votes': votes,
        'stationary_votes': stationary_votes,
        'consensus': consensus,
        'confidence': confidence,
        'summary': summary,
        'alpha': alpha
    }

    logger.info(f"Combined stationarity check: {consensus} ({confidence} confidence)")

    return result


def test_multiple_d_values(
    original_series: pd.Series,
    d_values: list,
    test_func: str = 'adf'
) -> pd.DataFrame:
    """
    Test stationarity for series at multiple d values.

    Useful for finding minimum d that achieves stationarity.

    Args:
        original_series: Original price series
        d_values: List of d values to test
        test_func: 'adf', 'kpss', 'pp', or 'combined'

    Returns:
        DataFrame with test results for each d value
    """
    from fractional_diff import fractional_diff_ffd

    results = []

    for d in d_values:
        # Apply fractional differentiation
        if d == 0:
            series = original_series
        else:
            series = fractional_diff_ffd(original_series, d)

        # Run stationarity test
        if test_func == 'adf':
            test_result = adf_test(series)
        elif test_func == 'kpss':
            test_result = kpss_test(series)
        elif test_func == 'pp':
            test_result = pp_test(series)
        elif test_func == 'combined':
            test_result = combined_stationarity_check(series)
            test_result['is_stationary'] = test_result['consensus'] == 'stationary'
        else:
            raise ValueError(f"Unknown test function: {test_func}")

        results.append({
            'd': d,
            'statistic': test_result['statistic'],
            'p_value': test_result['p_value'],
            'is_stationary': test_result['is_stationary']
        })

    return pd.DataFrame(results)
