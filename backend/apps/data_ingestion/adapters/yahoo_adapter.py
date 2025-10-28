"""
Yahoo Finance Data Adapter - Hybrid Solution for IBKR Subscription Limit
Polls Yahoo Finance for symbols that exceeded IBKR paper trading limit (Error 101)

Component Isolation:
- ONLY talks to Yahoo Finance API
- ONLY writes to QuestDB (via HTTP) and Valkey (cache)
- NO dependencies on other services
- Self-contained error handling
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

try:
    import yfinance as yf
except ImportError:
    yf = None

import redis.asyncio as redis
import httpx


@dataclass
class YahooConfig:
    """Yahoo Finance configuration"""
    poll_interval_seconds: int = 5  # Poll every 5 seconds during market hours
    max_retries: int = 3
    timeout_seconds: int = 10


@dataclass
class StoreConfig:
    """Data store configuration"""
    questdb_http_host: str
    questdb_http_port: int
    valkey_host: str
    valkey_port: int
    valkey_ttl_seconds: int = 300


class YahooAdapter:
    """
    Yahoo Finance Data Adapter with component isolation and fault tolerance

    Responsibilities:
    1. Poll Yahoo Finance for real-time/delayed quotes
    2. Write to QuestDB (persistent) and Valkey (cache)
    3. Handle rate limiting and errors gracefully
    4. Log all errors without crashing
    """

    def __init__(
        self,
        yahoo_config: YahooConfig,
        store_config: StoreConfig,
        symbols: List[str],
        logger: Optional[logging.Logger] = None
    ):
        self.yahoo_config = yahoo_config
        self.store_config = store_config
        self.symbols = symbols
        self.logger = logger or logging.getLogger(__name__)

        # Connection state
        self.connected = False
        self.running = False

        # Data stores
        self.valkey_client: Optional[redis.Redis] = None
        self.questdb_client: Optional[httpx.AsyncClient] = None
        self.questdb_url: str = f"http://{store_config.questdb_http_host}:{store_config.questdb_http_port}/write"

        # Tracking
        self.poll_count = 0
        self.error_count = 0
        self.last_poll_time = None

    async def start(self):
        """Start the adapter (connect to data stores and begin polling)"""
        self.logger.info("Starting Yahoo Finance Adapter...")

        if yf is None:
            self.logger.error("yfinance not installed, cannot start Yahoo adapter")
            return

        # Connect to data stores
        await self._connect_valkey()
        self._connect_questdb()

        self.connected = True
        self.running = True

        # Start polling loop
        asyncio.create_task(self._poll_loop())

        self.logger.info(f"Yahoo Finance Adapter started for {len(self.symbols)} symbols")

    async def stop(self):
        """Stop the adapter gracefully"""
        self.logger.info("Stopping Yahoo Finance Adapter...")

        self.running = False

        # Close data store connections
        if self.valkey_client:
            await self.valkey_client.close()
            self.logger.info("Closed Valkey connection")

        if self.questdb_client:
            await self.questdb_client.aclose()
            self.logger.info("Closed QuestDB connection")

        self.logger.info("Yahoo Finance Adapter stopped")

    # --- Connection Management ---

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
            limits = httpx.Limits(
                max_connections=100,
                max_keepalive_connections=50
            )
            self.questdb_client = httpx.AsyncClient(
                timeout=30.0,
                limits=limits
            )
            self.logger.info(f"Connected to QuestDB HTTP: {self.questdb_url}")
        except Exception as e:
            self.logger.error(f"Failed to connect to QuestDB: {e}")
            raise

    # --- Polling Loop ---

    async def _poll_loop(self):
        """Main polling loop"""
        self.logger.info(f"Starting polling loop (interval: {self.yahoo_config.poll_interval_seconds}s)")

        while self.running:
            try:
                start_time = time.time()
                await self._poll_all_symbols()
                self.last_poll_time = datetime.now()
                self.poll_count += 1

                # Log every 100 polls
                if self.poll_count % 100 == 0:
                    self.logger.info(
                        f"Poll #{self.poll_count}: {len(self.symbols)} symbols, "
                        f"{self.error_count} total errors"
                    )

                # Sleep for remaining interval
                elapsed = time.time() - start_time
                sleep_time = max(0, self.yahoo_config.poll_interval_seconds - elapsed)
                await asyncio.sleep(sleep_time)

            except Exception as e:
                self.logger.error(f"Error in polling loop: {e}")
                self.error_count += 1
                await asyncio.sleep(5)  # Back off on error

    async def _poll_all_symbols(self):
        """Poll all symbols from Yahoo Finance"""
        # Batch fetch for efficiency
        try:
            tickers = yf.Tickers(' '.join(self.symbols))

            # Process each symbol
            for symbol in self.symbols:
                try:
                    ticker = tickers.tickers[symbol]
                    await self._process_ticker(symbol, ticker)
                except Exception as e:
                    self.logger.debug(f"Error processing {symbol}: {e}")

        except Exception as e:
            self.logger.error(f"Error fetching batch from Yahoo: {e}")

    async def _process_ticker(self, symbol: str, ticker):
        """Process ticker data and write to stores"""
        try:
            # Get current quote
            info = ticker.info

            # Extract price data
            last = info.get('currentPrice') or info.get('regularMarketPrice')
            bid = info.get('bid')
            ask = info.get('ask')
            bid_size = info.get('bidSize', 0)
            ask_size = info.get('askSize', 0)
            volume = info.get('volume', 0)
            high = info.get('dayHigh') or info.get('regularMarketDayHigh')
            low = info.get('dayLow') or info.get('regularMarketDayLow')
            close = info.get('previousClose') or info.get('regularMarketPreviousClose')

            # Skip if no price data
            if last is None:
                return

            timestamp = int(time.time() * 1_000_000_000)  # nanoseconds

            # Write to QuestDB (persistent storage)
            await self._write_questdb(symbol, last, bid, ask, bid_size, ask_size, volume, high, low, close, timestamp)

            # Write to Valkey (hot cache)
            await self._write_valkey(symbol, last, bid, ask, bid_size, ask_size, volume, timestamp)

        except Exception as e:
            self.logger.debug(f"Error processing ticker {symbol}: {e}")

    async def _write_questdb(self, symbol: str, last, bid, ask, bid_size, ask_size, volume, high, low, close, timestamp: int):
        """Write data to QuestDB via HTTP"""
        if not self.questdb_client:
            return

        try:
            import math

            def safe_float(value):
                if value is None or (isinstance(value, float) and math.isnan(value)):
                    return 0.0
                return float(value)

            def safe_int(value):
                if value is None or (isinstance(value, float) and math.isnan(value)):
                    return 0
                return int(value)

            # Build ILP string
            line = (
                f"market_data_l1,"
                f"symbol={symbol} "
                f"last={safe_float(last)},"
                f"bid={safe_float(bid)},"
                f"ask={safe_float(ask)},"
                f"bid_size={safe_int(bid_size)}i,"
                f"ask_size={safe_int(ask_size)}i,"
                f"volume={safe_int(volume)}i,"
                f"high={safe_float(high)},"
                f"low={safe_float(low)},"
                f"close={safe_float(close)} "
                f"{timestamp}"
            )

            response = await self.questdb_client.post(
                self.questdb_url,
                params={"fmt": "ilp"},
                content=line.encode('utf-8'),
                headers={"Content-Type": "text/plain"}
            )
            response.raise_for_status()

        except Exception as e:
            self.logger.debug(f"Failed to write {symbol} to QuestDB: {e}")

    async def _write_valkey(self, symbol: str, last, bid, ask, bid_size, ask_size, volume, timestamp: int):
        """Write data to Valkey (hot cache)"""
        if not self.valkey_client:
            return

        try:
            import math

            def safe_float(value):
                if value is None or (isinstance(value, float) and math.isnan(value)):
                    return 0.0
                return float(value)

            def safe_int(value):
                if value is None or (isinstance(value, float) and math.isnan(value)):
                    return 0
                return int(value)

            key = f"market:l1:{symbol}"
            value = {
                "symbol": symbol,
                "last": safe_float(last),
                "bid": safe_float(bid),
                "ask": safe_float(ask),
                "bid_size": safe_int(bid_size),
                "ask_size": safe_int(ask_size),
                "volume": safe_int(volume),
                "timestamp": timestamp,
                "source": "yahoo"
            }

            await self.valkey_client.setex(
                key,
                self.store_config.valkey_ttl_seconds,
                json.dumps(value)
            )
        except Exception as e:
            self.logger.debug(f"Failed to write {symbol} to Valkey: {e}")

    # --- Health Check ---

    def is_healthy(self) -> bool:
        """Check if adapter is healthy"""
        return (
            self.connected and
            self.running and
            self.valkey_client is not None and
            self.questdb_client is not None and
            self.last_poll_time is not None
        )

    def get_status(self) -> dict:
        """Get adapter status"""
        return {
            "connected": self.connected,
            "running": self.running,
            "symbols": len(self.symbols),
            "poll_count": self.poll_count,
            "error_count": self.error_count,
            "last_poll": self.last_poll_time.isoformat() if self.last_poll_time else None,
            "poll_interval": f"{self.yahoo_config.poll_interval_seconds}s",
            "valkey_connected": self.valkey_client is not None,
            "questdb_connected": self.questdb_client is not None
        }


# --- Factory Function ---

def create_yahoo_adapter(
    yahoo_config: Dict,
    store_config: Dict,
    symbols: List[str],
    logger: Optional[logging.Logger] = None
) -> YahooAdapter:
    """Factory function to create Yahoo adapter from config dictionaries"""

    yahoo_cfg = YahooConfig(
        poll_interval_seconds=yahoo_config.get("poll_interval_seconds", 5),
        max_retries=yahoo_config.get("max_retries", 3),
        timeout_seconds=yahoo_config.get("timeout_seconds", 10)
    )

    store_cfg = StoreConfig(
        questdb_http_host=store_config.get("questdb_http_host", store_config.get("questdb_ilp_host", "questdb")),
        questdb_http_port=store_config.get("questdb_http_port", 9000),
        valkey_host=store_config["valkey_host"],
        valkey_port=store_config["valkey_port"],
        valkey_ttl_seconds=store_config.get("valkey_ttl_seconds", 300)
    )

    return YahooAdapter(yahoo_cfg, store_cfg, symbols, logger)
