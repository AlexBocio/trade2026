# optimizers.py - Portfolio optimization algorithms

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from pypfopt import EfficientFrontier, risk_models, expected_returns
from pypfopt import HRPOpt, BlackLittermanModel
from pypfopt.discrete_allocation import DiscreteAllocation
import cvxpy as cp

class PortfolioOptimizer:
    """
    Advanced portfolio optimization using multiple methods.
    """

    def __init__(self, prices_df):
        """
        Initialize with historical price data.

        Args:
            prices_df: DataFrame with dates as index, tickers as columns
        """
        self.prices = prices_df
        self.returns = prices_df.pct_change().dropna()
        self.tickers = prices_df.columns.tolist()

    def mean_variance(self, target_return=None, risk_free_rate=0.02):
        """
        Classic Markowitz Mean-Variance Optimization.

        Returns optimal weights for given return target or max Sharpe ratio.
        """
        # Calculate expected returns and covariance
        mu = expected_returns.mean_historical_return(self.prices)
        S = risk_models.sample_cov(self.prices)

        # Optimize
        ef = EfficientFrontier(mu, S)

        if target_return:
            ef.efficient_return(target_return)
        else:
            ef.max_sharpe(risk_free_rate=risk_free_rate)

        weights = ef.clean_weights()
        performance = ef.portfolio_performance(verbose=False, risk_free_rate=risk_free_rate)

        return {
            'weights': weights,
            'expected_return': performance[0],
            'volatility': performance[1],
            'sharpe_ratio': performance[2],
            'method': 'mean_variance'
        }

    def black_litterman(self, market_caps, views_dict, confidence_dict,
                        risk_free_rate=0.02, tau=0.05):
        """
        Black-Litterman model - combines market equilibrium with investor views.

        Args:
            market_caps: Dict of {ticker: market_cap}
            views_dict: Dict of {ticker: expected_return_view}
            confidence_dict: Dict of {ticker: confidence_in_view} (0-1)

        Example:
            market_caps = {'AAPL': 3000000000000, 'MSFT': 2800000000000}
            views_dict = {'AAPL': 0.15, 'MSFT': 0.12}  # 15% and 12% expected
            confidence_dict = {'AAPL': 0.8, 'MSFT': 0.6}
        """
        # Market-implied returns (equilibrium)
        mcaps = pd.Series(market_caps)
        S = risk_models.sample_cov(self.prices)
        delta = 2.5  # Risk aversion parameter

        # Black-Litterman
        bl = BlackLittermanModel(S, pi="market", market_caps=mcaps, risk_aversion=delta, tau=tau)

        # Add views
        for ticker, view in views_dict.items():
            confidence = confidence_dict.get(ticker, 0.5)
            bl.add_view({ticker: view}, confidence)

        # Get posterior returns
        bl_returns = bl.bl_returns()
        bl_cov = bl.bl_cov()

        # Optimize with Black-Litterman estimates
        ef = EfficientFrontier(bl_returns, bl_cov)
        ef.max_sharpe(risk_free_rate=risk_free_rate)
        weights = ef.clean_weights()
        performance = ef.portfolio_performance(verbose=False, risk_free_rate=risk_free_rate)

        return {
            'weights': weights,
            'expected_return': performance[0],
            'volatility': performance[1],
            'sharpe_ratio': performance[2],
            'posterior_returns': bl_returns.to_dict(),
            'method': 'black_litterman'
        }

    def risk_parity(self):
        """
        Risk Parity - allocate based on equal risk contribution.
        Each asset contributes equally to portfolio risk.
        """
        S = risk_models.sample_cov(self.prices)
        n = len(self.tickers)

        # Objective: minimize sum of squared differences in risk contributions
        def risk_parity_objective(weights):
            portfolio_vol = np.sqrt(weights @ S @ weights)
            marginal_contrib = S @ weights
            contrib = weights * marginal_contrib / portfolio_vol
            target_contrib = portfolio_vol / n
            return np.sum((contrib - target_contrib) ** 2)

        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # Weights sum to 1
        ]
        bounds = tuple((0, 1) for _ in range(n))

        # Initial guess - equal weights
        w0 = np.array([1/n] * n)

        # Optimize
        result = minimize(
            risk_parity_objective,
            w0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        weights_dict = dict(zip(self.tickers, result.x))

        # Calculate portfolio metrics
        portfolio_return = np.sum(result.x * self.returns.mean() * 252)
        portfolio_vol = np.sqrt(result.x @ S @ result.x)
        sharpe = portfolio_return / portfolio_vol

        return {
            'weights': weights_dict,
            'expected_return': portfolio_return,
            'volatility': portfolio_vol,
            'sharpe_ratio': sharpe,
            'method': 'risk_parity'
        }

    def hierarchical_risk_parity(self):
        """
        Hierarchical Risk Parity (HRP) - uses clustering for robustness.
        More stable than traditional mean-variance optimization.
        """
        hrp = HRPOpt(self.returns)
        weights = hrp.optimize()

        # Calculate performance
        portfolio_return = np.sum([weights[t] * self.returns[t].mean() * 252
                                  for t in self.tickers])
        S = risk_models.sample_cov(self.prices)
        w = np.array([weights[t] for t in self.tickers])
        portfolio_vol = np.sqrt(w @ S @ w)
        sharpe = portfolio_return / portfolio_vol

        return {
            'weights': weights,
            'expected_return': portfolio_return,
            'volatility': portfolio_vol,
            'sharpe_ratio': sharpe,
            'method': 'hierarchical_risk_parity'
        }

    def min_variance(self):
        """
        Minimum Variance Portfolio - lowest risk portfolio.
        """
        mu = expected_returns.mean_historical_return(self.prices)
        S = risk_models.sample_cov(self.prices)

        ef = EfficientFrontier(mu, S)
        ef.min_volatility()

        weights = ef.clean_weights()
        performance = ef.portfolio_performance(verbose=False)

        return {
            'weights': weights,
            'expected_return': performance[0],
            'volatility': performance[1],
            'sharpe_ratio': performance[2],
            'method': 'minimum_variance'
        }

    def max_diversification(self):
        """
        Maximum Diversification Portfolio.
        Maximizes the ratio of weighted average volatilities to portfolio volatility.
        """
        S = risk_models.sample_cov(self.prices)
        individual_vols = np.sqrt(np.diag(S))
        n = len(self.tickers)

        # Define diversification ratio
        def neg_diversification_ratio(weights):
            portfolio_vol = np.sqrt(weights @ S @ weights)
            weighted_avg_vol = np.sum(weights * individual_vols)
            return -weighted_avg_vol / portfolio_vol

        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
        ]
        bounds = tuple((0, 1) for _ in range(n))
        w0 = np.array([1/n] * n)

        result = minimize(
            neg_diversification_ratio,
            w0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        weights_dict = dict(zip(self.tickers, result.x))

        portfolio_return = np.sum(result.x * self.returns.mean() * 252)
        portfolio_vol = np.sqrt(result.x @ S @ result.x)
        sharpe = portfolio_return / portfolio_vol

        return {
            'weights': weights_dict,
            'expected_return': portfolio_return,
            'volatility': portfolio_vol,
            'sharpe_ratio': sharpe,
            'diversification_ratio': -result.fun,
            'method': 'max_diversification'
        }

    def efficient_frontier(self, n_points=50):
        """
        Generate the efficient frontier - optimal portfolios for different risk levels.
        """
        mu = expected_returns.mean_historical_return(self.prices)
        S = risk_models.sample_cov(self.prices)

        # Get min and max returns
        ef_min = EfficientFrontier(mu, S)
        ef_min.min_volatility()
        min_ret = ef_min.portfolio_performance()[0]

        ef_max = EfficientFrontier(mu, S)
        ef_max.max_sharpe()
        max_ret = ef_max.portfolio_performance()[0]

        # Generate frontier
        target_returns = np.linspace(min_ret, max_ret, n_points)
        frontier = []

        for target in target_returns:
            try:
                ef = EfficientFrontier(mu, S)
                ef.efficient_return(target)
                perf = ef.portfolio_performance()
                frontier.append({
                    'return': perf[0],
                    'volatility': perf[1],
                    'sharpe': perf[2]
                })
            except:
                continue

        return frontier

    def transaction_cost_optimization(self, current_weights, target_weights,
                                     cost_per_trade=0.001, min_trade_size=0.01):
        """
        Optimize portfolio with transaction costs.

        Args:
            current_weights: Current portfolio weights (dict)
            target_weights: Desired portfolio weights (dict)
            cost_per_trade: Transaction cost as fraction of trade value
            min_trade_size: Minimum trade size to execute (avoid tiny trades)
        """
        tickers = list(target_weights.keys())
        n = len(tickers)

        # Convert to arrays
        current = np.array([current_weights.get(t, 0) for t in tickers])
        target = np.array([target_weights[t] for t in tickers])

        # Decision variables: final weights
        w = cp.Variable(n)

        # Trade amounts
        trades = w - current

        # Objective: minimize distance to target + transaction costs
        mu = expected_returns.mean_historical_return(self.prices)
        mu_array = np.array([mu[t] for t in tickers])

        expected_return = mu_array @ w
        transaction_costs = cost_per_trade * cp.sum(cp.abs(trades))

        objective = cp.Maximize(expected_return - transaction_costs)

        # Constraints
        constraints = [
            cp.sum(w) == 1,  # Full investment
            w >= 0,  # Long only
        ]

        # Solve
        prob = cp.Problem(objective, constraints)
        prob.solve()

        final_weights = dict(zip(tickers, w.value))
        actual_trades = dict(zip(tickers, trades.value))

        return {
            'weights': final_weights,
            'trades': actual_trades,
            'transaction_cost': cost_per_trade * np.sum(np.abs(trades.value)),
            'method': 'transaction_cost_aware'
        }
