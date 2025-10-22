# tail_risk_metrics.py - Tail Risk Metrics
# CVaR, Expected Shortfall, Drawdown calculations

import numpy as np
import pandas as pd
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


def calculate_var(returns: np.ndarray, alpha: float = 0.05) -> float:
    """
    Calculate Value at Risk (VaR).

    VaR is the α-th percentile of the return distribution.
    For example, 95% VaR is the return below which 5% of returns fall.

    Args:
        returns: Array of returns
        alpha: Confidence level (0.05 = 95% VaR)

    Returns:
        VaR value (negative for losses)
    """
    var = np.percentile(returns, alpha * 100)
    return float(var)


def calculate_cvar(returns: np.ndarray, alpha: float = 0.05) -> float:
    """
    Calculate Conditional Value at Risk (CVaR) / Expected Shortfall (ES).

    CVaR is the expected return conditional on being in the worst α% of cases.
    It's the average of all returns below VaR.

    Args:
        returns: Array of returns
        alpha: Confidence level (0.05 = 95% CVaR)

    Returns:
        CVaR value (negative for losses)

    Reference:
        Rockafellar, R.T. & Uryasev, S. (2000)
    """
    var = calculate_var(returns, alpha)
    tail_returns = returns[returns <= var]

    if len(tail_returns) > 0:
        cvar = tail_returns.mean()
    else:
        cvar = var

    return float(cvar)


def calculate_tail_metrics(returns: pd.DataFrame,
                           alpha: float = 0.05) -> dict:
    """
    Calculate comprehensive tail risk metrics.

    Args:
        returns: Returns dataframe (T × N)
        alpha: Confidence level

    Returns:
        {
            'var_95': 95% VaR,
            'cvar_95': 95% CVaR,
            'var_99': 99% VaR,
            'cvar_99': 99% CVaR,
            'max_drawdown': Maximum drawdown,
            'skewness': Return skewness,
            'kurtosis': Return kurtosis,
            'worst_return': Single worst return,
            'best_return': Single best return
        }
    """
    if isinstance(returns, pd.DataFrame):
        returns_array = returns.values.flatten()
    else:
        returns_array = returns

    var_95 = calculate_var(returns_array, 0.05)
    cvar_95 = calculate_cvar(returns_array, 0.05)
    var_99 = calculate_var(returns_array, 0.01)
    cvar_99 = calculate_cvar(returns_array, 0.01)

    # Maximum drawdown
    if isinstance(returns, pd.DataFrame):
        cumulative = (1 + returns.mean(axis=1)).cumprod()
    else:
        cumulative = (1 + pd.Series(returns)).cumprod()

    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()

    # Higher moments
    skewness = pd.Series(returns_array).skew()
    kurtosis = pd.Series(returns_array).kurtosis()

    return {
        'var_95': float(var_95),
        'cvar_95': float(cvar_95),
        'var_99': float(var_99),
        'cvar_99': float(cvar_99),
        'max_drawdown': float(max_drawdown),
        'skewness': float(skewness),
        'kurtosis': float(kurtosis),
        'worst_return': float(np.min(returns_array)),
        'best_return': float(np.max(returns_array))
    }


def calculate_expected_shortfall(returns: np.ndarray, alpha: float = 0.05) -> float:
    """
    Calculate Expected Shortfall (ES).

    ES is the same as CVaR - the expected loss given that
    the loss exceeds VaR.

    Args:
        returns: Array of returns
        alpha: Confidence level

    Returns:
        Expected Shortfall
    """
    return calculate_cvar(returns, alpha)


def calculate_downside_deviation(returns: np.ndarray,
                                 mar: float = 0.0) -> float:
    """
    Calculate downside deviation (semi-deviation).

    Downside deviation only considers returns below a Minimum Acceptable
    Return (MAR), typically 0.

    Args:
        returns: Array of returns
        mar: Minimum Acceptable Return (default 0)

    Returns:
        Downside deviation
    """
    downside_returns = returns[returns < mar]

    if len(downside_returns) > 0:
        downside_dev = np.sqrt(np.mean((downside_returns - mar) ** 2))
    else:
        downside_dev = 0.0

    return float(downside_dev)


def calculate_sortino_ratio(returns: np.ndarray,
                            risk_free_rate: float = 0.0,
                            mar: float = 0.0,
                            periods_per_year: int = 252) -> float:
    """
    Calculate Sortino Ratio.

    Sortino Ratio = (Mean Return - MAR) / Downside Deviation

    Unlike Sharpe ratio, Sortino only penalizes downside volatility.

    Args:
        returns: Array of returns
        risk_free_rate: Risk-free rate (annualized)
        mar: Minimum Acceptable Return
        periods_per_year: Trading periods per year

    Returns:
        Annualized Sortino ratio
    """
    mean_return = np.mean(returns)
    downside_dev = calculate_downside_deviation(returns, mar)

    if downside_dev == 0:
        return 0.0

    # Annualize
    annualized_return = mean_return * periods_per_year
    annualized_downside_dev = downside_dev * np.sqrt(periods_per_year)

    sortino = (annualized_return - risk_free_rate) / annualized_downside_dev

    return float(sortino)


def calculate_omega_ratio(returns: np.ndarray,
                          threshold: float = 0.0) -> float:
    """
    Calculate Omega Ratio.

    Omega = Σ(gains above threshold) / Σ(losses below threshold)

    Args:
        returns: Array of returns
        threshold: Return threshold

    Returns:
        Omega ratio
    """
    gains = returns[returns > threshold] - threshold
    losses = threshold - returns[returns < threshold]

    if len(losses) > 0 and np.sum(losses) > 0:
        omega = np.sum(gains) / np.sum(losses)
    else:
        omega = np.inf if len(gains) > 0 else 0.0

    return float(omega) if not np.isinf(omega) else 999.0


def calculate_calmar_ratio(returns: pd.Series,
                           periods_per_year: int = 252) -> float:
    """
    Calculate Calmar Ratio.

    Calmar = Annualized Return / Max Drawdown

    Measures return per unit of drawdown risk.

    Args:
        returns: Returns series
        periods_per_year: Trading periods per year

    Returns:
        Calmar ratio
    """
    # Annualized return
    mean_return = returns.mean()
    annualized_return = mean_return * periods_per_year

    # Maximum drawdown
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = abs(drawdown.min())

    if max_drawdown == 0:
        return 0.0

    calmar = annualized_return / max_drawdown

    return float(calmar)


def portfolio_tail_risk_analysis(weights: np.ndarray,
                                 returns: pd.DataFrame,
                                 alpha: float = 0.05) -> dict:
    """
    Comprehensive tail risk analysis for a portfolio.

    Args:
        weights: Portfolio weights
        returns: Returns dataframe
        alpha: Confidence level for VaR/CVaR

    Returns:
        Comprehensive tail risk metrics
    """
    # Portfolio returns
    portfolio_returns = (returns @ weights)

    # Calculate all tail metrics
    tail_metrics = calculate_tail_metrics(portfolio_returns, alpha)

    # Additional portfolio-specific metrics
    downside_dev = calculate_downside_deviation(portfolio_returns.values)
    sortino = calculate_sortino_ratio(portfolio_returns.values)
    omega = calculate_omega_ratio(portfolio_returns.values)
    calmar = calculate_calmar_ratio(portfolio_returns)

    tail_metrics.update({
        'downside_deviation': float(downside_dev),
        'sortino_ratio': float(sortino),
        'omega_ratio': float(omega),
        'calmar_ratio': float(calmar)
    })

    logger.info(f"Tail risk - CVaR: {tail_metrics['cvar_95']:.4f}, "
                f"Sortino: {sortino:.2f}, Max DD: {tail_metrics['max_drawdown']:.2%}")

    return tail_metrics
