"""
Audit Logger - Delta Lake Integration
Phase 11: Live Trading Enablement
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from datetime import timedelta

logger = logging.getLogger(__name__)


class AuditLogger:
    """Append-only audit logging to Delta Lake"""

    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get('audit', {}).get('enabled', True)
        self.base_path = config.get('audit', {}).get('path', '/data/audit/live_gateway')

        # Note: Keeping implementation simple - Delta Lake requires pyarrow/deltalake
        # which were commented out in requirements.txt due to size
        # This is a placeholder implementation that logs to files

        # Create audit directories
        self.orders_path = Path(self.base_path) / 'orders'
        self.modes_path = Path(self.base_path) / 'mode_changes'
        self.circuits_path = Path(self.base_path) / 'circuit_events'

        if self.enabled:
            self.orders_path.mkdir(parents=True, exist_ok=True)
            self.modes_path.mkdir(parents=True, exist_ok=True)
            self.circuits_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"AuditLogger initialized: enabled={self.enabled}, path={self.base_path}")

    def log_order(self, order_data: Dict[str, Any]):
        """Log order submission/routing decision"""
        if not self.enabled:
            return

        try:
            timestamp = datetime.utcnow()
            record = {
                'timestamp': timestamp.isoformat(),
                'event_type': 'ORDER',
                **order_data
            }

            # Append to file (simple implementation)
            log_file = self.orders_path / f"{timestamp.strftime('%Y-%m-%d')}.jsonl"
            with open(log_file, 'a') as f:
                import json
                f.write(json.dumps(record) + '\n')

            logger.debug(f"Audit: Order logged {order_data.get('client_order_id')}")

        except Exception as e:
            logger.error(f"Audit logging failed: {e}")

    def log_mode_change(self, mode_data: Dict[str, Any]):
        """Log trading mode changes"""
        if not self.enabled:
            return

        try:
            timestamp = datetime.utcnow()
            record = {
                'timestamp': timestamp.isoformat(),
                'event_type': 'MODE_CHANGE',
                **mode_data
            }

            log_file = self.modes_path / f"{timestamp.strftime('%Y-%m-%d')}.jsonl"
            with open(log_file, 'a') as f:
                import json
                f.write(json.dumps(record) + '\n')

            logger.info(f"Audit: Mode change logged - {mode_data}")

        except Exception as e:
            logger.error(f"Audit logging failed: {e}")

    def log_circuit_event(self, circuit_data: Dict[str, Any]):
        """Log circuit breaker state changes"""
        if not self.enabled:
            return

        try:
            timestamp = datetime.utcnow()
            record = {
                'timestamp': timestamp.isoformat(),
                'event_type': 'CIRCUIT_EVENT',
                **circuit_data
            }

            log_file = self.circuits_path / f"{timestamp.strftime('%Y-%m-%d')}.jsonl"
            with open(log_file, 'a') as f:
                import json
                f.write(json.dumps(record) + '\n')

            logger.warning(f"Audit: Circuit event logged - {circuit_data}")

        except Exception as e:
            logger.error(f"Audit logging failed: {e}")

    def log_panic(self, panic_data: Dict[str, Any]):
        """Log panic button activation"""
        if not self.enabled:
            return

        try:
            timestamp = datetime.utcnow()
            record = {
                'timestamp': timestamp.isoformat(),
                'event_type': 'PANIC',
                **panic_data
            }

            # Log to all audit streams for visibility
            for path in [self.orders_path, self.modes_path, self.circuits_path]:
                log_file = path / f"{timestamp.strftime('%Y-%m-%d')}.jsonl"
                with open(log_file, 'a') as f:
                    import json
                    f.write(json.dumps(record) + '\n')

            logger.critical(f"Audit: PANIC logged - {panic_data}")

        except Exception as e:
            logger.error(f"Audit logging failed: {e}")

    def query_orders(self, start_date: datetime, end_date: datetime) -> list:
        """Query orders from audit log (simple file-based implementation)"""
        if not self.enabled:
            return []

        results = []
        current_date = start_date.date()
        end = end_date.date()

        while current_date <= end:
            log_file = self.orders_path / f"{current_date.isoformat()}.jsonl"
            if log_file.exists():
                with open(log_file, 'r') as f:
                    import json
                    for line in f:
                        record = json.loads(line)
                        record_ts = datetime.fromisoformat(record['timestamp'])
                        if start_date <= record_ts <= end_date:
                            results.append(record)

            current_date = (current_date + timedelta(days=1))

        return results


# Note for production: To use real Delta Lake:
# 1. Uncomment deltalake and pyarrow in requirements.txt
# 2. Replace file-based logging with:
#    from deltalake import write_deltalake
#    write_deltalake(table_path, [record], mode='append')
# 3. Query with:
#    from deltalake import DeltaTable
#    dt = DeltaTable(table_path)
#    df = dt.to_pyarrow_table().to_pandas()
