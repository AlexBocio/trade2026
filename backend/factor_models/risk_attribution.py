# risk_attribution.py - Risk attribution and decomposition

import numpy as np
import pandas as pd
from typing import Dict, List

class RiskAttributor:
    """
    Decompose portfolio risk into factor contributions.

    Methods:
    - Factor risk contribution
    - Marginal contribution to risk (MCR)
    - Component contribution to risk (CCR)
    - Risk budgeting
    """

    def __init__(self, factor_model):
        """
        Args:
            factor_model: A fitted BarraFactorModel instance
        """
        self.factor_model = factor_model

    def marginal_contribution_to_risk(self, weights: Dict[str, float]):
        """
        Calculate marginal contribution to risk (MCR) for each position.

        MCR: How much does portfolio risk increase if we increase
        a position by $1?
        """
        weight_array = np.array([weights.get(t, 0) for t in self.factor_model.tickers])

        # Portfolio factor exposures
        portfolio_exposures = (self.factor_model.factors.T @ weight_array).values

        # Factor covariance matrix
        F = self.factor_model.factor_covariance.values

        # Specific risk diagonal matrix
        D = np.diag([self.factor_model.specific_risk[t]**2 for t in self.factor_model.tickers])

        # Total portfolio variance
        factor_var = portfolio_exposures @ F @ portfolio_exposures
        specific_var = weight_array @ D @ weight_array
        portfolio_var = factor_var + specific_var
        portfolio_risk = np.sqrt(portfolio_var)

        # Marginal contribution to risk for each asset
        # MCR_i = (Beta_i @ F @ Portfolio_Exposures + specific_risk_i^2 * weight_i) / portfolio_risk
        mcr = {}

        for i, ticker in enumerate(self.factor_model.tickers):
            beta_i = self.factor_model.factors.loc[ticker].values

            factor_contribution = beta_i @ F @ portfolio_exposures
            specific_contribution = D[i, i] * weight_array[i]

            mcr[ticker] = (factor_contribution + specific_contribution) / portfolio_risk

        return mcr

    def component_contribution_to_risk(self, weights: Dict[str, float]):
        """
        Calculate component contribution to risk (CCR).

        CCR: How much of total portfolio risk comes from each position?
        CCR_i = weight_i * MCR_i
        """
        mcr = self.marginal_contribution_to_risk(weights)

        ccr = {ticker: weights.get(ticker, 0) * mcr[ticker]
               for ticker in self.factor_model.tickers}

        # Convert to percentage
        total_risk = sum(ccr.values())
        ccr_pct = {ticker: (ccr[ticker] / total_risk) * 100
                   for ticker in ccr}

        return {
            'absolute': ccr,
            'percentage': ccr_pct
        }

    def factor_risk_contribution(self, weights: Dict[str, float]):
        """
        Calculate how much each factor contributes to portfolio risk.
        """
        weight_array = np.array([weights.get(t, 0) for t in self.factor_model.tickers])

        # Portfolio factor exposures
        portfolio_exposures = (self.factor_model.factors.T @ weight_array).values

        # Factor covariance
        F = self.factor_model.factor_covariance.values

        # Total factor variance
        factor_var = portfolio_exposures @ F @ portfolio_exposures

        # Marginal contribution of each factor
        factor_mcr = F @ portfolio_exposures / np.sqrt(factor_var)

        # Component contribution of each factor
        factor_ccr = portfolio_exposures * factor_mcr

        # Convert to percentage
        factor_ccr_pct = (factor_ccr / np.sqrt(factor_var)) * 100

        return {
            'factor_names': self.factor_model.factors.columns.tolist(),
            'exposures': portfolio_exposures.tolist(),
            'marginal_contribution': factor_mcr.tolist(),
            'component_contribution': factor_ccr.tolist(),
            'contribution_percentage': factor_ccr_pct.tolist()
        }

    def risk_budget_analysis(self, weights: Dict[str, float],
                            target_budgets: Dict[str, float] = None):
        """
        Analyze how risk is budgeted across positions.

        Args:
            weights: Current portfolio weights
            target_budgets: Target risk budgets (optional)

        Returns:
            Comparison of actual vs target risk budgets
        """
        ccr = self.component_contribution_to_risk(weights)
        actual_budgets = ccr['percentage']

        if target_budgets is None:
            # Equal risk contribution
            n = len(self.factor_model.tickers)
            target_budgets = {ticker: 100.0 / n for ticker in self.factor_model.tickers}

        # Calculate deviations
        deviations = {ticker: actual_budgets[ticker] - target_budgets.get(ticker, 0)
                     for ticker in self.factor_model.tickers}

        # Sum of squared deviations
        total_deviation = np.sqrt(sum([d**2 for d in deviations.values()]))

        return {
            'actual_budgets': actual_budgets,
            'target_budgets': target_budgets,
            'deviations': deviations,
            'total_deviation': total_deviation
        }

    def stress_test(self, weights: Dict[str, float],
                   factor_shocks: Dict[str, float]):
        """
        Stress test: What happens to portfolio if factors move?

        Args:
            weights: Portfolio weights
            factor_shocks: Dict of {factor_name: shock_size}
                          e.g., {'Size': -0.02, 'Value': 0.03}

        Returns:
            Expected portfolio return under stress scenario
        """
        weight_array = np.array([weights.get(t, 0) for t in self.factor_model.tickers])

        # Portfolio factor exposures
        portfolio_exposures = self.factor_model.factors.T @ weight_array

        # Convert shocks to array
        shock_array = np.array([factor_shocks.get(f, 0)
                               for f in self.factor_model.factors.columns])

        # Expected return = exposures @ shocks
        expected_return = portfolio_exposures.values @ shock_array

        # Per-asset contribution
        asset_contributions = {}
        for ticker in self.factor_model.tickers:
            factor_exposures = self.factor_model.factors.loc[ticker].values
            contribution = factor_exposures @ shock_array * weights.get(ticker, 0)
            asset_contributions[ticker] = contribution

        return {
            'total_impact': expected_return * 100,  # Percentage
            'asset_contributions': asset_contributions,
            'factor_exposures': portfolio_exposures.to_dict()
        }

    def diversification_ratio(self, weights: Dict[str, float]):
        """
        Calculate diversification ratio.

        DR = (weighted average volatility) / (portfolio volatility)

        Higher DR = more diversified
        """
        weight_array = np.array([weights.get(t, 0) for t in self.factor_model.tickers])

        # Individual asset volatilities
        asset_vols = []
        for ticker in self.factor_model.tickers:
            # Total risk = sqrt(factor_risk^2 + specific_risk^2)
            factor_exp = self.factor_model.factors.loc[ticker].values
            factor_var = factor_exp @ self.factor_model.factor_covariance.values @ factor_exp
            specific_var = self.factor_model.specific_risk[ticker]**2
            total_vol = np.sqrt(factor_var + specific_var)
            asset_vols.append(total_vol)

        asset_vols = np.array(asset_vols)

        # Weighted average volatility
        weighted_avg_vol = weight_array @ asset_vols

        # Portfolio volatility
        risk_decomp = self.factor_model.decompose_portfolio_risk(weights)
        portfolio_vol = risk_decomp['total_risk'] / 100

        # Diversification ratio
        dr = weighted_avg_vol / portfolio_vol

        return {
            'diversification_ratio': dr,
            'weighted_avg_volatility': weighted_avg_vol * 100,
            'portfolio_volatility': portfolio_vol * 100,
            'diversification_benefit': (1 - 1/dr) * 100  # Percentage risk reduction
        }
