# cross_validation.py - Advanced cross-validation for time series

import numpy as np
import pandas as pd
from typing import List, Tuple
import itertools

class CombinatorialPurgedCV:
    """
    Combinatorial Purged Cross-Validation (CPCV).

    Prevents data leakage in time series by:
    1. Purging overlapping observations
    2. Using combinatorial splits instead of sequential
    3. Embargoing test sets
    """

    def __init__(self, n_splits: int = 5, purge_pct: float = 0.05,
                 embargo_pct: float = 0.01):
        """
        Args:
            n_splits: Number of CV splits
            purge_pct: Percentage of data to purge around test set
            embargo_pct: Percentage of data to embargo after test set
        """
        self.n_splits = n_splits
        self.purge_pct = purge_pct
        self.embargo_pct = embargo_pct

    def split(self, data: pd.DataFrame) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Generate train/test splits with purging and embargo.

        Returns:
            List of (train_indices, test_indices) tuples
        """
        n = len(data)
        test_size = n // self.n_splits
        purge_size = int(n * self.purge_pct)
        embargo_size = int(n * self.embargo_pct)

        splits = []

        # Generate all possible test set positions
        test_starts = np.linspace(0, n - test_size, self.n_splits, dtype=int)

        for test_start in test_starts:
            test_end = test_start + test_size

            # Test indices
            test_indices = np.arange(test_start, test_end)

            # Purge: remove data near test set
            purge_start = max(0, test_start - purge_size)
            purge_end = min(n, test_end + purge_size)

            # Embargo: remove data after test set
            embargo_end = min(n, test_end + embargo_size)

            # Train indices: everything except purged/embargoed regions
            train_indices = np.concatenate([
                np.arange(0, purge_start),
                np.arange(embargo_end, n)
            ])

            splits.append((train_indices, test_indices))

        return splits

    def evaluate_strategy(self, data: pd.DataFrame, strategy_func,
                         param_grid: dict):
        """
        Evaluate strategy using CPCV.

        Returns performance metrics that account for overfitting.
        """
        splits = self.split(data)

        results = []

        for train_idx, test_idx in splits:
            train_data = data.iloc[train_idx]
            test_data = data.iloc[test_idx]

            # Optimize on train
            best_params = self._optimize_params(train_data, strategy_func, param_grid)

            # Evaluate on test
            signals = strategy_func(test_data, best_params)
            returns = test_data['returns'] * signals.shift(1)
            returns = returns.dropna()

            sharpe = np.sqrt(252) * returns.mean() / returns.std() if returns.std() > 0 else 0

            results.append({
                'sharpe': sharpe,
                'return': (1 + returns).prod() - 1,
                'params': best_params
            })

        return {
            'mean_sharpe': np.mean([r['sharpe'] for r in results]),
            'std_sharpe': np.std([r['sharpe'] for r in results]),
            'mean_return': np.mean([r['return'] for r in results]),
            'probability_of_skill': self._calculate_pos(results)
        }

    def _optimize_params(self, data, strategy_func, param_grid):
        """Optimize parameters on training data."""
        best_sharpe = -np.inf
        best_params = None

        for params in self._generate_combinations(param_grid):
            signals = strategy_func(data, params)
            returns = data['returns'] * signals.shift(1)
            returns = returns.dropna()

            sharpe = np.sqrt(252) * returns.mean() / returns.std() if returns.std() > 0 else 0

            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_params = params

        return best_params

    def _generate_combinations(self, param_grid):
        """Generate parameter combinations."""
        keys = list(param_grid.keys())
        values = list(param_grid.values())

        for combination in itertools.product(*values):
            yield dict(zip(keys, combination))

    def _calculate_pos(self, results):
        """
        Calculate Probability of Skill (POS).
        Based on Sharpe ratio distribution.
        """
        sharpes = [r['sharpe'] for r in results]

        if len(sharpes) < 2:
            return 0.5

        # T-statistic
        mean_sharpe = np.mean(sharpes)
        std_sharpe = np.std(sharpes)
        n = len(sharpes)

        if std_sharpe == 0:
            return 1.0 if mean_sharpe > 0 else 0.0

        t_stat = mean_sharpe / (std_sharpe / np.sqrt(n))

        # Convert to probability (using normal approximation)
        from scipy import stats
        pos = stats.norm.cdf(t_stat)

        return pos
