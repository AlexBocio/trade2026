# herc.py - Hierarchical Equal Risk Contribution Implementation
# Improvement over HRP that equalizes risk contribution instead of using inverse variance

from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import squareform
import numpy as np
import pandas as pd
import logging
from risk_contribution import calculate_risk_contribution, calculate_cvar_contribution
from hrp import _quasi_diag, _get_cluster_assignments

logger = logging.getLogger(__name__)


def herc_portfolio(returns: pd.DataFrame,
                   cov_matrix: np.ndarray = None,
                   linkage_method: str = 'single',
                   risk_measure: str = 'volatility') -> dict:
    """
    Hierarchical Equal Risk Contribution portfolio.

    HERC Algorithm:
    1. Tree Clustering: Same as HRP (hierarchical clustering on correlation)
    2. Quasi-Diagonalization: Same as HRP (reorder assets)
    3. Recursive Bisection with Equal Risk Contribution: Different from HRP!
       - Allocate to equalize risk contribution between sub-clusters
       - Can use volatility or CVaR as risk measure

    Key Difference from HRP:
    - HRP: Allocates inversely proportional to variance (w ∝ 1/σ²)
    - HERC: Allocates to equalize risk contribution (RC_left = RC_right)

    Benefits:
    - More stable portfolios (less sensitive to estimation error)
    - Better tail risk management when using CVaR
    - More equal risk distribution

    Args:
        returns: Returns dataframe (T × N)
        cov_matrix: Covariance matrix (if None, computed from returns)
        linkage_method: 'single', 'complete', 'average', 'ward'
        risk_measure: 'volatility' or 'cvar' for tail risk

    Returns:
        {
            'weights': Final portfolio weights,
            'risk_contributions': Risk contribution per asset,
            'dendrogram': Linkage matrix for visualization,
            'clusters': Hierarchical cluster assignments,
            'portfolio_metrics': Metrics (vol, CVaR, diversification),
            'risk_measure': Risk measure used
        }

    Reference:
        Raffinot, T. (2017). "Hierarchical Clustering-Based Asset Allocation"
        Journal of Portfolio Management
    """
    if cov_matrix is None:
        cov_matrix = returns.cov().values

    n_assets = len(returns.columns)

    logger.info(f"Running HERC on {n_assets} assets using {linkage_method} linkage, "
                f"risk measure: {risk_measure}")

    # Step 1: Tree Clustering (same as HRP)
    corr_matrix = returns.corr().values
    dist_matrix = np.sqrt(0.5 * (1 - corr_matrix))

    # Perform hierarchical clustering
    link = linkage(squareform(dist_matrix), method=linkage_method)

    # Step 2: Quasi-diagonalization (same as HRP)
    sort_ix = _quasi_diag(link)
    sorted_returns = returns.iloc[:, sort_ix]
    sorted_cov = cov_matrix[np.ix_(sort_ix, sort_ix)]

    logger.info(f"Assets reordered: {sorted_returns.columns.tolist()}")

    # Step 3: Recursive Bisection with Equal Risk Contribution
    # This is the key difference from HRP!
    weights = _recursive_bisection_erc(
        sorted_cov,
        sorted_returns,
        risk_measure
    )

    # Unsort weights back to original order
    unsort_ix = np.argsort(sort_ix)
    final_weights = weights[unsort_ix]

    # Calculate risk contributions
    rc = calculate_risk_contribution(final_weights, cov_matrix)

    # Calculate portfolio metrics
    portfolio_vol = np.sqrt(final_weights @ cov_matrix @ final_weights)

    # CVaR if requested
    if risk_measure == 'cvar':
        cvar_results = calculate_cvar_contribution(final_weights, returns)
        portfolio_cvar = cvar_results['cvar']
    else:
        portfolio_cvar = None

    # Diversification ratio
    asset_vols = np.sqrt(np.diag(cov_matrix))
    weighted_avg_vol = final_weights @ asset_vols
    diversification_ratio = weighted_avg_vol / portfolio_vol if portfolio_vol > 0 else 1.0

    # Get cluster assignments
    clusters = _get_cluster_assignments(link, returns.columns)

    # Risk contribution concentration (lower is more equal)
    rc_concentration = np.std(rc['percentage_rc'])

    logger.info(f"HERC complete - Portfolio vol: {portfolio_vol:.4f}, "
                f"Diversification ratio: {diversification_ratio:.2f}, "
                f"RC concentration: {rc_concentration:.2f}")

    return {
        'weights': final_weights,
        'risk_contributions': rc['percentage_rc'],
        'dendrogram': link,
        'clusters': clusters,
        'portfolio_metrics': {
            'volatility': float(portfolio_vol * np.sqrt(252)),  # Annualized
            'cvar': float(portfolio_cvar) if portfolio_cvar else None,
            'diversification_ratio': float(diversification_ratio),
            'concentration': float(np.max(final_weights)),
            'rc_concentration': float(rc_concentration)
        },
        'risk_measure': risk_measure,
        'sorted_indices': sort_ix.tolist(),
        'method': 'herc'
    }


def _recursive_bisection_erc(cov_matrix: np.ndarray,
                              returns: pd.DataFrame,
                              risk_measure: str,
                              weights: np.ndarray = None) -> np.ndarray:
    """
    Recursive bisection to achieve equal risk contribution.

    Key Algorithm:
    At each split, we want: RC_left = RC_right

    Where:
    - RC = w × σ (for volatility) or w × CVaR (for tail risk)

    This gives us:
    - w_left × σ_left = w_right × σ_right
    - w_left + w_right = 1

    Solution:
    - w_left = σ_right / (σ_left + σ_right)
    - w_right = σ_left / (σ_left + σ_right)

    Args:
        cov_matrix: Covariance matrix (sorted)
        returns: Returns dataframe (sorted)
        risk_measure: 'volatility' or 'cvar'
        weights: Current weights (initialized if None)

    Returns:
        Optimal HERC weights
    """
    n = cov_matrix.shape[0]

    if weights is None:
        weights = np.ones(n)

    # Base case: single asset
    if n == 1:
        return weights

    # Split in half
    mid = n // 2

    # Left and right sub-clusters
    left_cov = cov_matrix[:mid, :mid]
    right_cov = cov_matrix[mid:, mid:]

    # Calculate risk of each sub-cluster using equal weights
    left_weights_temp = np.ones(mid) / mid
    right_weights_temp = np.ones(n - mid) / (n - mid)

    if risk_measure == 'volatility':
        # Cluster volatility
        left_risk = np.sqrt(left_weights_temp @ left_cov @ left_weights_temp)
        right_risk = np.sqrt(right_weights_temp @ right_cov @ right_weights_temp)

    elif risk_measure == 'cvar':
        # Cluster CVaR (tail risk)
        left_returns = returns.iloc[:, :mid]
        right_returns = returns.iloc[:, mid:]

        left_cvar = calculate_cvar_contribution(left_weights_temp, left_returns)
        right_cvar = calculate_cvar_contribution(right_weights_temp, right_returns)

        left_risk = abs(left_cvar['cvar'])
        right_risk = abs(right_cvar['cvar'])

    else:
        raise ValueError(f"Unknown risk measure: {risk_measure}")

    # Allocate to equalize risk contribution
    # We want: w_left × risk_left = w_right × risk_right
    # Subject to: w_left + w_right = 1
    #
    # Solving: w_left = risk_right / (risk_left + risk_right)
    total_risk = left_risk + right_risk

    if total_risk > 0:
        alpha_left = right_risk / total_risk
        alpha_right = left_risk / total_risk
    else:
        # Fallback to equal weights if both risks are zero
        alpha_left = 0.5
        alpha_right = 0.5

    # Update weights
    weights[:mid] *= alpha_left
    weights[mid:] *= alpha_right

    # Recurse on sub-clusters
    if mid > 1:
        weights[:mid] = _recursive_bisection_erc(
            left_cov,
            returns.iloc[:, :mid],
            risk_measure,
            weights[:mid]
        )
    if n - mid > 1:
        weights[mid:] = _recursive_bisection_erc(
            right_cov,
            returns.iloc[:, mid:],
            risk_measure,
            weights[mid:]
        )

    return weights


def herc_from_prices(prices: pd.DataFrame,
                     linkage_method: str = 'single',
                     risk_measure: str = 'volatility') -> dict:
    """
    Convenience function to run HERC directly from prices.

    Args:
        prices: Price dataframe
        linkage_method: Linkage method
        risk_measure: 'volatility' or 'cvar'

    Returns:
        HERC results
    """
    returns = prices.pct_change().dropna()
    return herc_portfolio(
        returns,
        linkage_method=linkage_method,
        risk_measure=risk_measure
    )


def herc_with_constraints(returns: pd.DataFrame,
                          min_weight: float = 0.0,
                          max_weight: float = 1.0,
                          risk_measure: str = 'volatility') -> dict:
    """
    HERC with weight constraints.

    Note: This is a post-hoc adjustment, not optimization with constraints.
    Weights are clipped and renormalized.

    Args:
        returns: Returns dataframe
        min_weight: Minimum weight per asset
        max_weight: Maximum weight per asset
        risk_measure: Risk measure

    Returns:
        HERC results with constrained weights
    """
    # Run standard HERC
    results = herc_portfolio(returns, risk_measure=risk_measure)

    # Clip weights
    weights = results['weights']
    weights = np.clip(weights, min_weight, max_weight)

    # Renormalize
    weights = weights / np.sum(weights)

    # Recalculate risk contributions
    cov_matrix = returns.cov().values
    rc = calculate_risk_contribution(weights, cov_matrix)

    results['weights'] = weights
    results['risk_contributions'] = rc['percentage_rc']
    results['constrained'] = True
    results['constraints'] = {
        'min_weight': min_weight,
        'max_weight': max_weight
    }

    return results
