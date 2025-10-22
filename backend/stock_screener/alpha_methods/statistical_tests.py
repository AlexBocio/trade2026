# statistical_tests.py - Statistical Tests for Pairs Trading
# Cointegration, half-life, Hurst exponent, and stationarity tests

from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from scipy import stats
from statsmodels.tsa.stattools import adfuller, coint
from statsmodels.regression.linear_model import OLS
import logging

logger = logging.getLogger(__name__)


class StatisticalTests:
    """
    Statistical tests for pairs trading validation.

    Tests implemented:
    1. Cointegration (Engle-Granger)
    2. Half-life of mean reversion
    3. Hurst exponent (mean reversion vs trending)
    4. Augmented Dickey-Fuller (stationarity)
    5. Correlation stability
    """

    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode

    def test_cointegration(self, symbol1: str, symbol2: str, lookback_days: int = 252) -> Dict:
        """
        Test if two symbols are cointegrated.

        Args:
            symbol1: First symbol
            symbol2: Second symbol
            lookback_days: Historical data period

        Returns:
            {
                'symbol1': str,
                'symbol2': str,
                'is_cointegrated': bool,
                'p_value': float,
                'test_statistic': float,
                'critical_values': Dict[str, float],
                'hedge_ratio': float,
                'interpretation': str,
                'confidence': str ('1%', '5%', '10%', 'not_significant')
            }
        """
        try:
            if self.mock_mode:
                return self._mock_cointegration_result(symbol1, symbol2)

            # Fetch data
            prices1 = self._fetch_prices(symbol1, lookback_days)
            prices2 = self._fetch_prices(symbol2, lookback_days)

            if prices1 is None or prices2 is None:
                return self._default_cointegration_result(symbol1, symbol2)

            # Align data
            df = pd.concat([prices1, prices2], axis=1).dropna()
            if len(df) < 30:
                return self._default_cointegration_result(symbol1, symbol2)

            # Engle-Granger cointegration test
            score, p_value, crit_values = coint(df.iloc[:, 0], df.iloc[:, 1])

            # Calculate hedge ratio (beta from OLS regression)
            model = OLS(df.iloc[:, 0], df.iloc[:, 1])
            results = model.fit()
            hedge_ratio = float(results.params[0])

            # Determine significance level
            is_cointegrated = bool(p_value < 0.05)

            if p_value < 0.01:
                confidence = '1%'
            elif p_value < 0.05:
                confidence = '5%'
            elif p_value < 0.10:
                confidence = '10%'
            else:
                confidence = 'not_significant'

            interpretation = self._interpret_cointegration(is_cointegrated, p_value, confidence)

            return {
                'symbol1': symbol1,
                'symbol2': symbol2,
                'is_cointegrated': is_cointegrated,
                'p_value': float(p_value),
                'test_statistic': float(score),
                'critical_values': {
                    '1%': float(crit_values[0]),
                    '5%': float(crit_values[1]),
                    '10%': float(crit_values[2])
                },
                'hedge_ratio': hedge_ratio,
                'confidence': confidence,
                'interpretation': interpretation,
                'analysis_date': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error testing cointegration {symbol1}/{symbol2}: {e}")
            return self._default_cointegration_result(symbol1, symbol2)

    def calculate_half_life(self, symbol1: str, symbol2: str, hedge_ratio: float, lookback_days: int = 252) -> Dict:
        """
        Calculate half-life of mean reversion for a spread.

        Args:
            symbol1: First symbol
            symbol2: Second symbol
            hedge_ratio: Hedge ratio from cointegration test
            lookback_days: Historical data period

        Returns:
            {
                'symbol1': str,
                'symbol2': str,
                'half_life_days': float,
                'is_tradeable': bool,
                'interpretation': str,
                'optimal_holding_period': float (days)
            }
        """
        try:
            if self.mock_mode:
                return self._mock_half_life_result(symbol1, symbol2)

            # Fetch data
            prices1 = self._fetch_prices(symbol1, lookback_days)
            prices2 = self._fetch_prices(symbol2, lookback_days)

            if prices1 is None or prices2 is None:
                return self._default_half_life_result(symbol1, symbol2)

            # Calculate spread
            df = pd.concat([prices1, prices2], axis=1).dropna()
            if len(df) < 30:
                return self._default_half_life_result(symbol1, symbol2)

            spread = df.iloc[:, 0] - hedge_ratio * df.iloc[:, 1]

            # Calculate half-life using AR(1) model
            spread_lag = spread.shift(1)
            spread_diff = spread - spread_lag

            # Remove NaN values
            df_hl = pd.concat([spread_diff, spread_lag], axis=1).dropna()

            if len(df_hl) < 10:
                return self._default_half_life_result(symbol1, symbol2)

            # Fit AR(1): spread_diff = lambda * spread_lag + epsilon
            model = OLS(df_hl.iloc[:, 0], df_hl.iloc[:, 1])
            results = model.fit()
            lambda_param = results.params[0]

            # Half-life = -log(2) / log(1 + lambda)
            if lambda_param >= 0:
                # No mean reversion
                half_life = np.inf
            else:
                half_life = -np.log(2) / np.log(1 + lambda_param)

            # Determine if tradeable (half-life between 1 and 30 days is ideal)
            is_tradeable = 1 <= half_life <= 30

            interpretation = self._interpret_half_life(half_life, is_tradeable)

            # Optimal holding period is ~2-3x half-life
            optimal_holding = half_life * 2.5 if half_life != np.inf else None

            return {
                'symbol1': symbol1,
                'symbol2': symbol2,
                'half_life_days': float(half_life) if half_life != np.inf else None,
                'is_tradeable': is_tradeable,
                'lambda': float(lambda_param),
                'optimal_holding_period': float(optimal_holding) if optimal_holding else None,
                'interpretation': interpretation,
                'analysis_date': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error calculating half-life {symbol1}/{symbol2}: {e}")
            return self._default_half_life_result(symbol1, symbol2)

    def calculate_hurst_exponent(self, symbol: str, lookback_days: int = 252) -> Dict:
        """
        Calculate Hurst exponent to determine mean reversion vs trending behavior.

        H < 0.5: Mean reverting
        H = 0.5: Random walk (Brownian motion)
        H > 0.5: Trending

        Args:
            symbol: Stock symbol
            lookback_days: Historical data period

        Returns:
            {
                'symbol': str,
                'hurst_exponent': float,
                'behavior': str ('mean_reverting', 'random_walk', 'trending'),
                'interpretation': str,
                'suitable_for_pairs': bool
            }
        """
        try:
            if self.mock_mode:
                return self._mock_hurst_result(symbol)

            # Fetch data
            prices = self._fetch_prices(symbol, lookback_days)

            if prices is None or len(prices) < 50:
                return self._default_hurst_result(symbol)

            # Calculate Hurst exponent using R/S analysis
            lags = range(2, 100)
            tau = []

            for lag in lags:
                # Split time series into lag-sized chunks
                n_chunks = len(prices) // lag

                if n_chunks < 2:
                    continue

                rs_values = []

                for i in range(n_chunks):
                    chunk = prices.iloc[i*lag:(i+1)*lag]

                    if len(chunk) < lag:
                        continue

                    # Calculate mean
                    mean_chunk = chunk.mean()

                    # Calculate cumulative deviation
                    cumsum = (chunk - mean_chunk).cumsum()

                    # Calculate range
                    R = cumsum.max() - cumsum.min()

                    # Calculate standard deviation
                    S = chunk.std()

                    if S > 0:
                        rs_values.append(R / S)

                if len(rs_values) > 0:
                    tau.append(np.mean(rs_values))

            if len(tau) < 10:
                return self._default_hurst_result(symbol)

            # Fit power law: log(R/S) = H * log(lag) + constant
            log_lags = np.log([lag for lag in lags[:len(tau)]])
            log_tau = np.log(tau)

            # Linear regression
            poly = np.polyfit(log_lags, log_tau, 1)
            hurst = float(poly[0])

            # Classify behavior
            if hurst < 0.4:
                behavior = 'mean_reverting'
                suitable_for_pairs = True
            elif hurst < 0.6:
                behavior = 'random_walk'
                suitable_for_pairs = False
            else:
                behavior = 'trending'
                suitable_for_pairs = False

            interpretation = self._interpret_hurst(hurst, behavior)

            return {
                'symbol': symbol,
                'hurst_exponent': hurst,
                'behavior': behavior,
                'suitable_for_pairs': suitable_for_pairs,
                'interpretation': interpretation,
                'analysis_date': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error calculating Hurst exponent for {symbol}: {e}")
            return self._default_hurst_result(symbol)

    def test_stationarity(self, symbol: str, lookback_days: int = 252) -> Dict:
        """
        Test if a price series is stationary using Augmented Dickey-Fuller test.

        Args:
            symbol: Stock symbol
            lookback_days: Historical data period

        Returns:
            {
                'symbol': str,
                'is_stationary': bool,
                'p_value': float,
                'test_statistic': float,
                'critical_values': Dict[str, float],
                'interpretation': str
            }
        """
        try:
            if self.mock_mode:
                return self._mock_stationarity_result(symbol)

            # Fetch data
            prices = self._fetch_prices(symbol, lookback_days)

            if prices is None or len(prices) < 30:
                return self._default_stationarity_result(symbol)

            # Augmented Dickey-Fuller test
            result = adfuller(prices, autolag='AIC')

            adf_statistic = result[0]
            p_value = result[1]
            critical_values = result[4]

            is_stationary = p_value < 0.05

            interpretation = self._interpret_stationarity(is_stationary, p_value)

            return {
                'symbol': symbol,
                'is_stationary': is_stationary,
                'p_value': float(p_value),
                'test_statistic': float(adf_statistic),
                'critical_values': {
                    '1%': float(critical_values['1%']),
                    '5%': float(critical_values['5%']),
                    '10%': float(critical_values['10%'])
                },
                'interpretation': interpretation,
                'analysis_date': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error testing stationarity for {symbol}: {e}")
            return self._default_stationarity_result(symbol)

    def _fetch_prices(self, symbol: str, lookback_days: int) -> Optional[pd.Series]:
        """Fetch historical closing prices."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days + 20)
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            return hist['Close'] if len(hist) >= 20 else None
        except:
            return None

    # Interpretation methods
    def _interpret_cointegration(self, is_cointegrated: bool, p_value: float, confidence: str) -> str:
        if is_cointegrated:
            return f"Strong cointegration detected (p={p_value:.4f}, {confidence} confidence). Suitable for pairs trading."
        return f"No significant cointegration (p={p_value:.4f}). Not recommended for pairs trading."

    def _interpret_half_life(self, half_life: float, is_tradeable: bool) -> str:
        if half_life == np.inf:
            return "No mean reversion detected. Spread does not revert."
        elif is_tradeable:
            return f"Good mean reversion ({half_life:.1f} days). Suitable for pairs trading."
        elif half_life < 1:
            return f"Very fast mean reversion ({half_life:.1f} days). May be too fast for practical trading."
        else:
            return f"Slow mean reversion ({half_life:.1f} days). May require long holding periods."

    def _interpret_hurst(self, hurst: float, behavior: str) -> str:
        if behavior == 'mean_reverting':
            return f"Mean reverting behavior (H={hurst:.3f}). Excellent for pairs trading."
        elif behavior == 'random_walk':
            return f"Random walk behavior (H={hurst:.3f}). Not suitable for pairs trading."
        else:
            return f"Trending behavior (H={hurst:.3f}). Not suitable for pairs trading."

    def _interpret_stationarity(self, is_stationary: bool, p_value: float) -> str:
        if is_stationary:
            return f"Stationary series (p={p_value:.4f}). Suitable for mean reversion strategies."
        return f"Non-stationary series (p={p_value:.4f}). Not suitable for mean reversion."

    # Default results for error cases
    def _default_cointegration_result(self, symbol1: str, symbol2: str) -> Dict:
        return {
            'symbol1': symbol1,
            'symbol2': symbol2,
            'is_cointegrated': False,
            'p_value': 1.0,
            'test_statistic': 0.0,
            'critical_values': {'1%': 0, '5%': 0, '10%': 0},
            'hedge_ratio': 0.0,
            'confidence': 'not_significant',
            'interpretation': 'Insufficient data',
            'analysis_date': datetime.now().isoformat()
        }

    def _default_half_life_result(self, symbol1: str, symbol2: str) -> Dict:
        return {
            'symbol1': symbol1,
            'symbol2': symbol2,
            'half_life_days': None,
            'is_tradeable': False,
            'lambda': 0.0,
            'optimal_holding_period': None,
            'interpretation': 'Insufficient data',
            'analysis_date': datetime.now().isoformat()
        }

    def _default_hurst_result(self, symbol: str) -> Dict:
        return {
            'symbol': symbol,
            'hurst_exponent': 0.5,
            'behavior': 'unknown',
            'suitable_for_pairs': False,
            'interpretation': 'Insufficient data',
            'analysis_date': datetime.now().isoformat()
        }

    def _default_stationarity_result(self, symbol: str) -> Dict:
        return {
            'symbol': symbol,
            'is_stationary': False,
            'p_value': 1.0,
            'test_statistic': 0.0,
            'critical_values': {'1%': 0, '5%': 0, '10%': 0},
            'interpretation': 'Insufficient data',
            'analysis_date': datetime.now().isoformat()
        }

    # Mock methods for testing
    def _mock_cointegration_result(self, symbol1: str, symbol2: str) -> Dict:
        p_value = np.random.uniform(0.01, 0.15)
        is_cointegrated = p_value < 0.05
        return {
            'symbol1': symbol1,
            'symbol2': symbol2,
            'is_cointegrated': is_cointegrated,
            'p_value': p_value,
            'test_statistic': np.random.uniform(-3, -1),
            'critical_values': {'1%': -3.5, '5%': -2.9, '10%': -2.6},
            'hedge_ratio': np.random.uniform(0.8, 1.2),
            'confidence': '5%' if is_cointegrated else 'not_significant',
            'interpretation': self._interpret_cointegration(is_cointegrated, p_value, '5%'),
            'analysis_date': datetime.now().isoformat()
        }

    def _mock_half_life_result(self, symbol1: str, symbol2: str) -> Dict:
        half_life = np.random.uniform(5, 25)
        is_tradeable = True
        return {
            'symbol1': symbol1,
            'symbol2': symbol2,
            'half_life_days': half_life,
            'is_tradeable': is_tradeable,
            'lambda': -0.05,
            'optimal_holding_period': half_life * 2.5,
            'interpretation': self._interpret_half_life(half_life, is_tradeable),
            'analysis_date': datetime.now().isoformat()
        }

    def _mock_hurst_result(self, symbol: str) -> Dict:
        hurst = np.random.uniform(0.3, 0.7)
        if hurst < 0.4:
            behavior = 'mean_reverting'
            suitable = True
        elif hurst < 0.6:
            behavior = 'random_walk'
            suitable = False
        else:
            behavior = 'trending'
            suitable = False

        return {
            'symbol': symbol,
            'hurst_exponent': hurst,
            'behavior': behavior,
            'suitable_for_pairs': suitable,
            'interpretation': self._interpret_hurst(hurst, behavior),
            'analysis_date': datetime.now().isoformat()
        }

    def _mock_stationarity_result(self, symbol: str) -> Dict:
        p_value = np.random.uniform(0.01, 0.15)
        is_stationary = p_value < 0.05
        return {
            'symbol': symbol,
            'is_stationary': is_stationary,
            'p_value': p_value,
            'test_statistic': np.random.uniform(-4, -1),
            'critical_values': {'1%': -3.5, '5%': -2.9, '10%': -2.6},
            'interpretation': self._interpret_stationarity(is_stationary, p_value),
            'analysis_date': datetime.now().isoformat()
        }


# Module-level instance
_stat_tests = StatisticalTests()


def test_cointegration(symbol1: str, symbol2: str, lookback_days: int = 252) -> Dict:
    """Test cointegration between two symbols."""
    return _stat_tests.test_cointegration(symbol1, symbol2, lookback_days)


def calculate_half_life(symbol1: str, symbol2: str, hedge_ratio: float, lookback_days: int = 252) -> Dict:
    """Calculate half-life of mean reversion."""
    return _stat_tests.calculate_half_life(symbol1, symbol2, hedge_ratio, lookback_days)


def calculate_hurst_exponent(symbol: str, lookback_days: int = 252) -> Dict:
    """Calculate Hurst exponent."""
    return _stat_tests.calculate_hurst_exponent(symbol, lookback_days)


def test_stationarity(symbol: str, lookback_days: int = 252) -> Dict:
    """Test stationarity using ADF test."""
    return _stat_tests.test_stationarity(symbol, lookback_days)
