# hrp.py - Hierarchical Risk Parity Implementation
# Baseline HRP for comparison with HERC

from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import squareform
import numpy as np
import pandas as pd
import logging
from risk_contribution import calculate_risk_contribution

logger = logging.getLogger(__name__)


def hrp_portfolio(returns: pd.DataFrame,
                  cov_matrix: np.ndarray = None,
                  linkage_method: str = 'single') -> dict:
    """
    Hierarchical Risk Parity portfolio optimization.

    HRP Algorithm (Lopez de Prado, 2016):
    1. Tree Clustering: Use hierarchical clustering on correlation matrix
    2. Quasi-Diagonalization: Reorder assets to minimize distance
    3. Recursive Bisection: Allocate inversely proportional to cluster variance

    Args:
        returns: Returns dataframe (T × N)
        cov_matrix: Covariance matrix (if None, computed from returns)
        linkage_method: 'single', 'complete', 'average', 'ward'

    Returns:
        {
            'weights': Portfolio weights,
            'risk_contributions': Risk contribution per asset,
            'dendrogram': Linkage matrix for visualization,
            'clusters': Cluster assignments,
            'portfolio_metrics': Volatility and diversification metrics
        }

    Reference:
        Lopez de Prado, M. (2016). "Building Diversified Portfolios that
        Outperform Out of Sample". Journal of Portfolio Management.
    """
    if cov_matrix is None:
        cov_matrix = returns.cov().values

    n_assets = len(returns.columns)

    logger.info(f"Running HRP on {n_assets} assets using {linkage_method} linkage")

    # Step 1: Tree Clustering
    # Convert correlation to distance matrix
    corr_matrix = returns.corr().values

    # Distance = sqrt(0.5 * (1 - correlation))
    # This ensures: perfect correlation (1) = distance 0, no correlation (0) = distance 0.707
    dist_matrix = np.sqrt(0.5 * (1 - corr_matrix))

    # Perform hierarchical clustering
    link = linkage(squareform(dist_matrix), method=linkage_method)

    # Step 2: Quasi-Diagonalization
    # Reorder assets to group similar ones together
    sort_ix = _quasi_diag(link)
    sorted_cov = cov_matrix[np.ix_(sort_ix, sort_ix)]

    logger.info(f"Assets reordered: {returns.columns[sort_ix].tolist()}")

    # Step 3: Recursive Bisection
    # Allocate inversely proportional to variance
    weights = _recursive_bisection_hrp(sorted_cov)

    # Unsort weights back to original order
    unsort_ix = np.argsort(sort_ix)
    final_weights = weights[unsort_ix]

    # Calculate risk contributions
    rc = calculate_risk_contribution(final_weights, cov_matrix)

    # Portfolio metrics
    portfolio_vol = np.sqrt(final_weights @ cov_matrix @ final_weights)

    # Diversification ratio
    asset_vols = np.sqrt(np.diag(cov_matrix))
    weighted_avg_vol = final_weights @ asset_vols
    diversification_ratio = weighted_avg_vol / portfolio_vol if portfolio_vol > 0 else 1.0

    # Get cluster assignments
    clusters = _get_cluster_assignments(link, returns.columns)

    logger.info(f"HRP complete - Portfolio vol: {portfolio_vol:.4f}, "
                f"Diversification ratio: {diversification_ratio:.2f}")

    return {
        'weights': final_weights,
        'risk_contributions': rc['percentage_rc'],
        'dendrogram': link,
        'clusters': clusters,
        'portfolio_metrics': {
            'volatility': float(portfolio_vol * np.sqrt(252)),  # Annualized
            'diversification_ratio': float(diversification_ratio),
            'concentration': float(np.max(final_weights))  # Max weight
        },
        'sorted_indices': sort_ix.tolist(),
        'method': 'hrp'
    }


def _quasi_diag(link: np.ndarray) -> np.ndarray:
    """
    Quasi-diagonalization: reorder assets by hierarchical clustering.

    This reorganizes the covariance matrix so that similar assets
    are close together, creating a block-diagonal structure.

    Args:
        link: Linkage matrix from scipy.cluster.hierarchy.linkage

    Returns:
        Indices that minimize distance between nearby assets
    """
    link = link.astype(int)
    sort_ix = pd.Series([link[-1, 0], link[-1, 1]])
    num_items = link[-1, 3]  # Number of original items

    # Expand clusters into individual items
    while sort_ix.max() >= num_items:
        sort_ix.index = range(0, sort_ix.shape[0] * 2, 2)
        df = sort_ix[sort_ix >= num_items]
        i = df.index
        j = df.values - num_items

        # Replace cluster index with its two children
        sort_ix[i] = link[j, 0]
        df = pd.Series(link[j, 1], index=i + 1)
        sort_ix = pd.concat([sort_ix, df]).sort_index()
        sort_ix.index = range(sort_ix.shape[0])

    return sort_ix.values.astype(int)


def _recursive_bisection_hrp(cov_matrix: np.ndarray,
                             weights: np.ndarray = None) -> np.ndarray:
    """
    Recursive bisection to allocate inversely proportional to variance.

    At each split:
    1. Divide cluster into two sub-clusters
    2. Allocate inversely proportional to cluster variance
    3. Recurse within each sub-cluster

    Args:
        cov_matrix: Covariance matrix (already sorted by quasi-diag)
        weights: Current weights (initialized to ones if None)

    Returns:
        Optimal HRP weights
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

    # Calculate cluster variances (inverse-variance weighted)
    left_inv_var = _get_cluster_var(left_cov)
    right_inv_var = _get_cluster_var(right_cov)

    # Allocate inversely proportional to variance
    # Lower variance → higher weight
    alpha_left = 1.0 - left_inv_var / (left_inv_var + right_inv_var)
    alpha_right = 1.0 - alpha_left

    # Update weights
    weights[:mid] *= alpha_left
    weights[mid:] *= alpha_right

    # Recurse on sub-clusters
    if mid > 1:
        weights[:mid] = _recursive_bisection_hrp(left_cov, weights[:mid])
    if n - mid > 1:
        weights[mid:] = _recursive_bisection_hrp(right_cov, weights[mid:])

    return weights


def _get_cluster_var(cov_matrix: np.ndarray) -> float:
    """
    Calculate cluster variance using inverse-variance weighting.

    For a cluster with covariance matrix Σ:
    - Weights: w_i = (1/σ_i²) / Σ(1/σ_j²)
    - Cluster variance: w^T Σ w

    Args:
        cov_matrix: Covariance matrix of cluster

    Returns:
        Cluster variance
    """
    # Get diagonal (individual variances)
    variances = np.diag(cov_matrix)

    # Inverse-variance weights
    inv_var = 1.0 / variances
    weights = inv_var / np.sum(inv_var)

    # Cluster variance
    cluster_var = weights @ cov_matrix @ weights

    return float(cluster_var)


def _get_cluster_assignments(link: np.ndarray,
                             columns: pd.Index,
                             n_clusters: int = 5) -> dict:
    """
    Extract cluster assignments from linkage matrix.

    Args:
        link: Linkage matrix
        columns: Asset names
        n_clusters: Number of clusters to extract

    Returns:
        Dict mapping cluster_id -> list of tickers
    """
    # Get cluster labels
    clusters = fcluster(link, n_clusters, criterion='maxclust')

    cluster_dict = {}
    for cluster_id in np.unique(clusters):
        mask = clusters == cluster_id
        cluster_dict[int(cluster_id)] = columns[mask].tolist()

    return cluster_dict


def hrp_from_prices(prices: pd.DataFrame,
                    linkage_method: str = 'single') -> dict:
    """
    Convenience function to run HRP directly from prices.

    Args:
        prices: Price dataframe
        linkage_method: Linkage method

    Returns:
        HRP results
    """
    returns = prices.pct_change().dropna()
    return hrp_portfolio(returns, linkage_method=linkage_method)
