"""
QuestDB Data Fetcher for Backend Analytics Services
Phase 7: Testing & Validation

Utility to fetch historical market data from QuestDB for backend analytics services.
"""

import requests
import pandas as pd
from typing import List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class QuestDBDataFetcher:
    """Fetches historical market data from QuestDB for analytics services."""

    def __init__(self, questdb_url: str = "http://questdb:9000"):
        """
        Initialize QuestDB data fetcher.

        Args:
            questdb_url: QuestDB HTTP endpoint (default: http://questdb:9000 for Docker)
        """
        self.questdb_url = questdb_url
        self.exec_endpoint = f"{questdb_url}/exec"

    def fetch_market_data(
        self,
        symbols: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 10000
    ) -> pd.DataFrame:
        """
        Fetch market data from QuestDB.

        Args:
            symbols: List of ticker symbols (e.g., ['AAPL', 'MSFT'])
            start_date: Start date in 'YYYY-MM-DD' format (optional)
            end_date: End date in 'YYYY-MM-DD' format (optional)
            limit: Maximum number of rows to return

        Returns:
            pandas DataFrame with columns: timestamp, symbol, bid, ask,
            bid_size, ask_size, last, volume, high, low, close
        """
        # Build query
        symbol_list = "', '".join(symbols)

        where_clauses = [f"symbol IN ('{symbol_list}')"]

        if start_date:
            where_clauses.append(f"timestamp >= '{start_date}'")

        if end_date:
            where_clauses.append(f"timestamp <= '{end_date}'")

        where_clause = " AND ".join(where_clauses)

        query = f"SELECT timestamp, symbol, last, bid, ask, bid_size, ask_size, volume, high, low, close FROM market_data_l1 WHERE {where_clause} ORDER BY timestamp DESC LIMIT {limit};"

        try:
            response = requests.get(self.exec_endpoint, params={"query": query}, timeout=10)
            response.raise_for_status()

            data = response.json()

            if "dataset" not in data or len(data["dataset"]) == 0:
                logger.warning(f"No data found for symbols: {symbols}")
                return pd.DataFrame()

            # Convert to DataFrame
            columns = [col["name"] for col in data["columns"]]
            df = pd.DataFrame(data["dataset"], columns=columns)

            # Convert timestamp to datetime
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])

            logger.info(f"Fetched {len(df)} rows for {len(symbols)} symbols")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch data from QuestDB: {e}")
            raise

    def get_ohlcv(
        self,
        symbols: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1h"
    ) -> pd.DataFrame:
        """
        Get OHLCV (Open, High, Low, Close, Volume) data aggregated by interval.

        Args:
            symbols: List of ticker symbols
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            interval: Time interval ('1m', '5m', '15m', '1h', '1d')

        Returns:
            pandas DataFrame with OHLCV data
        """
        # Map interval to QuestDB sample_by format
        interval_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "1h": "1h",
            "1d": "1d"
        }

        if interval not in interval_map:
            raise ValueError(f"Invalid interval: {interval}. Must be one of {list(interval_map.keys())}")

        sample_by = interval_map[interval]

        symbol_list = "', '".join(symbols)

        where_clauses = [f"symbol IN ('{symbol_list}')"]

        if start_date:
            where_clauses.append(f"timestamp >= '{start_date}'")

        if end_date:
            where_clauses.append(f"timestamp <= '{end_date}'")

        where_clause = " AND ".join(where_clauses)

        query = f"SELECT timestamp, symbol, first(last) as open, max(high) as high, min(low) as low, last(close) as close, sum(volume) as volume FROM market_data_l1 WHERE {where_clause} SAMPLE BY {sample_by} ALIGN TO CALENDAR ORDER BY timestamp DESC;"

        try:
            response = requests.get(self.exec_endpoint, params={"query": query}, timeout=10)
            response.raise_for_status()

            data = response.json()

            if "dataset" not in data or len(data["dataset"]) == 0:
                logger.warning(f"No OHLCV data found for symbols: {symbols}")
                return pd.DataFrame()

            columns = [col["name"] for col in data["columns"]]
            df = pd.DataFrame(data["dataset"], columns=columns)

            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])

            logger.info(f"Fetched {len(df)} OHLCV bars for {len(symbols)} symbols")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch OHLCV data from QuestDB: {e}")
            raise

    def get_returns(
        self,
        symbols: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Calculate returns from OHLCV data.

        Args:
            symbols: List of ticker symbols
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            interval: Time interval for returns calculation

        Returns:
            pandas DataFrame with returns (columns: timestamp, symbol, returns)
        """
        ohlcv = self.get_ohlcv(symbols, start_date, end_date, interval)

        if ohlcv.empty:
            return pd.DataFrame()

        # Calculate returns for each symbol
        returns_list = []

        for symbol in symbols:
            symbol_data = ohlcv[ohlcv["symbol"] == symbol].copy()
            symbol_data = symbol_data.sort_values("timestamp")
            symbol_data["returns"] = symbol_data["close"].pct_change()
            returns_list.append(symbol_data[["timestamp", "symbol", "returns"]])

        returns_df = pd.concat(returns_list, ignore_index=True)
        returns_df = returns_df.dropna(subset=["returns"])

        logger.info(f"Calculated returns for {len(symbols)} symbols")
        return returns_df

    def get_available_symbols(self) -> List[str]:
        """
        Get list of available symbols in QuestDB.

        Returns:
            List of ticker symbols
        """
        query = "SELECT DISTINCT symbol FROM market_data_l1 ORDER BY symbol;"

        try:
            response = requests.get(self.exec_endpoint, params={"query": query}, timeout=10)
            response.raise_for_status()

            data = response.json()

            if "dataset" not in data:
                return []

            symbols = [row[0] for row in data["dataset"]]
            logger.info(f"Found {len(symbols)} symbols in QuestDB")
            return symbols

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch symbols from QuestDB: {e}")
            raise

    def get_latest_timestamp(self, symbol: Optional[str] = None) -> Optional[datetime]:
        """
        Get the latest timestamp for a symbol or all symbols.

        Args:
            symbol: Ticker symbol (optional, if None returns latest across all symbols)

        Returns:
            Latest timestamp as datetime object
        """
        if symbol:
            query = f"SELECT MAX(timestamp) as latest FROM market_data_l1 WHERE symbol = '{symbol}';"
        else:
            query = "SELECT MAX(timestamp) as latest FROM market_data_l1;"

        try:
            response = requests.get(self.exec_endpoint, params={"query": query}, timeout=10)
            response.raise_for_status()

            data = response.json()

            if "dataset" not in data or len(data["dataset"]) == 0:
                return None

            timestamp_str = data["dataset"][0][0]
            if timestamp_str:
                return pd.to_datetime(timestamp_str)
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch latest timestamp from QuestDB: {e}")
            raise


# Convenience function for quick testing
def fetch_sample_data(symbols: List[str] = None, days: int = 7) -> pd.DataFrame:
    """
    Fetch sample market data for testing.

    Args:
        symbols: List of symbols (default: sector ETFs available in QuestDB)
        days: Number of days of historical data

    Returns:
        pandas DataFrame with market data
    """
    if symbols is None:
        # Default to sector ETFs available in QuestDB
        symbols = ["XLV", "XLK", "XLP", "XLI", "XLY", "XLF", "XLE"]

    fetcher = QuestDBDataFetcher()

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    return fetcher.fetch_market_data(symbols, start_date=start_date, end_date=end_date)


if __name__ == "__main__":
    # Test the fetcher
    logging.basicConfig(level=logging.INFO)

    print("QuestDB Data Fetcher Test\n" + "=" * 50)

    # Test 1: Get available symbols
    fetcher = QuestDBDataFetcher(questdb_url="http://localhost:9000")
    symbols = fetcher.get_available_symbols()
    print(f"\nAvailable symbols: {symbols}")

    # Test 2: Get latest timestamp
    latest = fetcher.get_latest_timestamp()
    print(f"Latest data timestamp: {latest}")

    # Test 3: Fetch market data
    if symbols:
        test_symbols = symbols[:3]  # Test with first 3 symbols
        print(f"\nFetching data for: {test_symbols}")

        df = fetcher.fetch_market_data(test_symbols, limit=100)
        print(f"Fetched {len(df)} rows")
        print(df.head())

        # Test 4: Get OHLCV data
        print(f"\nFetching OHLCV data (1h interval):")
        ohlcv = fetcher.get_ohlcv(test_symbols, interval="1h")
        print(f"Fetched {len(ohlcv)} OHLCV bars")
        print(ohlcv.head())

        # Test 5: Calculate returns
        print(f"\nCalculating returns:")
        returns = fetcher.get_returns(test_symbols, interval="1d")
        print(f"Calculated {len(returns)} return observations")
        print(returns.head())
