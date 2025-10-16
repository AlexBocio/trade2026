# Common Lake Library

Shared utilities for Data Lake sink services.

## Components

- **s3.py**: SeaweedFS S3 client with health checks and retry logic
- **os_client.py**: Optional OpenSearch client (Apache-2.0 licensed)
- **utils.py**: Hash functions, partition helpers, and JSON utilities

## Usage

```python
from common_lake.s3 import create_s3_client
from common_lake.os_client import create_opensearch_client
from common_lake.utils import compute_hash_id, get_partition_date

# S3 Client
s3_config = {
    'endpoint': 'http://localhost:8333',
    'bucket': 'trader2025',
    'access_key': 'test',
    'secret_key': 'test'
}
s3_client = create_s3_client(s3_config)

# OpenSearch Client (optional)
os_config = {
    'enabled': True,
    'url': 'http://localhost:9200',
    'index': 'alt_news'
}
os_client = create_opensearch_client(os_config)

# Utility functions
hash_id = compute_hash_id({'source': 'reuters', 'url': 'http://...', 'ts': '2024-01-01T12:00:00'})
partition = get_partition_date(datetime.utcnow())
```

## License

Apache-2.0