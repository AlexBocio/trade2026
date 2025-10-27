"""
IBKR Data Adapter - Phase 6 Week 1 Day 1-2
Streams Level 1, Level 2, and Time & Sales data from Interactive Brokers

Component Isolation:
- ONLY talks to IBKR API
- ONLY writes to QuestDB (via ILP) and Valkey (cache)
- NO dependencies on other services
- Self-contained error handling
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

try:
    from ib_insync import IB, Stock, Ticker
except ImportError:
    # For testing without ib_insync installed
    IB = None
    Stock = None
    Ticker = None

import redis.asyncio as redis
import httpx


@dataclass
class IBKRConfig:
    """IBKR connection configuration"""
    host: str
    port: int
    client_id: int
    reconnect_delay_seconds: int = 5
    max_reconnect_attempts: int = 5


@dataclass
class StoreConfig:
    """Data store configuration"""
    questdb_http_host: str
    questdb_http_port: int
    valkey_host: str
    valkey_port: int
    valkey_ttl_seconds: int = 300


class IBKRAdapter:
    """
    IBKR Data Adapter with component isolation and fault tolerance

    Responsibilities:
    1. Connect to IBKR TWS/Gateway
    2. Subscribe to Level 1, Level 2, Time & Sales
    3. Write to QuestDB (persistent) and Valkey (cache)
    4. Handle reconnection with exponential backoff
    5. Log all errors without crashing
    """

    def __init__(
        self,
        ibkr_config: IBKRConfig,
        store_config: StoreConfig,
        symbols: List[str],
        logger: Optional[logging.Logger] = None
    ):
        self.ibkr_config = ibkr_config
        self.store_config = store_config
        self.symbols = symbols
        self.logger = logger or logging.getLogger(__name__)

        # IBKR connection
        self.ib: Optional[IB] = None
        self.connected = False
        self.reconnect_attempts = 0

        # Data stores
        self.valkey_client: Optional[redis.Redis] = None
        self.questdb_client: Optional[httpx.AsyncClient] = None
        self.questdb_url: str = f"http://{store_config.questdb_http_host}:{store_config.questdb_http_port}/write"

        # Subscriptions tracking
        self.subscriptions: Dict[str, object] = {}
        self.failed_subscriptions: List[str] = []  # Track symbols that failed to subscribe (Error 101)

    async def start(self):
        """Start the adapter (connect to IBKR and data stores)"""
        self.logger.info("Starting IBKR Adapter...")

        # Connect to data stores
        await self._connect_valkey()
        self._connect_questdb()

        # Connect to IBKR
        await self._connect_ibkr()

        # Subscribe to market data
        await self._subscribe_all()

        self.logger.info("IBKR Adapter started successfully")

    async def stop(self):
        """Stop the adapter gracefully"""
        self.logger.info("Stopping IBKR Adapter...")

        # Unsubscribe from market data
        await self._unsubscribe_all()

        # Disconnect from IBKR
        if self.ib and self.ib.isConnected():
            self.ib.disconnect()
            self.logger.info("Disconnected from IBKR")

        # Close data store connections
        if self.valkey_client:
            await self.valkey_client.close()
            self.logger.info("Closed Valkey connection")

        if self.questdb_client:
            await self.questdb_client.aclose()
            self.logger.info("Closed QuestDB connection")

        self.logger.info("IBKR Adapter stopped")

    # --- Connection Management ---

    async def _connect_ibkr(self):
        """Connect to IBKR with exponential backoff retry"""
        if IB is None:
            self.logger.error("ib_insync not installed, cannot connect to IBKR")
            return

        while self.reconnect_attempts < self.ibkr_config.max_reconnect_attempts:
            try:
                self.ib = IB()
                await self.ib.connectAsync(
                    host=self.ibkr_config.host,
                    port=self.ibkr_config.port,
                    clientId=self.ibkr_config.client_id,
                    timeout=20
                )

                if self.ib.isConnected():
                    self.connected = True
                    self.reconnect_attempts = 0
                    self.logger.info(
                        f"Connected to IBKR at {self.ibkr_config.host}:{self.ibkr_config.port}"
                    )

                    # Set market data type (1=live, 2=frozen, 3=delayed, 4=delayed frozen)
                    self.ib.reqMarketDataType(3)  # Use delayed market data

                    # Set up error handler to track subscription failures (Error 101)
                    self.ib.errorEvent += self._on_error
                    return

            except Exception as e:
                self.reconnect_attempts += 1
                delay = min(
                    self.ibkr_config.reconnect_delay_seconds * (2 ** self.reconnect_attempts),
                    60
                )
                self.logger.error(
                    f"Failed to connect to IBKR (attempt {self.reconnect_attempts}): {e}"
                )
                self.logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)

        self.logger.error("Max reconnection attempts reached, giving up")

    async def _connect_valkey(self):
        """Connect to Valkey (Redis)"""
        try:
            self.valkey_client = await redis.Redis(
                host=self.store_config.valkey_host,
                port=self.store_config.valkey_port,
                decode_responses=False
            )
            await self.valkey_client.ping()
            self.logger.info("Connected to Valkey")
        except Exception as e:
            self.logger.error(f"Failed to connect to Valkey: {e}")
            raise

    def _connect_questdb(self):
        """Connect to QuestDB via HTTP"""
        try:
            # Configure connection pool for high-frequency concurrent writes
            # 62 symbols * 2 (concurrent requests) = 124 connections needed
            limits = httpx.Limits(
                max_connections=200,
                max_keepalive_connections=100
            )
            self.questdb_client = httpx.AsyncClient(
                timeout=30.0,  # Increased timeout for high load
                limits=limits
            )
            self.logger.info(f"Connected to QuestDB HTTP: {self.questdb_url}")
        except Exception as e:
            self.logger.error(f"Failed to connect to QuestDB: {e}")
            raise

    # --- Market Data Subscriptions ---

    async def _subscribe_all(self):
        """Subscribe to market data for all symbols"""
        if not self.ib or not self.ib.isConnected():
            self.logger.error("Cannot subscribe: not connected to IBKR")
            return

        for symbol in self.symbols:
            try:
                await self._subscribe_symbol(symbol)
            except Exception as e:
                self.logger.error(f"Failed to subscribe to {symbol}: {e}")
                # Continue with other symbols (fault isolation)

        # Wait a moment for Error 101 messages to arrive
        await asyncio.sleep(2)

        # Log subscription summary
        total = len(self.symbols)
        successful = len(self.subscriptions)
        failed = len(self.failed_subscriptions)
        success_rate = (successful / total * 100) if total > 0 else 0

        self.logger.info("=" * 80)
        self.logger.info("IBKR SUBSCRIPTION SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"Total Requested: {total}")
        self.logger.info(f"Successful: {successful} ({success_rate:.1f}%)")
        self.logger.info(f"Failed (Error 101): {failed}")

        if failed > 0:
            self.logger.warning(f"Failed Symbols ({failed}): {', '.join(sorted(self.failed_subscriptions))}")
            self.logger.warning(f"Note: IBKR paper trading has ~100-123 symbol limit")
            self.logger.warning(f"See IBKR_SUBSCRIPTION_LIMIT_ANALYSIS.md for details")

        self.logger.info("=" * 80)

    async def _subscribe_symbol(self, symbol: str):
        """Subscribe to Level 1, Level 2, and Time & Sales for a symbol"""
        if Stock is None:
            self.logger.error("ib_insync not installed, cannot subscribe")
            return

        contract = Stock(symbol, "SMART", "USD")

        # Request Level 1 data (top of book)
        ticker = self.ib.reqMktData(
            contract,
            genericTickList="",
            snapshot=False,
            regulatorySnapshot=False
        )

        # Request Level 2 data (market depth, 10 levels)
        # DISABLED: ETFs don't support L2, and it requires paid subscriptions
        # self.ib.reqMktDepth(contract, numRows=10)

        # Set up callbacks
        ticker.updateEvent += lambda t: asyncio.create_task(self._on_level1_update(symbol, t))

        self.subscriptions[symbol] = {
            "ticker": ticker,
            "contract": contract
        }

        self.logger.info(f"Subscribed to {symbol} (Level 1 only - bid/ask/size)")

    async def _unsubscribe_all(self):
        """Unsubscribe from all market data"""
        if not self.ib or not self.ib.isConnected():
            return

        for symbol, subscription in self.subscriptions.items():
            try:
                self.ib.cancelMktData(subscription["contract"])
                self.ib.cancelMktDepth(subscription["contract"])
                self.logger.info(f"Unsubscribed from {symbol}")
            except Exception as e:
                self.logger.error(f"Failed to unsubscribe from {symbol}: {e}")

        self.subscriptions.clear()

    # --- Data Callbacks ---

    async def _on_level1_update(self, symbol: str, ticker: 'Ticker'):
        """Handle Level 1 (top of book) market data update"""
        try:
            if ticker.last is None or ticker.last == 0:
                return  # No valid price yet

            timestamp = int(time.time() * 1_000_000_000)  # nanoseconds

            # Write to QuestDB (persistent storage)
            await self._write_level1_questdb(symbol, ticker, timestamp)

            # Write to Valkey (hot cache)
            await self._write_level1_valkey(symbol, ticker, timestamp)

        except Exception as e:
            self.logger.error(f"Error processing Level 1 update for {symbol}: {e}")
            # Don't crash - component isolation

    async def _write_level1_questdb(self, symbol: str, ticker: 'Ticker', timestamp: int):
        """Write Level 1 data to QuestDB via HTTP"""
        if not self.questdb_client:
            self.logger.warning(f"QuestDB client not initialized, skipping write for {symbol}")
            return

        try:
            import math

            # Helper to safely convert to int, handling NaN
            def safe_int(value):
                if value is None or (isinstance(value, float) and math.isnan(value)):
                    return 0
                return int(value)

            # Helper to safely convert to float, handling NaN
            def safe_float(value):
                if value is None or (isinstance(value, float) and math.isnan(value)):
                    return 0.0
                return float(value)

            # Build ILP (InfluxDB Line Protocol) string
            # Format: table_name,tag1=value1,tag2=value2 field1=value1,field2=value2 timestamp_ns
            line = (
                f"market_data_l1,"
                f"symbol={symbol} "
                f"last={safe_float(ticker.last)},"
                f"bid={safe_float(ticker.bid)},"
                f"ask={safe_float(ticker.ask)},"
                f"bid_size={safe_int(ticker.bidSize)}i,"
                f"ask_size={safe_int(ticker.askSize)}i,"
                f"volume={safe_int(ticker.volume)}i,"
                f"high={safe_float(ticker.high)},"
                f"low={safe_float(ticker.low)},"
                f"close={safe_float(ticker.close)} "
                f"{timestamp}"
            )

            # Send via HTTP POST to /write endpoint
            response = await self.questdb_client.post(
                self.questdb_url,
                params={"fmt": "ilp"},
                content=line.encode('utf-8'),
                headers={"Content-Type": "text/plain"}
            )
            response.raise_for_status()

            self.logger.debug(f"Successfully wrote {symbol} to QuestDB")

        except httpx.HTTPStatusError as e:
            self.logger.error(f"QuestDB HTTP error for {symbol}: status={e.response.status_code}, body={e.response.text}")
        except Exception as e:
            self.logger.error(f"Failed to write {symbol} to QuestDB: {type(e).__name__}: {e}", exc_info=True)

    async def _write_level1_valkey(self, symbol: str, ticker: 'Ticker', timestamp: int):
        """Write Level 1 data to Valkey (hot cache)"""
        if not self.valkey_client:
            return

        try:
            import math
            import json

            # Helper to safely convert to int, handling NaN
            def safe_int(value):
                if value is None or (isinstance(value, float) and math.isnan(value)):
                    return 0
                return int(value)

            # Helper to safely convert to float, handling NaN
            def safe_float(value):
                if value is None or (isinstance(value, float) and math.isnan(value)):
                    return 0.0
                return float(value)

            key = f"market:l1:{symbol}"
            value = {
                "symbol": symbol,
                "last": safe_float(ticker.last),
                "bid": safe_float(ticker.bid),
                "ask": safe_float(ticker.ask),
                "bid_size": safe_int(ticker.bidSize),
                "ask_size": safe_int(ticker.askSize),
                "volume": safe_int(ticker.volume),
                "timestamp": timestamp
            }

            await self.valkey_client.setex(
                key,
                self.store_config.valkey_ttl_seconds,
                json.dumps(value)
            )
        except Exception as e:
            self.logger.error(f"Failed to write {symbol} to Valkey: {e}")

    # --- Error Handling ---

    def _on_error(self, reqId, errorCode, errorString, contract):
        """Handle IBKR errors, specifically tracking Error 101 (subscription limit)"""
        # Error 101: Max number of tickers has been reached
        if errorCode == 101 and contract:
            symbol = contract.symbol if hasattr(contract, 'symbol') else 'Unknown'
            if symbol not in self.failed_subscriptions:
                self.failed_subscriptions.append(symbol)
                self.logger.debug(f"Tracked subscription failure for {symbol} (Error 101)")

    # --- Health Check ---

    def is_healthy(self) -> bool:
        """Check if adapter is healthy"""
        return (
            self.connected and
            self.ib is not None and
            self.ib.isConnected() and
            self.valkey_client is not None and
            self.questdb_client is not None
        )

    def get_status(self) -> dict:
        """Get adapter status with comprehensive subscription information"""
        total_requested = len(self.symbols)
        successful = len(self.subscriptions)
        failed = len(self.failed_subscriptions)

        return {
            "connected": self.connected,
            "ibkr_connected": self.ib.isConnected() if self.ib else False,
            "subscriptions": {
                "total_requested": total_requested,
                "successful": successful,
                "failed": failed,
                "success_rate": f"{(successful/total_requested*100):.1f}%" if total_requested > 0 else "0%",
                "subscribed_symbols": sorted(list(self.subscriptions.keys())),
                "failed_symbols": sorted(self.failed_subscriptions)
            },
            "reconnect_attempts": self.reconnect_attempts,
            "valkey_connected": self.valkey_client is not None,
            "questdb_connected": self.questdb_client is not None,
            "note": "IBKR paper trading has ~100-123 symbol limit. See IBKR_SUBSCRIPTION_LIMIT_ANALYSIS.md"
        }


# --- Factory Function ---

def create_ibkr_adapter(
    ibkr_config: Dict,
    store_config: Dict,
    symbols: List[str],
    logger: Optional[logging.Logger] = None
) -> IBKRAdapter:
    """Factory function to create IBKR adapter from config dictionaries"""

    ibkr_cfg = IBKRConfig(
        host=ibkr_config["host"],
        port=ibkr_config["port"],
        client_id=ibkr_config["client_id"],
        reconnect_delay_seconds=ibkr_config.get("reconnect_delay_seconds", 5),
        max_reconnect_attempts=ibkr_config.get("max_reconnect_attempts", 5)
    )

    store_cfg = StoreConfig(
        questdb_http_host=store_config.get("questdb_http_host", store_config.get("questdb_ilp_host", "questdb")),
        questdb_http_port=store_config.get("questdb_http_port", 9000),
        valkey_host=store_config["valkey_host"],
        valkey_port=store_config["valkey_port"],
        valkey_ttl_seconds=store_config.get("valkey_ttl_seconds", 300)
    )

    return IBKRAdapter(ibkr_cfg, store_cfg, symbols, logger)
