"""
ClickHouse Client for PRISM analytics storage.
Stores analytics metrics in ClickHouse for long-term analysis.
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
import httpx
from ..config.settings import settings

logger = logging.getLogger(__name__)


class ClickHouseClient:
    """
    ClickHouse client for storing PRISM analytics metrics.
    """

    def __init__(self, host: str = "localhost", port: int = 8123):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.client = httpx.Client(timeout=10.0)

        logger.info(f"ClickHouse Client initialized: {self.base_url}")

    async def initialize(self):
        """Initialize ClickHouse tables."""
        try:
            # Create analytics metrics table
            metrics_table = """
            CREATE TABLE IF NOT EXISTS prism_analytics (
                timestamp DateTime,
                symbol String,
                bid_ask_spread Nullable(Float64),
                mid_price Nullable(Float64),
                order_book_imbalance Nullable(Float64),
                bid_depth Nullable(Float64),
                ask_depth Nullable(Float64),
                total_depth Nullable(Float64),
                effective_spread Nullable(Float64),
                price_impact Nullable(Float64),
                realized_volatility Nullable(Float64),
                volume Float64,
                volatility Float64,
                momentum Float64,
                liquidity Float64
            ) ENGINE = MergeTree()
            ORDER BY (symbol, timestamp)
            PARTITION BY toYYYYMM(timestamp)
            """

            # Create order book snapshot table
            orderbook_table = """
            CREATE TABLE IF NOT EXISTS prism_orderbook_snapshots (
                timestamp DateTime,
                symbol String,
                level UInt8,
                bid_price Nullable(Float64),
                bid_quantity Nullable(Float64),
                bid_num_orders Nullable(UInt32),
                ask_price Nullable(Float64),
                ask_quantity Nullable(Float64),
                ask_num_orders Nullable(UInt32)
            ) ENGINE = MergeTree()
            ORDER BY (symbol, timestamp, level)
            PARTITION BY toYYYYMM(timestamp)
            """

            self._execute_query(metrics_table)
            self._execute_query(orderbook_table)

            logger.info("ClickHouse tables initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize ClickHouse tables: {e}")
            raise

    def _execute_query(self, query: str) -> str:
        """Execute a SQL query via HTTP."""
        try:
            response = self.client.post(
                self.base_url,
                data=query,
                headers={"Content-Type": "text/plain"}
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"ClickHouse query failed: {e}")
            raise

    async def store_analytics(self, symbol: str, metrics: Dict, market_state: Dict):
        """Store analytics metrics for a symbol."""
        try:
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

            # Extract metrics (use 0.0 for missing values to avoid NULL issues)
            bid_ask_spread = metrics.get('bid_ask_spread', 0.0) or 0.0
            mid_price = metrics.get('mid_price', 0.0) or 0.0
            order_book_imbalance = metrics.get('order_book_imbalance', 0.0) or 0.0

            # Depth metrics
            depth = metrics.get('depth_5', {})
            bid_depth = depth.get('bid_depth', 0.0) or 0.0
            ask_depth = depth.get('ask_depth', 0.0) or 0.0
            total_depth = depth.get('total_depth', 0.0) or 0.0

            # Other metrics
            effective_spread = metrics.get('effective_spread', 0.0) or 0.0
            price_impact = metrics.get('price_impact', 0.0) or 0.0
            realized_volatility = metrics.get('realized_volatility', 0.0) or 0.0

            # Market state
            volume = market_state.get('volume', 0.0)
            volatility = market_state.get('volatility', 0.0)
            momentum = market_state.get('momentum', 0.0)
            liquidity = market_state.get('liquidity', 0.0)

            # Build INSERT query using VALUES format
            query = f"INSERT INTO prism_analytics VALUES ('{timestamp}', '{symbol}', {bid_ask_spread}, {mid_price}, {order_book_imbalance}, {bid_depth}, {ask_depth}, {total_depth}, {effective_spread}, {price_impact}, {realized_volatility}, {volume}, {volatility}, {momentum}, {liquidity})"

            self._execute_query(query)
            logger.debug(f"Stored analytics for {symbol} to ClickHouse")

        except Exception as e:
            logger.error(f"Failed to store analytics in ClickHouse: {e}")
            # Don't raise - allow PRISM to continue even if storage fails

    async def store_orderbook_snapshot(self, symbol: str, order_book: Dict):
        """Store order book snapshot."""
        try:
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

            # Build batch insert for all levels
            values = []

            # Store bids
            for idx, bid in enumerate(order_book.get('bids', [])[:10]):  # Top 10 levels
                bid_price = bid.get('price', 0.0)
                bid_quantity = bid.get('quantity', 0.0)
                bid_num_orders = bid.get('num_orders', 0)

                values.append(
                    f"('{timestamp}', '{symbol}', {idx}, "
                    f"{bid_price}, {bid_quantity}, {bid_num_orders}, "
                    f"0, 0, 0)"
                )

            # Store asks
            for idx, ask in enumerate(order_book.get('asks', [])[:10]):
                ask_price = ask.get('price', 0.0)
                ask_quantity = ask.get('quantity', 0.0)
                ask_num_orders = ask.get('num_orders', 0)

                values.append(
                    f"('{timestamp}', '{symbol}', {idx}, "
                    f"0, 0, 0, "
                    f"{ask_price}, {ask_quantity}, {ask_num_orders})"
                )

            if values:
                query = f"INSERT INTO prism_orderbook_snapshots VALUES {','.join(values)}"
                self._execute_query(query)
                logger.debug(f"Stored order book snapshot for {symbol} to ClickHouse")

        except Exception as e:
            logger.error(f"Failed to store order book snapshot in ClickHouse: {e}")

    async def query_analytics(
        self,
        symbol: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """Query analytics from ClickHouse."""
        try:
            query = "SELECT * FROM prism_analytics WHERE 1=1"

            if symbol:
                query += f" AND symbol = '{symbol}'"

            if start_time:
                query += f" AND timestamp >= '{start_time.strftime('%Y-%m-%d %H:%M:%S')}'"

            if end_time:
                query += f" AND timestamp <= '{end_time.strftime('%Y-%m-%d %H:%M:%S')}'"

            query += f" ORDER BY timestamp DESC LIMIT {limit} FORMAT JSONEachRow"

            result = self._execute_query(query)

            # Parse JSON lines
            import json
            lines = result.strip().split('\n')
            return [json.loads(line) for line in lines if line]

        except Exception as e:
            logger.error(f"Failed to query analytics from ClickHouse: {e}")
            return []

    def close(self):
        """Close the HTTP client."""
        self.client.close()


# Global ClickHouse client instance
clickhouse_client = ClickHouseClient(
    host=getattr(settings, 'CLICKHOUSE_HOST', 'localhost'),
    port=getattr(settings, 'CLICKHOUSE_HTTP_PORT', 8123)
)
