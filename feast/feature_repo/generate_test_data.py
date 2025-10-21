"""
Generate test data for Feast feature store.

Creates synthetic market data with technical indicators and saves to parquet.
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add library to path so we can import the pipeline
library_path = Path(__file__).parent.parent.parent / "library"
sys.path.insert(0, str(library_path))

from pipelines.default_ml.features.pipeline import FeaturePipeline


def generate_feast_test_data(
    n_samples: int = 1000,
    symbols: list = None,
    output_path: str = "data/features.parquet"
):
    """
    Generate test data for Feast feature store.

    Args:
        n_samples: Number of samples per symbol
        symbols: List of trading symbols (default: ['BTCUSDT', 'ETHUSDT'])
        output_path: Path to save parquet file
    """
    if symbols is None:
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']

    print("=" * 70)
    print("FEAST TEST DATA GENERATION")
    print("=" * 70)

    # Initialize feature pipeline
    pipeline = FeaturePipeline()

    all_data = []

    for symbol in symbols:
        print(f"\n[{symbol}] Generating {n_samples} samples...")

        # Generate synthetic price data
        np.random.seed(hash(symbol) % 2**32)

        # Random walk with drift
        returns = np.random.normal(0.0001, 0.02, n_samples)
        prices = 100 * np.exp(np.cumsum(returns))

        # Create base dataframe
        start_time = datetime.now() - timedelta(hours=n_samples)
        timestamps = [start_time + timedelta(hours=i) for i in range(n_samples)]

        df = pd.DataFrame({
            'timestamp': timestamps,
            'symbol': symbol,
            'open': prices * (1 + np.random.normal(0, 0.001, n_samples)),
            'high': prices * (1 + np.abs(np.random.normal(0, 0.005, n_samples))),
            'low': prices * (1 - np.abs(np.random.normal(0, 0.005, n_samples))),
            'close': prices,
            'volume': np.random.uniform(1000, 10000, n_samples)
        })

        # Calculate all technical indicators
        print(f"  Calculating technical indicators...")
        df_with_features = pipeline.calculate_all_features(df)

        print(f"  Generated {len(df_with_features)} rows with features")
        print(f"  Features: {[col for col in df_with_features.columns if col not in ['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume']]}")

        all_data.append(df_with_features)

    # Combine all symbols
    combined_df = pd.concat(all_data, ignore_index=True)

    # Ensure timestamp is datetime type (Feast requires proper datetime, not integers)
    combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'])

    # Select columns for Feast
    feast_columns = [
        'timestamp', 'symbol', 'close',
        'rsi', 'macd', 'macd_signal', 'macd_histogram', 'macd_crossover',
        'bb_upper', 'bb_middle', 'bb_lower', 'bb_bandwidth', 'bb_percent_b',
        'bb_squeeze', 'bb_breakout'
    ]

    df_feast = combined_df[feast_columns].copy()

    # Save to parquet
    output_file = Path(__file__).parent / output_path
    output_file.parent.mkdir(parents=True, exist_ok=True)

    df_feast.to_parquet(output_file, index=False)

    print("\n" + "=" * 70)
    print("[SUCCESS] Test data generated")
    print("=" * 70)
    print(f"Output file: {output_file}")
    print(f"Total rows: {len(df_feast)}")
    print(f"Symbols: {df_feast['symbol'].unique().tolist()}")
    print(f"Time range: {pd.to_datetime(df_feast['timestamp'], unit='s').min()} to {pd.to_datetime(df_feast['timestamp'], unit='s').max()}")
    print(f"Columns: {list(df_feast.columns)}")
    print(f"\nSample data:")
    print(df_feast.head(3))

    return df_feast


if __name__ == '__main__':
    generate_feast_test_data(n_samples=500)
