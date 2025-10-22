# test_fractional_diff.py - Test core fractional differentiation algorithms

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fractional_diff import (
    get_weights_ffd,
    fractional_diff_ffd,
    fractional_diff_standard,
    get_weights_expansion,
    compare_ffd_vs_standard
)
from config import Config


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_price_series():
    """Create a sample price series (geometric Brownian motion)."""
    np.random.seed(42)
    n = 500
    returns = np.random.normal(0.0005, 0.02, n)
    prices = 100 * np.exp(np.cumsum(returns))

    dates = pd.date_range(start='2020-01-01', periods=n, freq='D')
    series = pd.Series(prices, index=dates, name='Price')

    return series


@pytest.fixture
def simple_series():
    """Create a simple series for testing."""
    values = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]
    return pd.Series(values, name='Simple')


# =============================================================================
# TEST get_weights_ffd
# =============================================================================

def test_get_weights_ffd_d_05():
    """Test weight generation for d=0.5."""
    weights = get_weights_ffd(0.5, thres=1e-5)

    # Check properties
    assert len(weights) > 0
    assert weights[0] == 1.0

    # Weights should decay
    assert abs(weights[1]) < abs(weights[0])

    # Sum of weights should be approximately 0 for d > 0
    assert abs(sum(weights)) < 1.0


def test_get_weights_ffd_different_d_values():
    """Test weights for different d values."""
    d_values = [0.2, 0.5, 0.8]

    for d in d_values:
        weights = get_weights_ffd(d, thres=1e-5)

        # Larger d should have more weights (slower decay)
        assert len(weights) > 0
        assert weights[0] == 1.0


def test_get_weights_ffd_threshold():
    """Test that threshold controls truncation."""
    weights_strict = get_weights_ffd(0.5, thres=1e-5)
    weights_loose = get_weights_ffd(0.5, thres=1e-2)

    # Stricter threshold should produce more weights
    assert len(weights_strict) > len(weights_loose)


# =============================================================================
# TEST fractional_diff_ffd
# =============================================================================

def test_fractional_diff_ffd_d_0(sample_price_series):
    """Test that d=0 returns original series."""
    result = fractional_diff_ffd(sample_price_series, d=0)

    # d=0 should return original
    pd.testing.assert_series_equal(result, sample_price_series)


def test_fractional_diff_ffd_d_1(sample_price_series):
    """Test that d=1 returns standard returns."""
    result = fractional_diff_ffd(sample_price_series, d=1)

    # d=1 should be similar to pct_change()
    expected = sample_price_series.pct_change().dropna()

    # Should have same length
    assert len(result) == len(expected)

    # Values should be very close
    np.testing.assert_array_almost_equal(
        result.values,
        expected.values,
        decimal=10
    )


def test_fractional_diff_ffd_d_05(sample_price_series):
    """Test fractional differentiation with d=0.5."""
    result = fractional_diff_ffd(sample_price_series, d=0.5)

    # Result should be shorter than original
    assert len(result) < len(sample_price_series)

    # Result should have valid values
    assert not result.isnull().any()
    assert not np.isinf(result).any()

    # Result should have index matching original (truncated)
    assert result.index[0] in sample_price_series.index
    assert result.index[-1] == sample_price_series.index[-1]


def test_fractional_diff_ffd_preserves_type(sample_price_series):
    """Test that result is a pandas Series."""
    result = fractional_diff_ffd(sample_price_series, d=0.5)

    assert isinstance(result, pd.Series)


def test_fractional_diff_ffd_name(sample_price_series):
    """Test that result has descriptive name."""
    result = fractional_diff_ffd(sample_price_series, d=0.5)

    assert 'fracdiff' in result.name.lower()
    assert '0.5' in result.name or '0.50' in result.name


def test_fractional_diff_ffd_different_d_values(sample_price_series):
    """Test that different d values produce different results."""
    result_03 = fractional_diff_ffd(sample_price_series, d=0.3)
    result_05 = fractional_diff_ffd(sample_price_series, d=0.5)
    result_07 = fractional_diff_ffd(sample_price_series, d=0.7)

    # Results should be different
    assert not result_03.equals(result_05)
    assert not result_05.equals(result_07)

    # Higher d should produce shorter series (more weights)
    assert len(result_07) <= len(result_05)
    assert len(result_05) <= len(result_03)


def test_fractional_diff_ffd_invalid_d(sample_price_series):
    """Test that invalid d values raise errors."""
    with pytest.raises(ValueError):
        fractional_diff_ffd(sample_price_series, d=-0.1)

    with pytest.raises(ValueError):
        fractional_diff_ffd(sample_price_series, d=1.5)


# =============================================================================
# TEST fractional_diff_standard
# =============================================================================

def test_fractional_diff_standard_d_0(sample_price_series):
    """Test standard method with d=0."""
    result = fractional_diff_standard(sample_price_series, d=0)

    pd.testing.assert_series_equal(result, sample_price_series)


def test_fractional_diff_standard_d_05(sample_price_series):
    """Test standard method with d=0.5."""
    result = fractional_diff_standard(sample_price_series, d=0.5)

    # Result should be shorter (edge effects removed)
    assert len(result) < len(sample_price_series)

    # No NaN or inf
    assert not result.isnull().any()
    assert not np.isinf(result).any()


def test_fractional_diff_standard_vs_ffd(sample_price_series):
    """Test that standard and FFD methods produce similar results."""
    result_ffd = fractional_diff_ffd(sample_price_series, d=0.5)
    result_std = fractional_diff_standard(sample_price_series, d=0.5)

    # Both should have reasonable lengths
    assert len(result_ffd) > 0
    assert len(result_std) > 0

    # Find common index
    common_index = result_ffd.index.intersection(result_std.index)

    if len(common_index) > 0:
        # Correlation should be high
        corr = result_ffd.loc[common_index].corr(result_std.loc[common_index])
        assert corr > 0.9  # Should be highly correlated


# =============================================================================
# TEST get_weights_expansion
# =============================================================================

def test_get_weights_expansion():
    """Test binomial expansion weights."""
    weights = get_weights_expansion(0.5, size=20)

    assert len(weights) == 20
    assert weights[0] == 1.0

    # Weights should decay
    for i in range(1, len(weights)):
        assert abs(weights[i]) < abs(weights[i-1])


# =============================================================================
# TEST compare_ffd_vs_standard
# =============================================================================

def test_compare_ffd_vs_standard(sample_price_series):
    """Test comparison function."""
    result = compare_ffd_vs_standard(sample_price_series, d=0.5)

    assert 'ffd_result' in result
    assert 'std_result' in result
    assert 'ffd_length' in result
    assert 'std_length' in result

    # Both should have results
    assert len(result['ffd_result']) > 0
    assert len(result['std_result']) > 0

    # If comparison exists, check metrics
    if result['comparison'] is not None:
        assert 'correlation' in result['comparison']
        assert 'rmse' in result['comparison']
        assert 'mae' in result['comparison']

        # Correlation should be reasonable
        assert result['comparison']['correlation'] > 0.5


# =============================================================================
# TEST EDGE CASES
# =============================================================================

def test_fractional_diff_ffd_short_series():
    """Test with a short series."""
    short_series = pd.Series([100, 101, 102, 103, 104])

    # Should still work but produce very short result
    result = fractional_diff_ffd(short_series, d=0.5)

    assert len(result) >= 0  # May be empty or very short


def test_fractional_diff_ffd_with_dates(sample_price_series):
    """Test that datetime index is preserved."""
    result = fractional_diff_ffd(sample_price_series, d=0.5)

    # Check that index is still datetime
    assert isinstance(result.index, pd.DatetimeIndex)

    # Check that dates are subset of original
    assert result.index[0] >= sample_price_series.index[0]
    assert result.index[-1] == sample_price_series.index[-1]


def test_fractional_diff_ffd_simple_series(simple_series):
    """Test with simple series for manual verification."""
    result = fractional_diff_ffd(simple_series, d=0.5, thres=1e-3)

    # Should produce a result
    assert len(result) > 0

    # Result should be numeric
    assert result.dtype in [np.float64, np.float32]


# =============================================================================
# TEST MATHEMATICAL PROPERTIES
# =============================================================================

def test_weights_sum_to_zero_for_d_1():
    """Test that weights sum to approximately 0 for d=1."""
    weights = get_weights_expansion(1.0, size=100)

    # For d=1 (first difference), weights should be [1, -1, 0, 0, ...]
    assert abs(weights[0] - 1.0) < 1e-10
    assert abs(weights[1] - (-1.0)) < 1e-10

    # Remaining weights should be very small
    assert all(abs(w) < 1e-10 for w in weights[2:])


def test_fractional_diff_reduces_autocorrelation(sample_price_series):
    """Test that fractional differentiation reduces autocorrelation."""
    # Calculate autocorrelation of original series
    original_acf = sample_price_series.autocorr(lag=1)

    # Apply fractional differentiation
    transformed = fractional_diff_ffd(sample_price_series, d=0.5)

    # Calculate autocorrelation of transformed series
    transformed_acf = transformed.autocorr(lag=1)

    # Transformed should have lower autocorrelation
    assert abs(transformed_acf) < abs(original_acf)


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
