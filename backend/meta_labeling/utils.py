# utils.py - Utility functions for meta-labeling system

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.data_fetcher import fetch_prices
from config import Config

logger = logging.getLogger(__name__)


def validate_series(series: pd.Series, min_length: int = None) -> pd.Series:
    """
    Validate and clean time series data.

    Args:
        series: Time series to validate
        min_length: Minimum required length

    Returns:
        Cleaned series

    Raises:
        ValueError: If series is invalid
    """
    if not isinstance(series, pd.Series):
        raise ValueError("Input must be a pandas Series")

    if min_length is None:
        min_length = Config.MIN_DATA_POINTS

    # Remove NaN and inf
    series_clean = series.replace([np.inf, -np.inf], np.nan).dropna()

    if len(series_clean) < min_length:
        raise ValueError(f"Insufficient data: {len(series_clean)} < {min_length}")

    if len(series_clean) > Config.MAX_DATA_POINTS:
        logger.warning(f"Truncating series from {len(series_clean)} to {Config.MAX_DATA_POINTS}")
        series_clean = series_clean.iloc[-Config.MAX_DATA_POINTS:]

    return series_clean


def fetch_price_data(ticker: str,
                    start_date: str = None,
                    end_date: str = None,
                    period: str = '2y') -> pd.DataFrame:
    """
    Fetch OHLCV price data for a ticker.

    Args:
        ticker: Stock ticker symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        period: Period if dates not specified ('1y', '2y', '5y', 'max')

    Returns:
        DataFrame with OHLCV data
    """
    logger.info(f"Fetching data for {ticker}")

    try:
        if start_date and end_date:
            prices = fetch_prices(ticker, start=start_date, end=end_date, progress=False)
        else:
            prices = fetch_prices(ticker, period=period, progress=False)

        # For OHLCV data, we need to fallback to yfinance since unified fetcher only returns Close
        # This is acceptable for meta-labeling which often needs full OHLCV
        import yfinance as yf
        if start_date and end_date:
            data = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=False)
        else:
            data = yf.download(ticker, period=period, progress=False, auto_adjust=False)

        if data.empty:
            raise ValueError(f"No data returned for {ticker}")

        # Handle multi-level columns (if multiple tickers downloaded)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Ensure column names are lowercase
        data.columns = [col.lower() if isinstance(col, str) else col for col in data.columns]

        logger.info(f"Fetched {len(data)} rows for {ticker}")
        return data

    except Exception as e:
        logger.error(f"Failed to fetch data for {ticker}: {str(e)}")
        raise ValueError(f"Could not fetch data for {ticker}: {str(e)}")


def calculate_returns(prices: pd.Series,
                     method: str = 'simple') -> pd.Series:
    """
    Calculate returns from prices.

    Args:
        prices: Price series
        method: 'simple' or 'log'

    Returns:
        Returns series
    """
    if method == 'simple':
        returns = prices.pct_change()
    elif method == 'log':
        returns = np.log(prices / prices.shift(1))
    else:
        raise ValueError(f"Unknown method: {method}")

    return returns.dropna()


def calculate_sharpe_ratio(returns: pd.Series,
                          risk_free_rate: float = 0.02) -> float:
    """
    Calculate annualized Sharpe ratio.

    Args:
        returns: Returns series
        risk_free_rate: Annual risk-free rate

    Returns:
        Sharpe ratio
    """
    if len(returns) == 0:
        return 0.0

    # Annualize
    annual_return = returns.mean() * 252
    annual_vol = returns.std() * np.sqrt(252)

    if annual_vol == 0:
        return 0.0

    sharpe = (annual_return - risk_free_rate) / annual_vol

    return float(sharpe)


def calculate_max_drawdown(returns: pd.Series) -> float:
    """
    Calculate maximum drawdown.

    Args:
        returns: Returns series

    Returns:
        Maximum drawdown (positive number)
    """
    if len(returns) == 0:
        return 0.0

    # Calculate cumulative returns
    cumulative = (1 + returns).cumprod()

    # Calculate running maximum
    running_max = cumulative.expanding().max()

    # Calculate drawdown
    drawdown = (cumulative - running_max) / running_max

    max_dd = drawdown.min()

    return float(abs(max_dd))


def calculate_win_rate(returns: pd.Series) -> float:
    """
    Calculate win rate (percentage of positive returns).

    Args:
        returns: Returns series

    Returns:
        Win rate (0 to 1)
    """
    if len(returns) == 0:
        return 0.0

    wins = (returns > 0).sum()
    total = len(returns)

    return float(wins / total)


def calculate_profit_factor(returns: pd.Series) -> float:
    """
    Calculate profit factor (gross profit / gross loss).

    Args:
        returns: Returns series

    Returns:
        Profit factor
    """
    if len(returns) == 0:
        return 0.0

    gains = returns[returns > 0].sum()
    losses = abs(returns[returns < 0].sum())

    if losses == 0:
        return np.inf if gains > 0 else 0.0

    return float(gains / losses)


def calculate_calmar_ratio(returns: pd.Series) -> float:
    """
    Calculate Calmar ratio (annual return / max drawdown).

    Args:
        returns: Returns series

    Returns:
        Calmar ratio
    """
    if len(returns) == 0:
        return 0.0

    annual_return = returns.mean() * 252
    max_dd = calculate_max_drawdown(returns)

    if max_dd == 0:
        return 0.0

    return float(annual_return / max_dd)


def calculate_strategy_returns(market_returns: pd.Series,
                               positions: pd.Series) -> pd.Series:
    """
    Calculate strategy returns from market returns and positions.

    Args:
        market_returns: Market returns
        positions: Position sizes (+1 long, -1 short, 0 flat, or fractional)

    Returns:
        Strategy returns
    """
    # Align indices
    common_idx = market_returns.index.intersection(positions.index)
    market_returns = market_returns.loc[common_idx]
    positions = positions.loc[common_idx]

    # Strategy returns = position * market_returns
    strategy_returns = positions * market_returns

    return strategy_returns


def calculate_performance_metrics(returns: pd.Series,
                                  risk_free_rate: float = 0.02) -> dict:
    """
    Calculate comprehensive performance metrics.

    Args:
        returns: Returns series
        risk_free_rate: Annual risk-free rate

    Returns:
        Dictionary of performance metrics
    """
    if len(returns) == 0:
        return {
            'total_return': 0.0,
            'annual_return': 0.0,
            'annual_volatility': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'calmar_ratio': 0.0,
            'n_trades': 0
        }

    total_return = (1 + returns).prod() - 1
    annual_return = returns.mean() * 252
    annual_vol = returns.std() * np.sqrt(252)

    return {
        'total_return': float(total_return),
        'annual_return': float(annual_return),
        'annual_volatility': float(annual_vol),
        'sharpe_ratio': calculate_sharpe_ratio(returns, risk_free_rate),
        'max_drawdown': calculate_max_drawdown(returns),
        'win_rate': calculate_win_rate(returns),
        'profit_factor': calculate_profit_factor(returns),
        'calmar_ratio': calculate_calmar_ratio(returns),
        'n_trades': int((returns != 0).sum())
    }


def align_series(*series_list) -> tuple:
    """
    Align multiple series to common index.

    Args:
        *series_list: Variable number of series to align

    Returns:
        Tuple of aligned series
    """
    if len(series_list) == 0:
        return tuple()

    # Find common index
    common_idx = series_list[0].index
    for series in series_list[1:]:
        common_idx = common_idx.intersection(series.index)

    # Align all series
    aligned = tuple(series.loc[common_idx] for series in series_list)

    return aligned


def series_to_json(series: pd.Series) -> dict:
    """
    Convert pandas Series to JSON-serializable format.

    Args:
        series: Pandas series

    Returns:
        Dictionary with values and index
    """
    return {
        'values': series.values.tolist(),
        'index': series.index.astype(str).tolist(),
        'length': len(series)
    }


def dataframe_to_json(df: pd.DataFrame) -> dict:
    """
    Convert pandas DataFrame to JSON-serializable format.

    Args:
        df: Pandas dataframe

    Returns:
        Dictionary representation
    """
    return {
        'data': df.to_dict('records'),
        'columns': df.columns.tolist(),
        'index': df.index.astype(str).tolist(),
        'shape': df.shape
    }
