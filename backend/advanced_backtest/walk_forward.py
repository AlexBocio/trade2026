# walk_forward.py - Proper walk-forward analysis

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Tuple

class WalkForwardOptimizer:
    """
    Walk-Forward Optimization - prevents overfitting by continuously
    optimizing on in-sample data and testing on out-of-sample data.
    """

    def __init__(self, data: pd.DataFrame, strategy_func: Callable,
                 param_grid: Dict, train_period: int = 252,
                 test_period: int = 63):
        """
        Args:
            data: Price data DataFrame
            strategy_func: Function that takes (data, params) and returns signals
            param_grid: Dict of parameter ranges to optimize
            train_period: Training window size (days)
            test_period: Testing window size (days)
        """
        self.data = data
        self.strategy_func = strategy_func
        self.param_grid = param_grid
        self.train_period = train_period
        self.test_period = test_period

        self.results = []
        self.optimal_params_history = []

    def _generate_param_combinations(self):
        """Generate all parameter combinations from grid."""
        import itertools

        keys = list(self.param_grid.keys())
        values = list(self.param_grid.values())

        for combination in itertools.product(*values):
            yield dict(zip(keys, combination))

    def _calculate_sharpe(self, returns: pd.Series):
        """Calculate annualized Sharpe ratio."""
        if len(returns) == 0 or returns.std() == 0:
            return 0
        return np.sqrt(252) * returns.mean() / returns.std()

    def _optimize_window(self, train_data: pd.DataFrame):
        """Optimize parameters on training data."""
        best_sharpe = -np.inf
        best_params = None

        for params in self._generate_param_combinations():
            signals = self.strategy_func(train_data, params)
            returns = train_data['returns'] * signals.shift(1)
            returns = returns.dropna()

            sharpe = self._calculate_sharpe(returns)

            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_params = params

        return best_params, best_sharpe

    def run(self):
        """
        Run walk-forward optimization.

        Process:
        1. Train on window [0, train_period]
        2. Test on window [train_period, train_period + test_period]
        3. Slide window forward by test_period
        4. Repeat
        """
        total_length = len(self.data)
        current_start = 0

        while current_start + self.train_period + self.test_period <= total_length:
            # Define windows
            train_end = current_start + self.train_period
            test_end = train_end + self.test_period

            train_data = self.data.iloc[current_start:train_end].copy()
            test_data = self.data.iloc[train_end:test_end].copy()

            # Optimize on training data
            best_params, train_sharpe = self._optimize_window(train_data)
            self.optimal_params_history.append(best_params)

            # Test on out-of-sample data
            signals = self.strategy_func(test_data, best_params)
            test_returns = test_data['returns'] * signals.shift(1)
            test_returns = test_returns.dropna()

            test_sharpe = self._calculate_sharpe(test_returns)
            test_total_return = (1 + test_returns).prod() - 1

            self.results.append({
                'train_start': self.data.index[current_start],
                'train_end': self.data.index[train_end - 1],
                'test_start': self.data.index[train_end],
                'test_end': self.data.index[test_end - 1],
                'optimal_params': best_params,
                'train_sharpe': train_sharpe,
                'test_sharpe': test_sharpe,
                'test_return': test_total_return,
                'test_returns': test_returns
            })

            # Slide window
            current_start += self.test_period

        return self.results

    def get_summary(self):
        """Get summary statistics of walk-forward test."""
        if not self.results:
            return None

        all_test_returns = pd.concat([r['test_returns'] for r in self.results])

        return {
            'num_windows': len(self.results),
            'avg_test_sharpe': np.mean([r['test_sharpe'] for r in self.results]),
            'avg_test_return': np.mean([r['test_return'] for r in self.results]),
            'total_return': (1 + all_test_returns).prod() - 1,
            'total_sharpe': self._calculate_sharpe(all_test_returns),
            'win_rate': sum([r['test_return'] > 0 for r in self.results]) / len(self.results),
            'parameter_stability': self._calculate_param_stability()
        }

    def _calculate_param_stability(self):
        """
        Calculate how stable optimal parameters are across windows.
        Lower variance = more stable strategy.
        """
        if len(self.optimal_params_history) < 2:
            return 1.0

        # For each parameter, calculate coefficient of variation
        stability_scores = []

        for param_name in self.optimal_params_history[0].keys():
            values = [params[param_name] for params in self.optimal_params_history]

            if len(set(values)) == 1:  # All same value
                stability_scores.append(1.0)
            else:
                cv = np.std(values) / np.mean(values) if np.mean(values) != 0 else 1.0
                stability_scores.append(1 / (1 + cv))  # Convert to 0-1 score

        return np.mean(stability_scores)


# Example strategy function
def moving_average_crossover_strategy(data: pd.DataFrame, params: Dict):
    """
    Simple MA crossover strategy.

    params: {'fast': int, 'slow': int}
    """
    fast_ma = data['Close'].rolling(params['fast']).mean()
    slow_ma = data['Close'].rolling(params['slow']).mean()

    signals = pd.Series(0, index=data.index)
    signals[fast_ma > slow_ma] = 1   # Long
    signals[fast_ma <= slow_ma] = -1  # Short or flat

    return signals
