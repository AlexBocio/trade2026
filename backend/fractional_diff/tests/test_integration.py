# test_integration.py - Integration tests for Flask API

import pytest
import json
import numpy as np
import pandas as pd

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def app():
    """Create Flask app for testing."""
    flask_app.config['TESTING'] = True
    return flask_app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_values():
    """Sample price values for testing."""
    np.random.seed(42)
    n = 200
    returns = np.random.normal(0.0005, 0.02, n)
    prices = 100 * np.exp(np.cumsum(returns))
    return prices.tolist()


# =============================================================================
# TEST /health
# =============================================================================

def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get('/health')

    assert response.status_code == 200

    data = json.loads(response.data)

    assert data['status'] == 'healthy'
    assert data['service'] == 'fractional-diff-engine'
    assert data['port'] == 5006


# =============================================================================
# TEST /api/fracdiff/transform
# =============================================================================

def test_transform_with_values(client, sample_values):
    """Test transform endpoint with raw values."""
    payload = {
        'values': sample_values,
        'd': 0.5,
        'method': 'ffd'
    }

    response = client.post(
        '/api/fracdiff/transform',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200

    data = json.loads(response.data)

    assert data['success'] == True
    assert 'original' in data
    assert 'transformed' in data
    assert 'stationarity' in data
    assert 'memory' in data
    assert 'config' in data

    # Check original data
    assert 'data' in data['original']
    assert 'statistics' in data['original']
    assert len(data['original']['data']['values']) == len(sample_values)

    # Check transformed data
    assert 'data' in data['transformed']
    assert len(data['transformed']['data']['values']) > 0
    assert len(data['transformed']['data']['values']) < len(sample_values)

    # Check stationarity
    assert 'consensus' in data['stationarity']
    assert data['stationarity']['consensus'] in ['stationary', 'non-stationary', 'inconclusive']

    # Check memory
    assert 'retention_score' in data['memory']
    assert 0 <= data['memory']['retention_score'] <= 1

    # Check config
    assert data['config']['d'] == 0.5
    assert data['config']['method'] == 'ffd'


def test_transform_with_different_d_values(client, sample_values):
    """Test transform with different d values."""
    d_values = [0.3, 0.5, 0.7]

    for d in d_values:
        payload = {
            'values': sample_values,
            'd': d,
            'method': 'ffd'
        }

        response = client.post(
            '/api/fracdiff/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] == True
        assert data['config']['d'] == d


def test_transform_with_standard_method(client, sample_values):
    """Test transform with standard method."""
    payload = {
        'values': sample_values,
        'd': 0.5,
        'method': 'standard'
    }

    response = client.post(
        '/api/fracdiff/transform',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['success'] == True
    assert data['config']['method'] == 'standard'


def test_transform_with_invalid_method(client, sample_values):
    """Test transform with invalid method."""
    payload = {
        'values': sample_values,
        'd': 0.5,
        'method': 'invalid_method'
    }

    response = client.post(
        '/api/fracdiff/transform',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 400

    data = json.loads(response.data)
    assert data['success'] == False
    assert 'error' in data


def test_transform_without_data(client):
    """Test transform without providing data."""
    payload = {
        'd': 0.5
    }

    response = client.post(
        '/api/fracdiff/transform',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 400

    data = json.loads(response.data)
    assert data['success'] == False


def test_transform_with_invalid_d(client, sample_values):
    """Test transform with invalid d value."""
    payload = {
        'values': sample_values,
        'd': 1.5  # Invalid: d must be between 0 and 1
    }

    response = client.post(
        '/api/fracdiff/transform',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 500  # Validation error

    data = json.loads(response.data)
    assert data['success'] == False


# =============================================================================
# TEST /api/fracdiff/find-optimal-d
# =============================================================================

def test_find_optimal_d(client, sample_values):
    """Test find optimal d endpoint."""
    payload = {
        'values': sample_values,
        'd_range': [0.0, 1.0],
        'step': 0.1,
        'method': 'adf'
    }

    response = client.post(
        '/api/fracdiff/find-optimal-d',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200

    data = json.loads(response.data)

    assert data['success'] == True
    assert 'optimal_d' in data
    assert 'memory_retained' in data
    assert 'stationarity_results' in data
    assert 'recommendation' in data
    assert 'visualization_data' in data

    # Optimal d should be in range
    assert 0.0 <= data['optimal_d'] <= 1.0

    # Memory retained should be between 0 and 1
    assert 0.0 <= data['memory_retained'] <= 1.0

    # Visualization data should have arrays
    viz = data['visualization_data']
    assert 'd_values' in viz
    assert 'is_stationary' in viz
    assert 'p_values' in viz
    assert 'memory_scores' in viz


def test_find_optimal_d_combined_method(client, sample_values):
    """Test find optimal d with combined method."""
    payload = {
        'values': sample_values,
        'd_range': [0.0, 1.0],
        'step': 0.2,
        'method': 'combined'
    }

    response = client.post(
        '/api/fracdiff/find-optimal-d',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['success'] == True
    assert data['method'] == 'combined'


# =============================================================================
# TEST /api/fracdiff/compare
# =============================================================================

def test_compare_endpoint(client, sample_values):
    """Test compare endpoint."""
    payload = {
        'values': sample_values,
        'd_values': [0.0, 0.3, 0.5, 0.7, 1.0]
    }

    response = client.post(
        '/api/fracdiff/compare',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200

    data = json.loads(response.data)

    assert data['success'] == True
    assert 'comparison' in data
    assert 'memory_comparison' in data
    assert 'summary' in data

    # Comparison should have 5 entries
    assert len(data['comparison']) == 5

    # Each entry should have required fields
    for entry in data['comparison']:
        assert 'd' in entry
        assert 'is_stationary' in entry
        assert 'adf_p_value' in entry

    # Summary should have counts
    summary = data['summary']
    assert 'total_tested' in summary
    assert 'stationary_count' in summary
    assert summary['total_tested'] == 5


def test_compare_with_default_d_values(client, sample_values):
    """Test compare with default d values."""
    payload = {
        'values': sample_values
    }

    response = client.post(
        '/api/fracdiff/compare',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['success'] == True


# =============================================================================
# TEST /api/fracdiff/batch
# =============================================================================

def test_batch_endpoint_with_values(client, sample_values):
    """Test batch endpoint (though it's designed for tickers)."""
    # Note: Batch is primarily for tickers with yfinance
    # We can test the structure even if data fetching might fail

    payload = {
        'tickers': ['SPY'],  # May fail if no internet
        'd': 0.5,
        'method': 'ffd'
    }

    response = client.post(
        '/api/fracdiff/batch',
        data=json.dumps(payload),
        content_type='application/json'
    )

    # Response should be 200 even if individual tickers fail
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['success'] == True
    assert 'results' in data
    assert 'summary' in data


def test_batch_without_tickers(client):
    """Test batch without tickers."""
    payload = {
        'd': 0.5
    }

    response = client.post(
        '/api/fracdiff/batch',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 400

    data = json.loads(response.data)
    assert data['success'] == False


# =============================================================================
# TEST /api/fracdiff/stationarity-test
# =============================================================================

def test_stationarity_test_endpoint(client, sample_values):
    """Test stationarity test endpoint."""
    payload = {
        'values': sample_values,
        'test': 'adf',
        'alpha': 0.05
    }

    response = client.post(
        '/api/fracdiff/stationarity-test',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200

    data = json.loads(response.data)

    assert data['success'] == True
    assert 'test_results' in data
    assert 'is_stationary' in data
    assert 'conclusion' in data

    # Test results should have ADF structure
    test_results = data['test_results']
    assert test_results['test'] == 'ADF'
    assert 'statistic' in test_results
    assert 'p_value' in test_results


def test_stationarity_test_kpss(client, sample_values):
    """Test stationarity with KPSS."""
    payload = {
        'values': sample_values,
        'test': 'kpss'
    }

    response = client.post(
        '/api/fracdiff/stationarity-test',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['test_results']['test'] == 'KPSS'


def test_stationarity_test_combined(client, sample_values):
    """Test stationarity with combined method."""
    payload = {
        'values': sample_values,
        'test': 'combined'
    }

    response = client.post(
        '/api/fracdiff/stationarity-test',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200

    data = json.loads(response.data)

    # Combined test should have all three tests
    test_results = data['test_results']
    assert 'adf' in test_results
    assert 'kpss' in test_results
    assert 'pp' in test_results
    assert 'consensus' in test_results


def test_stationarity_test_invalid_test(client, sample_values):
    """Test stationarity with invalid test name."""
    payload = {
        'values': sample_values,
        'test': 'invalid_test'
    }

    response = client.post(
        '/api/fracdiff/stationarity-test',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 400

    data = json.loads(response.data)
    assert data['success'] == False


# =============================================================================
# TEST ERROR HANDLING
# =============================================================================

def test_transform_with_no_json(client):
    """Test transform with no JSON data."""
    response = client.post('/api/fracdiff/transform')

    assert response.status_code == 400

    data = json.loads(response.data)
    assert data['success'] == False


def test_transform_with_empty_json(client):
    """Test transform with empty JSON."""
    response = client.post(
        '/api/fracdiff/transform',
        data=json.dumps({}),
        content_type='application/json'
    )

    assert response.status_code == 400


def test_invalid_endpoint(client):
    """Test invalid endpoint."""
    response = client.get('/api/fracdiff/invalid')

    assert response.status_code == 404


# =============================================================================
# TEST DATA SERIALIZATION
# =============================================================================

def test_transform_output_is_json_serializable(client, sample_values):
    """Test that all output is JSON serializable."""
    payload = {
        'values': sample_values,
        'd': 0.5
    }

    response = client.post(
        '/api/fracdiff/transform',
        data=json.dumps(payload),
        content_type='application/json'
    )

    # Should be able to load JSON
    data = json.loads(response.data)

    # Should be able to dump it again
    json_str = json.dumps(data)

    assert isinstance(json_str, str)


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
