# utils.py - Utility functions for Fractional Differentiation Engine

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import logging
from config import Config

logger = logging.getLogger(__name__)


def validate_series(series: pd.Series) -> pd.Series:
    """
    Validate and clean time series data.

    Args:
        series: Time series data

    Returns:
        Cleaned series

    Raises:
        ValueError: If series is invalid
    """
    if not isinstance(series, pd.Series):
        raise ValueError("Input must be a pandas Series")

    if len(series) < Config.MIN_DATA_POINTS:
        raise ValueError(f"Insufficient data points. Minimum: {Config.MIN_DATA_POINTS}, got: {len(series)}")

    if len(series) > Config.MAX_DATA_POINTS:
        logger.warning(f"Series has {len(series)} points, truncating to {Config.MAX_DATA_POINTS}")
        series = series.iloc[-Config.MAX_DATA_POINTS:]

    # Remove NaN values
    series_clean = series.dropna()

    if len(series_clean) < Config.MIN_DATA_POINTS:
        raise ValueError(f"Too many NaN values. Valid points: {len(series_clean)}")

    # Check for infinite values
    if np.any(np.isinf(series_clean)):
        logger.warning("Infinite values detected, removing them")
        series_clean = series_clean[~np.isinf(series_clean)]

    return series_clean


def validate_d(d: float) -> float:
    """
    Validate fractional differentiation parameter d.

    Args:
        d: Differentiation order

    Returns:
        Validated d value

    Raises:
        ValueError: If d is out of valid range
    """
    if not isinstance(d, (int, float)):
        raise ValueError("d must be a number")

    if d < Config.MIN_D or d > Config.MAX_D:
        raise ValueError(f"d must be between {Config.MIN_D} and {Config.MAX_D}, got: {d}")

    return float(d)


def fetch_price_data(
    ticker: str,
    start_date: str = None,
    end_date: str = None,
    column: str = 'Close'
) -> pd.Series:
    """
    Fetch price data for a ticker.

    Args:
        ticker: Stock ticker symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        column: Price column to use ('Open', 'High', 'Low', 'Close', 'Adj Close')

    Returns:
        Price series

    Raises:
        ValueError: If data cannot be fetched
    """
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')

    logger.info(f"Fetching {ticker} from {start_date} to {end_date}")

    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)

        if data.empty:
            raise ValueError(f"No data found for ticker: {ticker}")

        if column not in data.columns:
            # Handle multi-column case (when multiple tickers)
            if column in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
                price_series = data[column]
                if isinstance(price_series, pd.DataFrame):
                    price_series = price_series.iloc[:, 0]  # Take first column
            else:
                raise ValueError(f"Column '{column}' not found in data")
        else:
            price_series = data[column]

        price_series = price_series.dropna()

        if len(price_series) == 0:
            raise ValueError(f"No valid data for {ticker}")

        logger.info(f"Fetched {len(price_series)} data points for {ticker}")
        return price_series

    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {str(e)}")
        raise ValueError(f"Could not fetch data for {ticker}: {str(e)}")


def series_to_returns(series: pd.Series) -> pd.Series:
    """
    Convert price series to returns.

    Args:
        series: Price series

    Returns:
        Returns series (log returns)
    """
    returns = np.log(series / series.shift(1))
    return returns.dropna()


def create_comparison_dataframe(
    original: pd.Series,
    transformed_dict: dict,
    stationarity_dict: dict = None,
    memory_dict: dict = None
) -> pd.DataFrame:
    """
    Create comparison DataFrame for multiple transformations.

    Args:
        original: Original series
        transformed_dict: Dictionary of transformed series {label: series}
        stationarity_dict: Optional stationarity results {label: is_stationary}
        memory_dict: Optional memory retention scores {label: score}

    Returns:
        Comparison DataFrame
    """
    comparison_data = []

    # Original series
    row = {
        'transformation': 'Original (d=0)',
        'mean': original.mean(),
        'std': original.std(),
        'min': original.min(),
        'max': original.max()
    }

    if stationarity_dict and 'Original' in stationarity_dict:
        row['stationary'] = stationarity_dict['Original']

    if memory_dict and 'Original' in memory_dict:
        row['memory_retained'] = memory_dict['Original']

    comparison_data.append(row)

    # Transformed series
    for label, series in transformed_dict.items():
        row = {
            'transformation': label,
            'mean': series.mean(),
            'std': series.std(),
            'min': series.min(),
            'max': series.max()
        }

        if stationarity_dict and label in stationarity_dict:
            row['stationary'] = stationarity_dict[label]

        if memory_dict and label in memory_dict:
            row['memory_retained'] = memory_dict[label]

        comparison_data.append(row)

    return pd.DataFrame(comparison_data)


def format_stationarity_result(result: dict) -> dict:
    """
    Format stationarity test result for JSON serialization.

    Args:
        result: Stationarity test result dictionary

    Returns:
        Formatted result with proper types
    """
    formatted = {}

    for key, value in result.items():
        if isinstance(value, (np.integer, np.floating)):
            formatted[key] = float(value)
        elif isinstance(value, (np.ndarray, pd.Series)):
            formatted[key] = value.tolist()
        elif isinstance(value, dict):
            formatted[key] = format_stationarity_result(value)
        else:
            formatted[key] = value

    return formatted


def calculate_summary_statistics(series: pd.Series) -> dict:
    """
    Calculate comprehensive summary statistics for a series.

    Args:
        series: Time series data

    Returns:
        Dictionary of statistics
    """
    return {
        'count': int(len(series)),
        'mean': float(series.mean()),
        'std': float(series.std()),
        'min': float(series.min()),
        'max': float(series.max()),
        'median': float(series.median()),
        'skewness': float(series.skew()),
        'kurtosis': float(series.kurtosis()),
        'q25': float(series.quantile(0.25)),
        'q75': float(series.quantile(0.75))
    }
