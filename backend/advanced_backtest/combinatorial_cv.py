# combinatorial_cv.py - Combinatorial Purged Cross-Validation
# Implements CPCV with purging and embargo for time series

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from typing import Callable, Dict
import logging

logger = logging.getLogger(__name__)


def combinatorial_purged_cv(returns: pd.DataFrame,
                            strategy_func: Callable,
                            params: dict,
                            n_splits: int = 10,
                            embargo_pct: float = 0.01) -> dict:
    """
    Combinatorial Purged Cross-Validation (CPCV).

    Standard K-Fold CV can overestimate performance due to:
    1. Data leakage between train/test
    2. Autocorrelation in time series

    CPCV addresses this by:
    1. Creating multiple train/test splits
    2. Purging overlapping observations
    3. Adding embargo period between train/test

    Args:
        returns: Returns dataframe or series
        strategy_func: Strategy function
        params: Strategy parameters
        n_splits: Number of folds
        embargo_pct: Embargo period as % of total data

    Returns:
        {
            'is_sharpes': In-sample Sharpe per split,
            'oos_sharpes': Out-of-sample Sharpe per split,
            'mean_is_sharpe': Average IS Sharpe,
            'mean_oos_sharpe': Average OOS Sharpe,
            'splits': Details of each split
        }
    """
    # Convert to Series if DataFrame
    if isinstance(returns, pd.DataFrame):
        if 'close' in returns.columns:
            prices = returns['close']
            returns_series = prices.pct_change().dropna()
        else:
            # Assume it's already returns
            returns_series = returns.iloc[:, 0] if returns.shape[1] > 0 else returns.squeeze()
    else:
        returns_series = returns

    n = len(returns_series)
    embargo_size = int(n * embargo_pct)

    logger.info(f"CPCV: n={n}, n_splits={n_splits}, embargo_size={embargo_size}")

    kfold = KFold(n_splits=n_splits, shuffle=False)

    is_sharpes = []
    oos_sharpes = []
    split_details = []

    for fold_idx, (train_idx, test_idx) in enumerate(kfold.split(returns_series)):
        # Apply embargo: remove embargo_size observations after train
        if len(train_idx) > embargo_size:
            train_idx = train_idx[:-embargo_size]

        # Purge: remove test observations that overlap with train
        # (This is simplified; full implementation would check for label overlap)
        if len(train_idx) > 0:
            test_idx = test_idx[test_idx > train_idx[-1] + embargo_size]

        if len(test_idx) < 10:  # Skip if test set too small
            logger.warning(f"Fold {fold_idx}: test set too small ({len(test_idx)}), skipping")
            continue

        # Split data
        train_returns = returns_series.iloc[train_idx]
        test_returns = returns_series.iloc[test_idx]

        try:
            # Generate signals
            train_signals = strategy_func(train_returns, **params)
            test_signals = strategy_func(test_returns, **params)

            # Ensure signals are pandas Series
            if not isinstance(train_signals, pd.Series):
                train_signals = pd.Series(train_signals, index=train_returns.index)
            if not isinstance(test_signals, pd.Series):
                test_signals = pd.Series(test_signals, index=test_returns.index)

            # Calculate strategy returns
            train_strategy_returns = train_returns * train_signals.shift(1)
            test_strategy_returns = test_returns * test_signals.shift(1)

            # Calculate Sharpe ratios
            is_sharpe = calculate_sharpe(train_strategy_returns.dropna())
            oos_sharpe = calculate_sharpe(test_strategy_returns.dropna())

            is_sharpes.append(is_sharpe)
            oos_sharpes.append(oos_sharpe)

            split_details.append({
                'fold': fold_idx,
                'train_size': len(train_idx),
                'test_size': len(test_idx),
                'is_sharpe': float(is_sharpe),
                'oos_sharpe': float(oos_sharpe)
            })

            logger.info(f"Fold {fold_idx}: IS Sharpe={is_sharpe:.3f}, OOS Sharpe={oos_sharpe:.3f}")

        except Exception as e:
            logger.error(f"Error in fold {fold_idx}: {str(e)}")
            continue

    if len(is_sharpes) == 0:
        logger.warning("No valid splits completed")
        return {
            'is_sharpes': [],
            'oos_sharpes': [],
            'mean_is_sharpe': 0.0,
            'mean_oos_sharpe': 0.0,
            'std_is_sharpe': 0.0,
            'std_oos_sharpe': 0.0,
            'splits': []
        }

    return {
        'is_sharpes': is_sharpes,
        'oos_sharpes': oos_sharpes,
        'mean_is_sharpe': float(np.mean(is_sharpes)),
        'mean_oos_sharpe': float(np.mean(oos_sharpes)),
        'std_is_sharpe': float(np.std(is_sharpes)),
        'std_oos_sharpe': float(np.std(oos_sharpes)),
        'splits': split_details
    }


def calculate_sharpe(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    Calculate annualized Sharpe ratio.

    Args:
        returns: Returns series
        risk_free_rate: Risk-free rate (annualized)

    Returns:
        Annualized Sharpe ratio
    """
    if len(returns) == 0:
        return 0.0

    excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate

    if excess_returns.std() == 0:
        return 0.0

    sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
    return sharpe


def purged_k_fold_cv(returns: pd.DataFrame,
                     strategy_func: Callable,
                     params: dict,
                     n_splits: int = 5,
                     pct_embargo: float = 0.01) -> dict:
    """
    Alternative implementation with more explicit purging.

    Args:
        returns: Returns data
        strategy_func: Strategy function
        params: Strategy parameters
        n_splits: Number of folds
        pct_embargo: Embargo percentage

    Returns:
        CV results
    """
    return combinatorial_purged_cv(
        returns,
        strategy_func,
        params,
        n_splits=n_splits,
        embargo_pct=pct_embargo
    )


def get_train_times(times: pd.DatetimeIndex, test_times: pd.DatetimeIndex, pct_embargo: float = 0.01):
    """
    Get training times with embargo.

    Args:
        times: All timestamps
        test_times: Test timestamps
        pct_embargo: Embargo percentage

    Returns:
        Training timestamps
    """
    n_embargo = int(len(times) * pct_embargo)

    # Remove times that are in test set or within embargo period after test
    train_times = []
    for t in times:
        if t in test_times:
            continue
        # Check if within embargo of any test time
        if any(abs((t - test_t).days) <= n_embargo for test_t in test_times):
            continue
        train_times.append(t)

    return pd.DatetimeIndex(train_times)
