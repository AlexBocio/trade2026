# test_integration.py - Integration tests for Flask API

import pytest
import sys
sys.path.insert(0, '..')

from app import app


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200

    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['port'] == 5005


def test_bootstrap_endpoint(client):
    """Test bootstrap simulation endpoint."""
    request_data = {
        'ticker': 'SPY',
        'method': 'standard',
        'n_simulations': 100
    }

    response = client.post('/api/simulation/bootstrap', json=request_data)
    assert response.status_code == 200

    data = response.get_json()
    assert data['ticker'] == 'SPY'
    assert data['method'] == 'standard'
    assert 'statistics' in data


def test_stress_test_endpoint(client):
    """Test stress test endpoint."""
    request_data = {
        'portfolio': {'SPY': 0.6, 'TLT': 0.4},
        'shocks': {'SPY': -0.20, 'TLT': 0.10}
    }

    response = client.post('/api/simulation/stress-test', json=request_data)
    assert response.status_code == 200

    data = response.get_json()
    assert 'total_impact' in data
    assert 'asset_impacts' in data


def test_comprehensive_endpoint(client):
    """Test comprehensive simulation endpoint."""
    request_data = {
        'ticker': 'SPY',
        'include_bootstrap': True,
        'include_monte_carlo': True,
        'include_scenario': False,
        'n_simulations': 100
    }

    response = client.post('/api/simulation/comprehensive', json=request_data)
    assert response.status_code == 200

    data = response.get_json()
    assert 'bootstrap' in data
    assert 'monte_carlo' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
