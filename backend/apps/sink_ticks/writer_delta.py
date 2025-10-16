"""
Delta Lake Writer for Market Ticks
Phase 7B: Data Lake Sinks
"""

import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from deltalake import write_deltalake, DeltaTable
from deltalake.exceptions import TableNotFoundError

logger = logging.getLogger(__name__)


class DeltaWriter:
    """Delta Lake writer with schema management and compaction"""

    def __init__(self, table_uri: str, partition_by: List[str] = None,
                 compression: str = 'zstd', enable_compaction: bool = False,
                 small_file_target_mb: int = 256, writer_threads: int = 2):
        """
        Initialize Delta writer

        Args:
            table_uri: S3 URI for Delta table
            partition_by: List of partition columns
            compression: Compression type (zstd, snappy, gzip)
            enable_compaction: Enable automatic compaction
            small_file_target_mb: Target file size for compaction
            writer_threads: Number of writer threads
        """
        self.table_uri = table_uri
        self.partition_by = partition_by or ['dt']
        self.compression = compression
        self.enable_compaction = enable_compaction
        self.small_file_target_mb = small_file_target_mb
        self.writer_threads = writer_threads

        # Stats
        self.stats = {
            'batches_written': 0,
            'rows_written': 0,
            'bytes_written': 0,
            'write_errors': 0,
            'compactions': 0
        }

        # Delta table instance
        self.delta_table = None
        self._table_exists = False

        # Skip table check during init to avoid blocking
        logger.info(f"Delta writer initialized for {self.table_uri}")

    def _check_table(self):
        """Check if Delta table exists (called lazily on first write)"""
        if self.delta_table is not None:
            return

        try:
            self.delta_table = DeltaTable(self.table_uri)
            self._table_exists = True
            logger.info(f"Delta table exists at {self.table_uri}")

            # Log table info
            version = self.delta_table.version()
            files = len(self.delta_table.files())
            logger.info(f"Table version: {version}, files: {files}")

        except TableNotFoundError:
            logger.info(f"Delta table does not exist at {self.table_uri}, will create on first write")
            self._table_exists = False
        except Exception as e:
            logger.warning(f"Error checking Delta table: {e}, will attempt write anyway")
            self._table_exists = False

    def write_batch(self, records: List[Dict[str, Any]]) -> bool:
        """
        Write a batch of records to Delta table

        Args:
            records: List of tick records

        Returns:
            True if successful
        """
        if not records:
            return True

        # Check table on first write
        if self.delta_table is None and self._table_exists is False:
            self._check_table()

        try:
            # Convert to DataFrame
            df = pd.DataFrame(records)

            # Ensure datetime columns are proper type
            if 'event_ts' in df.columns:
                df['event_ts'] = pd.to_datetime(df['event_ts'])
            if 'ingest_ts' in df.columns:
                df['ingest_ts'] = pd.to_datetime(df['ingest_ts'])

            # Ensure partition column exists
            if 'dt' not in df.columns and 'event_ts' in df.columns:
                df['dt'] = df['event_ts'].dt.strftime('%Y-%m-%d')

            # Replace None values with empty strings for string columns
            string_columns = ['side', 'trade_id', 'source_seq']
            for col in string_columns:
                if col in df.columns:
                    df[col] = df[col].fillna('')

            # Convert to PyArrow table
            table = pa.Table.from_pandas(df)

            # Write to Delta
            write_deltalake(
                self.table_uri,
                table,
                mode='append',
                partition_by=self.partition_by,
                engine='rust'  # Use Rust engine for performance
                # Note: writer_properties removed due to compatibility issues
            )

            # Update stats
            self.stats['batches_written'] += 1
            self.stats['rows_written'] += len(records)
            self.stats['bytes_written'] += table.nbytes

            logger.info(f"Wrote {len(records)} ticks to Delta table")

            # Mark table as existing
            if not self._table_exists:
                self._table_exists = True
                self._check_table()

            # Trigger compaction if enabled
            if self.enable_compaction and self.stats['batches_written'] % 100 == 0:
                self.compact()

            return True

        except Exception as e:
            logger.error(f"Failed to write batch to Delta: {e}")
            self.stats['write_errors'] += 1
            return False

    def compact(self, target_size_mb: Optional[int] = None) -> bool:
        """
        Compact small files in Delta table

        Args:
            target_size_mb: Target file size in MB

        Returns:
            True if successful
        """
        if not self._table_exists:
            return False

        try:
            target_size = target_size_mb or self.small_file_target_mb
            target_bytes = target_size * 1024 * 1024

            logger.info(f"Starting Delta table compaction (target: {target_size}MB)")

            # Get current table
            dt = DeltaTable(self.table_uri)

            # Note: Full compaction support requires Delta-RS features
            # For now, we'll log the intent
            # In production, you might use Spark or Delta-RS optimize command

            version_before = dt.version()
            files_before = len(dt.files())

            # Placeholder for actual compaction
            # dt.optimize.compact()  # Would be the actual command

            logger.info(f"Compaction placeholder - would compact {files_before} files")

            self.stats['compactions'] += 1
            return True

        except Exception as e:
            logger.error(f"Compaction failed: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get writer statistics"""
        stats = self.stats.copy()

        # Add table info if exists
        if self._table_exists:
            try:
                dt = DeltaTable(self.table_uri)
                stats['table_version'] = dt.version()
                stats['table_files'] = len(dt.files())
            except:
                pass

        return stats

    def get_table_info(self) -> Optional[Dict[str, Any]]:
        """Get Delta table information"""
        if not self._table_exists:
            return None

        try:
            dt = DeltaTable(self.table_uri)

            # Get schema
            schema = dt.schema()

            # Get history (last 10 operations)
            history = dt.history(limit=10)

            # Get files
            files = dt.files()

            info = {
                'uri': self.table_uri,
                'version': dt.version(),
                'num_files': len(files),
                'total_size_bytes': sum(f.get('size', 0) for f in files),
                'partition_columns': self.partition_by,
                'schema': str(schema),
                'recent_operations': history.to_dict('records') if hasattr(history, 'to_dict') else []
            }

            return info

        except Exception as e:
            logger.error(f"Failed to get table info: {e}")
            return None

    def vacuum(self, retention_hours: int = 168) -> bool:
        """
        Vacuum old files from Delta table

        Args:
            retention_hours: Files older than this are deleted

        Returns:
            True if successful
        """
        if not self._table_exists:
            return False

        try:
            dt = DeltaTable(self.table_uri)

            # Vacuum old files
            # Note: This removes files not referenced by Delta log
            # dt.vacuum(retention_hours)  # Would be the actual command

            logger.info(f"Vacuum placeholder - would clean files older than {retention_hours} hours")
            return True

        except Exception as e:
            logger.error(f"Vacuum failed: {e}")
            return False