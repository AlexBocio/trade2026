"""
Optional OpenSearch Client (Apache-2.0 Licensed)
Phase 7B: Data Lake Sinks
"""

import logging
from typing import Optional, Dict, Any, List
import json

logger = logging.getLogger(__name__)

# OpenSearch is optional - only import if enabled
try:
    from opensearchpy import OpenSearch, helpers
    from opensearchpy.exceptions import ConnectionError, NotFoundError
    OPENSEARCH_AVAILABLE = True
except ImportError:
    OPENSEARCH_AVAILABLE = False
    logger.info("OpenSearch client not available - install opensearch-py if needed")


class OpenSearchClient:
    """OpenSearch client for optional full-text indexing"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenSearch client

        Args:
            config: OpenSearch configuration with url, index, etc.
        """
        self.enabled = config.get('enabled', False)
        self.url = config.get('url', 'http://localhost:9200')
        self.index = config.get('index', 'alt_news')
        self.client = None
        self._connected = False

        if not self.enabled:
            logger.info("OpenSearch indexing disabled")
            return

        if not OPENSEARCH_AVAILABLE:
            logger.warning("OpenSearch enabled but opensearch-py not installed")
            self.enabled = False
            return

        self._initialize_client()

    def _initialize_client(self):
        """Initialize OpenSearch client"""
        try:
            # Parse URL for host and port
            from urllib.parse import urlparse
            parsed = urlparse(self.url)

            # Create client (development mode - no auth)
            self.client = OpenSearch(
                hosts=[{
                    'host': parsed.hostname or 'localhost',
                    'port': parsed.port or 9200
                }],
                http_compress=True,
                use_ssl=False,
                verify_certs=False,
                ssl_assert_hostname=False,
                ssl_show_warn=False
            )

            # Test connection
            info = self.client.info()
            logger.info(f"Connected to OpenSearch {info['version']['number']}")
            self._connected = True

            # Ensure index exists with proper mapping
            self._ensure_index()

        except Exception as e:
            logger.error(f"Failed to connect to OpenSearch: {e}")
            self._connected = False

    def _ensure_index(self):
        """Ensure index exists with proper mapping"""
        if not self._connected:
            return

        try:
            # Check if index exists
            if not self.client.indices.exists(index=self.index):
                # Create index with mapping
                mapping = {
                    "mappings": {
                        "properties": {
                            "event_ts": {"type": "date"},
                            "fetch_ts": {"type": "date"},
                            "source": {"type": "keyword"},
                            "source_type": {"type": "keyword"},
                            "category": {"type": "keyword"},
                            "title": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword", "ignore_above": 256}
                                }
                            },
                            "url": {"type": "keyword"},
                            "summary": {"type": "text"},
                            "author": {"type": "keyword"},
                            "lang": {"type": "keyword"},
                            "score": {"type": "float"},
                            "symbol": {"type": "keyword"},
                            "tags": {"type": "keyword"},
                            "hash_id": {"type": "keyword"}
                        }
                    }
                }

                self.client.indices.create(index=self.index, body=mapping)
                logger.info(f"Created OpenSearch index '{self.index}'")
            else:
                logger.info(f"OpenSearch index '{self.index}' exists")

        except Exception as e:
            logger.error(f"Failed to ensure index: {e}")

    def index_document(self, doc: Dict[str, Any]) -> bool:
        """
        Index a single document

        Args:
            doc: Document to index (must have hash_id)

        Returns:
            True if successful
        """
        if not self.enabled or not self._connected:
            return False

        try:
            # Use hash_id as document ID for idempotency
            doc_id = doc.get('hash_id')
            if not doc_id:
                logger.warning("Document missing hash_id, skipping index")
                return False

            # Index document
            response = self.client.index(
                index=self.index,
                id=doc_id,
                body=doc,
                refresh=False  # Don't refresh immediately for performance
            )

            return response['result'] in ['created', 'updated']

        except Exception as e:
            logger.error(f"Failed to index document: {e}")
            return False

    def bulk_index(self, docs: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Bulk index documents

        Args:
            docs: List of documents to index

        Returns:
            Dict with counts of indexed, failed
        """
        if not self.enabled or not self._connected or not docs:
            return {'indexed': 0, 'failed': 0}

        try:
            # Prepare bulk actions
            actions = []
            for doc in docs:
                doc_id = doc.get('hash_id')
                if not doc_id:
                    continue

                actions.append({
                    '_op_type': 'index',
                    '_index': self.index,
                    '_id': doc_id,
                    '_source': doc
                })

            if not actions:
                return {'indexed': 0, 'failed': 0}

            # Bulk index
            success, failed = helpers.bulk(
                self.client,
                actions,
                raise_on_error=False,
                raise_on_exception=False
            )

            if failed:
                logger.warning(f"Failed to index {len(failed)} documents")

            return {'indexed': success, 'failed': len(failed)}

        except Exception as e:
            logger.error(f"Bulk indexing failed: {e}")
            return {'indexed': 0, 'failed': len(docs)}

    def search(self, query: str, size: int = 10) -> List[Dict[str, Any]]:
        """
        Search documents

        Args:
            query: Search query
            size: Number of results

        Returns:
            List of matching documents
        """
        if not self.enabled or not self._connected:
            return []

        try:
            # Simple query string search
            body = {
                "query": {
                    "query_string": {
                        "query": query,
                        "fields": ["title^2", "summary", "tags"]
                    }
                },
                "size": size,
                "sort": [{"event_ts": {"order": "desc"}}]
            }

            response = self.client.search(index=self.index, body=body)

            # Extract documents
            results = []
            for hit in response['hits']['hits']:
                results.append(hit['_source'])

            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def count(self) -> int:
        """Get total document count"""
        if not self.enabled or not self._connected:
            return 0

        try:
            response = self.client.count(index=self.index)
            return response['count']
        except:
            return 0

    def health_check(self) -> bool:
        """Check OpenSearch health"""
        if not self.enabled:
            return True  # Return True if disabled

        try:
            health = self.client.cluster.health()
            return health['status'] in ['green', 'yellow']
        except:
            return False

    @property
    def is_connected(self) -> bool:
        """Check if connected to OpenSearch"""
        return self._connected if self.enabled else True


def create_opensearch_client(config: Dict[str, Any]) -> OpenSearchClient:
    """Factory function to create OpenSearch client"""
    return OpenSearchClient(config)