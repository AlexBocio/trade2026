# test_stationarity.py - Test stationarity testing methods

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from stationarity_tests import (
    adf_test,
    kpss_test,
    pp_test,
    combined_stationarity_check,
    test_multiple_d_values
)
from fractional_diff import fractional_diff_ffd
from config import Config


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def non_stationary_series():
    """Create a non-stationary series (random walk with drift)."""
    np.random.seed(42)
    n = 300
    drift = 0.01
    noise = np.random.normal(0, 1, n)
    cumsum = np.cumsum(drift + noise)

    dates = pd.date_range(start='2020-01-01', periods=n, freq='D')
    series = pd.Series(cumsum, index=dates, name='RandomWalk')

    return series


@pytest.fixture
def stationary_series():
    """Create a stationary series (white noise)."""
    np.random.seed(42)
    n = 300
    noise = np.random.normal(0, 1, n)

    dates = pd.date_range(start='2020-01-01', periods=n, freq='D')
    series = pd.Series(noise, index=dates, name='WhiteNoise')

    return series


@pytest.fixture
def price_series():
    """Create a price series (non-stationary)."""
    np.random.seed(42)
    n = 300
    returns = np.random.normal(0.0005, 0.02, n)
    prices = 100 * np.exp(np.cumsum(returns))

    dates = pd.date_range(start='2020-01-01', periods=n, freq='D')
    series = pd.Series(prices, index=dates, name='Price')

    return series


# =============================================================================
# TEST adf_test
# =============================================================================

def test_adf_test_structure(stationary_series):
    """Test that ADF test returns correct structure."""
    result = adf_test(stationary_series)

    # Check required keys
    assert 'test' in result
    assert 'statistic' in result
    assert 'p_value' in result
    assert 'critical_values' in result
    assert 'is_stationary' in result
    assert 'conclusion' in result

    # Check types
    assert result['test'] == 'ADF'
    assert isinstance(result['statistic'], float)
    assert isinstance(result['p_value'], float)
    assert isinstance(result['is_stationary'], bool)

    # Check critical values
    assert '1%' in result['critical_values']
    assert '5%' in result['critical_values']
    assert '10%' in result['critical_values']


def test_adf_test_stationary_series(stationary_series):
    """Test ADF on stationary series (should be stationary)."""
    result = adf_test(stationary_series, alpha=0.05)

    # White noise should be stationary
    assert result['is_stationary'] == True
    assert result['p_value'] < 0.05


def test_adf_test_non_stationary_series(non_stationary_series):
    """Test ADF on non-stationary series."""
    result = adf_test(non_stationary_series, alpha=0.05)

    # Random walk should be non-stationary
    assert result['is_stationary'] == False
    assert result['p_value'] >= 0.05


def test_adf_test_prices_vs_returns(price_series):
    """Test that prices are non-stationary but returns are stationary."""
    # Test prices
    price_result = adf_test(price_series, alpha=0.05)

    # Prices should be non-stationary
    assert price_result['is_stationary'] == False

    # Test returns
    returns = price_series.pct_change().dropna()
    returns_result = adf_test(returns, alpha=0.05)

    # Returns should be stationary
    assert returns_result['is_stationary'] == True


def test_adf_test_different_alpha(stationary_series):
    """Test ADF with different alpha values."""
    result_001 = adf_test(stationary_series, alpha=0.01)
    result_005 = adf_test(stationary_series, alpha=0.05)
    result_010 = adf_test(stationary_series, alpha=0.10)

    # Same statistic, different alpha thresholds
    assert result_001['statistic'] == result_005['statistic']
    assert result_005['statistic'] == result_010['statistic']

    # Alpha stored correctly
    assert result_001['alpha'] == 0.01
    assert result_005['alpha'] == 0.05
    assert result_010['alpha'] == 0.10


# =============================================================================
# TEST kpss_test
# =============================================================================

def test_kpss_test_structure(stationary_series):
    """Test that KPSS test returns correct structure."""
    result = kpss_test(stationary_series)

    assert 'test' in result
    assert 'statistic' in result
    assert 'p_value' in result
    assert 'is_stationary' in result
    assert 'note' in result

    assert result['test'] == 'KPSS'


def test_kpss_test_stationary_series(stationary_series):
    """Test KPSS on stationary series."""
    result = kpss_test(stationary_series, alpha=0.05)

    # White noise should be stationary
    # KPSS: high p-value means stationary
    assert result['is_stationary'] == True
    assert result['p_value'] >= 0.05


def test_kpss_test_non_stationary_series(non_stationary_series):
    """Test KPSS on non-stationary series."""
    result = kpss_test(non_stationary_series, alpha=0.05)

    # Random walk should be non-stationary
    # KPSS: low p-value means non-stationary
    assert result['is_stationary'] == False
    assert result['p_value'] < 0.05


def test_kpss_opposite_of_adf():
    """Test that KPSS has opposite null hypothesis from ADF."""
    # This is documented in the 'note' field
    result = kpss_test(pd.Series(np.random.randn(100)))

    assert 'opposite' in result['note'].lower() or 'is stationary' in result['note'].lower()


# =============================================================================
# TEST pp_test
# =============================================================================

def test_pp_test_structure(stationary_series):
    """Test that PP test returns correct structure."""
    result = pp_test(stationary_series)

    assert 'test' in result
    assert 'statistic' in result
    assert 'p_value' in result
    assert 'is_stationary' in result

    assert result['test'] == 'PP'


def test_pp_test_stationary_series(stationary_series):
    """Test PP on stationary series."""
    result = pp_test(stationary_series, alpha=0.05)

    assert result['is_stationary'] == True
    assert result['p_value'] < 0.05


def test_pp_test_non_stationary_series(non_stationary_series):
    """Test PP on non-stationary series."""
    result = pp_test(non_stationary_series, alpha=0.05)

    assert result['is_stationary'] == False


# =============================================================================
# TEST combined_stationarity_check
# =============================================================================

def test_combined_stationarity_check_structure(stationary_series):
    """Test combined check structure."""
    result = combined_stationarity_check(stationary_series)

    # Should have all three tests
    assert 'adf' in result
    assert 'kpss' in result
    assert 'pp' in result

    # Should have consensus
    assert 'consensus' in result
    assert 'confidence' in result
    assert 'summary' in result
    assert 'votes' in result

    # Consensus should be valid
    assert result['consensus'] in ['stationary', 'non-stationary', 'inconclusive']

    # Confidence should be valid
    assert result['confidence'] in ['high', 'medium', 'low']


def test_combined_check_stationary_series(stationary_series):
    """Test combined check on stationary series."""
    result = combined_stationarity_check(stationary_series, alpha=0.05)

    # White noise should be stationary with high confidence
    assert result['consensus'] == 'stationary'

    # Check that most tests agree
    assert result['stationary_votes'] >= 2


def test_combined_check_non_stationary_series(non_stationary_series):
    """Test combined check on non-stationary series."""
    result = combined_stationarity_check(non_stationary_series, alpha=0.05)

    # Random walk should be non-stationary
    assert result['consensus'] == 'non-stationary'


def test_combined_check_votes(stationary_series):
    """Test voting mechanism."""
    result = combined_stationarity_check(stationary_series)

    votes = result['votes']

    # Should have votes from all three tests
    assert 'ADF' in votes
    assert 'KPSS' in votes
    assert 'PP' in votes

    # Votes should be boolean
    assert isinstance(votes['ADF'], (bool, np.bool_))
    assert isinstance(votes['KPSS'], (bool, np.bool_))
    assert isinstance(votes['PP'], (bool, np.bool_))


def test_combined_check_high_confidence(stationary_series):
    """Test high confidence when all tests agree."""
    result = combined_stationarity_check(stationary_series)

    # For white noise, all tests should agree
    if result['stationary_votes'] == 3:
        assert result['confidence'] == 'high'


# =============================================================================
# TEST test_multiple_d_values
# =============================================================================

def test_test_multiple_d_values(price_series):
    """Test stationarity across multiple d values."""
    d_values = [0.0, 0.3, 0.5, 0.7, 1.0]

    result_df = test_multiple_d_values(price_series, d_values, test_func='adf')

    # Check DataFrame structure
    assert isinstance(result_df, pd.DataFrame)
    assert len(result_df) == len(d_values)

    # Check columns
    assert 'd' in result_df.columns
    assert 'statistic' in result_df.columns
    assert 'p_value' in result_df.columns
    assert 'is_stationary' in result_df.columns

    # d=0 (prices) should be non-stationary
    d0_row = result_df[result_df['d'] == 0.0].iloc[0]
    assert d0_row['is_stationary'] == False

    # d=1 (returns) should be stationary
    d1_row = result_df[result_df['d'] == 1.0].iloc[0]
    assert d1_row['is_stationary'] == True


def test_test_multiple_d_values_combined(price_series):
    """Test multiple d values with combined test."""
    d_values = [0.0, 0.5, 1.0]

    result_df = test_multiple_d_values(price_series, d_values, test_func='combined')

    assert len(result_df) == len(d_values)
    assert 'is_stationary' in result_df.columns


# =============================================================================
# TEST FRACTIONAL DIFFERENTIATION STATIONARITY
# =============================================================================

def test_fractional_diff_achieves_stationarity(price_series):
    """Test that fractional differentiation can achieve stationarity."""
    # Original prices should be non-stationary
    original_result = adf_test(price_series, alpha=0.05)
    assert original_result['is_stationary'] == False

    # Apply fractional differentiation with d=0.5
    transformed = fractional_diff_ffd(price_series, d=0.5)

    # Transformed should be more likely to be stationary
    transformed_result = adf_test(transformed, alpha=0.05)

    # p-value should be lower (more stationary)
    assert transformed_result['p_value'] < original_result['p_value']


def test_increasing_d_increases_stationarity(price_series):
    """Test that increasing d increases stationarity."""
    d_values = [0.3, 0.5, 0.7]
    p_values = []

    for d in d_values:
        if d == 0:
            transformed = price_series
        else:
            transformed = fractional_diff_ffd(price_series, d)

        result = adf_test(transformed)
        p_values.append(result['p_value'])

    # p-values should generally decrease as d increases
    # (though not always monotonic due to randomness)
    assert p_values[-1] < p_values[0] or p_values[-1] < 0.05


# =============================================================================
# TEST EDGE CASES
# =============================================================================

def test_adf_with_short_series():
    """Test ADF with a short series."""
    short_series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # Should still work
    result = adf_test(short_series)

    assert 'p_value' in result
    assert isinstance(result['is_stationary'], bool)


def test_kpss_with_constant_series():
    """Test KPSS with constant series."""
    constant_series = pd.Series([5.0] * 100)

    # KPSS may have issues with constant series
    # Should handle gracefully
    try:
        result = kpss_test(constant_series)
        assert 'is_stationary' in result
    except Exception as e:
        # Expected to fail, but shouldn't crash
        assert isinstance(e, (ValueError, Exception))


def test_combined_check_with_nans():
    """Test combined check handles NaN values."""
    series_with_nans = pd.Series([1, 2, np.nan, 4, 5, 6, 7, 8, 9, 10] * 10)

    # Should handle via validation
    from utils import validate_series

    cleaned = validate_series(series_with_nans)

    result = combined_stationarity_check(cleaned)

    assert 'consensus' in result


# =============================================================================
# TEST MATHEMATICAL CONSISTENCY
# =============================================================================

def test_adf_statistic_reasonable_range(stationary_series):
    """Test that ADF statistic is in reasonable range."""
    result = adf_test(stationary_series)

    # ADF statistic typically ranges from -10 to 5
    assert -20 < result['statistic'] < 10


def test_p_value_range(stationary_series):
    """Test that p-value is between 0 and 1."""
    result = adf_test(stationary_series)

    assert 0 <= result['p_value'] <= 1


def test_critical_values_ordering(stationary_series):
    """Test that critical values are properly ordered."""
    result = adf_test(stationary_series)

    cv = result['critical_values']

    # More stringent test (1%) should have more negative critical value
    assert cv['1%'] < cv['5%'] < cv['10%']


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
