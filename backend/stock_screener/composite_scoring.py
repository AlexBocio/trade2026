# composite_scoring.py - Multi-Factor Composite Scoring and Ranking
# Z-score normalization, weighted scoring, and stock ranking

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def normalize_factors(factor_data: pd.DataFrame,
                     factor_names: List[str],
                     method: str = 'zscore') -> pd.DataFrame:
    """
    Normalize factors across the universe.

    Args:
        factor_data: DataFrame with factors (rows=stocks, cols=factors)
        factor_names: List of factor column names to normalize
        method: 'zscore' or 'percentile'

    Returns:
        DataFrame with normalized factors
    """
    normalized = factor_data.copy()

    for factor in factor_names:
        if factor not in factor_data.columns:
            continue

        values = factor_data[factor].values.reshape(-1, 1)

        # Remove NaN for normalization
        valid_mask = ~np.isnan(values.flatten())
        if valid_mask.sum() < 2:
            # Not enough valid data
            normalized[factor] = 0
            continue

        if method == 'zscore':
            # Z-score normalization
            scaler = StandardScaler()

            # Fit only on valid values
            valid_values = values[valid_mask].reshape(-1, 1)
            scaler.fit(valid_values)

            # Transform all values
            normalized_values = np.full(len(values), np.nan)
            valid_indices = np.where(valid_mask)[0]
            normalized_values[valid_indices] = scaler.transform(values[valid_mask].reshape(-1, 1)).flatten()

            normalized[factor] = normalized_values

        elif method == 'percentile':
            # Percentile ranking (0-100)
            valid_values = values[valid_mask].flatten()
            percentile_values = np.full(len(values), np.nan)

            for i, val in enumerate(values.flatten()):
                if valid_mask[i]:
                    percentile = (valid_values < val).sum() / len(valid_values) * 100
                    percentile_values[i] = percentile

            normalized[factor] = percentile_values

    return normalized


def calculate_composite_score(factor_data: pd.DataFrame,
                              factor_weights: Dict[str, float],
                              normalize: bool = True) -> pd.Series:
    """
    Calculate weighted composite score.

    Args:
        factor_data: DataFrame with factors (rows=stocks, cols=factors)
        factor_weights: Dict mapping factor name -> weight
        normalize: Whether to z-score normalize first

    Returns:
        Series with composite scores (index=stock tickers)
    """
    # Normalize factors if requested
    if normalize:
        factor_names = list(factor_weights.keys())
        normalized_data = normalize_factors(factor_data, factor_names, method='zscore')
    else:
        normalized_data = factor_data

    # Calculate weighted sum
    composite_scores = pd.Series(0.0, index=factor_data.index)

    for factor, weight in factor_weights.items():
        if factor in normalized_data.columns:
            # Fill NaN with 0 for missing factors
            factor_values = normalized_data[factor].fillna(0)
            composite_scores += factor_values * weight

    return composite_scores


def rank_stocks_by_factors(factor_data: pd.DataFrame,
                           factor_weights: Dict[str, float],
                           top_n: int = 50,
                           min_valid_factors: int = 5) -> pd.DataFrame:
    """
    Rank stocks by composite factor score.

    Args:
        factor_data: DataFrame with factors (rows=stocks, cols=factors)
        factor_weights: Factor weights
        top_n: Number of top stocks to return
        min_valid_factors: Minimum number of valid factors required

    Returns:
        DataFrame with top N stocks, sorted by score
    """
    # Filter stocks with insufficient data
    factor_cols = list(factor_weights.keys())
    valid_factor_count = factor_data[factor_cols].notna().sum(axis=1)
    filtered_data = factor_data[valid_factor_count >= min_valid_factors].copy()

    logger.info(f"Ranking {len(filtered_data)} stocks with >= {min_valid_factors} valid factors")

    if len(filtered_data) == 0:
        logger.warning("No stocks meet minimum factor requirement")
        return pd.DataFrame()

    # Calculate composite scores
    composite_scores = calculate_composite_score(filtered_data, factor_weights)

    # Create results dataframe
    results = filtered_data.copy()
    results['composite_score'] = composite_scores
    results['rank'] = composite_scores.rank(ascending=False)

    # Sort by score descending
    results = results.sort_values('composite_score', ascending=False)

    # Return top N
    top_stocks = results.head(top_n)

    logger.info(f"Top stock: {top_stocks.index[0]} with score {top_stocks['composite_score'].iloc[0]:.2f}")

    return top_stocks


def calculate_information_coefficient(factor_values: pd.Series,
                                      forward_returns: pd.Series,
                                      method: str = 'spearman') -> float:
    """
    Calculate Information Coefficient (IC).

    IC measures the correlation between factor values and forward returns.
    High IC indicates predictive power.

    Args:
        factor_values: Factor values for stocks
        forward_returns: Forward returns for same stocks
        method: 'spearman' or 'pearson'

    Returns:
        IC value (-1 to 1)
    """
    # Align and remove NaN
    aligned = pd.concat([factor_values, forward_returns], axis=1, join='inner').dropna()

    if len(aligned) < 3:
        return np.nan

    if method == 'spearman':
        ic = aligned.iloc[:, 0].corr(aligned.iloc[:, 1], method='spearman')
    else:
        ic = aligned.iloc[:, 0].corr(aligned.iloc[:, 1], method='pearson')

    return float(ic)


def dynamic_factor_weighting(factor_data: pd.DataFrame,
                            forward_returns: pd.DataFrame,
                            base_weights: Dict[str, float],
                            ic_window: int = 20) -> Dict[str, float]:
    """
    Dynamically adjust factor weights based on recent IC.

    Factors with higher recent IC get higher weights.

    Args:
        factor_data: Historical factor values (rows=dates, cols=factors)
        forward_returns: Historical forward returns (rows=dates)
        base_weights: Base factor weights
        ic_window: Window for IC calculation

    Returns:
        Adjusted factor weights
    """
    # Calculate IC for each factor
    factor_ics = {}

    for factor in base_weights.keys():
        if factor not in factor_data.columns:
            factor_ics[factor] = 0.0
            continue

        # Recent factor values
        recent_factors = factor_data[factor].iloc[-ic_window:]
        recent_returns = forward_returns.iloc[-ic_window:]

        ic = calculate_information_coefficient(recent_factors, recent_returns)

        # Use absolute IC (we care about predictive power, not direction)
        factor_ics[factor] = abs(ic) if not np.isnan(ic) else 0.0

    logger.info(f"Factor ICs: {factor_ics}")

    # Adjust weights based on IC
    adjusted_weights = {}
    total_ic = sum(factor_ics.values())

    if total_ic == 0:
        # Fallback to base weights if no IC
        return base_weights

    for factor, base_weight in base_weights.items():
        ic_weight = factor_ics.get(factor, 0.0) / total_ic

        # Blend base weight and IC weight (70% base, 30% IC)
        adjusted_weights[factor] = 0.7 * base_weight + 0.3 * ic_weight

    # Normalize weights to sum to 1
    total_weight = sum(adjusted_weights.values())
    if total_weight > 0:
        adjusted_weights = {k: v / total_weight for k, v in adjusted_weights.items()}

    logger.info(f"Adjusted weights: {adjusted_weights}")

    return adjusted_weights


def calculate_factor_exposure(stock_factors: Dict[str, float],
                              universe_factor_data: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate factor exposure (z-score) for a single stock.

    Args:
        stock_factors: Factor values for the stock
        universe_factor_data: Factor values for entire universe

    Returns:
        Dict of factor exposures (z-scores)
    """
    exposures = {}

    for factor, value in stock_factors.items():
        if factor not in universe_factor_data.columns or pd.isna(value):
            exposures[factor] = 0.0
            continue

        universe_values = universe_factor_data[factor].dropna()

        if len(universe_values) < 2:
            exposures[factor] = 0.0
            continue

        mean = universe_values.mean()
        std = universe_values.std()

        if std == 0:
            exposures[factor] = 0.0
        else:
            z_score = (value - mean) / std
            exposures[factor] = float(z_score)

    return exposures


def score_with_percentiles(factor_data: pd.DataFrame,
                           factor_weights: Dict[str, float]) -> pd.DataFrame:
    """
    Score stocks using percentile ranking.

    Args:
        factor_data: DataFrame with factors
        factor_weights: Factor weights

    Returns:
        DataFrame with percentile scores and ranks
    """
    # Normalize to percentiles (0-100)
    percentile_data = normalize_factors(factor_data, list(factor_weights.keys()), method='percentile')

    # Calculate weighted percentile score
    composite_scores = pd.Series(0.0, index=factor_data.index)

    for factor, weight in factor_weights.items():
        if factor in percentile_data.columns:
            factor_values = percentile_data[factor].fillna(50)  # Neutral percentile
            composite_scores += factor_values * weight

    # Create results
    results = factor_data.copy()
    results['percentile_score'] = composite_scores
    results['percentile_rank'] = composite_scores.rank(ascending=False)

    return results.sort_values('percentile_score', ascending=False)


def factor_correlation_analysis(factor_data: pd.DataFrame,
                                factor_names: List[str]) -> pd.DataFrame:
    """
    Analyze correlation between factors.

    High correlation indicates redundancy.

    Args:
        factor_data: DataFrame with factors
        factor_names: List of factor names

    Returns:
        Correlation matrix
    """
    # Select only specified factors
    selected_factors = factor_data[factor_names].dropna()

    if len(selected_factors) < 2:
        return pd.DataFrame()

    # Calculate correlation matrix
    corr_matrix = selected_factors.corr()

    logger.info(f"Factor correlation analysis complete. Shape: {corr_matrix.shape}")

    return corr_matrix


def detect_outliers(factor_data: pd.DataFrame,
                   factor_name: str,
                   threshold: float = 3.0) -> pd.Series:
    """
    Detect outliers using z-score method.

    Args:
        factor_data: DataFrame with factors
        factor_name: Factor to check
        threshold: Z-score threshold for outliers

    Returns:
        Boolean series (True = outlier)
    """
    if factor_name not in factor_data.columns:
        return pd.Series(False, index=factor_data.index)

    values = factor_data[factor_name].dropna()

    if len(values) < 2:
        return pd.Series(False, index=factor_data.index)

    # Calculate z-scores
    mean = values.mean()
    std = values.std()

    if std == 0:
        return pd.Series(False, index=factor_data.index)

    z_scores = (factor_data[factor_name] - mean) / std
    outliers = abs(z_scores) > threshold

    return outliers


def backtest_factor_strategy(factor_data: pd.DataFrame,
                            returns_data: pd.DataFrame,
                            factor_weights: Dict[str, float],
                            rebalance_frequency: int = 20,
                            top_n: int = 10) -> Dict[str, float]:
    """
    Backtest a factor-based strategy.

    Args:
        factor_data: Historical factor values (multi-index: date, ticker)
        returns_data: Historical returns (multi-index: date, ticker)
        factor_weights: Factor weights for scoring
        rebalance_frequency: Days between rebalancing
        top_n: Number of stocks to hold

    Returns:
        Performance metrics
    """
    # This is a simplified backtest
    # In production, you'd use more sophisticated logic

    logger.info(f"Backtesting factor strategy with {rebalance_frequency}d rebalance, top {top_n} stocks")

    # For now, return placeholder metrics
    # Full implementation would require proper date alignment and portfolio tracking

    return {
        'total_return': 0.0,
        'sharpe_ratio': 0.0,
        'max_drawdown': 0.0,
        'win_rate': 0.0,
        'avg_holding_period': rebalance_frequency
    }
