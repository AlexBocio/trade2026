# test_bootstrap.py - Bootstrap module tests

import pytest
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, '..')

import bootstrap


@pytest.fixture
def sample_returns():
    """Generate sample returns data."""
    np.random.seed(42)
    returns = pd.Series(np.random.normal(0.001, 0.02, 252))
    returns.index = pd.date_range('2023-01-01', periods=252, freq='D')
    return returns


def test_standard_bootstrap(sample_returns):
    """Test standard bootstrap."""
    samples = bootstrap.standard_bootstrap(sample_returns, n_simulations=100)

    assert samples.shape == (100, 252)
    assert np.allclose(samples.mean(), sample_returns.mean(), atol=0.01)


def test_block_bootstrap(sample_returns):
    """Test block bootstrap."""
    samples = bootstrap.block_bootstrap(sample_returns, block_size=10, n_simulations=100)

    assert samples.shape == (100, 252)


def test_circular_block_bootstrap(sample_returns):
    """Test circular block bootstrap."""
    samples = bootstrap.circular_block_bootstrap(sample_returns, block_size=10, n_simulations=100)

    assert samples.shape == (100, 252)


def test_stationary_bootstrap(sample_returns):
    """Test stationary bootstrap."""
    samples = bootstrap.stationary_bootstrap(sample_returns, avg_block_size=10, n_simulations=100)

    assert samples.shape == (100, 252)


def test_wild_bootstrap(sample_returns):
    """Test wild bootstrap."""
    samples = bootstrap.wild_bootstrap(sample_returns, n_simulations=100)

    assert samples.shape == (100, 252)


def test_bootstrap_confidence_interval(sample_returns):
    """Test bootstrap confidence interval."""
    def mean_func(series):
        return series.mean()

    ci = bootstrap.bootstrap_confidence_interval(
        sample_returns,
        mean_func,
        bootstrap_method='standard',
        n_simulations=100
    )

    assert 'point_estimate' in ci
    assert 'lower_bound' in ci
    assert 'upper_bound' in ci
    assert ci['lower_bound'] < ci['upper_bound']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
