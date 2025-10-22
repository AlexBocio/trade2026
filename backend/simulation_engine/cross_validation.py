# cross_validation.py - Advanced cross-validation methods for time series

import numpy as np
import pandas as pd
from typing import Callable, Dict, List, Tuple
import logging
from config import Config
from utils import calculate_metrics

logger = logging.getLogger(__name__)


def purged_kfold_cv(
    data: pd.DataFrame,
    strategy_func: Callable,
    param_grid: Dict,
    n_splits: int = None,
    embargo: int = None
) -> Dict:
    """
    Purged K-Fold Cross-Validation for time series.

    Prevents data leakage by purging (removing) observations near test set
    and embargoing observations immediately after test set.

    Args:
        data: DataFrame with 'returns' column
        strategy_func: Function(data, params) -> signals
        param_grid: Dictionary of parameter ranges
        n_splits: Number of CV splits
        embargo: Number of periods to embargo after each test set

    Returns:
        Dictionary with cross-validation results

    Raises:
        ValueError: If data is invalid
    """
    if n_splits is None:
        n_splits = Config.DEFAULT_CV_SPLITS
    if embargo is None:
        embargo = Config.DEFAULT_EMBARGO_DAYS

    logger.info(f"Starting purged K-fold CV (n_splits={n_splits}, embargo={embargo})")

    n = len(data)
    test_size = n // n_splits

    results = []
    param_combinations = _generate_param_combinations(param_grid)

    for split_idx in range(n_splits):
        # Test set indices
        test_start = split_idx * test_size
        test_end = min(test_start + test_size, n)
        test_indices = np.arange(test_start, test_end)

        # Purged indices: remove observations overlapping with test set
        # In practice, overlap depends on holding period
        purge_start = max(0, test_start - embargo)
        purge_end = min(n, test_end + embargo)

        # Train indices: all except purged region
        train_indices = np.concatenate([
            np.arange(0, purge_start),
            np.arange(purge_end, n)
        ])

        if len(train_indices) == 0:
            logger.warning(f"Split {split_idx}: No training data after purging")
            continue

        # Split data
        train_data = data.iloc[train_indices].copy()
        test_data = data.iloc[test_indices].copy()

        # Optimize on training data
        best_params, best_score = _optimize_params(train_data, strategy_func, param_combinations)

        # Test on test data
        test_signals = strategy_func(test_data, best_params)
        test_returns = test_data['returns'] * test_signals.shift(1)
        test_returns = test_returns.dropna()

        # Calculate metrics
        test_metrics = calculate_metrics(test_returns)

        results.append({
            'split': split_idx,
            'train_size': len(train_indices),
            'test_size': len(test_indices),
            'best_params': best_params,
            'train_score': best_score,
            **test_metrics
        })

    # Aggregate results
    if results:
        summary = {
            'n_splits': len(results),
            'avg_sharpe': np.mean([r['sharpe_ratio'] for r in results]),
            'std_sharpe': np.std([r['sharpe_ratio'] for r in results]),
            'avg_return': np.mean([r['total_return'] for r in results]),
            'win_rate': np.mean([r['total_return'] > 0 for r in results])
        }
    else:
        summary = {}

    logger.info(f"Purged K-fold CV completed: {len(results)} splits")

    return {
        'method': 'purged_kfold',
        'results': results,
        'summary': summary,
        'config': {'n_splits': n_splits, 'embargo': embargo}
    }


def nested_cv(
    data: pd.DataFrame,
    strategy_func: Callable,
    param_grid: Dict,
    outer_splits: int = 5,
    inner_splits: int = 3
) -> Dict:
    """
    Nested cross-validation for unbiased hyperparameter tuning.

    Outer loop: Model assessment (performance estimation)
    Inner loop: Model selection (hyperparameter optimization)

    Args:
        data: DataFrame with 'returns' column
        strategy_func: Function(data, params) -> signals
        param_grid: Dictionary of parameter ranges
        outer_splits: Number of outer CV splits
        inner_splits: Number of inner CV splits

    Returns:
        Dictionary with nested CV results
    """
    logger.info(f"Starting nested CV (outer={outer_splits}, inner={inner_splits})")

    n = len(data)
    outer_test_size = n // outer_splits

    outer_results = []

    for outer_idx in range(outer_splits):
        # Outer test set
        outer_test_start = outer_idx * outer_test_size
        outer_test_end = min(outer_test_start + outer_test_size, n)

        outer_train_indices = np.concatenate([
            np.arange(0, outer_test_start),
            np.arange(outer_test_end, n)
        ])

        outer_test_indices = np.arange(outer_test_start, outer_test_end)

        outer_train_data = data.iloc[outer_train_indices].copy()
        outer_test_data = data.iloc[outer_test_indices].copy()

        # Inner cross-validation for hyperparameter tuning
        inner_train_size = len(outer_train_data)
        inner_test_size = inner_train_size // inner_splits

        param_combinations = _generate_param_combinations(param_grid)
        param_scores = {str(p): [] for p in param_combinations}

        for inner_idx in range(inner_splits):
            # Inner split
            inner_test_start = inner_idx * inner_test_size
            inner_test_end = min(inner_test_start + inner_test_size, inner_train_size)

            inner_train_indices = np.concatenate([
                np.arange(0, inner_test_start),
                np.arange(inner_test_end, inner_train_size)
            ])

            inner_test_indices = np.arange(inner_test_start, inner_test_end)

            inner_train = outer_train_data.iloc[inner_train_indices].copy()
            inner_test = outer_train_data.iloc[inner_test_indices].copy()

            # Evaluate each parameter combination
            for params in param_combinations:
                try:
                    signals = strategy_func(inner_train, params)
                    train_returns = inner_train['returns'] * signals.shift(1)
                    train_returns = train_returns.dropna()

                    # Score on inner test set
                    test_signals = strategy_func(inner_test, params)
                    test_returns = inner_test['returns'] * test_signals.shift(1)
                    test_returns = test_returns.dropna()

                    if len(test_returns) > 0 and test_returns.std() > 0:
                        score = np.sqrt(252) * test_returns.mean() / test_returns.std()
                        param_scores[str(params)].append(score)

                except Exception as e:
                    logger.debug(f"Error evaluating params {params}: {str(e)}")
                    continue

        # Select best parameters based on inner CV
        best_params = None
        best_avg_score = -np.inf

        for params in param_combinations:
            scores = param_scores[str(params)]
            if scores:
                avg_score = np.mean(scores)
                if avg_score > best_avg_score:
                    best_avg_score = avg_score
                    best_params = params

        if best_params is None:
            logger.warning(f"Outer split {outer_idx}: No valid parameters found")
            continue

        # Evaluate on outer test set with best parameters
        test_signals = strategy_func(outer_test_data, best_params)
        test_returns = outer_test_data['returns'] * test_signals.shift(1)
        test_returns = test_returns.dropna()

        test_metrics = calculate_metrics(test_returns)

        outer_results.append({
            'outer_split': outer_idx,
            'best_params': best_params,
            'inner_cv_score': best_avg_score,
            **test_metrics
        })

    # Aggregate results
    if outer_results:
        summary = {
            'n_outer_splits': len(outer_results),
            'avg_sharpe': np.mean([r['sharpe_ratio'] for r in outer_results]),
            'std_sharpe': np.std([r['sharpe_ratio'] for r in outer_results]),
            'avg_return': np.mean([r['total_return'] for r in outer_results])
        }
    else:
        summary = {}

    logger.info(f"Nested CV completed: {len(outer_results)} outer splits")

    return {
        'method': 'nested_cv',
        'results': outer_results,
        'summary': summary,
        'config': {'outer_splits': outer_splits, 'inner_splits': inner_splits}
    }


def walk_forward_cv_hybrid(
    data: pd.DataFrame,
    strategy_func: Callable,
    param_grid: Dict,
    n_splits: int = 5,
    train_size: int = None,
    test_size: int = None
) -> Dict:
    """
    Hybrid walk-forward / cross-validation.

    Combines walk-forward optimization with cross-validation for robustness.

    Args:
        data: DataFrame with 'returns' column
        strategy_func: Function(data, params) -> signals
        param_grid: Dictionary of parameter ranges
        n_splits: Number of CV splits within each walk-forward window
        train_size: Walk-forward training window size
        test_size: Walk-forward test window size

    Returns:
        Dictionary with hybrid CV results
    """
    if train_size is None:
        train_size = Config.DEFAULT_TRAIN_SIZE
    if test_size is None:
        test_size = Config.DEFAULT_TEST_SIZE

    logger.info(f"Starting walk-forward CV hybrid (n_splits={n_splits})")

    n = len(data)
    results = []
    current_position = 0

    while current_position + train_size + test_size <= n:
        # Walk-forward window
        wf_train_data = data.iloc[current_position:current_position + train_size].copy()
        wf_test_data = data.iloc[current_position + train_size:current_position + train_size + test_size].copy()

        # Cross-validation within training window
        cv_test_size = len(wf_train_data) // n_splits
        param_combinations = _generate_param_combinations(param_grid)
        param_scores = {str(p): [] for p in param_combinations}

        for cv_idx in range(n_splits):
            cv_test_start = cv_idx * cv_test_size
            cv_test_end = min(cv_test_start + cv_test_size, len(wf_train_data))

            cv_train_indices = np.concatenate([
                np.arange(0, cv_test_start),
                np.arange(cv_test_end, len(wf_train_data))
            ])

            cv_test_indices = np.arange(cv_test_start, cv_test_end)

            cv_train = wf_train_data.iloc[cv_train_indices].copy()
            cv_test = wf_train_data.iloc[cv_test_indices].copy()

            # Evaluate parameters
            for params in param_combinations:
                try:
                    signals = strategy_func(cv_test, params)
                    returns = cv_test['returns'] * signals.shift(1)
                    returns = returns.dropna()

                    if len(returns) > 0 and returns.std() > 0:
                        score = np.sqrt(252) * returns.mean() / returns.std()
                        param_scores[str(params)].append(score)

                except Exception:
                    continue

        # Select best parameters
        best_params = None
        best_avg_score = -np.inf

        for params in param_combinations:
            scores = param_scores[str(params)]
            if scores:
                avg_score = np.mean(scores)
                if avg_score > best_avg_score:
                    best_avg_score = avg_score
                    best_params = params

        if best_params is None:
            current_position += test_size
            continue

        # Test on walk-forward test set
        test_signals = strategy_func(wf_test_data, best_params)
        test_returns = wf_test_data['returns'] * test_signals.shift(1)
        test_returns = test_returns.dropna()

        test_metrics = calculate_metrics(test_returns)

        results.append({
            'wf_window': len(results),
            'best_params': best_params,
            'cv_score': best_avg_score,
            **test_metrics
        })

        current_position += test_size

    # Aggregate results
    if results:
        summary = {
            'n_windows': len(results),
            'avg_sharpe': np.mean([r['sharpe_ratio'] for r in results]),
            'avg_return': np.mean([r['total_return'] for r in results])
        }
    else:
        summary = {}

    logger.info(f"Walk-forward CV hybrid completed: {len(results)} windows")

    return {
        'method': 'walk_forward_cv_hybrid',
        'results': results,
        'summary': summary,
        'config': {'n_splits': n_splits, 'train_size': train_size, 'test_size': test_size}
    }


# Helper functions

def _optimize_params(data: pd.DataFrame, strategy_func: Callable, param_combinations: List[Dict]) -> Tuple:
    """Optimize parameters on data."""
    best_params = None
    best_score = -np.inf

    for params in param_combinations:
        try:
            signals = strategy_func(data, params)
            returns = data['returns'] * signals.shift(1)
            returns = returns.dropna()

            if len(returns) == 0 or returns.std() == 0:
                continue

            score = np.sqrt(252) * returns.mean() / returns.std()

            if score > best_score:
                best_score = score
                best_params = params

        except Exception:
            continue

    if best_params is None:
        best_params = param_combinations[0] if param_combinations else {}
        best_score = 0

    return best_params, best_score


def _generate_param_combinations(param_grid: Dict) -> List[Dict]:
    """Generate all parameter combinations from grid."""
    import itertools

    keys = list(param_grid.keys())
    values = list(param_grid.values())

    combinations = []
    for combination in itertools.product(*values):
        combinations.append(dict(zip(keys, combination)))

    return combinations
