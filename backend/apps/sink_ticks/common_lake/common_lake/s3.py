"""
S3 Client for SeaweedFS
Phase 7B: Data Lake
"""

import logging
import time
from typing import Dict, Any, Optional, List, BinaryIO
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)


class S3Client:
    """S3 client for SeaweedFS"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize S3 client

        Args:
            config: S3 configuration dict with keys:
                - endpoint: S3 endpoint URL
                - region: AWS region (default: us-east-1)
                - access_key: Access key
                - secret_key: Secret key
                - bucket: Default bucket name
        """
        self.endpoint = config.get('endpoint', 'http://localhost:8333')
        self.region = config.get('region', 'us-east-1')
        self.bucket = config.get('bucket', 'trader2025')

        # Create S3 client
        self.client = boto3.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=config.get('access_key', 'test'),
            aws_secret_access_key=config.get('secret_key', 'test'),
            region_name=self.region,
            use_ssl=False,
            verify=False
        )

        self.resource = boto3.resource(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=config.get('access_key', 'test'),
            aws_secret_access_key=config.get('secret_key', 'test'),
            region_name=self.region,
            use_ssl=False,
            verify=False
        )

        # Connection status
        self.is_connected = False
        self._check_connection()

    def _check_connection(self):
        """Check S3 connection"""
        try:
            # Try to list buckets
            self.client.list_buckets()
            self.is_connected = True
            logger.info(f"Connected to S3 at {self.endpoint}")

            # Ensure default bucket exists
            self._ensure_bucket_exists(self.bucket)

        except Exception as e:
            logger.error(f"Failed to connect to S3: {e}")
            self.is_connected = False

    def _ensure_bucket_exists(self, bucket_name: str):
        """Ensure bucket exists, create if not"""
        try:
            self.client.head_bucket(Bucket=bucket_name)
            logger.info(f"Bucket {bucket_name} exists")
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                try:
                    self.client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.region}
                        if self.region != 'us-east-1' else {}
                    )
                    logger.info(f"Created bucket {bucket_name}")
                except Exception as create_error:
                    logger.error(f"Failed to create bucket {bucket_name}: {create_error}")
            else:
                logger.error(f"Error checking bucket {bucket_name}: {e}")

    def put_object(self,
                   key: str,
                   data: bytes,
                   bucket: Optional[str] = None,
                   metadata: Optional[Dict[str, str]] = None) -> bool:
        """
        Put object to S3

        Args:
            key: Object key
            data: Object data as bytes
            bucket: Bucket name (uses default if not specified)
            metadata: Optional metadata dict

        Returns:
            True if successful
        """
        bucket = bucket or self.bucket

        try:
            kwargs = {
                'Bucket': bucket,
                'Key': key,
                'Body': data
            }

            if metadata:
                kwargs['Metadata'] = metadata

            self.client.put_object(**kwargs)
            logger.debug(f"Put object {key} to {bucket}")
            return True

        except Exception as e:
            logger.error(f"Failed to put object {key}: {e}")
            return False

    def get_object(self,
                   key: str,
                   bucket: Optional[str] = None) -> Optional[bytes]:
        """
        Get object from S3

        Args:
            key: Object key
            bucket: Bucket name (uses default if not specified)

        Returns:
            Object data as bytes or None if error
        """
        bucket = bucket or self.bucket

        try:
            response = self.client.get_object(Bucket=bucket, Key=key)
            data = response['Body'].read()
            logger.debug(f"Got object {key} from {bucket}")
            return data

        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.warning(f"Object {key} not found in {bucket}")
            else:
                logger.error(f"Failed to get object {key}: {e}")
            return None

    def list_objects(self,
                     prefix: str = '',
                     bucket: Optional[str] = None,
                     max_keys: int = 1000) -> List[Dict[str, Any]]:
        """
        List objects in bucket

        Args:
            prefix: Key prefix to filter
            bucket: Bucket name (uses default if not specified)
            max_keys: Maximum number of keys to return

        Returns:
            List of object metadata dicts
        """
        bucket = bucket or self.bucket

        try:
            response = self.client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                MaxKeys=max_keys
            )

            objects = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    objects.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'etag': obj.get('ETag', '').strip('"')
                    })

            logger.debug(f"Listed {len(objects)} objects with prefix {prefix}")
            return objects

        except Exception as e:
            logger.error(f"Failed to list objects: {e}")
            return []

    def delete_object(self,
                      key: str,
                      bucket: Optional[str] = None) -> bool:
        """
        Delete object from S3

        Args:
            key: Object key
            bucket: Bucket name (uses default if not specified)

        Returns:
            True if successful
        """
        bucket = bucket or self.bucket

        try:
            self.client.delete_object(Bucket=bucket, Key=key)
            logger.debug(f"Deleted object {key} from {bucket}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete object {key}: {e}")
            return False

    def object_exists(self,
                      key: str,
                      bucket: Optional[str] = None) -> bool:
        """
        Check if object exists

        Args:
            key: Object key
            bucket: Bucket name (uses default if not specified)

        Returns:
            True if object exists
        """
        bucket = bucket or self.bucket

        try:
            self.client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(f"Error checking object {key}: {e}")
                return False

    def get_presigned_url(self,
                          key: str,
                          bucket: Optional[str] = None,
                          expiration: int = 3600) -> Optional[str]:
        """
        Generate presigned URL for object

        Args:
            key: Object key
            bucket: Bucket name (uses default if not specified)
            expiration: URL expiration in seconds

        Returns:
            Presigned URL or None if error
        """
        bucket = bucket or self.bucket

        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=expiration
            )
            return url

        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None

    def health_check(self) -> bool:
        """Check S3 health"""
        try:
            self.client.list_buckets()
            return True
        except Exception:
            return False


def create_s3_client(config: Dict[str, Any]) -> S3Client:
    """
    Create S3 client instance

    Args:
        config: S3 configuration dict

    Returns:
        S3Client instance
    """
    return S3Client(config)


def wait_for_s3(endpoint: str, timeout: int = 30, retry_interval: int = 5):
    """
    Wait for S3 endpoint to be available

    Args:
        endpoint: S3 endpoint URL
        timeout: Maximum time to wait in seconds
        retry_interval: Time between retries in seconds
    """
    import requests

    logger.info(f"Waiting for S3 at {endpoint}")

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Try to connect to S3 endpoint (S3 API returns XML on root)
            response = requests.get(endpoint, timeout=2)
            if response.status_code in [200, 403]:  # S3 returns 200 with XML or 403 without auth
                logger.info("S3 endpoint is available")
                return
        except Exception:
            pass

        time.sleep(retry_interval)

    logger.warning(f"S3 endpoint at {endpoint} not responding after {timeout} seconds, continuing anyway")
    # Don't raise error, just continue
    return