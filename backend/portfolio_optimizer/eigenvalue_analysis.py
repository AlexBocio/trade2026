# eigenvalue_analysis.py - Eigenvalue diagnostics and analysis for covariance matrices

import numpy as np
import pandas as pd
from scipy.linalg import eigh
from typing import Dict, List
import logging

from random_matrix_theory import (
    marchenko_pastur_pdf,
    get_marchenko_pastur_bounds,
    compare_eigenvalue_distributions
)

logger = logging.getLogger(__name__)


def analyze_eigenvalues(cov_matrix: np.ndarray,
                        returns: pd.DataFrame = None) -> dict:
    """
    Comprehensive eigenvalue analysis of covariance matrix.

    Args:
        cov_matrix: Covariance matrix to analyze
        returns: Returns dataframe (optional, for RMT analysis)

    Returns:
        {
            'eigenvalues': List of eigenvalues (descending),
            'eigenvectors': Eigenvector matrix,
            'condition_number': Condition number,
            'effective_rank': Effective rank,
            'concentration_metrics': {...},
            'rmt_analysis': {...} (if returns provided)
        }
    """
    logger.info("Analyzing eigenvalue spectrum")

    # Get eigenvalues and eigenvectors
    eigenvalues, eigenvectors = eigh(cov_matrix)

    # Sort descending
    idx = eigenvalues.argsort()[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Basic metrics
    condition_number = eigenvalues[0] / eigenvalues[-1] if eigenvalues[-1] > 0 else np.inf
    total_variance = np.sum(eigenvalues)

    # Effective rank (entropy-based)
    eigenvalue_probs = eigenvalues / total_variance
    effective_rank = np.exp(-np.sum(eigenvalue_probs * np.log(eigenvalue_probs + 1e-10)))

    # Concentration metrics
    concentration_metrics = calculate_concentration_metrics(eigenvalues)

    # RMT analysis if returns provided
    rmt_analysis = None
    if returns is not None:
        T, N = returns.shape
        rmt_analysis = compare_eigenvalue_distributions(eigenvalues, T, N)

    result = {
        'eigenvalues': eigenvalues.tolist(),
        'n_eigenvalues': len(eigenvalues),
        'condition_number': float(condition_number),
        'effective_rank': float(effective_rank),
        'total_variance': float(total_variance),
        'concentration_metrics': concentration_metrics
    }

    if rmt_analysis:
        result['rmt_analysis'] = rmt_analysis

    return result


def calculate_concentration_metrics(eigenvalues: np.ndarray) -> dict:
    """
    Calculate concentration of variance in top eigenvalues.

    Args:
        eigenvalues: Array of eigenvalues (sorted descending)

    Returns:
        Concentration metrics
    """
    total_variance = np.sum(eigenvalues)

    # Cumulative variance explained
    cumulative_variance = np.cumsum(eigenvalues) / total_variance

    # Find number of eigenvalues to explain thresholds
    pct_thresholds = [0.5, 0.7, 0.8, 0.9, 0.95, 0.99]
    n_components = {}

    for threshold in pct_thresholds:
        n = np.searchsorted(cumulative_variance, threshold) + 1
        n_components[f'n_for_{int(threshold*100)}pct'] = int(n)

    # Top k variance explained
    top_k_variance = {
        'top_1': float(eigenvalues[0] / total_variance),
        'top_3': float(np.sum(eigenvalues[:3]) / total_variance),
        'top_5': float(np.sum(eigenvalues[:5]) / total_variance),
        'top_10': float(np.sum(eigenvalues[:10]) / total_variance) if len(eigenvalues) >= 10 else 1.0
    }

    # Herfindahl-Hirschman Index (HHI) for concentration
    eigenvalue_shares = eigenvalues / total_variance
    hhi = np.sum(eigenvalue_shares**2)

    return {
        'n_components_for_variance': n_components,
        'top_k_variance_explained': top_k_variance,
        'herfindahl_index': float(hhi),
        'cumulative_variance': cumulative_variance.tolist()
    }


def eigenvalue_plot_data(cov_matrix: np.ndarray,
                         returns: pd.DataFrame = None,
                         log_scale: bool = False) -> dict:
    """
    Prepare data for eigenvalue scree plot and MP comparison.

    Args:
        cov_matrix: Covariance matrix
        returns: Returns dataframe (for MP comparison)
        log_scale: Use log scale for eigenvalues

    Returns:
        Data ready for plotting
    """
    # Get eigenvalues
    eigenvalues = np.linalg.eigvalsh(cov_matrix)
    eigenvalues = np.sort(eigenvalues)[::-1]

    # Apply log scale if requested
    if log_scale:
        eigenvalues_plot = np.log(eigenvalues + 1e-10)
    else:
        eigenvalues_plot = eigenvalues

    plot_data = {
        'eigenvalue_index': list(range(1, len(eigenvalues) + 1)),
        'eigenvalues': eigenvalues_plot.tolist(),
        'eigenvalues_original': eigenvalues.tolist(),
        'log_scale': log_scale
    }

    # Add Marchenko-Pastur bounds if returns provided
    if returns is not None:
        T, N = returns.shape
        mp_bounds = get_marchenko_pastur_bounds(T, N)

        # Normalize eigenvalues for MP comparison
        var_scale = np.mean(eigenvalues)
        eigenvalues_normalized = eigenvalues / var_scale

        plot_data['marchenko_pastur'] = {
            'lambda_min': mp_bounds['lambda_min'],
            'lambda_max': mp_bounds['lambda_max'],
            'q_ratio': mp_bounds['q'],
            'eigenvalues_normalized': eigenvalues_normalized.tolist(),
            'variance_scale': float(var_scale)
        }

        # Generate MP PDF curve
        x = np.linspace(0, mp_bounds['lambda_max'] * 1.5, 200)
        mp_pdf = marchenko_pastur_pdf(x, mp_bounds['q'], sigma=1.0)

        plot_data['marchenko_pastur']['pdf_x'] = x.tolist()
        plot_data['marchenko_pastur']['pdf_y'] = mp_pdf.tolist()

    return plot_data


def compare_before_after_cleaning(cov_before: np.ndarray,
                                  cov_after: np.ndarray,
                                  returns: pd.DataFrame = None) -> dict:
    """
    Compare eigenvalue spectra before and after cleaning.

    Args:
        cov_before: Original covariance matrix
        cov_after: Cleaned covariance matrix
        returns: Returns dataframe

    Returns:
        Comparison metrics and plot data
    """
    logger.info("Comparing eigenvalues before/after cleaning")

    # Analyze both
    analysis_before = analyze_eigenvalues(cov_before, returns)
    analysis_after = analyze_eigenvalues(cov_after, returns)

    # Calculate improvements
    improvements = {
        'condition_number_reduction': (
            analysis_before['condition_number'] / analysis_after['condition_number']
        ),
        'effective_rank_change': (
            analysis_after['effective_rank'] - analysis_before['effective_rank']
        ),
        'hhi_reduction': (
            analysis_before['concentration_metrics']['herfindahl_index'] -
            analysis_after['concentration_metrics']['herfindahl_index']
        )
    }

    # Side-by-side eigenvalues
    eigenvalues_before = np.array(analysis_before['eigenvalues'])
    eigenvalues_after = np.array(analysis_after['eigenvalues'])

    comparison_df = pd.DataFrame({
        'rank': range(1, len(eigenvalues_before) + 1),
        'eigenvalue_before': eigenvalues_before,
        'eigenvalue_after': eigenvalues_after,
        'ratio': eigenvalues_after / (eigenvalues_before + 1e-10)
    })

    return {
        'analysis_before': analysis_before,
        'analysis_after': analysis_after,
        'improvements': improvements,
        'eigenvalue_comparison': comparison_df.to_dict('records')
    }


def find_noise_signal_boundary(eigenvalues: np.ndarray,
                               T: int,
                               N: int,
                               method: str = 'marchenko_pastur') -> dict:
    """
    Find boundary between signal and noise eigenvalues.

    Args:
        eigenvalues: Array of eigenvalues
        T: Number of observations
        N: Number of variables
        method: 'marchenko_pastur' or 'elbow'

    Returns:
        {
            'boundary_index': Index separating signal from noise,
            'n_signal': Number of signal eigenvalues,
            'n_noise': Number of noise eigenvalues,
            'boundary_value': Eigenvalue at boundary
        }
    """
    if method == 'marchenko_pastur':
        # Use MP upper bound
        q = T / N
        mp_bounds = get_marchenko_pastur_bounds(T, N)

        # Normalize eigenvalues
        var_scale = np.mean(eigenvalues)
        eigenvalues_normalized = eigenvalues / var_scale

        # Find first eigenvalue below MP bound
        above_bound = eigenvalues_normalized > mp_bounds['lambda_max']
        n_signal = np.sum(above_bound)

        if n_signal > 0:
            boundary_index = n_signal
            boundary_value = eigenvalues[n_signal - 1]
        else:
            boundary_index = 0
            boundary_value = eigenvalues[0]

    elif method == 'elbow':
        # Use elbow method (maximum curvature)
        n_signal = find_elbow_point(eigenvalues)
        boundary_index = n_signal
        boundary_value = eigenvalues[n_signal] if n_signal < len(eigenvalues) else eigenvalues[-1]

    else:
        raise ValueError(f"Unknown method: {method}")

    n_noise = N - n_signal

    return {
        'boundary_index': int(boundary_index),
        'n_signal': int(n_signal),
        'n_noise': int(n_noise),
        'boundary_value': float(boundary_value),
        'method': method
    }


def find_elbow_point(eigenvalues: np.ndarray) -> int:
    """
    Find elbow point in eigenvalue scree plot.

    Uses maximum curvature method.

    Args:
        eigenvalues: Array of eigenvalues (sorted descending)

    Returns:
        Index of elbow point
    """
    n = len(eigenvalues)

    # Normalize eigenvalues to [0, 1]
    eigenvalues_norm = (eigenvalues - eigenvalues.min()) / (eigenvalues.max() - eigenvalues.min() + 1e-10)

    # Calculate distances to line from first to last point
    x = np.arange(n)
    y = eigenvalues_norm

    # Line from (0, y[0]) to (n-1, y[-1])
    line_vec = np.array([n - 1, y[-1] - y[0]])
    line_len = np.linalg.norm(line_vec)

    if line_len == 0:
        return 1

    line_unitvec = line_vec / line_len

    # Vector from line start to each point
    vec_from_start = np.column_stack([x, y - y[0]])

    # Cross product gives perpendicular distance
    dist_to_line = np.abs(np.cross(vec_from_start, line_unitvec))

    # Elbow is at maximum distance
    elbow_idx = np.argmax(dist_to_line)

    return int(elbow_idx) + 1  # +1 because we return count, not index


def eigenportfolio_analysis(cov_matrix: np.ndarray,
                            asset_names: List[str],
                            n_components: int = 3) -> dict:
    """
    Analyze composition of eigenportfolios (principal components).

    Args:
        cov_matrix: Covariance matrix
        asset_names: List of asset names
        n_components: Number of top eigenportfolios to analyze

    Returns:
        Eigenportfolio loadings and interpretations
    """
    # Get eigenvalues and eigenvectors
    eigenvalues, eigenvectors = eigh(cov_matrix)

    # Sort descending
    idx = eigenvalues.argsort()[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    eigenportfolios = []

    for i in range(min(n_components, len(eigenvalues))):
        # Get loadings for this eigenportfolio
        loadings = eigenvectors[:, i]

        # Create DataFrame with loadings
        loadings_df = pd.DataFrame({
            'asset': asset_names,
            'loading': loadings,
            'abs_loading': np.abs(loadings)
        }).sort_values('abs_loading', ascending=False)

        # Variance explained
        variance_explained = eigenvalues[i] / np.sum(eigenvalues)

        eigenportfolios.append({
            'component': i + 1,
            'eigenvalue': float(eigenvalues[i]),
            'variance_explained': float(variance_explained),
            'loadings': loadings_df.to_dict('records'),
            'top_positive': loadings_df[loadings_df['loading'] > 0].head(5).to_dict('records'),
            'top_negative': loadings_df[loadings_df['loading'] < 0].head(5).to_dict('records')
        })

    return {
        'eigenportfolios': eigenportfolios,
        'total_variance': float(np.sum(eigenvalues))
    }


def validate_cleaning_quality(cov_original: np.ndarray,
                              cov_cleaned: np.ndarray) -> dict:
    """
    Validate quality of covariance cleaning.

    Checks:
    - Matrix remains PSD
    - Condition number improved
    - Reasonable variance preserved
    - Correlation structure not destroyed

    Args:
        cov_original: Original covariance matrix
        cov_cleaned: Cleaned covariance matrix

    Returns:
        Validation metrics and warnings
    """
    warnings = []

    # Check PSD
    eigenvalues_cleaned = np.linalg.eigvalsh(cov_cleaned)
    is_psd = np.all(eigenvalues_cleaned > -1e-10)

    if not is_psd:
        warnings.append("Cleaned matrix is not positive semi-definite")

    # Check condition number
    eigenvalues_original = np.linalg.eigvalsh(cov_original)
    cond_original = eigenvalues_original.max() / eigenvalues_original.min()
    cond_cleaned = eigenvalues_cleaned.max() / eigenvalues_cleaned.min()

    if cond_cleaned > cond_original:
        warnings.append("Condition number increased (cleaning may have degraded matrix)")

    # Check variance preservation
    var_original = np.trace(cov_original)
    var_cleaned = np.trace(cov_cleaned)
    var_ratio = var_cleaned / var_original

    if var_ratio < 0.5:
        warnings.append(f"More than 50% variance removed (ratio={var_ratio:.2f})")
    elif var_ratio > 1.5:
        warnings.append(f"Variance increased significantly (ratio={var_ratio:.2f})")

    # Check frobenius norm distance
    frobenius_distance = np.linalg.norm(cov_original - cov_cleaned, 'fro')
    frobenius_ratio = frobenius_distance / np.linalg.norm(cov_original, 'fro')

    return {
        'is_positive_definite': bool(is_psd),
        'condition_number_original': float(cond_original),
        'condition_number_cleaned': float(cond_cleaned),
        'condition_improved': bool(cond_cleaned < cond_original),
        'variance_ratio': float(var_ratio),
        'frobenius_distance': float(frobenius_distance),
        'frobenius_ratio': float(frobenius_ratio),
        'warnings': warnings,
        'quality_score': _calculate_quality_score(cond_cleaned, var_ratio, is_psd)
    }


def _calculate_quality_score(condition_number: float,
                             variance_ratio: float,
                             is_psd: bool) -> float:
    """Calculate overall quality score (0-100) for cleaned matrix."""
    score = 100.0

    # Penalize high condition number
    if condition_number > 100:
        score -= min(30, (condition_number - 100) / 10)

    # Penalize variance loss/gain
    if variance_ratio < 0.8:
        score -= (0.8 - variance_ratio) * 50
    elif variance_ratio > 1.2:
        score -= (variance_ratio - 1.2) * 50

    # Penalize non-PSD
    if not is_psd:
        score -= 50

    return max(0.0, float(score))
