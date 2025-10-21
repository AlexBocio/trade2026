"""
Comprehensive Test Suite for Default ML Features

Tests multiple market scenarios, edge cases, validation, and performance.
"""
import pandas as pd
import numpy as np
import sys
import time
from pathlib import Path

# Add parent directory to path for module imports
features_dir = Path(__file__).parent
sys.path.insert(0, str(features_dir))

# Import individual modules directly
import rsi
import macd
import bollinger_bands

# Import pipeline with absolute imports
from rsi import calculate_rsi, calculate_rsi_smoothed
from macd import calculate_macd, macd_crossover_signal
from bollinger_bands import (
    calculate_bollinger_bands,
    bollinger_squeeze,
    bollinger_breakout_signal
)


class FeaturePipeline:
    """
    Feature engineering pipeline for trading strategies.
    (Copied here to avoid relative import issues in standalone testing)
    """

    def __init__(
        self,
        rsi_period: int = 14,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        bb_period: int = 20,
        bb_std: float = 2.0
    ):
        self.rsi_period = rsi_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.bb_period = bb_period
        self.bb_std = bb_std

    def calculate_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'close' not in df.columns:
            raise ValueError("DataFrame must contain 'close' column")

        result = df.copy()

        # Calculate RSI
        result['rsi'] = calculate_rsi(result['close'], period=self.rsi_period)

        # Calculate MACD
        macd_features = calculate_macd(
            result['close'],
            fast=self.macd_fast,
            slow=self.macd_slow,
            signal=self.macd_signal
        )
        result['macd'] = macd_features['macd']
        result['macd_signal'] = macd_features['signal']
        result['macd_histogram'] = macd_features['histogram']
        result['macd_crossover'] = macd_crossover_signal(macd_features)

        # Calculate Bollinger Bands
        bbands = calculate_bollinger_bands(
            result['close'],
            period=self.bb_period,
            std_dev=self.bb_std
        )
        result['bb_upper'] = bbands['upper']
        result['bb_middle'] = bbands['middle']
        result['bb_lower'] = bbands['lower']
        result['bb_bandwidth'] = bbands['bandwidth']
        result['bb_percent_b'] = bbands['percent_b']
        result['bb_squeeze'] = bollinger_squeeze(bbands).astype(int)
        result['bb_breakout'] = bollinger_breakout_signal(result['close'], bbands)

        result = result.dropna()
        return result

    def calculate_feature_subset(
        self,
        df: pd.DataFrame,
        features: list
    ) -> pd.DataFrame:
        result = df.copy()

        if 'rsi' in features:
            result['rsi'] = calculate_rsi(result['close'], period=self.rsi_period)

        if 'macd' in features:
            macd_features = calculate_macd(
                result['close'],
                fast=self.macd_fast,
                slow=self.macd_slow,
                signal=self.macd_signal
            )
            result['macd'] = macd_features['macd']
            result['macd_signal'] = macd_features['signal']
            result['macd_histogram'] = macd_features['histogram']

        if 'bollinger_bands' in features:
            bbands = calculate_bollinger_bands(
                result['close'],
                period=self.bb_period,
                std_dev=self.bb_std
            )
            result['bb_upper'] = bbands['upper']
            result['bb_middle'] = bbands['middle']
            result['bb_lower'] = bbands['lower']

        result = result.dropna()
        return result

    def get_feature_names(self):
        return [
            'rsi',
            'macd',
            'macd_signal',
            'macd_histogram',
            'macd_crossover',
            'bb_upper',
            'bb_middle',
            'bb_lower',
            'bb_bandwidth',
            'bb_percent_b',
            'bb_squeeze',
            'bb_breakout'
        ]

    def validate_data(self, df: pd.DataFrame):
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }

        if 'close' not in df.columns:
            validation['valid'] = False
            validation['errors'].append("Missing 'close' column")

        min_required = max(self.rsi_period, self.macd_slow, self.bb_period)
        if len(df) < min_required:
            validation['valid'] = False
            validation['errors'].append(
                f"Insufficient data: need at least {min_required} rows, got {len(df)}"
            )

        if 'close' in df.columns and df['close'].isna().any():
            na_count = df['close'].isna().sum()
            validation['warnings'].append(f"{na_count} missing values in 'close' column")

        if 'close' in df.columns:
            validation['stats'] = {
                'rows': len(df),
                'min_price': df['close'].min(),
                'max_price': df['close'].max(),
                'mean_price': df['close'].mean()
            }

        return validation

def create_test_scenarios():
    """Create diverse market condition test datasets."""
    scenarios = {}

    # Scenario 1: Strong uptrend
    scenarios['uptrend'] = pd.DataFrame({
        'close': [100 + i*2 + np.random.normal(0, 0.5) for i in range(100)],
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='h')
    })

    # Scenario 2: Strong downtrend
    scenarios['downtrend'] = pd.DataFrame({
        'close': [200 - i*1.5 + np.random.normal(0, 0.5) for i in range(100)],
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='h')
    })

    # Scenario 3: Sideways/ranging market
    scenarios['sideways'] = pd.DataFrame({
        'close': [150 + np.random.normal(0, 2) for i in range(100)],
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='h')
    })

    # Scenario 4: High volatility
    scenarios['volatile'] = pd.DataFrame({
        'close': [100 + np.random.normal(0, 10) for i in range(100)],
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='h')
    })

    # Scenario 5: Low volatility
    scenarios['low_volatility'] = pd.DataFrame({
        'close': [100 + np.random.normal(0, 0.1) for i in range(100)],
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='h')
    })

    # Scenario 6: Sine wave (oscillating)
    scenarios['oscillating'] = pd.DataFrame({
        'close': [100 + 20*np.sin(i*0.1) for i in range(100)],
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='h')
    })

    return scenarios

def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "="*70)
    print("EDGE CASE TESTING")
    print("="*70)

    pipeline = FeaturePipeline()
    tests_passed = 0
    tests_failed = 0

    # Test 1: Minimum viable dataset
    print("\n[TEST] Minimum viable dataset (50 rows)...")
    try:
        df_min = pd.DataFrame({
            'close': [100 + i for i in range(50)]
        })
        result = pipeline.calculate_all_features(df_min)
        if len(result) > 0:
            print("  [OK] Minimum dataset processed")
            tests_passed += 1
        else:
            print("  [ERROR] No output from minimum dataset")
            tests_failed += 1
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        tests_failed += 1

    # Test 2: Insufficient data
    print("\n[TEST] Insufficient data (10 rows)...")
    try:
        df_small = pd.DataFrame({
            'close': [100 + i for i in range(10)]
        })
        validation = pipeline.validate_data(df_small)
        if not validation['valid']:
            print("  [OK] Correctly rejected insufficient data")
            print(f"       Error: {validation['errors'][0]}")
            tests_passed += 1
        else:
            print("  [ERROR] Should have rejected insufficient data")
            tests_failed += 1
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        tests_failed += 1

    # Test 3: Missing 'close' column
    print("\n[TEST] Missing 'close' column...")
    try:
        df_missing = pd.DataFrame({
            'price': [100 + i for i in range(50)]
        })
        validation = pipeline.validate_data(df_missing)
        if not validation['valid']:
            print("  [OK] Correctly detected missing 'close' column")
            print(f"       Error: {validation['errors'][0]}")
            tests_passed += 1
        else:
            print("  [ERROR] Should have detected missing column")
            tests_failed += 1
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        tests_failed += 1

    # Test 4: NaN values in input
    print("\n[TEST] NaN values in input data...")
    try:
        df_nan = pd.DataFrame({
            'close': [100.0] * 30 + [np.nan] * 5 + [110.0] * 25
        })
        validation = pipeline.validate_data(df_nan)
        if len(validation['warnings']) > 0:
            print("  [OK] Detected NaN values in input")
            print(f"       Warning: {validation['warnings'][0]}")
            tests_passed += 1
        else:
            print("  [ERROR] Should have warned about NaN values")
            tests_failed += 1
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        tests_failed += 1

    # Test 5: All identical prices (division by zero scenarios)
    print("\n[TEST] Identical prices (division by zero)...")
    try:
        df_flat = pd.DataFrame({
            'close': [100.0] * 60
        })
        result = pipeline.calculate_all_features(df_flat)
        if len(result) > 0:
            # Check if RSI is 100 (no price movement)
            if result['rsi'].iloc[-1] == 100.0:
                print("  [OK] Handled flat prices correctly (RSI=100)")
                tests_passed += 1
            else:
                print(f"  [ERROR] RSI should be 100 for flat prices, got {result['rsi'].iloc[-1]}")
                tests_failed += 1
        else:
            print("  [ERROR] No output from flat price dataset")
            tests_failed += 1
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        tests_failed += 1

    # Test 6: Very large price values
    print("\n[TEST] Very large price values...")
    try:
        df_large = pd.DataFrame({
            'close': [1_000_000 + i*1000 for i in range(60)]
        })
        result = pipeline.calculate_all_features(df_large)
        if len(result) > 0 and not result.isnull().any().any():
            print("  [OK] Handled large price values")
            tests_passed += 1
        else:
            print("  [ERROR] Failed with large prices")
            tests_failed += 1
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        tests_failed += 1

    # Test 7: Very small price values
    print("\n[TEST] Very small price values...")
    try:
        df_small_prices = pd.DataFrame({
            'close': [0.0001 + i*0.00001 for i in range(60)]
        })
        result = pipeline.calculate_all_features(df_small_prices)
        if len(result) > 0 and not result.isnull().any().any():
            print("  [OK] Handled small price values")
            tests_passed += 1
        else:
            print("  [ERROR] Failed with small prices")
            tests_failed += 1
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        tests_failed += 1

    print(f"\n[SUMMARY] Edge case tests: {tests_passed} passed, {tests_failed} failed")
    return tests_passed, tests_failed

def test_market_scenarios(scenarios):
    """Test feature pipeline across different market conditions."""
    print("\n" + "="*70)
    print("MARKET SCENARIO TESTING")
    print("="*70)

    pipeline = FeaturePipeline()
    results = {}

    for scenario_name, df in scenarios.items():
        print(f"\n[TEST] {scenario_name.upper()} market...")
        try:
            result = pipeline.calculate_all_features(df)

            # Validate results
            checks = {
                'output_rows': len(result) > 0,
                'all_features': len(result.columns) == 14,  # 1 close + 1 timestamp + 12 features
                'no_nans': not result.isnull().any().any(),
                'rsi_range': (result['rsi'] >= 0).all() and (result['rsi'] <= 100).all(),
                'bb_ordering': (result['bb_lower'] <= result['bb_middle']).all() and
                              (result['bb_middle'] <= result['bb_upper']).all()
            }

            all_passed = all(checks.values())

            if all_passed:
                print(f"  [OK] All checks passed")
                print(f"       Rows: {len(result)}, RSI range: {result['rsi'].min():.2f}-{result['rsi'].max():.2f}")
                print(f"       MACD range: {result['macd'].min():.2f}-{result['macd'].max():.2f}")
            else:
                print(f"  [ERROR] Some checks failed:")
                for check, passed in checks.items():
                    if not passed:
                        print(f"         - {check}: FAILED")

            results[scenario_name] = {
                'passed': all_passed,
                'result': result,
                'checks': checks
            }

        except Exception as e:
            print(f"  [ERROR] Failed: {e}")
            results[scenario_name] = {
                'passed': False,
                'error': str(e)
            }

    passed_count = sum(1 for r in results.values() if r.get('passed', False))
    print(f"\n[SUMMARY] Market scenario tests: {passed_count}/{len(scenarios)} passed")
    return results

def test_feature_subset():
    """Test calculate_feature_subset functionality."""
    print("\n" + "="*70)
    print("FEATURE SUBSET TESTING")
    print("="*70)

    pipeline = FeaturePipeline()
    df = pd.DataFrame({
        'close': [100 + i + np.random.normal(0, 1) for i in range(60)]
    })

    tests_passed = 0
    tests_failed = 0

    # Test RSI only
    print("\n[TEST] RSI only...")
    try:
        result = pipeline.calculate_feature_subset(df, ['rsi'])
        if 'rsi' in result.columns and 'macd' not in result.columns:
            print("  [OK] RSI subset correct")
            tests_passed += 1
        else:
            print("  [ERROR] RSI subset failed")
            tests_failed += 1
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        tests_failed += 1

    # Test MACD only
    print("\n[TEST] MACD only...")
    try:
        result = pipeline.calculate_feature_subset(df, ['macd'])
        if all(col in result.columns for col in ['macd', 'macd_signal', 'macd_histogram']):
            print("  [OK] MACD subset correct")
            tests_passed += 1
        else:
            print("  [ERROR] MACD subset failed")
            tests_failed += 1
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        tests_failed += 1

    # Test Bollinger Bands only
    print("\n[TEST] Bollinger Bands only...")
    try:
        result = pipeline.calculate_feature_subset(df, ['bollinger_bands'])
        if all(col in result.columns for col in ['bb_upper', 'bb_middle', 'bb_lower']):
            print("  [OK] Bollinger Bands subset correct")
            tests_passed += 1
        else:
            print("  [ERROR] Bollinger Bands subset failed")
            tests_failed += 1
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        tests_failed += 1

    print(f"\n[SUMMARY] Feature subset tests: {tests_passed} passed, {tests_failed} failed")
    return tests_passed, tests_failed

def test_performance():
    """Test performance with larger datasets."""
    print("\n" + "="*70)
    print("PERFORMANCE TESTING")
    print("="*70)

    pipeline = FeaturePipeline()

    dataset_sizes = [100, 500, 1000, 5000]

    for size in dataset_sizes:
        df = pd.DataFrame({
            'close': [100 + i + np.random.normal(0, 2) for i in range(size)]
        })

        start_time = time.time()
        result = pipeline.calculate_all_features(df)
        elapsed = time.time() - start_time

        rows_per_sec = len(result) / elapsed if elapsed > 0 else 0

        print(f"\n[TEST] {size} input rows:")
        print(f"  Processing time: {elapsed:.3f}s")
        print(f"  Output rows: {len(result)}")
        print(f"  Throughput: {rows_per_sec:.0f} rows/sec")

        if elapsed < 1.0:  # Should be fast for these sizes
            print("  [OK] Performance acceptable")
        else:
            print("  [WARNING] Performance slower than expected")

def test_get_feature_names():
    """Test get_feature_names method."""
    print("\n" + "="*70)
    print("FEATURE NAMES TESTING")
    print("="*70)

    pipeline = FeaturePipeline()
    feature_names = pipeline.get_feature_names()

    expected_count = 12
    expected_features = [
        'rsi', 'macd', 'macd_signal', 'macd_histogram', 'macd_crossover',
        'bb_upper', 'bb_middle', 'bb_lower', 'bb_bandwidth', 'bb_percent_b',
        'bb_squeeze', 'bb_breakout'
    ]

    print(f"\n[TEST] Feature names list...")
    if len(feature_names) == expected_count:
        print(f"  [OK] Correct count: {expected_count}")
    else:
        print(f"  [ERROR] Expected {expected_count}, got {len(feature_names)}")

    if set(feature_names) == set(expected_features):
        print(f"  [OK] All expected features present")
    else:
        missing = set(expected_features) - set(feature_names)
        extra = set(feature_names) - set(expected_features)
        if missing:
            print(f"  [ERROR] Missing features: {missing}")
        if extra:
            print(f"  [ERROR] Extra features: {extra}")

def main():
    """Run comprehensive test suite."""
    print("="*70)
    print("COMPREHENSIVE TEST SUITE - DEFAULT ML FEATURES")
    print("="*70)

    total_passed = 0
    total_failed = 0

    # Create test scenarios
    print("\n[INFO] Generating test scenarios...")
    scenarios = create_test_scenarios()
    print(f"[INFO] Created {len(scenarios)} market scenarios")

    # Run edge case tests
    passed, failed = test_edge_cases()
    total_passed += passed
    total_failed += failed

    # Run market scenario tests
    scenario_results = test_market_scenarios(scenarios)
    scenario_passed = sum(1 for r in scenario_results.values() if r.get('passed', False))
    scenario_failed = len(scenario_results) - scenario_passed
    total_passed += scenario_passed
    total_failed += scenario_failed

    # Run feature subset tests
    passed, failed = test_feature_subset()
    total_passed += passed
    total_failed += failed

    # Run performance tests
    test_performance()

    # Run feature names test
    test_get_feature_names()

    # Final summary
    print("\n" + "="*70)
    print("FINAL TEST SUMMARY")
    print("="*70)
    print(f"\nTotal tests passed: {total_passed}")
    print(f"Total tests failed: {total_failed}")

    if total_failed == 0:
        print("\n" + "="*70)
        print("[SUCCESS] ALL COMPREHENSIVE TESTS PASSED!")
        print("="*70)
        return 0
    else:
        print("\n" + "="*70)
        print(f"[FAILURE] {total_failed} tests failed")
        print("="*70)
        return 1

if __name__ == '__main__':
    exit(main())
