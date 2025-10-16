"""
Market Tick Data Schemas
Phase 7B: Data Lake Sinks
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
import pyarrow as pa


class MarketTick(BaseModel):
    """Market tick data model"""

    # Core fields
    event_ts: datetime = Field(..., description="Event timestamp from producer")
    ingest_ts: datetime = Field(default_factory=datetime.utcnow, description="Sink write time")
    venue: str = Field(..., description="Exchange or broker")
    symbol: str = Field(..., description="Trading symbol")

    # Price/Size
    price: float = Field(..., gt=0, description="Trade price")
    size: float = Field(..., gt=0, description="Trade size")

    # Optional fields
    side: Optional[str] = Field(None, description="Buy/Sell side")
    trade_id: Optional[str] = Field(None, description="Exchange trade ID")
    source_seq: Optional[str] = Field(None, description="Source sequence number")

    # Deduplication
    hash_id: str = Field("", description="SHA256 hash for dedup")

    # Partition field
    dt: str = Field("", description="Partition date YYYY-MM-DD")

    @validator('dt', always=True)
    def compute_partition_date(cls, v, values):
        """Compute partition date from event_ts"""
        if v:
            return v
        event_ts = values.get('event_ts')
        if event_ts:
            return event_ts.strftime('%Y-%m-%d')
        return datetime.utcnow().strftime('%Y-%m-%d')

    @validator('hash_id', always=True)
    def compute_hash(cls, v, values):
        """Compute hash if not provided"""
        if v:
            return v

        import hashlib
        venue = values.get('venue', '')
        symbol = values.get('symbol', '')
        event_ts = values.get('event_ts')
        price = values.get('price', 0)
        size = values.get('size', 0)
        trade_id = values.get('trade_id', '')

        # Create unique string
        unique_str = f"{venue}|{symbol}|{event_ts}|{price}|{size}"
        if trade_id:
            unique_str += f"|{trade_id}"

        # Generate hash
        hash_obj = hashlib.sha256(unique_str.encode('utf-8'))
        return hash_obj.hexdigest()[:16]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


def get_tick_schema() -> pa.Schema:
    """Get PyArrow schema for Delta Lake"""
    return pa.schema([
        ('event_ts', pa.timestamp('us')),
        ('ingest_ts', pa.timestamp('us')),
        ('venue', pa.string()),
        ('symbol', pa.string()),
        ('price', pa.float64()),
        ('size', pa.float64()),
        ('side', pa.string()),
        ('trade_id', pa.string()),
        ('source_seq', pa.string()),
        ('hash_id', pa.string()),
        ('dt', pa.string()),
    ])


def normalize_tick_message(msg: dict) -> Optional[MarketTick]:
    """
    Normalize a tick message from NATS

    Args:
        msg: Raw message dict

    Returns:
        MarketTick or None if invalid
    """
    try:
        # Handle different timestamp formats
        if 'event_ts' in msg:
            if isinstance(msg['event_ts'], str):
                msg['event_ts'] = datetime.fromisoformat(msg['event_ts'].replace('Z', '+00:00'))
            elif isinstance(msg['event_ts'], (int, float)):
                msg['event_ts'] = datetime.fromtimestamp(msg['event_ts'])
        elif 'timestamp' in msg:
            # Handle millisecond timestamps
            if isinstance(msg['timestamp'], (int, float)):
                msg['event_ts'] = datetime.fromtimestamp(msg['timestamp'] / 1000.0)
            elif isinstance(msg['timestamp'], str):
                msg['event_ts'] = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
        elif 'ts' in msg:
            if isinstance(msg['ts'], str):
                msg['event_ts'] = datetime.fromisoformat(msg['ts'].replace('Z', '+00:00'))
            elif isinstance(msg['ts'], (int, float)):
                msg['event_ts'] = datetime.fromtimestamp(msg['ts'])
        else:
            msg['event_ts'] = datetime.utcnow()

        # Create tick object
        return MarketTick(**msg)

    except Exception as e:
        import logging
        logging.error(f"Failed to normalize tick: {e}, msg: {msg}")
        return None