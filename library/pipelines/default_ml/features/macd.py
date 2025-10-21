"""
MACD (Moving Average Convergence Divergence) Calculator.

MACD is a trend-following momentum indicator that shows the relationship between
two exponential moving averages (EMAs) of prices. It consists of three components:
- MACD Line: Difference between fast EMA and slow EMA
- Signal Line: EMA of the MACD line
- Histogram: Difference between MACD line and signal line
"""
import pandas as pd
import numpy as np


def calculate_macd(
    prices: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9
) -> pd.DataFrame:
    """
    Calculate MACD indicator with all three components.

    Args:
        prices: pandas Series of closing prices
        fast: period for fast EMA (default: 12)
        slow: period for slow EMA (default: 26)
        signal: period for signal line EMA (default: 9)

    Returns:
        pandas DataFrame with columns: 'macd', 'signal', 'histogram'

    Example:
        >>> prices = pd.Series([100, 102, 101, 103, 105, 107, 106, 108])
        >>> macd_df = calculate_macd(prices, fast=5, slow=10, signal=3)
        >>> print(macd_df[['macd', 'signal', 'histogram']])
    """
    # Calculate EMAs
    ema_fast = prices.ewm(span=fast, adjust=False, min_periods=fast).mean()
    ema_slow = prices.ewm(span=slow, adjust=False, min_periods=slow).mean()

    # Calculate MACD line
    macd_line = ema_fast - ema_slow

    # Calculate signal line
    signal_line = macd_line.ewm(span=signal, adjust=False, min_periods=signal).mean()

    # Calculate histogram
    histogram = macd_line - signal_line

    # Combine into DataFrame
    result = pd.DataFrame({
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    })

    return result


def calculate_macd_simple(prices: pd.Series) -> pd.Series:
    """
    Calculate just the MACD line (fast - slow) with default parameters.

    Args:
        prices: pandas Series of closing prices

    Returns:
        pandas Series of MACD line values
    """
    ema_fast = prices.ewm(span=12, adjust=False).mean()
    ema_slow = prices.ewm(span=26, adjust=False).mean()
    return ema_fast - ema_slow


def macd_crossover_signal(macd_df: pd.DataFrame) -> pd.Series:
    """
    Detect MACD crossover signals.

    Returns:
        pandas Series with values:
        - 1 for bullish crossover (MACD crosses above signal)
        - -1 for bearish crossover (MACD crosses below signal)
        - 0 for no crossover
    """
    # Current position: is MACD above signal?
    current_position = (macd_df['macd'] > macd_df['signal']).astype(int)

    # Previous position
    prev_position = current_position.shift(1)

    # Crossover detection
    crossover = current_position - prev_position

    return crossover
