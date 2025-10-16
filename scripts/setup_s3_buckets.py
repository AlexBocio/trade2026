#!/usr/bin/env python3
"""
Setup S3 buckets in SeaweedFS for Trade2026
"""
import boto3
from botocore.client import Config

# SeaweedFS S3 configuration
s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:8333',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

def create_bucket(bucket_name):
    """Create S3 bucket if it doesn't exist"""
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"✓ Bucket '{bucket_name}' already exists")
    except:
        try:
            s3.create_bucket(Bucket=bucket_name)
            print(f"✓ Created bucket '{bucket_name}'")
        except Exception as e:
            print(f"✗ Failed to create '{bucket_name}': {e}")

def list_buckets():
    """List all buckets"""
    try:
        response = s3.list_buckets()
        print("\nExisting buckets:")
        for bucket in response.get('Buckets', []):
            print(f"  - {bucket['Name']}")
    except Exception as e:
        print(f"Failed to list buckets: {e}")

if __name__ == "__main__":
    print("=== Setting up S3 buckets ===\n")

    # Create required buckets
    create_bucket('trader2025')  # Main bucket for delta lake
    create_bucket('trader2026')  # Future bucket

    # List all buckets
    list_buckets()

    print("\n✓ S3 setup complete")
