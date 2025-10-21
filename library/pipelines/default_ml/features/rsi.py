"""
RSI (Relative Strength Index) Calculator.

The RSI is a momentum oscillator that measures the speed and magnitude of price changes.
Values range from 0 to 100, with readings above 70 indicating overbought conditions
and readings below 30 indicating oversold conditions.
"""
import pandas as pd
import numpy as np


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).

    Args:
        prices: pandas Series of closing prices
        period: lookback period for RSI calculation (default: 14)

    Returns:
        pandas Series of RSI values (0-100)

    Example:
        >>> prices = pd.Series([100, 102, 101, 103, 105])
        >>> rsi = calculate_rsi(prices, period=3)
    """
    # Calculate price changes
    delta = prices.diff()

    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Calculate rolling average of gains and losses
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    # Calculate relative strength
    rs = avg_gain / avg_loss

    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))

    # Handle division by zero (when avg_loss = 0)
    rsi = rsi.fillna(100)

    return rsi


def calculate_rsi_smoothed(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate smoothed RSI using Wilder's smoothing method.

    This is the traditional RSI calculation that uses exponential smoothing
    rather than simple moving average.

    Args:
        prices: pandas Series of closing prices
        period: lookback period for RSI calculation (default: 14)

    Returns:
        pandas Series of smoothed RSI values (0-100)
    """
    delta = prices.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Use exponential weighted moving average for smoothing
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.fillna(100)

    return rsi
