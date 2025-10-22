# factor_library.py - Multi-Factor Stock Screening Library
# Comprehensive factor calculations for stock screening and ranking

import numpy as np
import pandas as pd
import yfinance as yf
from typing import Dict, Optional, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TechnicalFactors:
    """
    Technical factor calculations.

    Focuses on price action, momentum, volume, and volatility indicators.
    """

    @staticmethod
    def momentum(prices: pd.Series, period: int = 20) -> float:
        """
        Calculate momentum as percentage price change.

        Args:
            prices: Price series (most recent last)
            period: Lookback period in days

        Returns:
            Momentum as percentage change
        """
        if len(prices) < period + 1:
            return np.nan

        current = prices.iloc[-1]
        previous = prices.iloc[-period - 1]

        if previous == 0:
            return np.nan

        momentum = (current - previous) / previous * 100
        return float(momentum)

    @staticmethod
    def rsi(prices: pd.Series, period: int = 14) -> float:
        """
        Calculate Relative Strength Index (RSI).

        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss

        Args:
            prices: Price series
            period: RSI period (default 14)

        Returns:
            RSI value (0-100)
        """
        if len(prices) < period + 1:
            return np.nan

        # Calculate price changes
        delta = prices.diff()

        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)

        # Calculate average gain and loss
        avg_gain = gains.rolling(window=period).mean().iloc[-1]
        avg_loss = losses.rolling(window=period).mean().iloc[-1]

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return float(rsi)

    @staticmethod
    def macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
        """
        Calculate MACD (Moving Average Convergence Divergence).

        Args:
            prices: Price series
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period

        Returns:
            {
                'macd': MACD line,
                'signal': Signal line,
                'histogram': MACD histogram,
                'crossover': 1 if bullish crossover, -1 if bearish, 0 otherwise
            }
        """
        if len(prices) < slow + signal:
            return {'macd': np.nan, 'signal': np.nan, 'histogram': np.nan, 'crossover': 0}

        # Calculate EMAs
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()

        # MACD line
        macd_line = ema_fast - ema_slow

        # Signal line
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()

        # Histogram
        histogram = macd_line - signal_line

        # Detect crossover
        crossover = 0
        if len(histogram) >= 2:
            prev_hist = histogram.iloc[-2]
            curr_hist = histogram.iloc[-1]

            if prev_hist <= 0 and curr_hist > 0:
                crossover = 1  # Bullish crossover
            elif prev_hist >= 0 and curr_hist < 0:
                crossover = -1  # Bearish crossover

        return {
            'macd': float(macd_line.iloc[-1]),
            'signal': float(signal_line.iloc[-1]),
            'histogram': float(histogram.iloc[-1]),
            'crossover': crossover
        }

    @staticmethod
    def bollinger_bands(prices: pd.Series, period: int = 20, num_std: float = 2.0) -> Dict[str, float]:
        """
        Calculate Bollinger Bands and position.

        Args:
            prices: Price series
            period: Moving average period
            num_std: Number of standard deviations

        Returns:
            {
                'upper': Upper band,
                'middle': Middle band (SMA),
                'lower': Lower band,
                'percent_b': Position within bands (0-1),
                'bandwidth': Band width as % of middle
            }
        """
        if len(prices) < period:
            return {
                'upper': np.nan, 'middle': np.nan, 'lower': np.nan,
                'percent_b': np.nan, 'bandwidth': np.nan
            }

        # Calculate SMA and standard deviation
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()

        # Bollinger Bands
        upper = sma + (std * num_std)
        lower = sma - (std * num_std)

        current_price = prices.iloc[-1]
        middle = sma.iloc[-1]
        upper_val = upper.iloc[-1]
        lower_val = lower.iloc[-1]

        # %B: Position within bands (0 = lower band, 1 = upper band)
        if upper_val != lower_val:
            percent_b = (current_price - lower_val) / (upper_val - lower_val)
        else:
            percent_b = 0.5

        # Bandwidth: Width of bands as % of middle
        if middle != 0:
            bandwidth = (upper_val - lower_val) / middle * 100
        else:
            bandwidth = 0

        return {
            'upper': float(upper_val),
            'middle': float(middle),
            'lower': float(lower_val),
            'percent_b': float(percent_b),
            'bandwidth': float(bandwidth)
        }

    @staticmethod
    def volume_surge(volumes: pd.Series, period: int = 20) -> float:
        """
        Calculate volume surge as ratio to average volume.

        Args:
            volumes: Volume series
            period: Average volume period

        Returns:
            Volume surge ratio (current / average)
        """
        if len(volumes) < period + 1:
            return np.nan

        current_volume = volumes.iloc[-1]
        avg_volume = volumes.iloc[-period-1:-1].mean()

        if avg_volume == 0:
            return np.nan

        surge = current_volume / avg_volume
        return float(surge)

    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> float:
        """
        Calculate Average True Range (ATR).

        ATR measures volatility.

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ATR period

        Returns:
            ATR value
        """
        if len(high) < period + 1:
            return np.nan

        # True Range components
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))

        # True Range is the max of the three
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # ATR is the moving average of TR
        atr_val = tr.rolling(window=period).mean().iloc[-1]

        return float(atr_val)

    @staticmethod
    def support_resistance_distance(prices: pd.Series, period: int = 50) -> Dict[str, float]:
        """
        Calculate distance from support and resistance levels.

        Support = Recent low
        Resistance = Recent high

        Args:
            prices: Price series
            period: Lookback period

        Returns:
            {
                'distance_to_support': % distance to support,
                'distance_to_resistance': % distance to resistance,
                'support_level': Support price,
                'resistance_level': Resistance price
            }
        """
        if len(prices) < period:
            return {
                'distance_to_support': np.nan,
                'distance_to_resistance': np.nan,
                'support_level': np.nan,
                'resistance_level': np.nan
            }

        recent_prices = prices.iloc[-period:]
        current_price = prices.iloc[-1]

        support = recent_prices.min()
        resistance = recent_prices.max()

        # Distance as percentage
        if support != 0:
            dist_to_support = (current_price - support) / support * 100
        else:
            dist_to_support = np.nan

        if resistance != 0:
            dist_to_resistance = (resistance - current_price) / current_price * 100
        else:
            dist_to_resistance = np.nan

        return {
            'distance_to_support': float(dist_to_support),
            'distance_to_resistance': float(dist_to_resistance),
            'support_level': float(support),
            'resistance_level': float(resistance)
        }


class FundamentalFactors:
    """
    Fundamental factor calculations.

    Focuses on valuation, growth, profitability, and financial health.
    """

    @staticmethod
    def pe_ratio_zscore(ticker: str, universe_pe_ratios: List[float]) -> float:
        """
        Calculate P/E ratio z-score relative to universe.

        Negative z-score = undervalued relative to universe
        Positive z-score = overvalued relative to universe

        Args:
            ticker: Stock ticker
            universe_pe_ratios: List of P/E ratios for universe

        Returns:
            P/E z-score
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            pe_ratio = info.get('trailingPE', None) or info.get('forwardPE', None)

            if pe_ratio is None or pd.isna(pe_ratio):
                return np.nan

            # Filter out invalid P/E ratios
            valid_universe_pe = [pe for pe in universe_pe_ratios if pe is not None and not pd.isna(pe) and pe > 0]

            if len(valid_universe_pe) < 2:
                return np.nan

            # Calculate z-score
            mean_pe = np.mean(valid_universe_pe)
            std_pe = np.std(valid_universe_pe)

            if std_pe == 0:
                return 0.0

            z_score = (pe_ratio - mean_pe) / std_pe
            return float(z_score)

        except Exception as e:
            logger.warning(f"Error calculating P/E z-score for {ticker}: {e}")
            return np.nan

    @staticmethod
    def earnings_growth(ticker: str) -> float:
        """
        Calculate year-over-year earnings growth.

        Args:
            ticker: Stock ticker

        Returns:
            Earnings growth percentage
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            earnings_growth = info.get('earningsQuarterlyGrowth', None)

            if earnings_growth is None or pd.isna(earnings_growth):
                return np.nan

            return float(earnings_growth * 100)  # Convert to percentage

        except Exception as e:
            logger.warning(f"Error calculating earnings growth for {ticker}: {e}")
            return np.nan

    @staticmethod
    def revenue_growth(ticker: str) -> float:
        """
        Calculate year-over-year revenue growth.

        Args:
            ticker: Stock ticker

        Returns:
            Revenue growth percentage
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            revenue_growth = info.get('revenueGrowth', None)

            if revenue_growth is None or pd.isna(revenue_growth):
                return np.nan

            return float(revenue_growth * 100)  # Convert to percentage

        except Exception as e:
            logger.warning(f"Error calculating revenue growth for {ticker}: {e}")
            return np.nan

    @staticmethod
    def profit_margin(ticker: str) -> float:
        """
        Calculate profit margin.

        Args:
            ticker: Stock ticker

        Returns:
            Profit margin percentage
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            margin = info.get('profitMargins', None)

            if margin is None or pd.isna(margin):
                return np.nan

            return float(margin * 100)  # Convert to percentage

        except Exception as e:
            logger.warning(f"Error calculating profit margin for {ticker}: {e}")
            return np.nan

    @staticmethod
    def debt_to_equity(ticker: str) -> float:
        """
        Calculate debt-to-equity ratio.

        Lower is generally better (less leverage).

        Args:
            ticker: Stock ticker

        Returns:
            Debt-to-equity ratio
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            debt_to_equity = info.get('debtToEquity', None)

            if debt_to_equity is None or pd.isna(debt_to_equity):
                return np.nan

            return float(debt_to_equity)

        except Exception as e:
            logger.warning(f"Error calculating debt-to-equity for {ticker}: {e}")
            return np.nan

    @staticmethod
    def institutional_ownership(ticker: str) -> float:
        """
        Calculate institutional ownership percentage.

        Higher institutional ownership can indicate quality.

        Args:
            ticker: Stock ticker

        Returns:
            Institutional ownership percentage
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            inst_own = info.get('heldPercentInstitutions', None)

            if inst_own is None or pd.isna(inst_own):
                return np.nan

            return float(inst_own * 100)  # Convert to percentage

        except Exception as e:
            logger.warning(f"Error calculating institutional ownership for {ticker}: {e}")
            return np.nan


class StatisticalFactors:
    """
    Statistical factor calculations.

    Focuses on risk-adjusted returns, correlation, and statistical properties.
    """

    @staticmethod
    def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02, periods_per_year: int = 252) -> float:
        """
        Calculate Sharpe ratio.

        Sharpe = (Mean Return - Risk Free Rate) / Std Dev of Returns

        Args:
            returns: Return series
            risk_free_rate: Annual risk-free rate
            periods_per_year: Trading periods per year

        Returns:
            Annualized Sharpe ratio
        """
        if len(returns) < 2:
            return np.nan

        # Annualize mean and std
        mean_return = returns.mean() * periods_per_year
        std_return = returns.std() * np.sqrt(periods_per_year)

        if std_return == 0:
            return 0.0

        sharpe = (mean_return - risk_free_rate) / std_return
        return float(sharpe)

    @staticmethod
    def correlation_to_spy(returns: pd.Series, spy_returns: pd.Series) -> float:
        """
        Calculate correlation to SPY (market).

        Args:
            returns: Stock returns
            spy_returns: SPY returns

        Returns:
            Correlation coefficient (-1 to 1)
        """
        if len(returns) < 2 or len(spy_returns) < 2:
            return np.nan

        # Align series
        aligned = pd.concat([returns, spy_returns], axis=1, join='inner')

        if len(aligned) < 2:
            return np.nan

        corr = aligned.corr().iloc[0, 1]
        return float(corr)

    @staticmethod
    def mean_reversion_zscore(prices: pd.Series, period: int = 20) -> float:
        """
        Calculate mean reversion z-score.

        Z-score = (Current Price - SMA) / Std Dev

        Extreme z-scores indicate potential mean reversion opportunities.

        Args:
            prices: Price series
            period: Lookback period

        Returns:
            Z-score
        """
        if len(prices) < period + 1:
            return np.nan

        recent_prices = prices.iloc[-period-1:]
        current_price = prices.iloc[-1]

        mean = recent_prices.mean()
        std = recent_prices.std()

        if std == 0:
            return 0.0

        z_score = (current_price - mean) / std
        return float(z_score)

    @staticmethod
    def liquidity_score(volumes: pd.Series, prices: pd.Series, period: int = 20) -> float:
        """
        Calculate liquidity score (dollar volume).

        Liquidity = Average Daily Dollar Volume

        Args:
            volumes: Volume series
            prices: Price series
            period: Average period

        Returns:
            Average daily dollar volume
        """
        if len(volumes) < period or len(prices) < period:
            return np.nan

        # Calculate dollar volume
        dollar_volume = volumes * prices

        # Average over period
        avg_dollar_volume = dollar_volume.iloc[-period:].mean()

        return float(avg_dollar_volume)

    @staticmethod
    def hurst_exponent(prices: pd.Series, lags: List[int] = None) -> float:
        """
        Calculate Hurst exponent.

        H < 0.5: Mean-reverting
        H = 0.5: Random walk
        H > 0.5: Trending

        Args:
            prices: Price series
            lags: Lag periods to use

        Returns:
            Hurst exponent (0-1)
        """
        if lags is None:
            lags = [2, 4, 8, 16, 32]

        if len(prices) < max(lags) * 2:
            return np.nan

        try:
            tau = []
            lagvec = []

            for lag in lags:
                # Calculate std for this lag
                pp = np.subtract(prices[lag:].values, prices[:-lag].values)
                lagvec.append(lag)
                tau.append(np.std(pp))

            # Linear regression in log-log space
            if len(lagvec) < 2:
                return np.nan

            poly = np.polyfit(np.log(lagvec), np.log(tau), 1)
            hurst = poly[0]

            # Clamp to valid range
            hurst = max(0.0, min(1.0, hurst))

            return float(hurst)

        except Exception as e:
            logger.warning(f"Error calculating Hurst exponent: {e}")
            return np.nan


def calculate_all_factors(ticker: str,
                         period_days: int = 60,
                         universe_pe_ratios: List[float] = None,
                         spy_returns: pd.Series = None) -> Dict[str, float]:
    """
    Calculate all factors for a given ticker.

    Args:
        ticker: Stock ticker
        period_days: Historical data period
        universe_pe_ratios: P/E ratios for universe (for z-score)
        spy_returns: SPY returns for correlation

    Returns:
        Dictionary of all factor values
    """
    try:
        # Fetch data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days + 30)  # Extra buffer

        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)

        if len(hist) < 20:
            logger.warning(f"Insufficient data for {ticker}")
            return {}

        # Extract price series
        close = hist['Close']
        high = hist['High']
        low = hist['Low']
        volume = hist['Volume']
        returns = close.pct_change().dropna()

        # Technical factors
        tech = TechnicalFactors()
        momentum_20 = tech.momentum(close, 20)
        momentum_60 = tech.momentum(close, 60)
        rsi_val = tech.rsi(close)
        macd_data = tech.macd(close)
        bb_data = tech.bollinger_bands(close)
        vol_surge = tech.volume_surge(volume)
        atr_val = tech.atr(high, low, close)
        sr_data = tech.support_resistance_distance(close)

        # Fundamental factors
        fund = FundamentalFactors()
        pe_zscore = fund.pe_ratio_zscore(ticker, universe_pe_ratios) if universe_pe_ratios else np.nan
        earnings_gr = fund.earnings_growth(ticker)
        revenue_gr = fund.revenue_growth(ticker)
        profit_mgn = fund.profit_margin(ticker)
        debt_eq = fund.debt_to_equity(ticker)
        inst_own = fund.institutional_ownership(ticker)

        # Statistical factors
        stat = StatisticalFactors()
        sharpe = stat.sharpe_ratio(returns)
        corr_spy = stat.correlation_to_spy(returns, spy_returns) if spy_returns is not None else np.nan
        mean_rev_z = stat.mean_reversion_zscore(close)
        liquidity = stat.liquidity_score(volume, close)
        hurst = stat.hurst_exponent(close)

        return {
            # Technical
            'momentum_20d': momentum_20,
            'momentum_60d': momentum_60,
            'rsi': rsi_val,
            'macd': macd_data['macd'],
            'macd_signal': macd_data['signal'],
            'macd_histogram': macd_data['histogram'],
            'macd_crossover': macd_data['crossover'],
            'bb_percent_b': bb_data['percent_b'],
            'bb_bandwidth': bb_data['bandwidth'],
            'volume_surge': vol_surge,
            'atr': atr_val,
            'distance_to_support': sr_data['distance_to_support'],
            'distance_to_resistance': sr_data['distance_to_resistance'],

            # Fundamental
            'pe_zscore': pe_zscore,
            'earnings_growth': earnings_gr,
            'revenue_growth': revenue_gr,
            'profit_margin': profit_mgn,
            'debt_to_equity': debt_eq,
            'institutional_ownership': inst_own,

            # Statistical
            'sharpe_ratio': sharpe,
            'correlation_to_spy': corr_spy,
            'mean_reversion_zscore': mean_rev_z,
            'liquidity': liquidity,
            'hurst_exponent': hurst,

            # Metadata
            'current_price': float(close.iloc[-1]),
            'data_points': len(hist)
        }

    except Exception as e:
        logger.error(f"Error calculating factors for {ticker}: {e}")
        return {}
