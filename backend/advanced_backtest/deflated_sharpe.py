# deflated_sharpe.py - Deflated Sharpe Ratio calculation
# Corrects for selection bias, backtest overfitting, and non-normality

import numpy as np
from scipy.stats import norm
from typing import Dict
import logging

logger = logging.getLogger(__name__)


def deflated_sharpe_ratio(observed_sharpe: float,
                          n_trials: int,
                          n_observations: int,
                          skewness: float = 0.0,
                          kurtosis: float = 3.0,
                          benchmark_sharpe: float = 0.0) -> dict:
    """
    Calculate Deflated Sharpe Ratio (DSR).

    The DSR adjusts the Sharpe ratio for:
    1. Multiple testing (trying many strategies)
    2. Non-normality (skewness, kurtosis)
    3. Number of observations

    DSR answers: "What's the probability that the observed Sharpe ratio
    is statistically significant after accounting for multiple testing?"

    Args:
        observed_sharpe: Sharpe ratio achieved
        n_trials: Number of strategies tested
        n_observations: Number of data points
        skewness: Return skewness
        kurtosis: Return kurtosis
        benchmark_sharpe: Sharpe to beat (default 0)

    Returns:
        {
            'dsr': Deflated Sharpe Ratio,
            'p_value': Probability of false positive,
            'is_significant': Boolean (DSR > 1.96 for 95% confidence),
            'inflation_factor': How much Sharpe was inflated by multiple testing,
            'expected_max_sr': Expected maximum Sharpe from n_trials under null,
            'interpretation': Text interpretation
        }

    Reference:
        Bailey, D.H. & Lopez de Prado, M. (2014)
        "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality"
    """
    logger.info(f"Calculating DSR: observed_sharpe={observed_sharpe:.3f}, n_trials={n_trials}, n_obs={n_observations}")

    # Adjustment for non-normality
    # Variance of Sharpe ratio estimate
    var_sr = (1 + (1 - skewness * observed_sharpe +
                   ((kurtosis - 1) / 4) * observed_sharpe**2)) / n_observations

    # Standard error
    se_sr = np.sqrt(var_sr)

    # Expected maximum Sharpe from n_trials trials under null
    # (using extreme value theory)
    expected_max_sr = ((1 - np.euler_gamma) * norm.ppf(1 - 1/n_trials) +
                       np.euler_gamma * norm.ppf(1 - 1/(n_trials * np.e)))

    # Deflated Sharpe Ratio
    dsr = (observed_sharpe - expected_max_sr) / se_sr

    # p-value: probability this is false positive
    p_value = 2 * (1 - norm.cdf(abs(dsr)))

    # Is it significant at 95% confidence?
    is_significant = abs(dsr) > 1.96

    # How much was Sharpe inflated by multiple testing?
    if observed_sharpe > expected_max_sr:
        inflation_factor = observed_sharpe / (observed_sharpe - expected_max_sr)
    else:
        inflation_factor = 1.0

    # Interpretation
    if is_significant:
        if dsr > 2.58:  # 99% confidence
            interpretation = "Highly Significant - Sharpe ratio is statistically significant at 99% confidence"
        else:
            interpretation = "Significant - Sharpe ratio is statistically significant at 95% confidence"
    else:
        if p_value > 0.5:
            interpretation = f"Not significant - Sharpe ratio likely due to luck (p={p_value:.3f})"
        else:
            interpretation = f"Marginally significant - Weak evidence (p={p_value:.3f})"

    logger.info(f"DSR = {dsr:.3f}, p-value = {p_value:.3f}, significant = {is_significant}")

    return {
        'dsr': float(dsr),
        'p_value': float(p_value),
        'is_significant': bool(is_significant),
        'inflation_factor': float(inflation_factor),
        'expected_max_sr': float(expected_max_sr),
        'observed_sharpe': float(observed_sharpe),
        'benchmark_sharpe': float(benchmark_sharpe),
        'standard_error': float(se_sr),
        'interpretation': interpretation
    }


def probabilistic_sharpe_ratio(observed_sharpe: float,
                                n_observations: int,
                                skewness: float = 0.0,
                                kurtosis: float = 3.0,
                                benchmark_sharpe: float = 0.0) -> dict:
    """
    Calculate Probabilistic Sharpe Ratio (PSR).

    PSR = P(Sharpe > benchmark_sharpe)

    Similar to DSR but doesn't account for multiple testing.

    Args:
        observed_sharpe: Observed Sharpe ratio
        n_observations: Number of observations
        skewness: Return skewness
        kurtosis: Return kurtosis
        benchmark_sharpe: Benchmark Sharpe to beat

    Returns:
        {
            'psr': Probabilistic Sharpe Ratio (0 to 1),
            'psr_percentage': PSR as percentage,
            'is_better_than_benchmark': Boolean,
            'interpretation': Text interpretation
        }

    Reference:
        Bailey, D.H. & Lopez de Prado, M. (2012)
        "The Sharpe Ratio Efficient Frontier"
    """
    # Variance of Sharpe ratio estimate
    var_sr = (1 + (1 - skewness * observed_sharpe +
                   ((kurtosis - 1) / 4) * observed_sharpe**2)) / n_observations

    se_sr = np.sqrt(var_sr)

    # Z-score
    z = (observed_sharpe - benchmark_sharpe) / se_sr

    # PSR = P(SR > benchmark)
    psr = norm.cdf(z)

    # Interpretation
    if psr > 0.95:
        interpretation = "Excellent - Very high probability of beating benchmark"
    elif psr > 0.90:
        interpretation = "Good - High probability of beating benchmark"
    elif psr > 0.75:
        interpretation = "Fair - Moderate probability of beating benchmark"
    elif psr > 0.50:
        interpretation = "Poor - Low probability of beating benchmark"
    else:
        interpretation = "Very Poor - Strategy likely underperforms benchmark"

    return {
        'psr': float(psr),
        'psr_percentage': float(psr * 100),
        'is_better_than_benchmark': bool(psr > 0.5),
        'z_score': float(z),
        'interpretation': interpretation
    }


def minimum_track_record_length(observed_sharpe: float,
                                 benchmark_sharpe: float = 0.0,
                                 skewness: float = 0.0,
                                 kurtosis: float = 3.0,
                                 confidence_level: float = 0.95) -> dict:
    """
    Calculate Minimum Track Record Length (MinTRL).

    MinTRL = minimum number of observations needed to be confident
    that observed Sharpe > benchmark Sharpe.

    Args:
        observed_sharpe: Observed Sharpe ratio
        benchmark_sharpe: Benchmark Sharpe
        skewness: Return skewness
        kurtosis: Return kurtosis
        confidence_level: Desired confidence level (default 0.95)

    Returns:
        {
            'min_track_record_length': Minimum number of observations,
            'years_at_daily_freq': Years if using daily data,
            'interpretation': Text interpretation
        }

    Reference:
        Bailey, D.H. & Lopez de Prado, M. (2012)
    """
    # Z-score for desired confidence level
    z_alpha = norm.ppf(confidence_level)

    # Variance adjustment
    var_adjustment = 1 - skewness * observed_sharpe + ((kurtosis - 1) / 4) * observed_sharpe**2

    # MinTRL formula
    min_trl = ((z_alpha * np.sqrt(var_adjustment)) / (observed_sharpe - benchmark_sharpe))**2

    years_daily = min_trl / 252

    # Interpretation
    if years_daily < 1:
        interpretation = f"Short track record needed - Less than 1 year ({min_trl:.0f} observations)"
    elif years_daily < 3:
        interpretation = f"Moderate track record needed - {years_daily:.1f} years"
    elif years_daily < 5:
        interpretation = f"Long track record needed - {years_daily:.1f} years"
    else:
        interpretation = f"Very long track record needed - {years_daily:.1f} years (strategy may not be robust)"

    return {
        'min_track_record_length': int(min_trl),
        'years_at_daily_freq': float(years_daily),
        'years_at_monthly_freq': float(min_trl / 12),
        'confidence_level': float(confidence_level),
        'interpretation': interpretation
    }
