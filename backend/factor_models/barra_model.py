# barra_model.py - Barra factor model implementation

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import yfinance as yf

class BarraFactorModel:
    """
    Barra-style multi-factor risk model.

    Factors:
    - Size (Market Cap)
    - Value (Book-to-Market)
    - Momentum (12-month return)
    - Quality (ROE)
    - Volatility (Historical Vol)
    - Growth (Revenue Growth)
    """

    def __init__(self, tickers: list, start_date: str, end_date: str):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date

        self.data = None
        self.factors = None
        self.factor_returns = None
        self.factor_covariance = None
        self.specific_risk = None

    def fetch_data(self):
        """Fetch price and fundamental data."""
        # Price data
        prices = yf.download(self.tickers, start=self.start_date,
                            end=self.end_date, progress=False)['Adj Close']

        returns = prices.pct_change().dropna()

        # Fetch fundamentals for each ticker
        fundamentals = []

        for ticker in self.tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info

                fundamentals.append({
                    'ticker': ticker,
                    'marketCap': info.get('marketCap', np.nan),
                    'bookValue': info.get('bookValue', np.nan),
                    'trailingPE': info.get('trailingPE', np.nan),
                    'profitMargins': info.get('profitMargins', np.nan),
                    'returnOnEquity': info.get('returnOnEquity', np.nan),
                    'revenueGrowth': info.get('revenueGrowth', np.nan)
                })
            except:
                fundamentals.append({
                    'ticker': ticker,
                    'marketCap': np.nan,
                    'bookValue': np.nan,
                    'trailingPE': np.nan,
                    'profitMargins': np.nan,
                    'returnOnEquity': np.nan,
                    'revenueGrowth': np.nan
                })

        fundamentals_df = pd.DataFrame(fundamentals).set_index('ticker')

        self.data = {
            'prices': prices,
            'returns': returns,
            'fundamentals': fundamentals_df
        }

        return self.data

    def calculate_factors(self):
        """Calculate factor exposures for each stock."""
        returns = self.data['returns']
        fundamentals = self.data['fundamentals']
        prices = self.data['prices']

        factors = pd.DataFrame(index=self.tickers)

        # Size factor (log of market cap)
        factors['Size'] = np.log(fundamentals['marketCap'])

        # Value factor (book-to-market ratio)
        market_cap = fundamentals['marketCap']
        book_value = fundamentals['bookValue']
        factors['Value'] = book_value / (market_cap / 1e9)  # Normalize

        # Momentum factor (12-month return)
        factors['Momentum'] = returns.iloc[-252:].mean() * 252  # Annualized

        # Quality factor (ROE)
        factors['Quality'] = fundamentals['returnOnEquity']

        # Volatility factor (historical volatility)
        factors['Volatility'] = returns.std() * np.sqrt(252)

        # Growth factor
        factors['Growth'] = fundamentals['revenueGrowth']

        # Standardize factors (z-scores)
        scaler = StandardScaler()
        factors_standardized = pd.DataFrame(
            scaler.fit_transform(factors.fillna(0)),
            index=factors.index,
            columns=factors.columns
        )

        self.factors = factors_standardized

        return self.factors

    def estimate_factor_returns(self):
        """Estimate factor returns using cross-sectional regression."""
        returns = self.data['returns']
        factors = self.factors

        # For each time period, regress stock returns on factor exposures
        factor_returns = pd.DataFrame(index=returns.index, columns=factors.columns)

        for date in returns.index:
            y = returns.loc[date].values  # Stock returns
            X = factors.values  # Factor exposures

            # Handle NaN values
            valid_idx = ~np.isnan(y) & ~np.any(np.isnan(X), axis=1)

            if valid_idx.sum() > len(factors.columns):
                model = LinearRegression()
                model.fit(X[valid_idx], y[valid_idx])
                factor_returns.loc[date] = model.coef_

        self.factor_returns = factor_returns.dropna()

        return self.factor_returns

    def calculate_factor_covariance(self):
        """Calculate factor covariance matrix."""
        if self.factor_returns is None:
            self.estimate_factor_returns()

        # Covariance of factor returns
        self.factor_covariance = self.factor_returns.cov()

        return self.factor_covariance

    def calculate_specific_risk(self):
        """Calculate stock-specific (idiosyncratic) risk."""
        returns = self.data['returns']
        factors = self.factors
        factor_returns = self.factor_returns

        # For each stock, calculate residual variance
        specific_risk = {}

        for ticker in self.tickers:
            stock_returns = returns[ticker].dropna()

            # Factor-explained returns
            factor_exposure = factors.loc[ticker].values
            explained_returns = factor_returns @ factor_exposure

            # Align indices
            common_idx = stock_returns.index.intersection(explained_returns.index)
            stock_returns_aligned = stock_returns.loc[common_idx]
            explained_returns_aligned = explained_returns.loc[common_idx]

            # Residual returns
            residual = stock_returns_aligned - explained_returns_aligned

            # Specific risk (volatility of residuals)
            specific_risk[ticker] = residual.std() * np.sqrt(252)  # Annualized

        self.specific_risk = pd.Series(specific_risk)

        return self.specific_risk

    def decompose_portfolio_risk(self, weights: dict):
        """
        Decompose portfolio risk into factor and specific components.

        Args:
            weights: Dict of {ticker: weight}

        Returns:
            Dict with risk decomposition
        """
        if self.factor_covariance is None:
            self.calculate_factor_covariance()

        if self.specific_risk is None:
            self.calculate_specific_risk()

        # Convert weights to array
        weight_array = np.array([weights.get(t, 0) for t in self.tickers])

        # Factor exposures of portfolio
        portfolio_exposures = (self.factors.T @ weight_array).values

        # Factor risk
        factor_variance = portfolio_exposures @ self.factor_covariance.values @ portfolio_exposures
        factor_risk = np.sqrt(factor_variance)

        # Specific risk
        specific_variance = sum([(weights.get(t, 0) ** 2) * (self.specific_risk[t] ** 2)
                                for t in self.tickers])
        specific_risk = np.sqrt(specific_variance)

        # Total risk
        total_risk = np.sqrt(factor_variance + specific_variance)

        return {
            'total_risk': total_risk * 100,  # Percentage
            'factor_risk': factor_risk * 100,
            'specific_risk': specific_risk * 100,
            'factor_contribution': (factor_variance / (factor_variance + specific_variance)) * 100,
            'factor_exposures': dict(zip(self.factors.columns, portfolio_exposures))
        }

    def factor_tilts(self, weights: dict):
        """Calculate how much portfolio tilts toward each factor."""
        weight_array = np.array([weights.get(t, 0) for t in self.tickers])
        tilts = self.factors.T @ weight_array

        return tilts.to_dict()
