# random_matrix_theory.py - Random Matrix Theory filtering for covariance matrices
# Marchenko-Pastur distribution and RMT-based denoising

import numpy as np
import pandas as pd
from scipy.linalg import eigh
import logging

logger = logging.getLogger(__name__)


def marchenko_pastur_pdf(x: np.ndarray, q: float, sigma: float = 1.0) -> np.ndarray:
    """
    Marchenko-Pastur probability density function.

    Describes eigenvalue distribution of random correlation matrices.

    Args:
        x: Eigenvalue points
        q: T/N ratio (observations / variables)
        sigma: Variance scale

    Returns:
        PDF values at x

    Reference:
        Marchenko, V. A., & Pastur, L. A. (1967).
        "Distribution of eigenvalues for some sets of random matrices"
    """
    lambda_min = sigma * (1 - np.sqrt(1/q))**2
    lambda_max = sigma * (1 + np.sqrt(1/q))**2

    pdf = np.zeros_like(x, dtype=float)
    mask = (x >= lambda_min) & (x <= lambda_max)

    if np.any(mask):
        pdf[mask] = (q / (2 * np.pi * sigma * x[mask])) * np.sqrt(
            (lambda_max - x[mask]) * (x[mask] - lambda_min)
        )

    return pdf


def get_marchenko_pastur_bounds(T: int, N: int, sigma: float = 1.0) -> dict:
    """
    Calculate Marchenko-Pastur eigenvalue bounds.

    Args:
        T: Number of observations (time periods)
        N: Number of variables (assets)
        sigma: Variance scale

    Returns:
        {
            'lambda_min': Lower bound,
            'lambda_max': Upper bound,
            'q': T/N ratio
        }
    """
    q = T / N

    lambda_min = sigma * (1 - np.sqrt(1/q))**2
    lambda_max = sigma * (1 + np.sqrt(1/q))**2

    return {
        'lambda_min': float(lambda_min),
        'lambda_max': float(lambda_max),
        'q': float(q)
    }


def rmt_denoise(cov_matrix: np.ndarray,
                returns: pd.DataFrame,
                q: float = None,
                method: str = 'targeted') -> dict:
    """
    Denoise covariance matrix using Random Matrix Theory.

    Eigenvalues below the Marchenko-Pastur upper bound are considered noise
    and replaced with their average (or removed).

    Args:
        cov_matrix: Raw covariance matrix
        returns: Returns dataframe (for T/N ratio)
        q: T/N ratio (auto-calculated if None)
        method: 'targeted' (replace with avg) or 'zero' (set to zero)

    Returns:
        {
            'denoised_cov': Cleaned covariance matrix,
            'n_signal_eigenvalues': Number of signal eigenvalues kept,
            'n_noise_eigenvalues': Number of noise eigenvalues cleaned,
            'lambda_max': Marchenko-Pastur upper bound,
            'eigenvalues_original': List of original eigenvalues,
            'eigenvalues_denoised': List of denoised eigenvalues
        }

    Reference:
        "Cleaning large correlation matrices: Tools from Random Matrix Theory"
        by Bouchaud, Potters (2009)
    """
    T, N = returns.shape

    if q is None:
        q = T / N

    logger.info(f"RMT denoising: T={T}, N={N}, q={q:.2f}")

    # Get eigenvalues and eigenvectors
    eigenvalues, eigenvectors = eigh(cov_matrix)

    # Sort descending
    idx = eigenvalues.argsort()[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Normalize to correlation matrix for MP bounds
    # (Marchenko-Pastur assumes correlation matrix)
    var_scale = np.mean(eigenvalues)
    eigenvalues_normalized = eigenvalues / var_scale

    # Marchenko-Pastur upper bound (for correlation matrix, sigma=1)
    lambda_max_normalized = (1 + np.sqrt(1/q))**2

    # Identify signal vs noise eigenvalues
    signal_mask = eigenvalues_normalized > lambda_max_normalized
    n_signal = np.sum(signal_mask)
    n_noise = N - n_signal

    logger.info(f"RMT: Found {n_signal} signal eigenvalues, {n_noise} noise eigenvalues")
    logger.info(f"MP upper bound (normalized): {lambda_max_normalized:.4f}")

    # Replace noise eigenvalues
    eigenvalues_denoised = eigenvalues.copy()

    if n_noise > 0:
        if method == 'targeted':
            # Replace with average of noise eigenvalues
            noise_avg = np.mean(eigenvalues[~signal_mask])
            eigenvalues_denoised[~signal_mask] = noise_avg
            logger.info(f"Replaced noise eigenvalues with average: {noise_avg:.6f}")

        elif method == 'zero':
            # Set noise eigenvalues to small positive value
            eigenvalues_denoised[~signal_mask] = 1e-6
            logger.info("Set noise eigenvalues to near-zero")

        elif method == 'min':
            # Set noise eigenvalues to minimum signal eigenvalue
            if n_signal > 0:
                min_signal = eigenvalues[signal_mask].min()
                eigenvalues_denoised[~signal_mask] = min_signal
                logger.info(f"Set noise eigenvalues to min signal: {min_signal:.6f}")
    else:
        logger.warning("No noise eigenvalues found - all eigenvalues above MP bound")

    # Reconstruct covariance matrix
    denoised_cov = eigenvectors @ np.diag(eigenvalues_denoised) @ eigenvectors.T

    # Ensure symmetry and PSD
    denoised_cov = (denoised_cov + denoised_cov.T) / 2

    # Scale back to original variance
    lambda_max_original = lambda_max_normalized * var_scale

    return {
        'denoised_cov': denoised_cov,
        'n_signal_eigenvalues': int(n_signal),
        'n_noise_eigenvalues': int(n_noise),
        'lambda_max': float(lambda_max_original),
        'lambda_max_normalized': float(lambda_max_normalized),
        'eigenvalues_original': eigenvalues.tolist(),
        'eigenvalues_denoised': eigenvalues_denoised.tolist(),
        'q_ratio': float(q),
        'variance_scale': float(var_scale)
    }


def constant_residual_eigenvalue(cov_matrix: np.ndarray,
                                 returns: pd.DataFrame,
                                 alpha: float = 0.0) -> dict:
    """
    Set all eigenvalues below max random eigenvalue to constant.

    More aggressive than standard RMT denoising.
    Based on constant residual eigenvalue method.

    Args:
        cov_matrix: Raw covariance matrix
        returns: Returns dataframe
        alpha: Fraction of average eigenvalue to use (0=zero, 1=average)

    Returns:
        Similar to rmt_denoise
    """
    T, N = returns.shape
    q = T / N

    # Get eigenvalues and eigenvectors
    eigenvalues, eigenvectors = eigh(cov_matrix)
    idx = eigenvalues.argsort()[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Normalize
    var_scale = np.mean(eigenvalues)
    eigenvalues_normalized = eigenvalues / var_scale

    # MP bound
    lambda_max_normalized = (1 + np.sqrt(1/q))**2

    # Identify signal
    signal_mask = eigenvalues_normalized > lambda_max_normalized
    n_signal = np.sum(signal_mask)

    # Set residual eigenvalue
    eigenvalues_cleaned = eigenvalues.copy()

    if n_signal < N:
        # Average of non-signal eigenvalues
        residual_avg = np.mean(eigenvalues[~signal_mask])

        # Set all non-signal to constant
        eigenvalues_cleaned[~signal_mask] = alpha * residual_avg

    # Reconstruct
    cleaned_cov = eigenvectors @ np.diag(eigenvalues_cleaned) @ eigenvectors.T
    cleaned_cov = (cleaned_cov + cleaned_cov.T) / 2

    return {
        'cleaned_cov': cleaned_cov,
        'n_signal': int(n_signal),
        'n_noise': int(N - n_signal),
        'residual_eigenvalue': float(alpha * residual_avg) if n_signal < N else 0.0,
        'eigenvalues_original': eigenvalues.tolist(),
        'eigenvalues_cleaned': eigenvalues_cleaned.tolist()
    }


def generate_random_correlation_matrix(N: int, T: int, seed: int = None) -> np.ndarray:
    """
    Generate random correlation matrix following Marchenko-Pastur distribution.

    Useful for testing and validation.

    Args:
        N: Number of assets
        T: Number of time periods
        seed: Random seed

    Returns:
        Random correlation matrix (N x N)
    """
    if seed is not None:
        np.random.seed(seed)

    # Generate random returns
    random_returns = np.random.randn(T, N)

    # Calculate correlation matrix
    correlation_matrix = np.corrcoef(random_returns, rowvar=False)

    return correlation_matrix


def empirical_eigenvalue_distribution(eigenvalues: np.ndarray,
                                     bins: int = 50) -> dict:
    """
    Calculate empirical eigenvalue distribution (histogram).

    Args:
        eigenvalues: Array of eigenvalues
        bins: Number of histogram bins

    Returns:
        {
            'bin_centers': Centers of histogram bins,
            'density': Density values (normalized histogram),
            'counts': Raw counts
        }
    """
    counts, bin_edges = np.histogram(eigenvalues, bins=bins, density=False)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Normalize to PDF
    bin_width = bin_edges[1] - bin_edges[0]
    density = counts / (len(eigenvalues) * bin_width)

    return {
        'bin_centers': bin_centers.tolist(),
        'density': density.tolist(),
        'counts': counts.tolist(),
        'bin_edges': bin_edges.tolist()
    }


def compare_eigenvalue_distributions(eigenvalues: np.ndarray,
                                    T: int,
                                    N: int,
                                    bins: int = 50) -> dict:
    """
    Compare empirical eigenvalue distribution to Marchenko-Pastur theory.

    Args:
        eigenvalues: Empirical eigenvalues
        T: Number of observations
        N: Number of variables
        bins: Number of bins for histogram

    Returns:
        {
            'empirical': Empirical distribution,
            'theoretical': Theoretical MP distribution,
            'mp_bounds': MP bounds,
            'n_above_bound': Number of eigenvalues above MP bound
        }
    """
    q = T / N

    # Normalize eigenvalues
    var_scale = np.mean(eigenvalues)
    eigenvalues_normalized = eigenvalues / var_scale

    # Empirical distribution
    empirical = empirical_eigenvalue_distribution(eigenvalues_normalized, bins)

    # Theoretical MP distribution
    x = np.array(empirical['bin_centers'])
    mp_pdf = marchenko_pastur_pdf(x, q, sigma=1.0)

    # MP bounds
    mp_bounds = get_marchenko_pastur_bounds(T, N, sigma=1.0)

    # Count eigenvalues above bound
    n_above_bound = np.sum(eigenvalues_normalized > mp_bounds['lambda_max'])

    return {
        'empirical': empirical,
        'theoretical': {
            'x': x.tolist(),
            'pdf': mp_pdf.tolist()
        },
        'mp_bounds': mp_bounds,
        'n_above_bound': int(n_above_bound),
        'n_below_bound': int(N - n_above_bound),
        'variance_scale': float(var_scale)
    }


def fitHermitPoly(eigenvalues: np.ndarray,
                  q: float,
                  max_order: int = 4) -> dict:
    """
    Fit Hermite polynomial to eigenvalue distribution.

    Used for advanced RMT analysis beyond Marchenko-Pastur.

    Args:
        eigenvalues: Array of eigenvalues
        q: T/N ratio
        max_order: Maximum polynomial order

    Returns:
        Hermite polynomial coefficients
    """
    # This is a placeholder for advanced RMT techniques
    # Full implementation would require Hermite polynomial fitting

    return {
        'note': 'Hermite polynomial fitting not fully implemented',
        'q': float(q),
        'n_eigenvalues': len(eigenvalues)
    }
