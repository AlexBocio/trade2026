"""
Bollinger Bands Calculator.

Bollinger Bands are a volatility indicator consisting of three lines:
- Middle Band: Simple moving average (SMA)
- Upper Band: SMA + (standard deviation × multiplier)
- Lower Band: SMA - (standard deviation × multiplier)

Prices touching or exceeding the bands can indicate overbought/oversold conditions.
"""
import pandas as pd
import numpy as np


def calculate_bollinger_bands(
    prices: pd.Series,
    period: int = 20,
    std_dev: float = 2.0
) -> pd.DataFrame:
    """
    Calculate Bollinger Bands.

    Args:
        prices: pandas Series of closing prices
        period: lookback period for SMA (default: 20)
        std_dev: number of standard deviations for bands (default: 2.0)

    Returns:
        pandas DataFrame with columns: 'upper', 'middle', 'lower', 'bandwidth', 'percent_b'

    Example:
        >>> prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108])
        >>> bb = calculate_bollinger_bands(prices, period=5, std_dev=2)
        >>> print(bb[['upper', 'middle', 'lower']])
    """
    # Calculate middle band (SMA)
    middle_band = prices.rolling(window=period, min_periods=period).mean()

    # Calculate standard deviation
    rolling_std = prices.rolling(window=period, min_periods=period).std()

    # Calculate upper and lower bands
    upper_band = middle_band + (rolling_std * std_dev)
    lower_band = middle_band - (rolling_std * std_dev)

    # Calculate bandwidth (volatility indicator)
    bandwidth = (upper_band - lower_band) / middle_band

    # Calculate %B (position within bands)
    # %B = (Price - Lower Band) / (Upper Band - Lower Band)
    # Values > 1 mean price is above upper band
    # Values < 0 mean price is below lower band
    # Values around 0.5 mean price is near middle band
    # When bands are identical (zero volatility), %B is undefined, so we set it to 0.5
    band_width = upper_band - lower_band
    percent_b = (prices - lower_band) / band_width
    # Replace inf/nan with 0.5 (price is at middle when there's no volatility)
    percent_b = percent_b.replace([np.inf, -np.inf], np.nan).fillna(0.5)

    # Combine into DataFrame
    result = pd.DataFrame({
        'upper': upper_band,
        'middle': middle_band,
        'lower': lower_band,
        'bandwidth': bandwidth,
        'percent_b': percent_b
    })

    return result


def bollinger_squeeze(bb_df: pd.DataFrame, threshold: float = 0.05) -> pd.Series:
    """
    Detect Bollinger Band squeeze (low volatility periods).

    A squeeze occurs when bandwidth is below a threshold, indicating
    consolidation and potential upcoming volatility expansion.

    Args:
        bb_df: DataFrame from calculate_bollinger_bands()
        threshold: bandwidth threshold for squeeze detection (default: 0.05 = 5%)

    Returns:
        pandas Series of boolean values (True = squeeze detected)
    """
    return bb_df['bandwidth'] < threshold


def bollinger_breakout_signal(prices: pd.Series, bb_df: pd.DataFrame) -> pd.Series:
    """
    Detect Bollinger Band breakout signals.

    Returns:
        pandas Series with values:
        - 1 for upper band breakout (bullish)
        - -1 for lower band breakout (bearish)
        - 0 for no breakout
    """
    upper_breakout = (prices > bb_df['upper']).astype(int)
    lower_breakout = (prices < bb_df['lower']).astype(int) * -1

    return upper_breakout + lower_breakout


def calculate_bandwidth_percentile(bb_df: pd.DataFrame, window: int = 100) -> pd.Series:
    """
    Calculate bandwidth percentile rank over a rolling window.

    This helps identify whether current volatility is high or low
    relative to recent history.

    Args:
        bb_df: DataFrame from calculate_bollinger_bands()
        window: rolling window for percentile calculation

    Returns:
        pandas Series of percentile ranks (0-100)
    """
    return bb_df['bandwidth'].rolling(window=window).apply(
        lambda x: (x.iloc[-1] <= x).sum() / len(x) * 100,
        raw=False
    )
