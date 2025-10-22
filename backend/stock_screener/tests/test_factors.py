# test_factors.py - Test Factor Calculations

import sys
sys.path.append('..')

import numpy as np
import pandas as pd
from factor_library import TechnicalFactors, FundamentalFactors, StatisticalFactors


def test_momentum():
    """Test momentum calculation."""
    print("\n=== Test: Momentum ===")

    prices = pd.Series([100, 102, 105, 103, 108, 110, 115, 118, 120, 125])

    tech = TechnicalFactors()
    momentum = tech.momentum(prices, period=5)

    print(f"Momentum (5-day): {momentum:.2f}%")

    # Should be positive since prices are rising
    assert momentum > 0, "Expected positive momentum"
    print("✓ Momentum test passed")


def test_rsi():
    """Test RSI calculation."""
    print("\n=== Test: RSI ===")

    # Create a simple price series
    prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109,
                       111, 110, 112, 115, 114, 116, 118, 117, 119, 120])

    tech = TechnicalFactors()
    rsi = tech.rsi(prices, period=14)

    print(f"RSI (14-day): {rsi:.2f}")

    # RSI should be between 0 and 100
    assert 0 <= rsi <= 100, f"RSI should be between 0 and 100, got {rsi}"
    print("✓ RSI test passed")


def test_macd():
    """Test MACD calculation."""
    print("\n=== Test: MACD ===")

    # Trending up prices
    prices = pd.Series([100 + i * 0.5 for i in range(50)])

    tech = TechnicalFactors()
    macd = tech.macd(prices)

    print(f"MACD: {macd['macd']:.4f}")
    print(f"Signal: {macd['signal']:.4f}")
    print(f"Histogram: {macd['histogram']:.4f}")
    print(f"Crossover: {macd['crossover']}")

    assert 'macd' in macd
    assert 'signal' in macd
    assert 'histogram' in macd
    print("✓ MACD test passed")


def test_bollinger_bands():
    """Test Bollinger Bands calculation."""
    print("\n=== Test: Bollinger Bands ===")

    # Price with some volatility
    np.random.seed(42)
    prices = pd.Series([100] * 30)
    for i in range(1, 30):
        prices.iloc[i] = prices.iloc[i-1] * (1 + np.random.randn() * 0.02)

    tech = TechnicalFactors()
    bb = tech.bollinger_bands(prices)

    print(f"Upper Band: {bb['upper']:.2f}")
    print(f"Middle Band: {bb['middle']:.2f}")
    print(f"Lower Band: {bb['lower']:.2f}")
    print(f"%B: {bb['percent_b']:.2f}")
    print(f"Bandwidth: {bb['bandwidth']:.2f}%")

    # Upper should be greater than lower
    assert bb['upper'] > bb['lower'], "Upper band should be greater than lower"
    print("✓ Bollinger Bands test passed")


def test_sharpe_ratio():
    """Test Sharpe ratio calculation."""
    print("\n=== Test: Sharpe Ratio ===")

    # Generate some returns
    np.random.seed(42)
    returns = pd.Series(np.random.randn(252) * 0.01 + 0.0005)  # ~12.6% annual return

    stat = StatisticalFactors()
    sharpe = stat.sharpe_ratio(returns)

    print(f"Sharpe Ratio: {sharpe:.2f}")

    # Should be a reasonable value
    assert -5 < sharpe < 5, f"Sharpe ratio seems unreasonable: {sharpe}"
    print("✓ Sharpe ratio test passed")


def test_correlation():
    """Test correlation calculation."""
    print("\n=== Test: Correlation ===")

    # Create correlated returns
    np.random.seed(42)
    base_returns = pd.Series(np.random.randn(100) * 0.01)
    correlated_returns = base_returns * 0.7 + pd.Series(np.random.randn(100) * 0.01 * 0.3)

    stat = StatisticalFactors()
    corr = stat.correlation_to_spy(correlated_returns, base_returns)

    print(f"Correlation: {corr:.3f}")

    # Should be positive correlation
    assert 0 < corr < 1, f"Expected positive correlation, got {corr}"
    print("✓ Correlation test passed")


def test_all_factors():
    """Test that all factors can be calculated."""
    print("\n=== Test: All Factors ===")

    # Create sample data
    np.random.seed(42)
    n = 60
    prices = pd.Series([100] * n)
    for i in range(1, n):
        prices.iloc[i] = prices.iloc[i-1] * (1 + np.random.randn() * 0.015)

    tech = TechnicalFactors()

    # Test each factor
    factors = {
        'momentum_20d': tech.momentum(prices, 20),
        'momentum_60d': tech.momentum(prices, 60),
        'rsi': tech.rsi(prices),
        'volume_surge': 1.5,  # Placeholder
    }

    print(f"Calculated {len(factors)} factors:")
    for name, value in factors.items():
        print(f"  {name}: {value:.2f}")

    # All should be numeric
    for name, value in factors.items():
        assert isinstance(value, (int, float)), f"{name} should be numeric"

    print("✓ All factors test passed")


if __name__ == '__main__':
    print("Running Factor Library Tests...")

    try:
        test_momentum()
        test_rsi()
        test_macd()
        test_bollinger_bands()
        test_sharpe_ratio()
        test_correlation()
        test_all_factors()

        print("\n" + "="*50)
        print("✓ All tests passed!")
        print("="*50)

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
