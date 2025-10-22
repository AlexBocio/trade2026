# walk_forward_variants.py - Walk-forward optimization variants

import numpy as np
import pandas as pd
from typing import Callable, Dict, List, Tuple
import logging
from config import Config
from utils import calculate_sharpe_ratio, calculate_sortino_ratio, calculate_calmar_ratio, calculate_metrics

logger = logging.getLogger(__name__)


def anchored_walk_forward(
    data: pd.DataFrame,
    strategy_func: Callable,
    param_grid: Dict,
    train_size: int = None,
    test_size: int = None,
    step: int = None
) -> Dict:
    """
    Anchored walk-forward optimization.

    Training window grows from the start (anchored at beginning).
    Test window slides forward.

    Args:
        data: Price/returns DataFrame with 'returns' column
        strategy_func: Function(data, params) -> signals
        param_grid: Dictionary of parameter ranges
        train_size: Initial training window size
        test_size: Test window size
        step: Step size for sliding test window

    Returns:
        Dictionary with results and summary statistics
    """
    if train_size is None:
        train_size = Config.DEFAULT_TRAIN_SIZE
    if test_size is None:
        test_size = Config.DEFAULT_TEST_SIZE
    if step is None:
        step = Config.DEFAULT_STEP_SIZE

    total_length = len(data)
    results = []
    current_position = train_size

    logger.info(f"Starting anchored walk-forward (train={train_size}, test={test_size}, step={step})")

    while current_position + test_size <= total_length:
        # Training data: from start to current position (growing window)
        train_data = data.iloc[:current_position].copy()

        # Test data: next test_size periods
        test_data = data.iloc[current_position:current_position + test_size].copy()

        # Optimize on training data
        best_params, best_score = _optimize_params(train_data, strategy_func, param_grid)

        # Test on out-of-sample data
        test_signals = strategy_func(test_data, best_params)
        test_returns = test_data['returns'] * test_signals.shift(1)
        test_returns = test_returns.dropna()

        # Calculate metrics
        test_metrics = calculate_metrics(test_returns)

        results.append({
            'train_start': data.index[0],
            'train_end': data.index[current_position - 1],
            'test_start': data.index[current_position],
            'test_end': data.index[min(current_position + test_size - 1, total_length - 1)],
            'train_size': current_position,
            'test_size': test_size,
            'optimal_params': best_params,
            'train_score': best_score,
            **test_metrics
        })

        # Slide forward
        current_position += step

    # Aggregate results
    summary = _aggregate_results(results)

    logger.info(f"Anchored walk-forward completed: {len(results)} windows")

    return {
        'method': 'anchored',
        'results': results,
        'summary': summary,
        'config': {'train_size': train_size, 'test_size': test_size, 'step': step}
    }


def rolling_walk_forward(
    data: pd.DataFrame,
    strategy_func: Callable,
    param_grid: Dict,
    train_size: int = None,
    test_size: int = None,
    step: int = None
) -> Dict:
    """
    Rolling walk-forward optimization.

    Both training and test windows slide forward (fixed-size sliding window).

    Args:
        data: Price/returns DataFrame with 'returns' column
        strategy_func: Function(data, params) -> signals
        param_grid: Dictionary of parameter ranges
        train_size: Training window size (fixed)
        test_size: Test window size
        step: Step size for sliding windows

    Returns:
        Dictionary with results and summary statistics
    """
    if train_size is None:
        train_size = Config.DEFAULT_TRAIN_SIZE
    if test_size is None:
        test_size = Config.DEFAULT_TEST_SIZE
    if step is None:
        step = Config.DEFAULT_STEP_SIZE

    total_length = len(data)
    results = []
    current_position = 0

    logger.info(f"Starting rolling walk-forward (train={train_size}, test={test_size}, step={step})")

    while current_position + train_size + test_size <= total_length:
        # Training data: fixed window
        train_data = data.iloc[current_position:current_position + train_size].copy()

        # Test data: next test_size periods
        test_start = current_position + train_size
        test_data = data.iloc[test_start:test_start + test_size].copy()

        # Optimize on training data
        best_params, best_score = _optimize_params(train_data, strategy_func, param_grid)

        # Test on out-of-sample data
        test_signals = strategy_func(test_data, best_params)
        test_returns = test_data['returns'] * test_signals.shift(1)
        test_returns = test_returns.dropna()

        # Calculate metrics
        test_metrics = calculate_metrics(test_returns)

        results.append({
            'train_start': data.index[current_position],
            'train_end': data.index[current_position + train_size - 1],
            'test_start': data.index[test_start],
            'test_end': data.index[min(test_start + test_size - 1, total_length - 1)],
            'train_size': train_size,
            'test_size': test_size,
            'optimal_params': best_params,
            'train_score': best_score,
            **test_metrics
        })

        # Slide forward
        current_position += step

    # Aggregate results
    summary = _aggregate_results(results)

    logger.info(f"Rolling walk-forward completed: {len(results)} windows")

    return {
        'method': 'rolling',
        'results': results,
        'summary': summary,
        'config': {'train_size': train_size, 'test_size': test_size, 'step': step}
    }


def expanding_walk_forward(
    data: pd.DataFrame,
    strategy_func: Callable,
    param_grid: Dict,
    initial_train: int = None,
    test_size: int = None,
    step: int = None
) -> Dict:
    """
    Expanding walk-forward optimization.

    Both training and test windows expand over time.

    Args:
        data: Price/returns DataFrame with 'returns' column
        strategy_func: Function(data, params) -> signals
        param_grid: Dictionary of parameter ranges
        initial_train: Initial training window size
        test_size: Test window size (expands)
        step: Step size for expansion

    Returns:
        Dictionary with results and summary statistics
    """
    if initial_train is None:
        initial_train = Config.DEFAULT_TRAIN_SIZE
    if test_size is None:
        test_size = Config.DEFAULT_TEST_SIZE
    if step is None:
        step = Config.DEFAULT_STEP_SIZE

    total_length = len(data)
    results = []
    current_train_end = initial_train

    logger.info(f"Starting expanding walk-forward (initial_train={initial_train}, test={test_size}, step={step})")

    while current_train_end + test_size <= total_length:
        # Training data: from start to current_train_end (expanding)
        train_data = data.iloc[:current_train_end].copy()

        # Test data: expanding window after training
        test_end = min(current_train_end + test_size, total_length)
        test_data = data.iloc[current_train_end:test_end].copy()

        # Optimize on training data
        best_params, best_score = _optimize_params(train_data, strategy_func, param_grid)

        # Test on out-of-sample data
        test_signals = strategy_func(test_data, best_params)
        test_returns = test_data['returns'] * test_signals.shift(1)
        test_returns = test_returns.dropna()

        # Calculate metrics
        test_metrics = calculate_metrics(test_returns)

        results.append({
            'train_start': data.index[0],
            'train_end': data.index[current_train_end - 1],
            'test_start': data.index[current_train_end],
            'test_end': data.index[test_end - 1],
            'train_size': current_train_end,
            'test_size': len(test_data),
            'optimal_params': best_params,
            'train_score': best_score,
            **test_metrics
        })

        # Expand windows
        current_train_end += step
        test_size += step

    # Aggregate results
    summary = _aggregate_results(results)

    logger.info(f"Expanding walk-forward completed: {len(results)} windows")

    return {
        'method': 'expanding',
        'results': results,
        'summary': summary,
        'config': {'initial_train': initial_train, 'test_size': test_size, 'step': step}
    }


def multi_objective_walk_forward(
    data: pd.DataFrame,
    strategy_func: Callable,
    param_grid: Dict,
    objectives: List[str] = None,
    train_size: int = None,
    test_size: int = None
) -> Dict:
    """
    Multi-objective walk-forward optimization.

    Optimizes multiple metrics simultaneously, returns Pareto frontier.

    Args:
        data: Price/returns DataFrame with 'returns' column
        strategy_func: Function(data, params) -> signals
        param_grid: Dictionary of parameter ranges
        objectives: List of metrics to optimize ['sharpe', 'sortino', 'calmar']
        train_size: Training window size
        test_size: Test window size

    Returns:
        Dictionary with Pareto-optimal solutions
    """
    if objectives is None:
        objectives = ['sharpe_ratio', 'sortino_ratio', 'calmar_ratio']
    if train_size is None:
        train_size = Config.DEFAULT_TRAIN_SIZE
    if test_size is None:
        test_size = Config.DEFAULT_TEST_SIZE

    # Split data
    train_data = data.iloc[:train_size].copy()
    test_data = data.iloc[train_size:train_size + test_size].copy()

    # Evaluate all parameter combinations
    param_combinations = _generate_param_combinations(param_grid)
    evaluated_params = []

    for params in param_combinations:
        try:
            signals = strategy_func(train_data, params)
            returns = train_data['returns'] * signals.shift(1)
            returns = returns.dropna()

            metrics = calculate_metrics(returns)

            # Extract objective values
            obj_values = [metrics.get(obj, 0) for obj in objectives]

            evaluated_params.append({
                'params': params,
                'objectives': dict(zip(objectives, obj_values))
            })
        except Exception as e:
            logger.warning(f"Error evaluating params {params}: {str(e)}")
            continue

    # Find Pareto frontier
    pareto_frontier = _find_pareto_frontier(evaluated_params, objectives)

    # Test Pareto-optimal solutions
    pareto_results = []

    for solution in pareto_frontier:
        test_signals = strategy_func(test_data, solution['params'])
        test_returns = test_data['returns'] * test_signals.shift(1)
        test_returns = test_returns.dropna()

        test_metrics = calculate_metrics(test_returns)

        pareto_results.append({
            'params': solution['params'],
            'train_objectives': solution['objectives'],
            'test_metrics': test_metrics
        })

    logger.info(f"Multi-objective optimization: {len(pareto_frontier)} Pareto-optimal solutions found")

    return {
        'method': 'multi_objective',
        'objectives': objectives,
        'pareto_frontier': pareto_results,
        'n_evaluated': len(param_combinations),
        'n_pareto_optimal': len(pareto_frontier)
    }


def walk_forward_with_reoptimization(
    data: pd.DataFrame,
    strategy_func: Callable,
    param_grid: Dict,
    train_size: int = None,
    test_size: int = None,
    reopt_frequency: int = 20
) -> Dict:
    """
    Walk-forward with parameter drift tracking.

    Tracks how optimal parameters change over time.

    Args:
        data: Price/returns DataFrame with 'returns' column
        strategy_func: Function(data, params) -> signals
        param_grid: Dictionary of parameter ranges
        train_size: Training window size
        test_size: Test window size
        reopt_frequency: Re-optimize every N periods

    Returns:
        Dictionary with parameter drift analysis
    """
    if train_size is None:
        train_size = Config.DEFAULT_TRAIN_SIZE
    if test_size is None:
        test_size = Config.DEFAULT_TEST_SIZE

    total_length = len(data)
    results = []
    param_history = []
    current_position = 0

    logger.info(f"Starting walk-forward with reoptimization (freq={reopt_frequency})")

    while current_position + train_size + test_size <= total_length:
        # Training data
        train_data = data.iloc[current_position:current_position + train_size].copy()

        # Optimize parameters
        best_params, best_score = _optimize_params(train_data, strategy_func, param_grid)
        param_history.append(best_params.copy())

        # Test for next reopt_frequency periods
        for i in range(reopt_frequency):
            test_start = current_position + train_size + i
            test_end = test_start + 1

            if test_end > total_length:
                break

            test_data = data.iloc[test_start:test_end].copy()

            # Use current best params
            test_signals = strategy_func(test_data, best_params)
            test_return = test_data['returns'].iloc[0] if len(test_data) > 0 else 0

            results.append({
                'date': data.index[test_start],
                'return': test_return,
                'params': best_params.copy()
            })

        current_position += reopt_frequency

    # Analyze parameter drift
    param_stability = _analyze_parameter_drift(param_history)

    logger.info(f"Walk-forward with reoptimization completed: {len(results)} test periods")

    return {
        'method': 'reoptimization',
        'results': results,
        'param_history': param_history,
        'param_stability': param_stability,
        'reopt_frequency': reopt_frequency
    }


def compare_walk_forward_methods(
    data: pd.DataFrame,
    strategy_func: Callable,
    param_grid: Dict,
    methods: List[str] = None
) -> pd.DataFrame:
    """
    Compare different walk-forward methods.

    Args:
        data: Price/returns DataFrame with 'returns' column
        strategy_func: Function(data, params) -> signals
        param_grid: Dictionary of parameter ranges
        methods: List of methods to compare (None = all methods)

    Returns:
        DataFrame comparing methods
    """
    if methods is None:
        methods = ['anchored', 'rolling', 'expanding']

    comparison_results = []

    for method in methods:
        try:
            if method == 'anchored':
                result = anchored_walk_forward(data, strategy_func, param_grid)
            elif method == 'rolling':
                result = rolling_walk_forward(data, strategy_func, param_grid)
            elif method == 'expanding':
                result = expanding_walk_forward(data, strategy_func, param_grid)
            else:
                logger.warning(f"Unknown method: {method}")
                continue

            summary = result['summary']
            comparison_results.append({
                'method': method,
                **summary
            })

        except Exception as e:
            logger.error(f"Error in {method} walk-forward: {str(e)}")

    return pd.DataFrame(comparison_results)


# Helper functions

def _optimize_params(data: pd.DataFrame, strategy_func: Callable, param_grid: Dict) -> Tuple:
    """Optimize parameters on training data."""
    param_combinations = _generate_param_combinations(param_grid)

    best_params = None
    best_score = -np.inf

    for params in param_combinations:
        try:
            signals = strategy_func(data, params)
            returns = data['returns'] * signals.shift(1)
            returns = returns.dropna()

            if len(returns) == 0:
                continue

            # Optimize for Sharpe ratio
            score = calculate_sharpe_ratio(returns)

            if score > best_score:
                best_score = score
                best_params = params.copy()

        except Exception as e:
            logger.debug(f"Error evaluating params {params}: {str(e)}")
            continue

    if best_params is None:
        # Fallback: use first parameter combination
        best_params = param_combinations[0]
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


def _aggregate_results(results: List[Dict]) -> Dict:
    """Aggregate walk-forward results."""
    if not results:
        return {}

    return {
        'n_windows': len(results),
        'avg_sharpe': np.mean([r['sharpe_ratio'] for r in results]),
        'avg_return': np.mean([r['total_return'] for r in results]),
        'total_return': np.prod([1 + r['total_return'] for r in results]) - 1,
        'win_rate': np.mean([r['total_return'] > 0 for r in results]),
        'avg_drawdown': np.mean([r['max_drawdown'] for r in results])
    }


def _find_pareto_frontier(evaluated_params: List[Dict], objectives: List[str]) -> List[Dict]:
    """Find Pareto-optimal solutions."""
    pareto_frontier = []

    for candidate in evaluated_params:
        is_dominated = False

        for other in evaluated_params:
            if candidate == other:
                continue

            # Check if other dominates candidate
            dominates = all(
                other['objectives'][obj] >= candidate['objectives'][obj]
                for obj in objectives
            ) and any(
                other['objectives'][obj] > candidate['objectives'][obj]
                for obj in objectives
            )

            if dominates:
                is_dominated = True
                break

        if not is_dominated:
            pareto_frontier.append(candidate)

    return pareto_frontier


def _analyze_parameter_drift(param_history: List[Dict]) -> Dict:
    """Analyze how parameters change over time."""
    if not param_history:
        return {}

    # Convert to DataFrame for analysis
    param_df = pd.DataFrame(param_history)

    stability_metrics = {}

    for param in param_df.columns:
        values = param_df[param].values

        stability_metrics[param] = {
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'cv': float(np.std(values) / np.mean(values)) if np.mean(values) != 0 else 0
        }

    return stability_metrics
