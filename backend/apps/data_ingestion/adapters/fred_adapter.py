"""
FRED Economic Indicators Adapter - Phase 6 Week 1 Day 3
Fetches economic data from Federal Reserve Economic Data (FRED) API

Component Isolation:
- ONLY talks to FRED API
- ONLY writes to QuestDB (via ILP) and Valkey (cache)
- NO dependencies on other services
- Self-contained error handling
"""

import asyncio
import logging
import time
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

import httpx
import redis.asyncio as redis


@dataclass
class FREDConfig:
    """FRED API configuration"""
    api_key: str
    base_url: str
    update_interval_minutes: int = 60
    series: List[str] = None


@dataclass
class StoreConfig:
    """Data store configuration"""
    questdb_http_host: str
    questdb_http_port: int
    valkey_host: str
    valkey_port: int
    valkey_ttl_seconds: int = 3600  # 1 hour for economic data


class FREDAdapter:
    """
    FRED Economic Data Adapter with component isolation and fault tolerance

    Responsibilities:
    1. Connect to FRED API
    2. Fetch economic indicator series data
    3. Write to QuestDB (persistent) and Valkey (cache)
    4. Poll at configured intervals
    5. Log all errors without crashing
    """

    def __init__(
        self,
        fred_config: FREDConfig,
        store_config: StoreConfig,
        logger: Optional[logging.Logger] = None
    ):
        self.fred_config = fred_config
        self.store_config = store_config
        self.logger = logger or logging.getLogger(__name__)

        # HTTP client for FRED API
        self.http_client: Optional[httpx.AsyncClient] = None

        # Data stores
        self.valkey_client: Optional[redis.Redis] = None
        self.questdb_client: Optional[httpx.AsyncClient] = None
        self.questdb_url: str = f"http://{store_config.questdb_http_host}:{store_config.questdb_http_port}/write"

        # Control
        self.running = False
        self.fetch_task: Optional[asyncio.Task] = None

        # Series metadata cache (series_id -> {name, units, etc.})
        self.series_metadata: Dict[str, dict] = {}

    async def start(self):
        """Start the adapter (connect to data stores and begin polling)"""
        self.logger.info("Starting FRED Adapter...")

        # Connect to data stores
        await self._connect_valkey()
        self._connect_questdb()

        # Create HTTP client for FRED API
        self.http_client = httpx.AsyncClient(timeout=30.0)

        # Fetch metadata for all series
        await self._fetch_all_metadata()

        # Start background polling task
        self.running = True
        self.fetch_task = asyncio.create_task(self._poll_loop())

        self.logger.info("FRED Adapter started successfully")

    async def stop(self):
        """Stop the adapter gracefully"""
        self.logger.info("Stopping FRED Adapter...")

        # Stop polling loop
        self.running = False
        if self.fetch_task:
            self.fetch_task.cancel()
            try:
                await self.fetch_task
            except asyncio.CancelledError:
                pass

        # Close HTTP client
        if self.http_client:
            await self.http_client.aclose()
            self.logger.info("Closed FRED HTTP client")

        # Close data store connections
        if self.valkey_client:
            await self.valkey_client.close()
            self.logger.info("Closed Valkey connection")

        if self.questdb_client:
            await self.questdb_client.aclose()
            self.logger.info("Closed QuestDB connection")

        self.logger.info("FRED Adapter stopped")

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
            self.questdb_client = httpx.AsyncClient(timeout=10.0)
            self.logger.info(f"Connected to QuestDB HTTP: {self.questdb_url}")
        except Exception as e:
            self.logger.error(f"Failed to connect to QuestDB: {e}")
            raise

    # --- FRED API Methods ---

    async def _fetch_series_metadata(self, series_id: str) -> Optional[dict]:
        """Fetch metadata for a series from FRED API"""
        if not self.http_client:
            self.logger.error("HTTP client not initialized")
            return None

        try:
            url = f"{self.fred_config.base_url}/series"
            params = {
                "series_id": series_id,
                "api_key": self.fred_config.api_key,
                "file_type": "json"
            }

            response = await self.http_client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if "seriess" in data and len(data["seriess"]) > 0:
                series_info = data["seriess"][0]
                self.logger.info(f"Fetched metadata for {series_id}: {series_info.get('title', 'N/A')}")
                return series_info
            else:
                self.logger.warning(f"No metadata found for {series_id}")
                return None

        except httpx.HTTPStatusError as e:
            self.logger.error(f"FRED API error for {series_id} metadata: status={e.response.status_code}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to fetch metadata for {series_id}: {type(e).__name__}: {e}")
            return None

    async def _fetch_series_observations(self, series_id: str, limit: int = 100) -> Optional[List[dict]]:
        """Fetch recent observations for a series from FRED API"""
        if not self.http_client:
            self.logger.error("HTTP client not initialized")
            return None

        try:
            url = f"{self.fred_config.base_url}/series/observations"
            params = {
                "series_id": series_id,
                "api_key": self.fred_config.api_key,
                "file_type": "json",
                "limit": limit,
                "sort_order": "desc"  # Most recent first
            }

            response = await self.http_client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if "observations" in data:
                observations = data["observations"]
                self.logger.info(f"Fetched {len(observations)} observations for {series_id}")
                return observations
            else:
                self.logger.warning(f"No observations found for {series_id}")
                return None

        except httpx.HTTPStatusError as e:
            self.logger.error(f"FRED API error for {series_id} observations: status={e.response.status_code}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to fetch observations for {series_id}: {type(e).__name__}: {e}")
            return None

    async def _fetch_all_metadata(self):
        """Fetch metadata for all configured series"""
        for series_id in self.fred_config.series:
            metadata = await self._fetch_series_metadata(series_id)
            if metadata:
                self.series_metadata[series_id] = metadata
            await asyncio.sleep(0.5)  # Rate limiting - 2 requests/sec max

    async def _poll_loop(self):
        """Background task to poll FRED API at intervals"""
        self.logger.info(f"Starting FRED polling loop (interval: {self.fred_config.update_interval_minutes} minutes)")

        while self.running:
            try:
                await self._fetch_and_store_all_series()
            except Exception as e:
                self.logger.error(f"Error in polling loop: {type(e).__name__}: {e}")
                # Don't crash - component isolation

            # Wait for next interval
            await asyncio.sleep(self.fred_config.update_interval_minutes * 60)

    async def _fetch_and_store_all_series(self):
        """Fetch latest data for all series and store"""
        self.logger.info(f"Fetching data for {len(self.fred_config.series)} FRED series...")

        for series_id in self.fred_config.series:
            try:
                observations = await self._fetch_series_observations(series_id, limit=1)
                if observations and len(observations) > 0:
                    # Get most recent observation
                    latest = observations[0]
                    if latest.get("value") != ".":  # FRED uses "." for missing values
                        await self._write_observation(series_id, latest)

                # Rate limiting - 2 requests/sec max
                await asyncio.sleep(0.5)

            except Exception as e:
                self.logger.error(f"Error processing {series_id}: {type(e).__name__}: {e}")
                # Continue with other series - component isolation

    async def _write_observation(self, series_id: str, observation: dict):
        """Write a single observation to QuestDB and Valkey"""
        try:
            # Parse observation
            date_str = observation.get("date")
            value_str = observation.get("value")

            if not date_str or not value_str or value_str == ".":
                return

            value = float(value_str)

            # Convert date to timestamp
            obs_date = datetime.strptime(date_str, "%Y-%m-%d")
            timestamp = int(obs_date.timestamp() * 1_000_000_000)  # nanoseconds

            # Get metadata
            metadata = self.series_metadata.get(series_id, {})
            title = metadata.get("title", series_id)
            units = metadata.get("units", "")

            # Write to QuestDB
            await self._write_questdb(series_id, title, value, units, date_str, timestamp)

            # Write to Valkey
            await self._write_valkey(series_id, title, value, units, date_str, timestamp)

        except Exception as e:
            self.logger.error(f"Failed to write observation for {series_id}: {type(e).__name__}: {e}")

    async def _write_questdb(self, series_id: str, title: str, value: float, units: str, date_str: str, timestamp: int):
        """Write economic data to QuestDB via HTTP"""
        if not self.questdb_client:
            self.logger.warning(f"QuestDB client not initialized, skipping write for {series_id}")
            return

        try:
            # Build ILP (InfluxDB Line Protocol) string
            # Format: table_name,tag1=value1 field1=value1,field2=value2 timestamp_ns
            # Replace spaces in series_id with underscores for tag value
            safe_series_id = series_id.replace(" ", "_")
            safe_units = units.replace(" ", "_").replace(",", "")

            line = (
                f"fred_economic_data,"
                f"series_id={safe_series_id},"
                f"units={safe_units} "
                f"value={value},"
                f"date=\"{date_str}\" "
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

            self.logger.debug(f"Successfully wrote {series_id} to QuestDB: {value} ({date_str})")

        except httpx.HTTPStatusError as e:
            self.logger.error(f"QuestDB HTTP error for {series_id}: status={e.response.status_code}, body={e.response.text}")
        except Exception as e:
            self.logger.error(f"Failed to write {series_id} to QuestDB: {type(e).__name__}: {e}", exc_info=True)

    async def _write_valkey(self, series_id: str, title: str, value: float, units: str, date_str: str, timestamp: int):
        """Write economic data to Valkey (hot cache)"""
        if not self.valkey_client:
            return

        try:
            import json

            key = f"fred:{series_id}"
            value_dict = {
                "series_id": series_id,
                "title": title,
                "value": value,
                "units": units,
                "date": date_str,
                "timestamp": timestamp,
                "updated_at": int(time.time())
            }

            await self.valkey_client.setex(
                key,
                self.store_config.valkey_ttl_seconds,
                json.dumps(value_dict)
            )

            self.logger.debug(f"Successfully wrote {series_id} to Valkey: {value}")

        except Exception as e:
            self.logger.error(f"Failed to write {series_id} to Valkey: {type(e).__name__}: {e}")

    # --- Health Check ---

    def is_healthy(self) -> bool:
        """Check if adapter is healthy"""
        return (
            self.running and
            self.http_client is not None and
            self.valkey_client is not None and
            self.questdb_client is not None
        )

    def get_status(self) -> dict:
        """Get adapter status"""
        return {
            "running": self.running,
            "series_count": len(self.fred_config.series),
            "metadata_cached": len(self.series_metadata),
            "valkey_connected": self.valkey_client is not None,
            "questdb_connected": self.questdb_client is not None,
            "update_interval_minutes": self.fred_config.update_interval_minutes
        }


# --- Factory Function ---

def create_fred_adapter(
    fred_config: Dict,
    store_config: Dict,
    logger: Optional[logging.Logger] = None
) -> FREDAdapter:
    """Factory function to create FRED adapter from config dictionaries"""

    # Get API key from environment
    api_key = os.getenv(fred_config.get("api_key_env", "FRED_API_KEY"))
    if not api_key:
        raise ValueError("FRED_API_KEY environment variable not set")

    fred_cfg = FREDConfig(
        api_key=api_key,
        base_url=fred_config["base_url"],
        update_interval_minutes=fred_config.get("update_interval_minutes", 60),
        series=fred_config.get("series", [])
    )

    store_cfg = StoreConfig(
        questdb_http_host=store_config.get("questdb_http_host", store_config.get("questdb_ilp_host", "questdb")),
        questdb_http_port=store_config.get("questdb_http_port", 9000),
        valkey_host=store_config["valkey_host"],
        valkey_port=store_config["valkey_port"],
        valkey_ttl_seconds=store_config.get("valkey_ttl_seconds", 3600)
    )

    return FREDAdapter(fred_cfg, store_cfg, logger)
