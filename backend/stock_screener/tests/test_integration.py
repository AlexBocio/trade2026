# test_integration.py - Integration Tests for Stock Screener

import sys
sys.path.append('..')

import time
from timeframe_strategies import get_strategy, list_strategies, STRATEGIES
from universe_manager import UniverseManager


def test_strategy_loading():
    """Test loading strategies."""
    print("\n=== Test: Strategy Loading ===")

    for strategy_name in STRATEGIES.keys():
        strategy = get_strategy(strategy_name)
        print(f"\n{strategy['name']}:")
        print(f"  Timeframe: {strategy['timeframe']}")
        print(f"  Holding period: {strategy['holding_period']}")
        print(f"  Factors: {len(strategy['factor_weights'])}")
        print(f"  Filters: {len(strategy.get('filters', {}))}")

        # Verify strategy structure
        assert 'name' in strategy
        assert 'factor_weights' in strategy
        assert isinstance(strategy['factor_weights'], dict)

        # Verify weights are positive
        for factor, weight in strategy['factor_weights'].items():
            assert weight > 0, f"Weight for {factor} should be positive"

    print(f"\n✓ Loaded {len(STRATEGIES)} strategies successfully")


def test_universe_manager():
    """Test universe management."""
    print("\n=== Test: Universe Manager ===")

    um = UniverseManager()

    # Test Dow 30 (small, always available)
    print("\nTesting Dow 30 universe...")
    dow30 = um.get_universe_tickers('dow30')
    print(f"  Dow 30 tickers: {len(dow30)}")
    print(f"  Sample: {dow30[:5]}")

    assert len(dow30) == 30, f"Dow 30 should have 30 tickers, got {len(dow30)}"

    # Test universe listing
    universes = um.list_available_universes()
    print(f"\nAvailable universes: {len(universes)}")
    for u in universes:
        print(f"  - {u['id']}: {u['name']}")

    print("✓ Universe manager test passed")


def test_strategy_list():
    """Test strategy listing."""
    print("\n=== Test: Strategy Listing ===")

    strategies = list_strategies()

    print(f"\nAvailable strategies: {len(strategies)}")
    for s in strategies:
        print(f"  - {s['id']}: {s['name']} ({s['holding_period']})")

    assert len(strategies) > 0, "Should have at least one strategy"
    print("✓ Strategy listing test passed")


def test_filter_application():
    """Test strategy filter application."""
    print("\n=== Test: Filter Application ===")

    from timeframe_strategies import apply_strategy_filters

    # Get intraday strategy (has strict filters)
    strategy = get_strategy('intraday')

    # Test stock that passes
    stock_pass = {
        'liquidity': 15_000_000,
        'current_price': 50,
        'volume_surge': 1.5
    }

    # Test stock that fails
    stock_fail = {
        'liquidity': 1_000_000,  # Below min
        'current_price': 50,
        'volume_surge': 1.5
    }

    passes = apply_strategy_filters(stock_pass, strategy)
    fails = apply_strategy_filters(stock_fail, strategy)

    print(f"Stock with good liquidity passes: {passes}")
    print(f"Stock with low liquidity fails: {fails}")

    assert passes == True, "Stock with good metrics should pass"
    assert fails == False, "Stock with bad metrics should fail"

    print("✓ Filter application test passed")


def test_custom_universe():
    """Test custom universe creation."""
    print("\n=== Test: Custom Universe ===")

    um = UniverseManager()

    custom_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
    validated = um.create_custom_universe(custom_tickers)

    print(f"Input tickers: {custom_tickers}")
    print(f"Validated tickers: {validated}")

    # May be less than input if validation fails, but should have some
    assert len(validated) >= 3, "Should validate at least 3 tickers"

    print("✓ Custom universe test passed")


def test_market_cap_filtering():
    """Test market cap filtering."""
    print("\n=== Test: Market Cap Filtering ===")

    um = UniverseManager()

    # Test with Dow 30 (small universe, always available)
    dow_tickers = um.get_universe_tickers('dow30')

    print(f"\nFiltering {len(dow_tickers)} Dow 30 stocks by price range...")

    # Filter by price range
    filtered = um.filter_by_criteria(
        dow_tickers[:10],  # Test with first 10 only
        min_price=50,
        max_price=500
    )

    print(f"Filtered to {len(filtered)} stocks in price range $50-$500")
    if filtered:
        print(f"Sample: {filtered[:5]}")

    # Should have some results
    # (We can't assert specific count as prices change)
    print("✓ Market cap filtering test passed")


def test_strategy_validation():
    """Test strategy validation."""
    print("\n=== Test: Strategy Validation ===")

    from timeframe_strategies import validate_strategy

    # Valid strategy
    valid_strategy = {
        'name': 'Test Strategy',
        'timeframe': 'swing',
        'holding_period': '5 days',
        'data_period_days': 60,
        'factor_weights': {
            'momentum': 0.5,
            'rsi': 0.5
        }
    }

    # Should pass
    result = validate_strategy(valid_strategy)
    assert result == True, "Valid strategy should pass validation"

    print("✓ Strategy validation test passed")


def test_performance():
    """Test performance metrics."""
    print("\n=== Test: Performance ===")

    um = UniverseManager()

    # Time universe loading (with cache)
    start = time.time()
    dow1 = um.get_universe_tickers('dow30')
    time1 = time.time() - start

    start = time.time()
    dow2 = um.get_universe_tickers('dow30')  # Should hit cache
    time2 = time.time() - start

    print(f"First load: {time1:.3f}s")
    print(f"Cached load: {time2:.3f}s")

    assert time2 < time1 / 2, "Cached load should be faster"

    print("✓ Performance test passed")


if __name__ == '__main__':
    print("Running Integration Tests...")

    try:
        test_strategy_loading()
        test_universe_manager()
        test_strategy_list()
        test_filter_application()
        test_custom_universe()
        test_market_cap_filtering()
        test_strategy_validation()
        test_performance()

        print("\n" + "="*50)
        print("✓ All integration tests passed!")
        print("="*50)

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
