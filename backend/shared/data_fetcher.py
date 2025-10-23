"""
Unified Data Fetcher - Hybrid IBKR + yfinance

This module provides a unified interface for fetching market data.
Priority: IBKR real-time data (QuestDB) -> yfinance fallback

Architecture:
- Checks QuestDB for IBKR real-time data first
- Falls back to yfinance for historical data or unavailable symbols
- Returns pandas DataFrame in yfinance-compatible format
- Thread-safe with connection pooling

Usage:
    from shared.data_fetcher import fetch_prices

    # Same API as yf.download()
    prices = fetch_prices(['AAPL', 'MSFT'], start='2023-01-01', end='2024-01-01')
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Union, Optional
import requests
import yfinance as yf
from functools import lru_cache
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# QuestDB configuration
# Use environment variable or default to Docker service name
QUESTDB_URL = os.getenv("QUESTDB_URL", "http://questdb:9000")

# IBKR symbols currently available in QuestDB
IBKR_SYMBOLS = {'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLV', 'XLY',
                'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'GLD', 'TLT', 'SHY'}


def query_questdb(sql_query: str) -> pd.DataFrame:
    """
    Execute SQL query on QuestDB and return results as DataFrame.

    Args:
        sql_query: SQL query string

    Returns:
        DataFrame with query results
    """
    try:
        response = requests.get(
            f"{QUESTDB_URL}/exec",
            params={'query': sql_query},
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        if 'dataset' not in data or len(data['dataset']) == 0:
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(data['dataset'], columns=[col['name'] for col in data['columns']])

        # Convert timestamp column if present
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)

        return df

    except Exception as e:
        logger.warning(f"QuestDB query failed: {e}")
        return pd.DataFrame()


def fetch_from_questdb(symbol: str, start_date: str, end_date: str) -> Optional[pd.Series]:
    """
    Fetch price data from QuestDB (IBKR real-time data).

    Args:
        symbol: Stock ticker symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        Series with Close prices, indexed by timestamp, or None if not available
    """
    if symbol not in IBKR_SYMBOLS:
        return None

    try:
        # Query for OHLC data
        # Use 'close' field as the close price (last trade price)
        query = f"""
        SELECT
            timestamp,
            close as "Close"
        FROM market_data_l1
        WHERE symbol = '{symbol}'
          AND timestamp >= '{start_date}'
          AND timestamp < '{end_date}'
        ORDER BY timestamp
        """

        df = query_questdb(query)

        if df.empty:
            logger.warning(f"No IBKR data found for {symbol} in QuestDB")
            return None

        # Return Close prices as Series
        return df['Close']

    except Exception as e:
        logger.error(f"Error fetching {symbol} from QuestDB: {e}")
        return None


def fetch_from_yfinance(tickers: Union[str, List[str]],
                        start: str,
                        end: str,
                        progress: bool = False) -> Union[pd.Series, pd.DataFrame]:
    """
    Fetch price data from yfinance (fallback).

    Args:
        tickers: Single ticker or list of tickers
        start: Start date
        end: End date
        progress: Show progress bar

    Returns:
        Series or DataFrame with Adj Close prices
    """
    try:
        data = yf.download(tickers, start=start, end=end, progress=progress)

        if data.empty:
            logger.warning(f"No yfinance data for {tickers}")
            return pd.DataFrame() if isinstance(tickers, list) else pd.Series()

        # Return Adj Close column(s)
        if 'Adj Close' in data.columns:
            return data['Adj Close']
        else:
            return data

    except Exception as e:
        logger.error(f"Error fetching from yfinance: {e}")
        return pd.DataFrame() if isinstance(tickers, list) else pd.Series()


def fetch_prices(tickers: Union[str, List[str]],
                 start: Optional[str] = None,
                 end: Optional[str] = None,
                 period: Optional[str] = None,
                 progress: bool = False) -> Union[pd.Series, pd.DataFrame]:
    """
    Unified price fetcher - IBKR real-time (QuestDB) with yfinance fallback.

    Drop-in replacement for yf.download() with Adj Close data.

    Priority:
    1. Check QuestDB for IBKR real-time data
    2. Fall back to yfinance for historical data

    Args:
        tickers: Single ticker string or list of ticker strings
        start: Start date (YYYY-MM-DD) or None
        end: End date (YYYY-MM-DD) or None
        period: Period string ('1y', '2y', etc.) if start/end not provided
        progress: Show progress bar (for yfinance)

    Returns:
        Series (single ticker) or DataFrame (multiple tickers) with Close prices

    Examples:
        # Single ticker
        prices = fetch_prices('AAPL', start='2023-01-01', end='2024-01-01')

        # Multiple tickers
        prices = fetch_prices(['AAPL', 'MSFT', 'GOOGL'], period='2y')

        # Mix of IBKR and yfinance symbols
        prices = fetch_prices(['SPY', 'AAPL'], period='1y')
        # SPY from IBKR (real-time), AAPL from yfinance (delayed)
    """
    # Handle period parameter
    if period and not start:
        end_date = datetime.now()
        if period.endswith('y'):
            years = int(period[:-1])
            start_date = end_date - timedelta(days=365 * years)
        elif period.endswith('mo'):
            months = int(period[:-2])
            start_date = end_date - timedelta(days=30 * months)
        elif period.endswith('d'):
            days = int(period[:-1])
            start_date = end_date - timedelta(days=days)
        else:
            start_date = end_date - timedelta(days=365)  # default 1 year

        start = start_date.strftime('%Y-%m-%d')
        end = end_date.strftime('%Y-%m-%d')

    # Ensure we have start and end dates
    if not start:
        start = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    if not end:
        end = datetime.now().strftime('%Y-%m-%d')

    # Convert single ticker to list
    if isinstance(tickers, str):
        tickers = [tickers]
        single_ticker = True
    else:
        single_ticker = False

    # Separate IBKR symbols from yfinance symbols
    ibkr_tickers = [t for t in tickers if t in IBKR_SYMBOLS]
    yf_tickers = [t for t in tickers if t not in IBKR_SYMBOLS]

    results = {}

    # Fetch IBKR symbols from QuestDB
    for ticker in ibkr_tickers:
        series = fetch_from_questdb(ticker, start, end)
        if series is not None and not series.empty:
            results[ticker] = series
            logger.info(f"✓ {ticker}: Using IBKR real-time data from QuestDB")
        else:
            # Fallback to yfinance if QuestDB fetch failed
            yf_tickers.append(ticker)
            logger.info(f"✗ {ticker}: IBKR data unavailable, falling back to yfinance")

    # Fetch remaining symbols from yfinance
    if yf_tickers:
        logger.info(f"Fetching {len(yf_tickers)} symbols from yfinance: {yf_tickers}")
        yf_data = fetch_from_yfinance(yf_tickers, start, end, progress)

        if isinstance(yf_data, pd.Series):
            # Single ticker from yfinance
            results[yf_tickers[0]] = yf_data
        elif isinstance(yf_data, pd.DataFrame):
            # Multiple tickers from yfinance
            for ticker in yf_tickers:
                if ticker in yf_data.columns:
                    results[ticker] = yf_data[ticker]

    # Combine results
    if not results:
        return pd.Series() if single_ticker else pd.DataFrame()

    if single_ticker:
        return results[tickers[0]]
    else:
        # Combine into DataFrame
        df = pd.DataFrame(results)
        # Reorder columns to match input order
        df = df[[t for t in tickers if t in df.columns]]
        return df


def get_latest_price(symbol: str) -> Optional[float]:
    """
    Get latest price for a symbol (real-time from IBKR if available).

    Args:
        symbol: Ticker symbol

    Returns:
        Latest price or None
    """
    if symbol in IBKR_SYMBOLS:
        # Get latest from QuestDB
        query = f"""
        SELECT close
        FROM market_data_l1
        WHERE symbol = '{symbol}'
        ORDER BY timestamp DESC
        LIMIT 1
        """
        df = query_questdb(query)
        if not df.empty:
            return float(df.iloc[0]['close'])

    # Fallback to yfinance
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='1d')
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
    except:
        pass

    return None


@lru_cache(maxsize=128)
def get_available_symbols() -> tuple:
    """
    Get list of symbols available in IBKR feed.

    Returns:
        Tuple of available symbols
    """
    return tuple(IBKR_SYMBOLS)


def is_ibkr_symbol(symbol: str) -> bool:
    """Check if symbol is available in IBKR real-time feed."""
    return symbol in IBKR_SYMBOLS


# Provide backward-compatible alias
def download(*args, **kwargs):
    """Alias for fetch_prices() to match yfinance API."""
    return fetch_prices(*args, **kwargs)
