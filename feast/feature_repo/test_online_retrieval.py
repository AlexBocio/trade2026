"""
Test Online Feature Retrieval from Feast.

Tests that features can be retrieved from the online store with low latency.
"""
import time
from datetime import datetime
import pandas as pd
from feast import FeatureStore


def test_online_retrieval():
    """Test retrieving features from online store."""
    print("=" * 70)
    print("FEAST ONLINE FEATURE RETRIEVAL TEST")
    print("=" * 70)

    # Initialize feature store
    store = FeatureStore(repo_path=".")

    print("\n[INFO] Feature store initialized")
    print(f"  Project: {store.project}")
    print(f"  Registry: {store.config.registry.path}")
    print(f"  Online store: {store.config.online_store.type}")

    # List registered entities and feature views
    entities = store.list_entities()
    feature_views = store.list_feature_views()

    print(f"\n[INFO] Registered entities: {[e.name for e in entities]}")
    print(f"[INFO] Registered feature views: {[fv.name for fv in feature_views]}")

    # Prepare entity data for retrieval
    # Using symbols from our test data
    entity_df = pd.DataFrame({
        "symbol": ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
    })

    print(f"\n[INFO] Retrieving features for entities:")
    print(entity_df)

    # Define features to retrieve
    features = [
        "technical_indicators:rsi",
        "technical_indicators:macd",
        "technical_indicators:macd_signal",
        "technical_indicators:macd_histogram",
        "technical_indicators:bb_upper",
        "technical_indicators:bb_middle",
        "technical_indicators:bb_lower",
        "technical_indicators:bb_percent_b",
        "technical_indicators:close",
    ]

    print(f"\n[INFO] Features to retrieve ({len(features)} features):")
    for feat in features:
        print(f"  - {feat}")

    # Test retrieval with latency measurement
    print(f"\n[TEST] Retrieving features from online store...")

    start_time = time.time()
    feature_vector = store.get_online_features(
        features=features,
        entity_rows=[
            {"symbol": "BTCUSDT"},
            {"symbol": "ETHUSDT"},
            {"symbol": "BNBUSDT"},
        ]
    ).to_dict()
    end_time = time.time()

    latency_ms = (end_time - start_time) * 1000

    print(f"\n[RESULTS]")
    print(f"  Latency: {latency_ms:.2f} ms")
    print(f"  Entities retrieved: {len(feature_vector.get('symbol', []))}")

    # Display retrieved features
    print(f"\n[FEATURE VALUES]")
    for i, symbol in enumerate(feature_vector.get('symbol', [])):
        print(f"\n  Symbol: {symbol}")
        print(f"    Close: {feature_vector.get('close', [None] * (i+1))[i]}")
        print(f"    RSI: {feature_vector.get('rsi', [None] * (i+1))[i]}")
        print(f"    MACD: {feature_vector.get('macd', [None] * (i+1))[i]}")
        print(f"    MACD Signal: {feature_vector.get('macd_signal', [None] * (i+1))[i]}")
        print(f"    BB Upper: {feature_vector.get('bb_upper', [None] * (i+1))[i]}")
        print(f"    BB %B: {feature_vector.get('bb_percent_b', [None] * (i+1))[i]}")

    # Validate latency
    print(f"\n[VALIDATION]")
    if latency_ms < 10:
        print(f"  [OK] Latency {latency_ms:.2f}ms < 10ms target")
    elif latency_ms < 100:
        print(f"  [WARNING] Latency {latency_ms:.2f}ms is acceptable but higher than 10ms target")
    else:
        print(f"  [ERROR] Latency {latency_ms:.2f}ms exceeds acceptable threshold")

    # Check if features were retrieved
    if feature_vector.get('symbol'):
        print(f"  [OK] Features retrieved successfully")
    else:
        print(f"  [ERROR] No features retrieved")

    print("\n" + "=" * 70)
    if latency_ms < 100 and feature_vector.get('symbol'):
        print("[SUCCESS] Online feature retrieval test passed!")
    else:
        print("[FAILURE] Online feature retrieval test failed!")
    print("=" * 70)

    return latency_ms, feature_vector


def benchmark_retrieval(n_iterations=10):
    """Benchmark online feature retrieval latency."""
    print("\n" + "=" * 70)
    print("LATENCY BENCHMARK")
    print("=" * 70)

    store = FeatureStore(repo_path=".")

    features = [
        "technical_indicators:rsi",
        "technical_indicators:macd",
        "technical_indicators:close",
    ]

    latencies = []

    print(f"\n[INFO] Running {n_iterations} retrieval iterations...")

    for i in range(n_iterations):
        start_time = time.time()
        store.get_online_features(
            features=features,
            entity_rows=[{"symbol": "BTCUSDT"}]
        ).to_dict()
        end_time = time.time()

        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)

        if (i + 1) % 5 == 0:
            print(f"  Completed {i + 1}/{n_iterations} iterations...")

    # Calculate statistics
    import statistics

    print(f"\n[LATENCY STATISTICS]")
    print(f"  Min: {min(latencies):.2f} ms")
    print(f"  Max: {max(latencies):.2f} ms")
    print(f"  Mean: {statistics.mean(latencies):.2f} ms")
    print(f"  Median: {statistics.median(latencies):.2f} ms")
    print(f"  Std Dev: {statistics.stdev(latencies):.2f} ms")

    print(f"\n[TARGET VALIDATION]")
    if statistics.mean(latencies) < 10:
        print(f"  [OK] Mean latency {statistics.mean(latencies):.2f}ms < 10ms target")
    else:
        print(f"  [WARNING] Mean latency {statistics.mean(latencies):.2f}ms exceeds 10ms target")

    print("=" * 70)


if __name__ == '__main__':
    # Run online retrieval test
    latency, features = test_online_retrieval()

    # Run latency benchmark
    benchmark_retrieval(n_iterations=20)
