# covariance.py - Advanced covariance matrix estimation

import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf, OAS, ShrunkCovariance

class CovarianceEstimator:
    """
    Advanced covariance matrix estimation methods.
    """

    def __init__(self, returns_df):
        """
        Args:
            returns_df: DataFrame of asset returns
        """
        self.returns = returns_df
        self.n_assets = len(returns_df.columns)
        self.n_samples = len(returns_df)

    def sample_covariance(self):
        """
        Standard sample covariance (baseline).
        """
        return self.returns.cov().values

    def ledoit_wolf(self):
        """
        Ledoit-Wolf shrinkage estimator.
        Shrinks sample covariance towards constant correlation matrix.
        Better for high-dimensional data.
        """
        lw = LedoitWolf()
        lw.fit(self.returns)

        return {
            'covariance': lw.covariance_,
            'shrinkage': lw.shrinkage_,
            'method': 'ledoit_wolf'
        }

    def oracle_approximating_shrinkage(self):
        """
        Oracle Approximating Shrinkage (OAS).
        Similar to Ledoit-Wolf but with different shrinkage target.
        """
        oas = OAS()
        oas.fit(self.returns)

        return {
            'covariance': oas.covariance_,
            'shrinkage': oas.shrinkage_,
            'method': 'oas'
        }

    def exponentially_weighted(self, halflife=60):
        """
        Exponentially Weighted Moving Average (EWMA) covariance.
        Gives more weight to recent observations.

        Args:
            halflife: Half-life in days for exponential weighting
        """
        ewma_cov = self.returns.ewm(halflife=halflife).cov()
        # Take the last covariance matrix
        latest_cov = ewma_cov.groupby(level=1).tail(1)
        cov_matrix = latest_cov.values.reshape(self.n_assets, self.n_assets)

        return {
            'covariance': cov_matrix,
            'halflife': halflife,
            'method': 'ewma'
        }

    def constant_correlation(self):
        """
        Constant Correlation Model.
        Assumes all correlations are equal (useful for large universes).
        """
        # Calculate average correlation
        corr_matrix = self.returns.corr()
        avg_corr = (corr_matrix.sum().sum() - self.n_assets) / (self.n_assets * (self.n_assets - 1))

        # Build constant correlation matrix
        const_corr = np.full((self.n_assets, self.n_assets), avg_corr)
        np.fill_diagonal(const_corr, 1.0)

        # Apply to volatilities
        vols = self.returns.std().values
        cov_matrix = np.outer(vols, vols) * const_corr

        return {
            'covariance': cov_matrix,
            'average_correlation': avg_corr,
            'method': 'constant_correlation'
        }

    def denoised_covariance(self, n_factors=None):
        """
        Random Matrix Theory (RMT) denoising.
        Filters out noise from sample covariance.
        """
        # Sample covariance
        sample_cov = self.returns.cov().values

        # Eigenvalue decomposition
        eigenvalues, eigenvectors = np.linalg.eigh(sample_cov)
        eigenvalues = eigenvalues[::-1]  # Descending order
        eigenvectors = eigenvectors[:, ::-1]

        # Marchenko-Pastur threshold
        q = self.n_assets / self.n_samples
        lambda_max = (1 + np.sqrt(q))**2 * np.var(self.returns.values.flatten())

        # Filter eigenvalues
        if n_factors is None:
            # Keep only eigenvalues above MP threshold
            n_factors = np.sum(eigenvalues > lambda_max)

        # Reconstruct with top eigenvalues
        eigenvalues_filtered = np.zeros_like(eigenvalues)
        eigenvalues_filtered[:n_factors] = eigenvalues[:n_factors]

        # Denoised covariance
        denoised_cov = eigenvectors @ np.diag(eigenvalues_filtered) @ eigenvectors.T

        return {
            'covariance': denoised_cov,
            'n_factors': n_factors,
            'explained_variance': np.sum(eigenvalues[:n_factors]) / np.sum(eigenvalues),
            'method': 'denoised'
        }

    def compare_estimators(self):
        """
        Compare all covariance estimation methods.
        """
        estimators = {
            'Sample': self.sample_covariance(),
            'Ledoit-Wolf': self.ledoit_wolf()['covariance'],
            'OAS': self.oracle_approximating_shrinkage()['covariance'],
            'EWMA': self.exponentially_weighted()['covariance'],
            'Constant Corr': self.constant_correlation()['covariance'],
            'Denoised': self.denoised_covariance()['covariance']
        }

        # Calculate condition numbers (stability metric)
        condition_numbers = {}
        for name, cov in estimators.items():
            condition_numbers[name] = np.linalg.cond(cov)

        return {
            'estimators': estimators,
            'condition_numbers': condition_numbers
        }
