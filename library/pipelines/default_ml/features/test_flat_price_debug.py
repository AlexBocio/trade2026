"""Debug test for flat price scenario."""
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rsi import calculate_rsi
from macd import calculate_macd
from bollinger_bands import calculate_bollinger_bands

# Create flat price dataset
df_flat = pd.DataFrame({
    'close': [100.0] * 60
})

print("Testing flat prices with 60 rows...")
print(f"Input shape: {df_flat.shape}")
print(f"Input close values (first 10): {df_flat['close'].head(10).tolist()}")

# Test RSI
print("\n=== Testing RSI ===")
rsi = calculate_rsi(df_flat['close'], period=14)
print(f"RSI shape: {rsi.shape}")
print(f"RSI NaN count: {rsi.isna().sum()}")
print(f"RSI values (last 5): {rsi.tail(5).tolist()}")

# Test MACD
print("\n=== Testing MACD ===")
macd = calculate_macd(df_flat['close'], fast=12, slow=26, signal=9)
print(f"MACD shape: {macd.shape}")
print(f"MACD NaN count: {macd.isna().sum()}")
print(f"MACD values (last 5):\n{macd.tail(5)}")

# Test Bollinger Bands
print("\n=== Testing Bollinger Bands ===")
bbands = calculate_bollinger_bands(df_flat['close'], period=20, std_dev=2.0)
print(f"BBands shape: {bbands.shape}")
print(f"BBands NaN count: {bbands.isna().sum()}")
print(f"BBands values (last 5):\n{bbands.tail(5)}")

# Combine and dropna
print("\n=== Combined DataFrame ===")
result = df_flat.copy()
result['rsi'] = rsi
result['macd'] = macd['macd']
result['bb_upper'] = bbands['upper']

print(f"Before dropna: {result.shape}")
print(f"NaN count per column:\n{result.isna().sum()}")

result_clean = result.dropna()
print(f"\nAfter dropna: {result_clean.shape}")
