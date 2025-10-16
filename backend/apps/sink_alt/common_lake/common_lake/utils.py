"""
Lake Utility Functions
Phase 7B: Data Lake Sinks
"""

import hashlib
import json
from datetime import datetime, date
from typing import Any, Dict, Optional, Union
import logging

logger = logging.getLogger(__name__)


def compute_hash_id(data: Dict[str, Any], fields: list = None) -> str:
    """
    Compute deterministic hash ID for deduplication

    Args:
        data: Data dictionary
        fields: List of fields to include in hash. If None, uses all fields.

    Returns:
        16-character hash string
    """
    if fields:
        # Use specified fields
        hash_data = {k: data.get(k) for k in fields if k in data}
    else:
        # Use all fields
        hash_data = data

    # Create stable string representation
    hash_str = json.dumps(hash_data, sort_keys=True, default=str)

    # Generate SHA256 hash
    hash_obj = hashlib.sha256(hash_str.encode('utf-8'))

    # Return first 16 characters
    return hash_obj.hexdigest()[:16]


def compute_tick_hash(venue: str, symbol: str, event_ts: datetime,
                      price: float, size: float, trade_id: Optional[str] = None) -> str:
    """
    Compute hash for tick data

    Args:
        venue: Exchange/broker
        symbol: Trading symbol
        event_ts: Event timestamp
        price: Trade price
        size: Trade size
        trade_id: Optional trade ID

    Returns:
        16-character hash string
    """
    # Create unique string
    unique_str = f"{venue}|{symbol}|{event_ts.isoformat()}|{price}|{size}"
    if trade_id:
        unique_str += f"|{trade_id}"

    # Generate hash
    hash_obj = hashlib.sha256(unique_str.encode('utf-8'))
    return hash_obj.hexdigest()[:16]


def compute_alt_hash(source: str, url: str, event_ts: datetime) -> str:
    """
    Compute hash for alternative data

    Args:
        source: Data source
        url: Document URL
        event_ts: Event timestamp

    Returns:
        16-character hash string
    """
    # Create unique string
    unique_str = f"{source}|{url}|{event_ts.isoformat()}"

    # Generate hash
    hash_obj = hashlib.sha256(unique_str.encode('utf-8'))
    return hash_obj.hexdigest()[:16]


def get_partition_date(ts: Union[datetime, str]) -> str:
    """
    Get partition date string (YYYY-MM-DD)

    Args:
        ts: Timestamp (datetime or ISO string)

    Returns:
        Date string in YYYY-MM-DD format
    """
    if isinstance(ts, str):
        ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))

    return ts.strftime('%Y-%m-%d')


def get_partition_values(ts: Union[datetime, str]) -> Dict[str, Any]:
    """
    Get partition values for year/month/day partitioning

    Args:
        ts: Timestamp

    Returns:
        Dict with year, month, day values
    """
    if isinstance(ts, str):
        ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))

    return {
        'year': ts.year,
        'month': ts.month,
        'day': ts.day,
        'dt': ts.strftime('%Y-%m-%d')
    }


def json_safe(obj: Any) -> Any:
    """
    Convert object to JSON-safe representation

    Args:
        obj: Any object

    Returns:
        JSON-safe version
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, bytes):
        return obj.decode('utf-8', errors='ignore')
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    else:
        return str(obj)


def batch_records(records: list, max_size: int = 1000) -> list:
    """
    Batch records into chunks

    Args:
        records: List of records
        max_size: Maximum batch size

    Returns:
        List of batches
    """
    batches = []
    for i in range(0, len(records), max_size):
        batches.append(records[i:i + max_size])
    return batches


def parse_nats_timestamp(ts: Any) -> datetime:
    """
    Parse NATS timestamp to datetime

    Args:
        ts: Timestamp from NATS (various formats)

    Returns:
        datetime object
    """
    if isinstance(ts, datetime):
        return ts
    elif isinstance(ts, str):
        # Try ISO format first
        try:
            return datetime.fromisoformat(ts.replace('Z', '+00:00'))
        except:
            pass

        # Try timestamp
        try:
            return datetime.fromtimestamp(float(ts))
        except:
            pass
    elif isinstance(ts, (int, float)):
        # Unix timestamp
        return datetime.fromtimestamp(ts)

    # Default to now if can't parse
    logger.warning(f"Could not parse timestamp: {ts}, using current time")
    return datetime.utcnow()


def format_bytes(num_bytes: int) -> str:
    """
    Format bytes as human-readable string

    Args:
        num_bytes: Number of bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Format duration as human-readable string

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "1h 23m 45s")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)