#!/usr/bin/env python3
"""
QuestDB Historical Data Backfill Script
========================================

Backfills QuestDB with historical daily OHLCV data from yfinance.
Populates the market_data_l1 table with 30-90 days of historical data.

Usage:
    python backfill_questdb.py --days 60
    python backfill_questdb.py --days 90 --symbols SPY,QQQ,IWM
"""

import argparse
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List
import time
import sys


# Default symbols: 15 sector ETFs
DEFAULT_SYMBOLS = [
    'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLV', 'XLY',  # Sector ETFs
    'SPY', 'QQQ', 'IWM', 'DIA', 'VTI',                # Market ETFs
    'GLD', 'TLT', 'SHY'                                # Alternative assets
]

# QuestDB configuration
QUESTDB_HOST = "localhost"
QUESTDB_PORT = 9000
QUESTDB_WRITE_URL = f"http://{QUESTDB_HOST}:{QUESTDB_PORT}/write"

# Target table: market_data_historical (NO WAL, immediately queryable)
TARGET_TABLE = "market_data_historical"


def fetch_historical_data(symbols: List[str], days: int) -> pd.DataFrame:
    """
    Fetch historical OHLCV data from yfinance.

    Args:
        symbols: List of ticker symbols
        days: Number of days of historical data

    Returns:
        DataFrame with OHLCV data
    """
    print(f"\nFetching {days} days of historical data for {len(symbols)} symbols...")
    print(f"Symbols: {', '.join(symbols)}")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    print(f"Date range: {start_date.date()} to {end_date.date()}")

    # Download data from yfinance
    # Note: NOT using group_by='ticker' so that symbols are in level 1 (easier to handle)
    data = yf.download(
        symbols,
        start=start_date,
        end=end_date,
        progress=True
    )

    if data.empty:
        print("ERROR: No data returned from yfinance")
        sys.exit(1)

    print(f"[OK] Downloaded data: {len(data)} rows")
    return data


def convert_to_ilp_format(symbol: str, row: pd.Series, timestamp_ns: int) -> str:
    """
    Convert a single OHLCV bar to QuestDB ILP format.

    Args:
        symbol: Ticker symbol
        row: DataFrame row with OHLCV data
        timestamp_ns: Timestamp in nanoseconds

    Returns:
        ILP formatted string
    """
    # Extract OHLCV values
    open_price = float(row['Open']) if pd.notna(row['Open']) else 0.0
    high_price = float(row['High']) if pd.notna(row['High']) else 0.0
    low_price = float(row['Low']) if pd.notna(row['Low']) else 0.0
    close_price = float(row['Close']) if pd.notna(row['Close']) else 0.0
    volume = int(row['Volume']) if pd.notna(row['Volume']) else 0

    # For daily bars, use close as last price
    last_price = close_price

    # Create synthetic bid/ask with 0.01 spread (1 cent)
    bid_price = close_price - 0.01 if close_price > 0 else 0.0
    ask_price = close_price + 0.01 if close_price > 0 else 0.0

    # Dummy bid/ask sizes (not available in daily data)
    bid_size = 0
    ask_size = 0

    # Build ILP line
    # Format: table_name,tag1=value1 field1=value1,field2=value2 timestamp_ns
    line = (
        f"market_data_l1,"
        f"symbol={symbol} "
        f"last={last_price},"
        f"bid={bid_price},"
        f"ask={ask_price},"
        f"bid_size={bid_size}i,"
        f"ask_size={ask_size}i,"
        f"volume={volume}i,"
        f"high={high_price},"
        f"low={low_price},"
        f"close={close_price} "
        f"{timestamp_ns}"
    )

    return line


def write_to_questdb_sql(data_rows: List[tuple]) -> bool:
    """
    Write data to QuestDB using SQL INSERT statements.

    Args:
        data_rows: List of tuples (symbol, ohlcv data, timestamp)

    Returns:
        True if successful, False otherwise
    """
    total_rows = len(data_rows)

    print(f"\nWriting {total_rows} records to QuestDB via SQL INSERT...")

    success_count = 0
    error_count = 0

    # Build bulk INSERT statement
    values_list = []
    for symbol, row, timestamp_ns in data_rows:
        # Convert timestamp from nanoseconds to microseconds for QuestDB
        timestamp_us = timestamp_ns // 1000

        # Extract OHLCV values
        open_val = float(row['Open']) if pd.notna(row['Open']) else 0.0
        high_val = float(row['High']) if pd.notna(row['High']) else 0.0
        low_val = float(row['Low']) if pd.notna(row['Low']) else 0.0
        close_val = float(row['Close']) if pd.notna(row['Close']) else 0.0
        volume_val = int(row['Volume']) if pd.notna(row['Volume']) else 0

        # Synthetic bid/ask
        bid_val = close_val - 0.01 if close_val > 0 else 0.0
        ask_val = close_val + 0.01 if close_val > 0 else 0.0

        values_list.append(
            f"('{symbol}', {open_val}, {high_val}, {low_val}, {close_val}, {volume_val}, "
            f"cast({timestamp_us} as timestamp))"
        )

    # Insert in batches of 100
    batch_size = 100
    for i in range(0, len(values_list), batch_size):
        batch = values_list[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(values_list) + batch_size - 1) // batch_size

        query = f"""
        INSERT INTO {TARGET_TABLE} (symbol, open, high, low, close, volume, timestamp)
        VALUES {', '.join(batch)}
        """

        try:
            response = requests.get(
                f"http://{QUESTDB_HOST}:{QUESTDB_PORT}/exec",
                params={"query": query},
                timeout=60
            )
            response.raise_for_status()
            result = response.json()

            if 'error' in result:
                error_count += len(batch)
                print(f"  Batch {batch_num}/{total_batches}: [FAIL] - {result['error']}")
            else:
                success_count += len(batch)
                print(f"  Batch {batch_num}/{total_batches}: [OK] {len(batch)} records written")

        except Exception as e:
            error_count += len(batch)
            print(f"  Batch {batch_num}/{total_batches}: [FAIL] - {e}")

    print(f"\nResults: {success_count} succeeded, {error_count} failed")
    return error_count == 0


def backfill_questdb(symbols: List[str], days: int):
    """
    Main backfill function.

    Args:
        symbols: List of ticker symbols
        days: Number of days of historical data
    """
    print("=" * 70)
    print("QuestDB Historical Data Backfill")
    print("=" * 70)

    # Step 1: Fetch data from yfinance
    data = fetch_historical_data(symbols, days)

    # Step 2: Convert to data rows for SQL INSERT
    print("\nPreparing data for SQL INSERT...")
    data_rows = []

    if len(symbols) == 1:
        # Single symbol - data is a simple DataFrame
        symbol = symbols[0]
        for date, row in data.iterrows():
            # Convert date to nanoseconds timestamp
            timestamp_ns = int(date.timestamp() * 1_000_000_000)
            data_rows.append((symbol, row, timestamp_ns))
    else:
        # Multiple symbols - data has MultiIndex columns (Price, Ticker)
        # Symbols are in level 1 of the MultiIndex
        for symbol in symbols:
            if symbol not in data.columns.get_level_values(1):
                print(f"  WARNING: {symbol} not found in data, skipping")
                continue

            # Extract data for this symbol by selecting all columns where level 1 == symbol
            # This gives us a DataFrame with columns: Open, High, Low, Close, Volume
            symbol_data = data.xs(symbol, axis=1, level=1)

            for date, row in symbol_data.iterrows():
                # Convert date to nanoseconds timestamp
                timestamp_ns = int(date.timestamp() * 1_000_000_000)
                data_rows.append((symbol, row, timestamp_ns))

    print(f"[OK] Prepared {len(data_rows)} records for insertion")

    # Step 3: Write to QuestDB via SQL
    success = write_to_questdb_sql(data_rows)

    # Step 4: Verify
    print("\nVerifying backfill...")
    time.sleep(2)  # Wait for QuestDB to process

    try:
        response = requests.get(
            f"http://{QUESTDB_HOST}:{QUESTDB_PORT}/exec",
            params={"query": f"SELECT symbol, MIN(timestamp) as first, MAX(timestamp) as last, COUNT(*) as count FROM {TARGET_TABLE} GROUP BY symbol ORDER BY symbol"},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()

        print("\nQuestDB Data Summary:")
        print("-" * 70)
        print(f"{'Symbol':<10} {'First Record':<22} {'Last Record':<22} {'Count':>8}")
        print("-" * 70)

        for row in result.get('dataset', []):
            symbol, first, last, count = row
            # Format timestamps
            first_dt = datetime.fromisoformat(first.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
            last_dt = datetime.fromisoformat(last.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
            print(f"{symbol:<10} {first_dt:<22} {last_dt:<22} {count:>8}")

    except Exception as e:
        print(f"  WARNING: Failed to verify: {e}")

    # Done
    print("\n" + "=" * 70)
    if success:
        print("[SUCCESS] Backfill completed successfully")
    else:
        print("[ERROR] Backfill completed with errors")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Backfill QuestDB with historical market data from yfinance"
    )
    parser.add_argument(
        '--days',
        type=int,
        default=60,
        help='Number of days of historical data to backfill (default: 60)'
    )
    parser.add_argument(
        '--symbols',
        type=str,
        default=None,
        help=f'Comma-separated list of symbols (default: {",".join(DEFAULT_SYMBOLS[:5])}...)'
    )
    parser.add_argument(
        '--questdb-host',
        type=str,
        default='localhost',
        help='QuestDB host (default: localhost)'
    )
    parser.add_argument(
        '--questdb-port',
        type=int,
        default=9000,
        help='QuestDB HTTP port (default: 9000)'
    )

    args = parser.parse_args()

    # Update QuestDB connection
    global QUESTDB_HOST, QUESTDB_PORT, QUESTDB_WRITE_URL
    QUESTDB_HOST = args.questdb_host
    QUESTDB_PORT = args.questdb_port
    QUESTDB_WRITE_URL = f"http://{QUESTDB_HOST}:{QUESTDB_PORT}/write"

    # Parse symbols
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(',')]
    else:
        symbols = DEFAULT_SYMBOLS

    # Run backfill
    backfill_questdb(symbols, args.days)


if __name__ == "__main__":
    main()
