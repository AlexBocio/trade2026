"""
Alpaca Data Adapter - Phase 6 Alternative to IBKR
Streams real-time Level 1 market data from Alpaca Markets (FREE)

Component Isolation:
- ONLY talks to Alpaca WebSocket API
- ONLY writes to QuestDB (via ILP) and Valkey (cache)
- NO dependencies on other services
- Self-contained error handling
"""

import asyncio
import logging
import time
import os
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
import json

try:
    from alpaca.data.live import StockDataStream
    from alpaca.data.models import Quote, Trade
except ImportError as e:
    # For testing without alpaca-py installed
    print(f"ERROR importing alpaca-py: {e}")
    import traceback
    traceback.print_exc()
    StockDataStream = None
    Quote = None
    Trade = None

import redis.asyncio as redis
import httpx


@dataclass
class AlpacaConfig:
    """Alpaca connection configuration"""
    api_key: str
    secret_key: str
    paper: bool = True  # Paper trading by default
    feed: str = "iex"  # Free IEX data feed


@dataclass
class StoreConfig:
    """Data store configuration"""
    questdb_http_host: str
    questdb_http_port: int
    valkey_host: str
    valkey_port: int
    valkey_ttl_seconds: int = 300


class AlpacaAdapter:
    """
    Alpaca Data Adapter with component isolation and fault tolerance

    Responsibilities:
    1. Connect to Alpaca WebSocket API
    2. Subscribe to real-time quotes (Level 1 data)
    3. Write to QuestDB (persistent) and Valkey (cache)
    4. Handle reconnection automatically
    5. Log all errors without crashing
    """

    def __init__(
        self,
        alpaca_config: AlpacaConfig,
        store_config: StoreConfig,
        symbols: List[str],
        logger: Optional[logging.Logger] = None
    ):
        self.alpaca_config = alpaca_config
        self.store_config = store_config
        self.symbols = symbols
        self.logger = logger or logging.getLogger(__name__)

        # Alpaca connection
        self.stream: Optional[StockDataStream] = None
        self.connected = False
        self.reconnecting = False

        # Data stores
        self.valkey_client: Optional[redis.Redis] = None
        self.questdb_client: Optional[httpx.AsyncClient] = None
        self.questdb_url: str = f"http://{store_config.questdb_http_host}:{store_config.questdb_http_port}/write"

        # Statistics
        self.stats = {
            "quotes_received": 0,
            "trades_received": 0,
            "writes_succeeded": 0,
            "writes_failed": 0,
            "last_quote_time": None
        }

    async def start(self):
        """Start the adapter (connect to Alpaca and data stores)"""
        self.logger.info("Starting Alpaca Adapter...")

        # Connect to data stores
        await self._connect_valkey()
        self._connect_questdb()

        # Connect to Alpaca
        await self._connect_alpaca()

        self.logger.info("Alpaca Adapter started successfully")

    async def stop(self):
        """Stop the adapter"""
        self.logger.info("Stopping Alpaca Adapter...")

        self.connected = False

        # Close WebSocket stream
        if self.stream:
            try:
                await self.stream.stop_ws()
                self.logger.info("Alpaca WebSocket closed")
            except Exception as e:
                self.logger.error(f"Error closing Alpaca WebSocket: {e}")

        # Close data store connections
        if self.valkey_client:
            await self.valkey_client.close()
            self.logger.info("Valkey connection closed")

        if self.questdb_client:
            await self.questdb_client.aclose()
            self.logger.info("QuestDB client closed")

        self.logger.info("Alpaca Adapter stopped")

    def is_healthy(self) -> bool:
        """Check if adapter is healthy"""
        return self.connected and self.valkey_client is not None and self.questdb_client is not None

    def get_status(self) -> Dict:
        """Get detailed adapter status"""
        return {
            "connected": self.connected,
            "reconnecting": self.reconnecting,
            "symbols": len(self.symbols),
            "subscribed_symbols": self.symbols if self.connected else [],
            "stats": self.stats,
            "data_stores": {
                "valkey": "connected" if self.valkey_client else "disconnected",
                "questdb": "connected" if self.questdb_client else "disconnected"
            }
        }

    # --- Connection Management ---

    async def _connect_valkey(self):
        """Connect to Valkey (Redis) cache"""
        try:
            self.valkey_client = redis.Redis(
                host=self.store_config.valkey_host,
                port=self.store_config.valkey_port,
                decode_responses=False,  # We'll handle encoding
                socket_timeout=5,
                socket_connect_timeout=5
            )
            # Test connection
            await self.valkey_client.ping()
            self.logger.info(f"Connected to Valkey at {self.store_config.valkey_host}:{self.store_config.valkey_port}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Valkey: {e}")
            self.valkey_client = None
            raise

    def _connect_questdb(self):
        """Connect to QuestDB HTTP endpoint"""
        try:
            self.questdb_client = httpx.AsyncClient(timeout=5.0)
            self.logger.info(f"QuestDB client initialized for {self.questdb_url}")
        except Exception as e:
            self.logger.error(f"Failed to initialize QuestDB client: {e}")
            self.questdb_client = None
            raise

    async def _connect_alpaca(self):
        """Connect to Alpaca WebSocket API"""
        if StockDataStream is None:
            self.logger.error("alpaca-py not installed, cannot connect")
            raise ImportError("alpaca-py library not installed")

        try:
            self.logger.info("Connecting to Alpaca WebSocket API...")

            # Create WebSocket stream (feed defaults to IEX which is free)
            self.stream = StockDataStream(
                api_key=self.alpaca_config.api_key,
                secret_key=self.alpaca_config.secret_key,
                raw_data=False
            )

            # Subscribe to quotes for all symbols
            async def quote_handler(quote: Quote):
                await self._on_quote_update(quote)

            async def trade_handler(trade: Trade):
                await self._on_trade_update(trade)

            # Subscribe to quotes ONLY (free tier limit: 30 channels)
            # Note: Subscribing to both quotes+trades would be 60 channels (exceeds limit)
            self.stream.subscribe_quotes(quote_handler, *self.symbols)
            # self.stream.subscribe_trades(trade_handler, *self.symbols)  # Disabled for free tier

            self.logger.info(f"Subscribed to {len(self.symbols)} symbols (quotes only): {self.symbols}")

            # Start the WebSocket stream in background
            asyncio.create_task(self._run_stream())

            # Wait a moment for connection to establish
            await asyncio.sleep(2)

            self.connected = True
            self.logger.info("Connected to Alpaca WebSocket API")

        except Exception as e:
            self.logger.error(f"Failed to connect to Alpaca: {e}")
            self.connected = False
            raise

    async def _run_stream(self):
        """Run the WebSocket stream (handles reconnection automatically)"""
        while True:
            try:
                self.logger.info("Starting Alpaca WebSocket stream...")
                # run() is a synchronous blocking method, so we run it in an executor
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.stream.run)
            except Exception as e:
                self.logger.error(f"Alpaca WebSocket error: {e}")
                if not self.reconnecting:
                    self.reconnecting = True
                    self.connected = False
                    self.logger.info("Reconnecting in 10 seconds...")
                    await asyncio.sleep(10)
                    self.reconnecting = False

    # --- Data Callbacks ---

    async def _on_quote_update(self, quote: Quote):
        """Handle real-time quote update (Level 1 data)"""
        try:
            symbol = quote.symbol
            timestamp = int(quote.timestamp.timestamp() * 1_000_000_000)  # nanoseconds

            self.stats["quotes_received"] += 1
            self.stats["last_quote_time"] = datetime.now().isoformat()

            # Write to QuestDB (persistent storage)
            await self._write_quote_questdb(symbol, quote, timestamp)

            # Write to Valkey (hot cache)
            await self._write_quote_valkey(symbol, quote, timestamp)

        except Exception as e:
            self.logger.error(f"Error processing quote update for {quote.symbol}: {e}")
            # Don't crash - component isolation

    async def _on_trade_update(self, trade: Trade):
        """Handle real-time trade update (Time & Sales)"""
        try:
            self.stats["trades_received"] += 1
            # We mainly focus on quotes for market data
            # Trades can be logged or processed separately if needed
            self.logger.debug(f"Trade received: {trade.symbol} @ {trade.price}")

        except Exception as e:
            self.logger.error(f"Error processing trade update for {trade.symbol}: {e}")

    async def _write_quote_questdb(self, symbol: str, quote: Quote, timestamp: int):
        """Write quote data to QuestDB via HTTP (ILP format)"""
        if not self.questdb_client:
            self.logger.warning(f"QuestDB client not initialized, skipping write for {symbol}")
            return

        try:
            # Build ILP (InfluxDB Line Protocol) string
            # Format: table_name,tag1=value1 field1=value1,field2=value2 timestamp_ns
            line = (
                f"market_data_l1,"
                f"symbol={symbol} "
                f"last={float(quote.ask_price) if quote.ask_price else 0.0},"  # Use ask as last price
                f"bid={float(quote.bid_price) if quote.bid_price else 0.0},"
                f"ask={float(quote.ask_price) if quote.ask_price else 0.0},"
                f"bid_size={int(quote.bid_size) if quote.bid_size else 0}i,"
                f"ask_size={int(quote.ask_size) if quote.ask_size else 0}i,"
                f"volume=0i,"  # Quotes don't have volume
                f"high=0.0,"
                f"low=0.0,"
                f"close=0.0 "
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

            self.stats["writes_succeeded"] += 1
            self.logger.debug(f"Successfully wrote {symbol} to QuestDB")

        except httpx.HTTPStatusError as e:
            self.stats["writes_failed"] += 1
            self.logger.error(f"QuestDB HTTP error for {symbol}: status={e.response.status_code}, body={e.response.text}")
        except Exception as e:
            self.stats["writes_failed"] += 1
            self.logger.error(f"Failed to write {symbol} to QuestDB: {type(e).__name__}: {e}")

    async def _write_quote_valkey(self, symbol: str, quote: Quote, timestamp: int):
        """Write quote data to Valkey (hot cache)"""
        if not self.valkey_client:
            return

        try:
            key = f"market:l1:{symbol}"
            value = {
                "symbol": symbol,
                "timestamp": timestamp,
                "last": float(quote.ask_price) if quote.ask_price else 0.0,
                "bid": float(quote.bid_price) if quote.bid_price else 0.0,
                "ask": float(quote.ask_price) if quote.ask_price else 0.0,
                "bid_size": int(quote.bid_size) if quote.bid_size else 0,
                "ask_size": int(quote.ask_size) if quote.ask_size else 0,
                "volume": 0,
                "high": 0.0,
                "low": 0.0,
                "close": 0.0
            }

            # Serialize to JSON
            value_json = json.dumps(value)

            # Write to Valkey with TTL
            await self.valkey_client.setex(
                key,
                self.store_config.valkey_ttl_seconds,
                value_json.encode('utf-8')
            )

            self.logger.debug(f"Successfully wrote {symbol} to Valkey")

        except Exception as e:
            self.logger.error(f"Failed to write {symbol} to Valkey: {e}")


# --- Factory Function ---

def create_alpaca_adapter(
    alpaca_config: Dict,
    store_config: Dict,
    symbols: List[str],
    logger: logging.Logger
) -> AlpacaAdapter:
    """
    Factory function to create Alpaca adapter from config dictionaries

    Args:
        alpaca_config: Dictionary with api_key, secret_key, paper, feed
        store_config: Dictionary with questdb_http_host, questdb_http_port, valkey_host, valkey_port, valkey_ttl_seconds
        symbols: List of stock symbols to subscribe to
        logger: Logger instance

    Returns:
        AlpacaAdapter instance
    """
    # Get API credentials from environment variables
    api_key = os.getenv(alpaca_config.get("api_key_env", "ALPACA_API_KEY"), "")
    secret_key = os.getenv(alpaca_config.get("secret_key_env", "ALPACA_SECRET_KEY"), "")

    if not api_key or not secret_key:
        raise ValueError("Alpaca API credentials not found in environment variables. Set ALPACA_API_KEY and ALPACA_SECRET_KEY")

    # Create Alpaca config
    alpaca_cfg = AlpacaConfig(
        api_key=api_key,
        secret_key=secret_key,
        paper=alpaca_config.get("paper", True),
        feed=alpaca_config.get("feed", "iex")
    )

    # Create store config
    store_cfg = StoreConfig(
        questdb_http_host=store_config["questdb_http_host"],
        questdb_http_port=store_config["questdb_http_port"],
        valkey_host=store_config["valkey_host"],
        valkey_port=store_config["valkey_port"],
        valkey_ttl_seconds=store_config.get("valkey_ttl_seconds", 300)
    )

    return AlpacaAdapter(
        alpaca_config=alpaca_cfg,
        store_config=store_cfg,
        symbols=symbols,
        logger=logger
    )
