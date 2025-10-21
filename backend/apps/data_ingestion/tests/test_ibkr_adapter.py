"""
Component Tests for IBKR Adapter
Tests adapter logic with MOCKED dependencies (no real IBKR connection)

Test Strategy:
1. Mock IB connection
2. Mock QuestDB and Valkey
3. Test subscription logic
4. Test data processing
5. Test error handling
6. Test reconnection logic
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from adapters.ibkr_adapter import (
    IBKRAdapter,
    IBKRConfig,
    StoreConfig,
    create_ibkr_adapter
)


@pytest.fixture
def ibkr_config():
    """Test IBKR configuration"""
    return IBKRConfig(
        host="127.0.0.1",
        port=7497,
        client_id=999,
        reconnect_delay_seconds=1,
        max_reconnect_attempts=3
    )


@pytest.fixture
def store_config():
    """Test store configuration"""
    return StoreConfig(
        questdb_ilp_host="localhost",
        questdb_ilp_port=9009,
        valkey_host="localhost",
        valkey_port=6379,
        valkey_ttl_seconds=60
    )


@pytest.fixture
def test_symbols():
    """Test symbol list"""
    return ["SPY", "QQQ", "AAPL"]


@pytest.fixture
def adapter(ibkr_config, store_config, test_symbols):
    """Create test adapter instance"""
    return IBKRAdapter(ibkr_config, store_config, test_symbols)


# --- Connection Tests ---

@pytest.mark.asyncio
async def test_adapter_initialization(adapter, test_symbols):
    """Test adapter initializes with correct configuration"""
    assert adapter.symbols == test_symbols
    assert adapter.connected is False
    assert adapter.ib is None
    assert adapter.valkey_client is None
    assert adapter.questdb_sender is None


@pytest.mark.asyncio
@patch('adapters.ibkr_adapter.IB')
@patch('adapters.ibkr_adapter.redis.Redis')
@patch('adapters.ibkr_adapter.Sender')
async def test_connect_success(mock_sender, mock_redis, mock_ib, adapter):
    """Test successful connection to IBKR and data stores"""
    # Mock IB connection
    mock_ib_instance = AsyncMock()
    mock_ib_instance.isConnected.return_value = True
    mock_ib.return_value = mock_ib_instance

    # Mock Valkey connection
    mock_valkey_instance = AsyncMock()
    mock_valkey_instance.ping = AsyncMock()
    mock_redis.return_value = mock_valkey_instance

    # Mock QuestDB sender
    mock_sender_instance = MagicMock()
    mock_sender.return_value = mock_sender_instance

    await adapter.start()

    assert adapter.connected is True
    assert adapter.ib is not None
    assert adapter.valkey_client is not None
    assert adapter.questdb_sender is not None


@pytest.mark.asyncio
@patch('adapters.ibkr_adapter.IB')
async def test_connect_retry_on_failure(mock_ib, adapter):
    """Test exponential backoff retry on connection failure"""
    # Mock IB to fail first 2 times, succeed on 3rd
    mock_ib_instance = AsyncMock()
    mock_ib_instance.connectAsync.side_effect = [
        Exception("Connection failed"),
        Exception("Connection failed"),
        None  # Success on 3rd attempt
    ]
    mock_ib_instance.isConnected.side_effect = [False, False, True]
    mock_ib.return_value = mock_ib_instance

    # Mock data stores to succeed
    with patch('adapters.ibkr_adapter.redis.Redis') as mock_redis:
        mock_valkey = AsyncMock()
        mock_valkey.ping = AsyncMock()
        mock_redis.return_value = mock_valkey

        with patch('adapters.ibkr_adapter.Sender') as mock_sender:
            await adapter._connect_ibkr()

            # Should have retried and eventually succeeded
            assert mock_ib_instance.connectAsync.call_count == 3
            assert adapter.reconnect_attempts == 0  # Reset after success


@pytest.mark.asyncio
@patch('adapters.ibkr_adapter.IB')
async def test_connect_max_retries_exceeded(mock_ib, adapter):
    """Test that adapter gives up after max retries"""
    # Mock IB to always fail
    mock_ib_instance = AsyncMock()
    mock_ib_instance.connectAsync.side_effect = Exception("Connection failed")
    mock_ib_instance.isConnected.return_value = False
    mock_ib.return_value = mock_ib_instance

    await adapter._connect_ibkr()

    # Should have tried max_reconnect_attempts times
    assert mock_ib_instance.connectAsync.call_count == adapter.ibkr_config.max_reconnect_attempts
    assert adapter.connected is False


# --- Subscription Tests ---

@pytest.mark.asyncio
@patch('adapters.ibkr_adapter.Stock')
async def test_subscribe_symbol(mock_stock, adapter):
    """Test subscribing to market data for a symbol"""
    # Mock IB connection
    adapter.ib = MagicMock()
    adapter.ib.isConnected.return_value = True
    adapter.connected = True

    # Mock ticker
    mock_ticker = MagicMock()
    mock_ticker.updateEvent = MagicMock()
    adapter.ib.reqMktData.return_value = mock_ticker

    await adapter._subscribe_symbol("SPY")

    # Verify subscription created
    assert "SPY" in adapter.subscriptions
    assert adapter.ib.reqMktData.called
    assert adapter.ib.reqMktDepth.called


@pytest.mark.asyncio
async def test_subscribe_all_symbols(adapter, test_symbols):
    """Test subscribing to all configured symbols"""
    adapter.ib = MagicMock()
    adapter.ib.isConnected.return_value = True
    adapter.connected = True

    with patch.object(adapter, '_subscribe_symbol', new_callable=AsyncMock) as mock_sub:
        await adapter._subscribe_all()

        # Verify all symbols subscribed
        assert mock_sub.call_count == len(test_symbols)


@pytest.mark.asyncio
async def test_subscribe_with_partial_failure(adapter):
    """Test that subscription continues even if one symbol fails"""
    adapter.ib = MagicMock()
    adapter.ib.isConnected.return_value = True
    adapter.connected = True

    call_count = 0

    async def mock_subscribe(symbol):
        nonlocal call_count
        call_count += 1
        if symbol == "QQQ":
            raise Exception("Failed to subscribe to QQQ")

    with patch.object(adapter, '_subscribe_symbol', new=mock_subscribe):
        await adapter._subscribe_all()

        # Should have attempted all symbols despite one failure
        assert call_count == len(adapter.symbols)


# --- Data Processing Tests ---

@pytest.mark.asyncio
async def test_level1_data_processing(adapter):
    """Test Level 1 data processing"""
    # Mock ticker with sample data
    mock_ticker = MagicMock()
    mock_ticker.last = 450.50
    mock_ticker.bid = 450.45
    mock_ticker.ask = 450.55
    mock_ticker.bidSize = 100
    mock_ticker.askSize = 200
    mock_ticker.volume = 1000000
    mock_ticker.high = 452.00
    mock_ticker.low = 449.00
    mock_ticker.close = 450.00

    # Mock data stores
    adapter.questdb_sender = MagicMock()
    adapter.questdb_sender.row = MagicMock()
    adapter.questdb_sender.flush = MagicMock()

    adapter.valkey_client = AsyncMock()
    adapter.valkey_client.setex = AsyncMock()

    await adapter._on_level1_update("SPY", mock_ticker)

    # Verify data written to both stores
    assert adapter.questdb_sender.row.called
    assert adapter.questdb_sender.flush.called
    assert adapter.valkey_client.setex.called


@pytest.mark.asyncio
async def test_level1_handles_invalid_data(adapter):
    """Test that adapter handles invalid/missing price data gracefully"""
    # Mock ticker with no price
    mock_ticker = MagicMock()
    mock_ticker.last = None

    adapter.questdb_sender = MagicMock()
    adapter.valkey_client = AsyncMock()

    # Should not crash
    await adapter._on_level1_update("SPY", mock_ticker)

    # Should not write invalid data
    assert not adapter.questdb_sender.row.called


@pytest.mark.asyncio
async def test_questdb_write_error_handled(adapter):
    """Test that QuestDB write errors don't crash adapter"""
    mock_ticker = MagicMock()
    mock_ticker.last = 450.50

    # Mock QuestDB to fail
    adapter.questdb_sender = MagicMock()
    adapter.questdb_sender.row.side_effect = Exception("QuestDB write failed")

    adapter.valkey_client = AsyncMock()
    adapter.valkey_client.setex = AsyncMock()

    # Should not crash, should log error
    await adapter._on_level1_update("SPY", mock_ticker)

    # Valkey should still be called (fault isolation)
    assert adapter.valkey_client.setex.called


# --- Health Check Tests ---

def test_is_healthy_when_connected(adapter):
    """Test health check returns True when fully connected"""
    adapter.connected = True
    adapter.ib = MagicMock()
    adapter.ib.isConnected.return_value = True
    adapter.valkey_client = MagicMock()
    adapter.questdb_sender = MagicMock()

    assert adapter.is_healthy() is True


def test_is_healthy_when_disconnected(adapter):
    """Test health check returns False when disconnected"""
    adapter.connected = False
    adapter.ib = None

    assert adapter.is_healthy() is False


def test_get_status(adapter):
    """Test status report"""
    adapter.connected = True
    adapter.ib = MagicMock()
    adapter.ib.isConnected.return_value = True
    adapter.subscriptions = {"SPY": {}, "QQQ": {}}
    adapter.reconnect_attempts = 0

    status = adapter.get_status()

    assert status["connected"] is True
    assert status["ibkr_connected"] is True
    assert status["subscriptions"] == 2
    assert status["reconnect_attempts"] == 0


# --- Factory Function Tests ---

def test_factory_function(ibkr_config, store_config, test_symbols):
    """Test factory function creates adapter correctly"""
    ibkr_dict = {
        "host": ibkr_config.host,
        "port": ibkr_config.port,
        "client_id": ibkr_config.client_id
    }

    store_dict = {
        "questdb_ilp_host": store_config.questdb_ilp_host,
        "questdb_ilp_port": store_config.questdb_ilp_port,
        "valkey_host": store_config.valkey_host,
        "valkey_port": store_config.valkey_port
    }

    adapter = create_ibkr_adapter(ibkr_dict, store_dict, test_symbols)

    assert adapter.ibkr_config.host == ibkr_config.host
    assert adapter.ibkr_config.port == ibkr_config.port
    assert adapter.symbols == test_symbols


# --- Graceful Shutdown Tests ---

@pytest.mark.asyncio
async def test_stop_adapter(adapter):
    """Test adapter stops gracefully"""
    # Setup connected state
    adapter.connected = True
    adapter.ib = MagicMock()
    adapter.ib.isConnected.return_value = True
    adapter.ib.disconnect = MagicMock()

    adapter.valkey_client = AsyncMock()
    adapter.valkey_client.close = AsyncMock()

    adapter.questdb_sender = MagicMock()
    adapter.questdb_sender.close = MagicMock()

    adapter.subscriptions = {"SPY": {"contract": MagicMock()}}

    with patch.object(adapter, '_unsubscribe_all', new_callable=AsyncMock):
        await adapter.stop()

        # Verify cleanup
        assert adapter.ib.disconnect.called
        assert adapter.valkey_client.close.called
        assert adapter.questdb_sender.close.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
