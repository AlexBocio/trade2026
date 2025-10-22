# factor_analysis.py - Factor analysis and extraction

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression

class FactorAnalyzer:
    """
    Extract factors from return data using PCA or other methods.
    """

    def __init__(self, returns_df: pd.DataFrame):
        """
        Args:
            returns_df: DataFrame of asset returns
        """
        self.returns = returns_df
        self.factors = None
        self.loadings = None

    def extract_pca_factors(self, n_factors: int = 5):
        """
        Extract factors using Principal Component Analysis.

        Returns statistical factors that explain most variance.
        """
        # Standardize returns
        returns_std = (self.returns - self.returns.mean()) / self.returns.std()

        # PCA
        pca = PCA(n_components=n_factors)
        factor_returns = pca.fit_transform(returns_std)

        # Convert to DataFrame
        self.factors = pd.DataFrame(
            factor_returns,
            index=self.returns.index,
            columns=[f'PC{i+1}' for i in range(n_factors)]
        )

        # Factor loadings (how each asset loads on factors)
        self.loadings = pd.DataFrame(
            pca.components_.T,
            index=self.returns.columns,
            columns=self.factors.columns
        )

        # Explained variance
        explained_var = pca.explained_variance_ratio_

        return {
            'factors': self.factors,
            'loadings': self.loadings,
            'explained_variance': explained_var.tolist(),
            'total_explained': explained_var.sum()
        }

    def calculate_factor_betas(self, asset_returns: pd.Series):
        """
        Calculate asset's exposure (beta) to each factor.
        """
        if self.factors is None:
            self.extract_pca_factors()

        # Align data
        common_idx = asset_returns.index.intersection(self.factors.index)
        y = asset_returns.loc[common_idx].values
        X = self.factors.loc[common_idx].values

        # Regression
        model = LinearRegression()
        model.fit(X, y)

        betas = dict(zip(self.factors.columns, model.coef_))
        alpha = model.intercept_
        r_squared = model.score(X, y)

        return {
            'betas': betas,
            'alpha': alpha,
            'r_squared': r_squared
        }

    def factor_mimicking_portfolio(self, factor_name: str):
        """
        Create a portfolio that mimics a specific factor.

        Returns weights that maximize exposure to target factor.
        """
        if self.loadings is None:
            self.extract_pca_factors()

        # Weights proportional to factor loadings
        raw_weights = self.loadings[factor_name]

        # Long-short portfolio (positive and negative weights)
        weights = raw_weights / raw_weights.abs().sum()

        return weights.to_dict()
