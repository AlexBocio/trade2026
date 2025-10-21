"""Test full pipeline with flat prices."""
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rsi import calculate_rsi, calculate_rsi_smoothed
from macd import calculate_macd, macd_crossover_signal
from bollinger_bands import (
    calculate_bollinger_bands,
    bollinger_squeeze,
    bollinger_breakout_signal
)

# Create flat price dataset
df = pd.DataFrame({'close': [100.0] * 60})

print("Testing FULL pipeline with flat prices...")
result = df.copy()

# Calculate RSI
result['rsi'] = calculate_rsi(result['close'], period=14)
print(f"After RSI - shape: {result.shape}, NaN: {result['rsi'].isna().sum()}")

# Calculate MACD
macd_features = calculate_macd(result['close'], fast=12, slow=26, signal=9)
result['macd'] = macd_features['macd']
result['macd_signal'] = macd_features['signal']
result['macd_histogram'] = macd_features['histogram']
result['macd_crossover'] = macd_crossover_signal(macd_features)
print(f"After MACD - shape: {result.shape}, NaN in macd: {result['macd'].isna().sum()}")

# Calculate Bollinger Bands
bbands = calculate_bollinger_bands(result['close'], period=20, std_dev=2.0)
result['bb_upper'] = bbands['upper']
result['bb_middle'] = bbands['middle']
result['bb_lower'] = bbands['lower']
result['bb_bandwidth'] = bbands['bandwidth']
result['bb_percent_b'] = bbands['percent_b']
print(f"After BBands - shape: {result.shape}")
print(f"  bb_upper NaN: {result['bb_upper'].isna().sum()}")
print(f"  bb_percent_b NaN: {result['bb_percent_b'].isna().sum()}")

result['bb_squeeze'] = bollinger_squeeze(bbands).astype(int)
result['bb_breakout'] = bollinger_breakout_signal(result['close'], bbands)

print(f"\nBefore dropna - shape: {result.shape}")
print(f"NaN count per column:")
for col in result.columns:
    nan_count = result[col].isna().sum()
    if nan_count > 0:
        print(f"  {col}: {nan_count}")

result_clean = result.dropna()
print(f"\nAfter dropna - shape: {result_clean.shape}")

if len(result_clean) == 0:
    print("\n*** PROBLEM: All rows dropped! ***")
    print("This is because bb_percent_b is all NaN (division by zero when prices are flat)")
else:
    print(f"\n*** SUCCESS: {len(result_clean)} rows remain ***")
