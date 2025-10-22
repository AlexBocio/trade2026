# test_scoring.py - Test Composite Scoring and Ranking

import sys
sys.path.append('..')

import numpy as np
import pandas as pd
from composite_scoring import (
    normalize_factors,
    calculate_composite_score,
    rank_stocks_by_factors
)


def test_zscore_normalization():
    """Test z-score normalization."""
    print("\n=== Test: Z-Score Normalization ===")

    # Create sample factor data
    factor_data = pd.DataFrame({
        'momentum': [10, 15, 20, 5, 12, 18, 8, 22, 11, 16],
        'rsi': [50, 60, 70, 40, 55, 65, 45, 75, 52, 62]
    }, index=[f'STOCK{i}' for i in range(10)])

    normalized = normalize_factors(factor_data, ['momentum', 'rsi'], method='zscore')

    print("Original momentum mean:", factor_data['momentum'].mean())
    print("Normalized momentum mean:", normalized['momentum'].mean())
    print("Normalized momentum std:", normalized['momentum'].std())

    # Z-score should have mean ~0 and std ~1
    assert abs(normalized['momentum'].mean()) < 0.01, "Z-score mean should be ~0"
    assert abs(normalized['momentum'].std() - 1.0) < 0.01, "Z-score std should be ~1"
    print("✓ Z-score normalization test passed")


def test_percentile_normalization():
    """Test percentile normalization."""
    print("\n=== Test: Percentile Normalization ===")

    factor_data = pd.DataFrame({
        'momentum': [10, 15, 20, 5, 12, 18, 8, 22, 11, 16]
    }, index=[f'STOCK{i}' for i in range(10)])

    normalized = normalize_factors(factor_data, ['momentum'], method='percentile')

    print("Percentile range:", normalized['momentum'].min(), "-", normalized['momentum'].max())

    # Percentiles should be 0-100
    assert normalized['momentum'].min() >= 0, "Percentile min should be >= 0"
    assert normalized['momentum'].max() <= 100, "Percentile max should be <= 100"
    print("✓ Percentile normalization test passed")


def test_composite_score():
    """Test composite score calculation."""
    print("\n=== Test: Composite Score ===")

    # Create sample data
    factor_data = pd.DataFrame({
        'momentum': [10, 15, 20, 5, 12],
        'rsi': [50, 60, 70, 40, 55],
        'sharpe': [1.0, 1.5, 2.0, 0.5, 1.2]
    }, index=['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA'])

    # Define weights
    weights = {
        'momentum': 0.4,
        'rsi': 0.3,
        'sharpe': 0.3
    }

    # Calculate scores
    scores = calculate_composite_score(factor_data, weights, normalize=True)

    print("\nComposite Scores:")
    for ticker, score in scores.items():
        print(f"  {ticker}: {score:.3f}")

    # Scores should be numeric
    assert all(isinstance(s, (int, float)) for s in scores.values())
    print("✓ Composite score test passed")


def test_stock_ranking():
    """Test stock ranking."""
    print("\n=== Test: Stock Ranking ===")

    # Create sample data
    np.random.seed(42)
    n_stocks = 20

    factor_data = pd.DataFrame({
        'momentum': np.random.randn(n_stocks) * 5 + 10,
        'rsi': np.random.randn(n_stocks) * 10 + 50,
        'sharpe': np.random.randn(n_stocks) * 0.5 + 1.0,
        'earnings_growth': np.random.randn(n_stocks) * 10 + 15,
    }, index=[f'STOCK{i}' for i in range(n_stocks)])

    weights = {
        'momentum': 0.3,
        'rsi': 0.2,
        'sharpe': 0.3,
        'earnings_growth': 0.2
    }

    # Rank stocks
    ranked = rank_stocks_by_factors(factor_data, weights, top_n=10)

    print(f"\nTop 10 Stocks:")
    for i, (ticker, row) in enumerate(ranked.head(10).iterrows(), 1):
        print(f"  {i}. {ticker}: Score={row['composite_score']:.2f}, Rank={row['rank']}")

    # Check ranking is correct
    assert len(ranked) <= 10, "Should return top 10"
    assert ranked['composite_score'].is_monotonic_decreasing, "Should be sorted descending"
    print("✓ Stock ranking test passed")


def test_filtering():
    """Test stock filtering with minimum valid factors."""
    print("\n=== Test: Stock Filtering ===")

    # Create data with some missing values
    factor_data = pd.DataFrame({
        'momentum': [10, 15, np.nan, 5, 12],
        'rsi': [50, np.nan, 70, 40, 55],
        'sharpe': [1.0, 1.5, 2.0, np.nan, 1.2],
        'earnings_growth': [np.nan, 10, 15, 20, 25]
    }, index=['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA'])

    weights = {
        'momentum': 0.25,
        'rsi': 0.25,
        'sharpe': 0.25,
        'earnings_growth': 0.25
    }

    print("\nFactor completeness:")
    for ticker in factor_data.index:
        valid_count = factor_data.loc[ticker].notna().sum()
        print(f"  {ticker}: {valid_count}/4 valid factors")

    # Rank with minimum 3 valid factors
    ranked = rank_stocks_by_factors(factor_data, weights, top_n=10, min_valid_factors=3)

    print(f"\nStocks passing filter (min 3 valid factors): {len(ranked)}")

    # Should filter out stocks with < 3 valid factors
    for ticker in ranked.index:
        valid_count = factor_data.loc[ticker].notna().sum()
        assert valid_count >= 3, f"{ticker} should have >= 3 valid factors"

    print("✓ Filtering test passed")


def test_weight_validation():
    """Test that weights sum correctly."""
    print("\n=== Test: Weight Validation ===")

    weights = {
        'momentum': 0.3,
        'rsi': 0.2,
        'sharpe': 0.3,
        'earnings_growth': 0.2
    }

    total_weight = sum(weights.values())
    print(f"Total weight: {total_weight:.2f}")

    assert abs(total_weight - 1.0) < 0.01, f"Weights should sum to 1.0, got {total_weight}"
    print("✓ Weight validation test passed")


if __name__ == '__main__':
    print("Running Composite Scoring Tests...")

    try:
        test_zscore_normalization()
        test_percentile_normalization()
        test_composite_score()
        test_stock_ranking()
        test_filtering()
        test_weight_validation()

        print("\n" + "="*50)
        print("✓ All tests passed!")
        print("="*50)

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
