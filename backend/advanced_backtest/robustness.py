# robustness.py - Test strategy robustness

import numpy as np
import pandas as pd
from typing import Callable, Dict

class RobustnessAnalyzer:
    """
    Test strategy robustness through various stress tests.
    """

    def __init__(self, data: pd.DataFrame, strategy_func: Callable, params: Dict):
        self.data = data
        self.strategy_func = strategy_func
        self.params = params

        # Baseline performance
        self.baseline_returns = self._calculate_returns(data, params)

    def _calculate_returns(self, data, params):
        """Calculate strategy returns."""
        signals = self.strategy_func(data, params)
        returns = data['returns'] * signals.shift(1)
        return returns.dropna()

    def monte_carlo_simulation(self, n_simulations=1000):
        """
        Monte Carlo simulation: randomly shuffle returns.
        Tests if strategy exploits genuine patterns vs. luck.
        """
        baseline_sharpe = np.sqrt(252) * self.baseline_returns.mean() / self.baseline_returns.std()

        simulated_sharpes = []

        for _ in range(n_simulations):
            # Shuffle returns (breaks time structure)
            shuffled_data = self.data.copy()
            shuffled_data['returns'] = np.random.permutation(shuffled_data['returns'].values)

            sim_returns = self._calculate_returns(shuffled_data, self.params)

            if len(sim_returns) > 0 and sim_returns.std() > 0:
                sim_sharpe = np.sqrt(252) * sim_returns.mean() / sim_returns.std()
                simulated_sharpes.append(sim_sharpe)

        # P-value: how often random performs better
        p_value = sum([s > baseline_sharpe for s in simulated_sharpes]) / len(simulated_sharpes)

        return {
            'baseline_sharpe': baseline_sharpe,
            'mean_random_sharpe': np.mean(simulated_sharpes),
            'p_value': p_value,
            'is_significant': p_value < 0.05
        }

    def parameter_sensitivity(self, param_name: str, variations: list):
        """
        Test how sensitive strategy is to parameter changes.
        Robust strategies should be stable across parameter range.
        """
        results = []

        for variation in variations:
            modified_params = self.params.copy()
            modified_params[param_name] = variation

            returns = self._calculate_returns(self.data, modified_params)

            if len(returns) > 0 and returns.std() > 0:
                sharpe = np.sqrt(252) * returns.mean() / returns.std()
                total_return = (1 + returns).prod() - 1
            else:
                sharpe = 0
                total_return = 0

            results.append({
                'param_value': variation,
                'sharpe': sharpe,
                'return': total_return
            })

        # Calculate sensitivity score
        sharpes = [r['sharpe'] for r in results]
        sensitivity = np.std(sharpes) / (np.abs(np.mean(sharpes)) + 1e-6)

        return {
            'results': results,
            'sensitivity_score': sensitivity,
            'is_robust': sensitivity < 0.5  # Lower = more robust
        }

    def kolmogorov_complexity(self):
        """
        Estimate strategy complexity.
        Simpler strategies (lower complexity) generalize better.

        We approximate K-complexity by counting:
        - Number of parameters
        - Number of indicators used
        - Number of conditional rules
        """
        # Count parameters
        n_params = len(self.params)

        # Count unique parameter values (proxy for rules)
        n_rules = len(set(self.params.values()))

        # Estimate complexity score (lower = simpler = better)
        complexity = n_params * np.log(n_rules + 1)

        return {
            'n_parameters': n_params,
            'n_rules': n_rules,
            'complexity_score': complexity,
            'is_simple': complexity < 5.0  # Threshold
        }

    def regime_change_test(self, split_point: str = None):
        """
        Test strategy performance before/after regime change.
        Robust strategies work in multiple market regimes.
        """
        if split_point is None:
            split_point = self.data.index[len(self.data) // 2]

        # Split data
        pre_regime = self.data.loc[:split_point]
        post_regime = self.data.loc[split_point:]

        # Performance in each regime
        pre_returns = self._calculate_returns(pre_regime, self.params)
        post_returns = self._calculate_returns(post_regime, self.params)

        pre_sharpe = np.sqrt(252) * pre_returns.mean() / pre_returns.std() if pre_returns.std() > 0 else 0
        post_sharpe = np.sqrt(252) * post_returns.mean() / post_returns.std() if post_returns.std() > 0 else 0

        # Stability score
        stability = min(pre_sharpe, post_sharpe) / max(pre_sharpe, post_sharpe) if max(pre_sharpe, post_sharpe) > 0 else 0

        return {
            'pre_regime_sharpe': pre_sharpe,
            'post_regime_sharpe': post_sharpe,
            'stability_score': stability,
            'is_stable': stability > 0.7
        }

    def comprehensive_report(self):
        """Generate comprehensive robustness report."""
        return {
            'monte_carlo': self.monte_carlo_simulation(n_simulations=500),
            'complexity': self.kolmogorov_complexity(),
            'regime_stability': self.regime_change_test()
        }
