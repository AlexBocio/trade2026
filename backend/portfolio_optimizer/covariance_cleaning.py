# covariance_cleaning.py - Advanced covariance matrix cleaning techniques
# Detoning, detrending, and combined cleaning methods

import numpy as np
import pandas as pd
from scipy.linalg import eigh
import logging

logger = logging.getLogger(__name__)


def detone_covariance(cov_matrix: np.ndarray,
                      returns: pd.DataFrame,
                      n_components: int = 1) -> dict:
    """
    Remove market eigenvalue (detoning) to reduce concentration risk.

    The largest eigenvalue typically represents "the market" and creates
    concentration. Removing it produces more diversified portfolios.

    Args:
        cov_matrix: Raw covariance matrix (n_assets x n_assets)
        returns: Returns dataframe (for validation)
        n_components: Number of top eigenvalues to remove (usually 1)

    Returns:
        {
            'detoned_cov': Cleaned covariance matrix,
            'removed_eigenvalues': List of removed eigenvalues,
            'removed_eigenvectors': Corresponding eigenvectors,
            'variance_explained_removed': % variance removed,
            'condition_number_before': float,
            'condition_number_after': float
        }

    Reference:
        "Advances in Financial Machine Learning" by Marcos Lopez de Prado,
        Chapter 2: "Denoising and Detoning"
    """
    logger.info(f"Detoning covariance matrix (removing top {n_components} eigenvalues)")

    # Get eigenvalues and eigenvectors
    eigenvalues, eigenvectors = eigh(cov_matrix)

    # Sort descending
    idx = eigenvalues.argsort()[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Remove top n_components (market component)
    removed_eigenvalues = eigenvalues[:n_components].copy()
    removed_eigenvectors = eigenvectors[:, :n_components].copy()

    # Set removed eigenvalues to mean of remaining
    eigenvalues_detoned = eigenvalues.copy()
    eigenvalues_detoned[:n_components] = np.mean(eigenvalues[n_components:])

    # Reconstruct covariance matrix
    detoned_cov = eigenvectors @ np.diag(eigenvalues_detoned) @ eigenvectors.T

    # Ensure symmetry
    detoned_cov = (detoned_cov + detoned_cov.T) / 2

    # Calculate metrics
    variance_explained_removed = np.sum(removed_eigenvalues) / np.sum(eigenvalues)
    condition_before = eigenvalues[0] / eigenvalues[-1]
    condition_after = eigenvalues_detoned[0] / eigenvalues_detoned[-1]

    logger.info(f"Detoning complete: Variance removed={variance_explained_removed:.2%}, "
                f"Condition number: {condition_before:.2f} -> {condition_after:.2f}")

    return {
        'detoned_cov': detoned_cov,
        'removed_eigenvalues': removed_eigenvalues.tolist(),
        'removed_eigenvectors': removed_eigenvectors,
        'variance_explained_removed': float(variance_explained_removed),
        'condition_number_before': float(condition_before),
        'condition_number_after': float(condition_after),
        'eigenvalues_original': eigenvalues.tolist(),
        'eigenvalues_detoned': eigenvalues_detoned.tolist()
    }


def detrend_covariance(cov_matrix: np.ndarray,
                       returns: pd.DataFrame,
                       lookback: int = 20) -> dict:
    """
    Remove serial correlation (detrending) to eliminate autocorrelation effects.

    Serial correlation in returns creates spurious correlations in covariance.
    This removes autoregressive components.

    Args:
        cov_matrix: Raw covariance matrix
        returns: Returns dataframe
        lookback: Lookback window for AR estimation

    Returns:
        {
            'detrended_cov': Cleaned covariance matrix,
            'ar_coefficients': Estimated AR(1) coefficients per asset,
            'autocorr_before': Average autocorrelation before,
            'autocorr_after': Average autocorrelation after
        }
    """
    logger.info(f"Detrending covariance matrix (lookback={lookback})")

    n_assets = len(returns.columns)
    detrended_returns = returns.copy()
    ar_coeffs = {}

    # Estimate and remove AR(1) for each asset
    for col in returns.columns:
        series = returns[col].dropna()
        if len(series) > lookback:
            # Simple AR(1): r_t = α + β*r_{t-1} + ε_t
            lagged = series.shift(1).dropna()
            current = series.iloc[1:]

            # Align indices
            common_idx = lagged.index.intersection(current.index)
            lagged = lagged.loc[common_idx]
            current = current.loc[common_idx]

            if len(lagged) > 0:
                # OLS estimation
                X = np.column_stack([np.ones(len(lagged)), lagged.values])
                y = current.values

                try:
                    beta = np.linalg.lstsq(X, y, rcond=None)[0]
                    ar_coeffs[col] = float(beta[1])

                    # Remove AR component: ε_t = r_t - β*r_{t-1}
                    residuals = current - beta[1] * lagged
                    detrended_returns.loc[residuals.index, col] = residuals
                except np.linalg.LinAlgError:
                    logger.warning(f"Failed to estimate AR(1) for {col}, skipping")
                    ar_coeffs[col] = 0.0

    # Calculate detrended covariance
    detrended_cov = detrended_returns.cov().values

    # Measure autocorrelation before/after
    autocorr_before = returns.apply(lambda x: x.autocorr(lag=1)).mean()
    autocorr_after = detrended_returns.apply(lambda x: x.autocorr(lag=1)).mean()

    logger.info(f"Detrending complete: Autocorr {autocorr_before:.4f} -> {autocorr_after:.4f}")

    return {
        'detrended_cov': detrended_cov,
        'ar_coefficients': ar_coeffs,
        'autocorr_before': float(autocorr_before),
        'autocorr_after': float(autocorr_after),
        'detrended_returns': detrended_returns
    }


def detone_and_detrend(cov_matrix: np.ndarray,
                       returns: pd.DataFrame,
                       n_detone: int = 1,
                       lookback: int = 20) -> dict:
    """
    Apply both detoning and detrending in sequence.

    Best practice: Detrend first, then detone.

    Args:
        cov_matrix: Raw covariance matrix
        returns: Returns dataframe
        n_detone: Number of eigenvalues to remove in detoning
        lookback: Lookback window for detrending

    Returns:
        Complete results from both operations plus final covariance
    """
    logger.info("Applying combined detone and detrend")

    # Step 1: Detrend
    detrend_results = detrend_covariance(cov_matrix, returns, lookback)

    # Step 2: Detone the detrended covariance
    detone_results = detone_covariance(
        detrend_results['detrended_cov'],
        detrend_results['detrended_returns'],
        n_detone
    )

    # Calculate improvement metrics
    condition_reduction = (
        detone_results['condition_number_before'] /
        detone_results['condition_number_after']
    )

    autocorr_reduction = (
        detrend_results['autocorr_before'] -
        detrend_results['autocorr_after']
    )

    return {
        'final_cov': detone_results['detoned_cov'],
        'detrend_results': {
            k: v for k, v in detrend_results.items()
            if k != 'detrended_returns'
        },
        'detone_results': {
            k: v for k, v in detone_results.items()
            if k != 'removed_eigenvectors'
        },
        'improvement_metrics': {
            'condition_number_reduction': float(condition_reduction),
            'market_variance_removed': detone_results['variance_explained_removed'],
            'autocorr_reduction': float(autocorr_reduction)
        }
    }


def shrink_covariance(cov_matrix: np.ndarray,
                      shrinkage: float = 0.1) -> np.ndarray:
    """
    Apply Ledoit-Wolf shrinkage to covariance matrix.

    Shrinks sample covariance toward identity matrix to reduce estimation error.

    Args:
        cov_matrix: Raw covariance matrix
        shrinkage: Shrinkage intensity (0=no shrinkage, 1=full shrinkage to identity)

    Returns:
        Shrunk covariance matrix
    """
    n = cov_matrix.shape[0]

    # Target: scaled identity matrix
    target = np.eye(n) * np.trace(cov_matrix) / n

    # Shrink toward target
    shrunk_cov = (1 - shrinkage) * cov_matrix + shrinkage * target

    return shrunk_cov


def validate_covariance_matrix(cov_matrix: np.ndarray) -> dict:
    """
    Validate that covariance matrix is positive semi-definite and well-conditioned.

    Args:
        cov_matrix: Covariance matrix to validate

    Returns:
        {
            'is_symmetric': bool,
            'is_positive_definite': bool,
            'condition_number': float,
            'min_eigenvalue': float,
            'max_eigenvalue': float,
            'is_valid': bool
        }
    """
    # Check symmetry
    is_symmetric = np.allclose(cov_matrix, cov_matrix.T)

    # Get eigenvalues
    eigenvalues = np.linalg.eigvalsh(cov_matrix)

    # Check positive definiteness
    is_positive_definite = np.all(eigenvalues > -1e-10)  # Allow small numerical errors

    # Condition number
    condition_number = eigenvalues.max() / eigenvalues.min() if eigenvalues.min() > 0 else np.inf

    # Overall validity
    is_valid = is_symmetric and is_positive_definite and condition_number < 1e10

    return {
        'is_symmetric': bool(is_symmetric),
        'is_positive_definite': bool(is_positive_definite),
        'condition_number': float(condition_number),
        'min_eigenvalue': float(eigenvalues.min()),
        'max_eigenvalue': float(eigenvalues.max()),
        'is_valid': bool(is_valid)
    }


def nearest_psd(cov_matrix: np.ndarray, epsilon: float = 1e-10) -> np.ndarray:
    """
    Find nearest positive semi-definite matrix.

    If covariance matrix is not PSD (due to numerical errors or cleaning),
    this finds the closest PSD matrix in Frobenius norm.

    Args:
        cov_matrix: Input covariance matrix
        epsilon: Minimum eigenvalue threshold

    Returns:
        Nearest PSD matrix
    """
    # Ensure symmetry
    cov_symmetric = (cov_matrix + cov_matrix.T) / 2

    # Get eigendecomposition
    eigenvalues, eigenvectors = eigh(cov_symmetric)

    # Clip negative eigenvalues to epsilon
    eigenvalues_clipped = np.maximum(eigenvalues, epsilon)

    # Reconstruct
    psd_matrix = eigenvectors @ np.diag(eigenvalues_clipped) @ eigenvectors.T

    return psd_matrix
