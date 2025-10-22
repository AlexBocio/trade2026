# test_walk_forward.py - Walk-forward module tests

import pytest
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, '..')

import walk_forward_variants


@pytest.fixture
def sample_data():
    """Generate sample price data."""
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    prices = 100 * np.exp(np.cumsum(np.random.normal(0.001, 0.02, 500)))

    data = pd.DataFrame({
        'Adj Close': prices,
        'returns': np.concatenate([[0], np.diff(prices) / prices[:-1]])
    }, index=dates)

    return data


def simple_strategy(data, params):
    """Simple moving average crossover strategy."""
    fast_ma = data['Adj Close'].rolling(params['fast']).mean()
    slow_ma = data['Adj Close'].rolling(params['slow']).mean()

    signals = pd.Series(0, index=data.index)
    signals[fast_ma > slow_ma] = 1
    signals[fast_ma <= slow_ma] = -1

    return signals


def test_anchored_walk_forward(sample_data):
    """Test anchored walk-forward optimization."""
    param_grid = {'fast': [10, 20], 'slow': [50, 100]}

    result = walk_forward_variants.anchored_walk_forward(
        sample_data,
        simple_strategy,
        param_grid,
        train_size=252,
        test_size=63,
        step=63
    )

    assert result['method'] == 'anchored'
    assert 'results' in result
    assert 'summary' in result
    assert len(result['results']) > 0


def test_rolling_walk_forward(sample_data):
    """Test rolling walk-forward optimization."""
    param_grid = {'fast': [10, 20], 'slow': [50, 100]}

    result = walk_forward_variants.rolling_walk_forward(
        sample_data,
        simple_strategy,
        param_grid,
        train_size=252,
        test_size=63,
        step=63
    )

    assert result['method'] == 'rolling'
    assert 'results' in result
    assert len(result['results']) > 0


def test_compare_walk_forward_methods(sample_data):
    """Test walk-forward method comparison."""
    param_grid = {'fast': [10, 20], 'slow': [50, 100]}

    comparison_df = walk_forward_variants.compare_walk_forward_methods(
        sample_data,
        simple_strategy,
        param_grid,
        methods=['anchored', 'rolling']
    )

    assert len(comparison_df) == 2
    assert 'method' in comparison_df.columns


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
