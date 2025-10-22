# test_monte_carlo.py - Monte Carlo module tests

import pytest
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, '..')

import monte_carlo_advanced


@pytest.fixture
def sample_returns():
    """Generate sample returns data."""
    np.random.seed(42)
    returns = pd.Series(np.random.normal(0.001, 0.02, 252))
    returns.index = pd.date_range('2023-01-01', periods=252, freq='D')
    return returns


def test_garch_simulation(sample_returns):
    """Test GARCH filtered historical simulation."""
    result = monte_carlo_advanced.filtered_historical_simulation(
        sample_returns,
        method='garch',
        n_simulations=10,
        forecast_horizon=50
    )

    assert 'simulated_paths' in result
    assert result['simulated_paths'].shape == (10, 50)
    assert 'fitted_params' in result
    assert 'aic' in result


def test_jump_diffusion_simulation(sample_returns):
    """Test jump-diffusion simulation."""
    result = monte_carlo_advanced.jump_diffusion_simulation(
        sample_returns,
        n_simulations=10,
        forecast_horizon=50
    )

    assert 'simulated_paths' in result
    assert result['simulated_paths'].shape == (10, 50)
    assert 'parameters' in result


def test_regime_switching_simulation(sample_returns):
    """Test regime-switching simulation."""
    result = monte_carlo_advanced.regime_switching_simulation(
        sample_returns,
        n_regimes=2,
        n_simulations=10,
        forecast_horizon=50
    )

    assert 'simulated_paths' in result
    assert 'regime_paths' in result
    assert result['n_regimes'] == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
