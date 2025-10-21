"""
QuestDB Client for PRISM execution storage.
Stores fills and market data in QuestDB for analytics.
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
import httpx
from ..core.models import Fill, MarketState
from ..config.settings import settings

logger = logging.getLogger(__name__)


class QuestDBClient:
    """
    QuestDB client for storing PRISM execution data.
    """

    def __init__(self, host: str = "localhost", port: int = 9000):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.client = httpx.Client(timeout=10.0)

        logger.info(f"QuestDB Client initialized: {self.base_url}")

    async def initialize(self):
        """Initialize QuestDB tables."""
        try:
            # Create fills table
            fills_table = """
            CREATE TABLE IF NOT EXISTS prism_fills (
                timestamp TIMESTAMP,
                fill_id UUID,
                order_id UUID,
                symbol SYMBOL,
                side SYMBOL,
                price DOUBLE,
                quantity DOUBLE,
                executed_at TIMESTAMP
            ) timestamp(timestamp) PARTITION BY DAY;
            """

            # Create market state table
            market_state_table = """
            CREATE TABLE IF NOT EXISTS prism_market_state (
                timestamp TIMESTAMP,
                symbol SYMBOL,
                last_price DOUBLE,
                volume DOUBLE,
                liquidity DOUBLE,
                volatility DOUBLE,
                momentum DOUBLE,
                spread DOUBLE
            ) timestamp(timestamp) PARTITION BY DAY;
            """

            # Execute table creation (QuestDB will ignore if exists)
            # Note: QuestDB uses /exec endpoint for DDL
            self._execute_query(fills_table)
            self._execute_query(market_state_table)

            logger.info("QuestDB tables initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize QuestDB tables: {e}")
            raise

    def _execute_query(self, query: str) -> dict:
        """Execute a SQL query via HTTP."""
        try:
            response = self.client.get(
                f"{self.base_url}/exec",
                params={"query": query}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"QuestDB query failed: {e}")
            raise

    async def store_fill(self, fill: Fill):
        """Store a single fill in QuestDB."""
        try:
            # Convert fill to InfluxDB Line Protocol (QuestDB's preferred format)
            timestamp_ns = int(fill.timestamp.timestamp() * 1e9)

            # Use ILP (InfluxDB Line Protocol) format
            line = (
                f"prism_fills,"
                f"symbol={fill.symbol},"
                f"side={fill.side.value} "
                f"fill_id=\"{fill.fill_id}\","
                f"order_id=\"{fill.order_id}\","
                f"price={fill.price},"
                f"quantity={fill.quantity} "
                f"{timestamp_ns}"
            )

            # Send via ILP endpoint
            response = self.client.post(
                f"{self.base_url}/write",
                params={"fmt": "ilp"},
                content=line.encode('utf-8'),
                headers={"Content-Type": "text/plain"}
            )
            response.raise_for_status()

            logger.debug(f"Stored fill {fill.fill_id} to QuestDB")

        except Exception as e:
            logger.error(f"Failed to store fill in QuestDB: {e}")
            # Don't raise - allow PRISM to continue even if storage fails

    async def store_fills(self, fills: List[Fill]):
        """Store multiple fills in QuestDB (batch)."""
        if not fills:
            return

        try:
            lines = []
            for fill in fills:
                timestamp_ns = int(fill.timestamp.timestamp() * 1e9)
                line = (
                    f"prism_fills,"
                    f"symbol={fill.symbol},"
                    f"side={fill.side.value} "
                    f"fill_id=\"{fill.fill_id}\","
                    f"order_id=\"{fill.order_id}\","
                    f"price={fill.price},"
                    f"quantity={fill.quantity} "
                    f"{timestamp_ns}"
                )
                lines.append(line)

            # Send batch via ILP
            batch_data = "\n".join(lines)
            response = self.client.post(
                f"{self.base_url}/write",
                params={"fmt": "ilp"},
                content=batch_data.encode('utf-8'),
                headers={"Content-Type": "text/plain"}
            )
            response.raise_for_status()

            logger.info(f"Stored {len(fills)} fills to QuestDB")

        except Exception as e:
            logger.error(f"Failed to store fills batch in QuestDB: {e}")

    async def store_market_state(self, market_state: MarketState, spread: float = 0.0):
        """Store market state snapshot."""
        try:
            timestamp_ns = int(datetime.utcnow().timestamp() * 1e9)

            line = (
                f"prism_market_state,"
                f"symbol={market_state.symbol} "
                f"last_price={market_state.last_price},"
                f"volume={market_state.volume},"
                f"liquidity={market_state.liquidity},"
                f"volatility={market_state.volatility},"
                f"momentum={market_state.momentum},"
                f"spread={spread} "
                f"{timestamp_ns}"
            )

            response = self.client.post(
                f"{self.base_url}/write",
                params={"fmt": "ilp"},
                content=line.encode('utf-8'),
                headers={"Content-Type": "text/plain"}
            )
            response.raise_for_status()

            logger.debug(f"Stored market state for {market_state.symbol} to QuestDB")

        except Exception as e:
            logger.error(f"Failed to store market state in QuestDB: {e}")

    async def query_fills(
        self,
        symbol: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """Query fills from QuestDB."""
        try:
            query = "SELECT * FROM prism_fills WHERE 1=1"

            if symbol:
                query += f" AND symbol = '{symbol}'"

            if start_time:
                query += f" AND timestamp >= '{start_time.isoformat()}'"

            if end_time:
                query += f" AND timestamp <= '{end_time.isoformat()}'"

            query += f" ORDER BY timestamp DESC LIMIT {limit}"

            result = self._execute_query(query)

            # Parse QuestDB result format
            if "dataset" in result:
                return result["dataset"]
            return []

        except Exception as e:
            logger.error(f"Failed to query fills from QuestDB: {e}")
            return []

    def close(self):
        """Close the HTTP client."""
        self.client.close()


# Global QuestDB client instance
questdb_client = QuestDBClient(
    host=getattr(settings, 'QUESTDB_HOST', 'localhost'),
    port=getattr(settings, 'QUESTDB_PORT', 9000)
)
