# primary_models.py - Primary trading strategies for meta-labeling

import numpy as np
import pandas as pd
import logging
from config import Config

logger = logging.getLogger(__name__)


def momentum_strategy(prices: pd.Series,
                     fast: int = None,
                     slow: int = None) -> pd.Series:
    """
    Simple momentum crossover strategy (primary model).

    Buy when fast SMA > slow SMA, sell when fast SMA < slow SMA.

    Args:
        prices: Price series
        fast: Fast SMA period
        slow: Slow SMA period

    Returns:
        Signal series: +1 (long), -1 (short), 0 (no position)
    """
    if fast is None:
        fast = Config.MOMENTUM_FAST
    if slow is None:
        slow = Config.MOMENTUM_SLOW

    logger.info(f"Momentum strategy: fast={fast}, slow={slow}")

    # Calculate SMAs
    sma_fast = prices.rolling(fast).mean()
    sma_slow = prices.rolling(slow).mean()

    # Generate signals
    signals = pd.Series(0, index=prices.index)
    signals[sma_fast > sma_slow] = 1   # Long
    signals[sma_fast < sma_slow] = -1  # Short

    # Remove initial NaN period
    signals = signals.iloc[slow:]

    logger.info(f"Generated {len(signals)} momentum signals")

    return signals


def mean_reversion_strategy(prices: pd.Series,
                            lookback: int = None,
                            threshold: float = None) -> pd.Series:
    """
    Bollinger Band mean reversion strategy (primary model).

    Buy when price < lower band (oversold), sell when price > upper band (overbought).

    Args:
        prices: Price series
        lookback: Lookback period for Bollinger Bands
        threshold: Number of standard deviations

    Returns:
        Signal series: +1 (long), -1 (short), 0 (no position)
    """
    if lookback is None:
        lookback = Config.MEAN_REVERSION_LOOKBACK
    if threshold is None:
        threshold = Config.MEAN_REVERSION_THRESHOLD

    logger.info(f"Mean reversion strategy: lookback={lookback}, threshold={threshold}")

    # Calculate Bollinger Bands
    sma = prices.rolling(lookback).mean()
    std = prices.rolling(lookback).std()

    upper_band = sma + threshold * std
    lower_band = sma - threshold * std

    # Generate signals
    signals = pd.Series(0, index=prices.index)
    signals[prices < lower_band] = 1   # Oversold -> Long
    signals[prices > upper_band] = -1  # Overbought -> Short

    # Remove initial NaN period
    signals = signals.iloc[lookback:]

    logger.info(f"Generated {len(signals)} mean reversion signals")

    return signals


def rsi_strategy(prices: pd.Series,
                period: int = 14,
                oversold: int = 30,
                overbought: int = 70) -> pd.Series:
    """
    RSI-based strategy (primary model).

    Buy when RSI < oversold, sell when RSI > overbought.

    Args:
        prices: Price series
        period: RSI period
        oversold: Oversold threshold
        overbought: Overbought threshold

    Returns:
        Signal series: +1 (long), -1 (short), 0 (no position)
    """
    logger.info(f"RSI strategy: period={period}, oversold={oversold}, overbought={overbought}")

    # Calculate RSI
    rsi = calculate_rsi(prices, period)

    # Generate signals
    signals = pd.Series(0, index=rsi.index)
    signals[rsi < oversold] = 1    # Oversold -> Long
    signals[rsi > overbought] = -1  # Overbought -> Short

    logger.info(f"Generated {len(signals)} RSI signals")

    return signals


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate RSI (Relative Strength Index).

    Args:
        prices: Price series
        period: RSI period

    Returns:
        RSI series (0-100)
    """
    # Calculate price changes
    delta = prices.diff()

    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Calculate average gain and loss
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def macd_strategy(prices: pd.Series,
                 fast: int = 12,
                 slow: int = 26,
                 signal: int = 9) -> pd.Series:
    """
    MACD strategy (primary model).

    Buy when MACD > signal, sell when MACD < signal.

    Args:
        prices: Price series
        fast: Fast EMA period
        slow: Slow EMA period
        signal: Signal line period

    Returns:
        Signal series: +1 (long), -1 (short), 0 (no position)
    """
    logger.info(f"MACD strategy: fast={fast}, slow={slow}, signal={signal}")

    # Calculate EMAs
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()

    # Calculate MACD and signal line
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal, adjust=False).mean()

    # Generate signals
    signals = pd.Series(0, index=prices.index)
    signals[macd > macd_signal] = 1   # Long
    signals[macd < macd_signal] = -1  # Short

    # Remove initial NaN period
    signals = signals.iloc[slow + signal:]

    logger.info(f"Generated {len(signals)} MACD signals")

    return signals


def breakout_strategy(prices: pd.Series,
                     lookback: int = 20,
                     percentile: float = 0.9) -> pd.Series:
    """
    Breakout strategy (primary model).

    Buy when price breaks above percentile, sell when below.

    Args:
        prices: Price series
        lookback: Lookback period
        percentile: Percentile for breakout (0-1)

    Returns:
        Signal series: +1 (long), -1 (short), 0 (no position)
    """
    logger.info(f"Breakout strategy: lookback={lookback}, percentile={percentile}")

    # Calculate rolling percentiles
    upper = prices.rolling(lookback).quantile(percentile)
    lower = prices.rolling(lookback).quantile(1 - percentile)

    # Generate signals
    signals = pd.Series(0, index=prices.index)
    signals[prices > upper] = 1   # Breakout up -> Long
    signals[prices < lower] = -1  # Breakout down -> Short

    # Remove initial NaN period
    signals = signals.iloc[lookback:]

    logger.info(f"Generated {len(signals)} breakout signals")

    return signals


def get_strategy(strategy_name: str,
                prices: pd.Series,
                **kwargs) -> pd.Series:
    """
    Get signals from specified strategy.

    Args:
        strategy_name: Name of strategy
        prices: Price series
        **kwargs: Strategy-specific parameters

    Returns:
        Signal series

    Raises:
        ValueError: If strategy not found
    """
    strategies = {
        'momentum': momentum_strategy,
        'mean_reversion': mean_reversion_strategy,
        'rsi': rsi_strategy,
        'macd': macd_strategy,
        'breakout': breakout_strategy
    }

    if strategy_name not in strategies:
        raise ValueError(f"Unknown strategy: {strategy_name}. Available: {list(strategies.keys())}")

    strategy_func = strategies[strategy_name]
    signals = strategy_func(prices, **kwargs)

    return signals


def combine_strategies(prices: pd.Series,
                      strategies: list,
                      method: str = 'average') -> pd.Series:
    """
    Combine multiple strategies.

    Args:
        prices: Price series
        strategies: List of (strategy_name, kwargs) tuples
        method: 'average', 'vote', or 'consensus'

    Returns:
        Combined signal series
    """
    logger.info(f"Combining {len(strategies)} strategies using {method}")

    all_signals = []

    for strategy_name, kwargs in strategies:
        signals = get_strategy(strategy_name, prices, **kwargs)
        all_signals.append(signals)

    # Align all signals
    common_idx = all_signals[0].index
    for signals in all_signals[1:]:
        common_idx = common_idx.intersection(signals.index)

    aligned_signals = [signals.loc[common_idx] for signals in all_signals]

    # Combine based on method
    if method == 'average':
        # Average of signals
        combined = sum(aligned_signals) / len(aligned_signals)

    elif method == 'vote':
        # Majority vote
        combined = pd.Series(0, index=common_idx)
        for idx in common_idx:
            votes = [signals.loc[idx] for signals in aligned_signals]
            if sum(votes) > 0:
                combined.loc[idx] = 1
            elif sum(votes) < 0:
                combined.loc[idx] = -1

    elif method == 'consensus':
        # All must agree
        combined = pd.Series(0, index=common_idx)
        for idx in common_idx:
            votes = [signals.loc[idx] for signals in aligned_signals]
            if all(v > 0 for v in votes):
                combined.loc[idx] = 1
            elif all(v < 0 for v in votes):
                combined.loc[idx] = -1

    else:
        raise ValueError(f"Unknown combination method: {method}")

    logger.info(f"Combined signals generated: {len(combined)}")

    return combined
