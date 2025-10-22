# risk_contribution.py - Risk Contribution Calculations
# Marginal and component risk contribution for portfolio analysis

import numpy as np
import pandas as pd
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


def calculate_marginal_risk_contribution(weights: np.ndarray,
                                        cov_matrix: np.ndarray) -> np.ndarray:
    """
    Calculate marginal contribution to portfolio risk.

    Marginal Risk Contribution (MRC) = ∂σ_p / ∂w_i = (Σw)_i / σ_p

    This measures how much portfolio volatility changes when you increase
    the weight of asset i by a small amount.

    Args:
        weights: Portfolio weights (n_assets,)
        cov_matrix: Covariance matrix (n_assets, n_assets)

    Returns:
        Marginal risk contribution for each asset

    Reference:
        Qian, E. (2005). "Risk Parity Portfolios"
    """
    portfolio_variance = weights @ cov_matrix @ weights
    portfolio_vol = np.sqrt(portfolio_variance)

    if portfolio_vol == 0:
        return np.zeros_like(weights)

    # MRC = (Covariance matrix × weights) / portfolio volatility
    mrc = (cov_matrix @ weights) / portfolio_vol

    return mrc


def calculate_risk_contribution(weights: np.ndarray,
                                cov_matrix: np.ndarray) -> dict:
    """
    Calculate absolute and percentage risk contribution.

    Risk Contribution (RC) = w_i × MRC_i
    Percentage RC = RC_i / σ_p × 100%

    The sum of all risk contributions equals total portfolio volatility.

    Args:
        weights: Portfolio weights
        cov_matrix: Covariance matrix

    Returns:
        {
            'marginal_rc': Marginal risk contribution,
            'absolute_rc': Absolute risk contribution,
            'percentage_rc': Percentage risk contribution,
            'portfolio_vol': Total portfolio volatility,
            'sum_rc': Sum of risk contributions (should equal portfolio_vol)
        }
    """
    mrc = calculate_marginal_risk_contribution(weights, cov_matrix)

    # Absolute risk contribution
    rc = weights * mrc

    # Portfolio volatility
    portfolio_vol = np.sqrt(weights @ cov_matrix @ weights)

    # Percentage risk contribution
    pct_rc = (rc / portfolio_vol) * 100 if portfolio_vol > 0 else np.zeros_like(rc)

    logger.info(f"Portfolio vol: {portfolio_vol:.4f}, Sum RC: {np.sum(rc):.4f}")

    return {
        'marginal_rc': mrc,
        'absolute_rc': rc,
        'percentage_rc': pct_rc,
        'portfolio_vol': portfolio_vol,
        'sum_rc': np.sum(rc)  # Should equal portfolio_vol
    }


def calculate_cvar_contribution(weights: np.ndarray,
                                returns: pd.DataFrame,
                                alpha: float = 0.05) -> dict:
    """
    Calculate contribution to Conditional Value at Risk (CVaR).

    CVaR (Expected Shortfall) measures tail risk - the expected loss
    in the worst α% of cases. This is more relevant for downside risk
    than volatility, especially for asymmetric return distributions.

    Args:
        weights: Portfolio weights
        returns: Returns dataframe (T × N)
        alpha: Confidence level (0.05 = 95% CVaR)

    Returns:
        {
            'cvar': Portfolio CVaR (negative number),
            'var': Value at Risk,
            'cvar_contribution': CVaR contribution per asset,
            'percentage_cvar_contribution': % contribution to CVaR,
            'alpha': Confidence level used
        }

    Reference:
        Rockafellar, R.T. & Uryasev, S. (2000).
        "Optimization of Conditional Value-at-Risk"
    """
    # Portfolio returns
    portfolio_returns = (returns @ weights).values

    # Calculate VaR (Value at Risk) - the α-th percentile
    var = np.percentile(portfolio_returns, alpha * 100)

    # Calculate CVaR (average of returns below VaR)
    tail_returns = portfolio_returns[portfolio_returns <= var]
    if len(tail_returns) > 0:
        cvar = tail_returns.mean()
    else:
        cvar = var

    # Component CVaR: contribution of each asset to tail risk
    # Use only the tail returns
    tail_mask = portfolio_returns <= var
    tail_return_matrix = returns[tail_mask]

    if len(tail_return_matrix) > 0:
        # Average return of each asset during tail events
        component_tail_returns = tail_return_matrix.mean()

        # CVaR contribution = weight × component tail return
        cvar_contribution = weights * component_tail_returns.values

        # Percentage contribution
        if cvar != 0:
            pct_cvar_contribution = (cvar_contribution / abs(cvar)) * 100
        else:
            pct_cvar_contribution = np.zeros_like(weights)
    else:
        cvar_contribution = np.zeros_like(weights)
        pct_cvar_contribution = np.zeros_like(weights)

    logger.info(f"CVaR ({alpha*100}%): {cvar:.4f}, VaR: {var:.4f}")

    return {
        'cvar': float(cvar),
        'var': float(var),
        'cvar_contribution': cvar_contribution,
        'percentage_cvar_contribution': pct_cvar_contribution,
        'alpha': alpha,
        'n_tail_observations': int(np.sum(tail_mask))
    }


def equal_risk_contribution_weights(cov_matrix: np.ndarray,
                                    max_iter: int = 1000,
                                    tol: float = 1e-8) -> np.ndarray:
    """
    Calculate Equal Risk Contribution (ERC) portfolio weights.

    ERC portfolio: all assets contribute equally to portfolio risk.
    This is also known as Risk Parity when all risk budgets are equal.

    Solve: minimize Σ(RC_i - RC_j)² subject to Σw_i = 1, w_i >= 0

    Args:
        cov_matrix: Covariance matrix
        max_iter: Maximum iterations
        tol: Convergence tolerance

    Returns:
        Optimal weights for equal risk contribution

    Reference:
        Maillard, S., Roncalli, T., & Teiletche, J. (2010).
        "The Properties of Equally Weighted Risk Contribution Portfolios"
    """
    n = cov_matrix.shape[0]

    # Initial guess: equal weights
    weights = np.ones(n) / n

    # Newton-Raphson iteration
    for iteration in range(max_iter):
        # Calculate risk contributions
        rc_dict = calculate_risk_contribution(weights, cov_matrix)
        rc = rc_dict['absolute_rc']

        # Target: all RC should be equal to portfolio_vol / n
        target_rc = rc_dict['portfolio_vol'] / n

        # Error
        error = rc - target_rc

        if np.max(np.abs(error)) < tol:
            logger.info(f"ERC converged in {iteration} iterations")
            break

        # Gradient and Hessian (simplified update)
        # Update rule: move weights to reduce RC imbalance
        mrc = rc_dict['marginal_rc']

        # Simple gradient descent update
        gradient = 2 * error * mrc
        step_size = 0.01 / (1 + iteration * 0.001)  # Decreasing step size

        weights = weights - step_size * gradient

        # Project to simplex (sum to 1, non-negative)
        weights = np.maximum(weights, 0)
        weights = weights / np.sum(weights)

    return weights


def risk_budget_optimization(cov_matrix: np.ndarray,
                             risk_budgets: np.ndarray,
                             max_iter: int = 1000,
                             tol: float = 1e-8) -> np.ndarray:
    """
    Optimize portfolio for specific risk budgets.

    Risk Budget: target percentage contribution to total risk for each asset.

    Args:
        cov_matrix: Covariance matrix
        risk_budgets: Target risk budgets (must sum to 1)
        max_iter: Maximum iterations
        tol: Tolerance

    Returns:
        Optimal weights
    """
    if not np.isclose(np.sum(risk_budgets), 1.0):
        raise ValueError("Risk budgets must sum to 1")

    n = cov_matrix.shape[0]
    weights = np.ones(n) / n

    for iteration in range(max_iter):
        rc_dict = calculate_risk_contribution(weights, cov_matrix)
        pct_rc = rc_dict['percentage_rc'] / 100  # Convert to fraction

        # Error: actual RC vs target
        error = pct_rc - risk_budgets

        if np.max(np.abs(error)) < tol:
            logger.info(f"Risk budget optimization converged in {iteration} iterations")
            break

        # Update weights
        mrc = rc_dict['marginal_rc']
        gradient = 2 * error * mrc
        step_size = 0.01 / (1 + iteration * 0.001)

        weights = weights - step_size * gradient
        weights = np.maximum(weights, 0)
        weights = weights / np.sum(weights)

    return weights
