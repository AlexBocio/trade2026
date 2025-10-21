#!/usr/bin/env python3
"""
Quick test script to verify NATS event publishing.
"""
import asyncio
import sys
from uuid import uuid4

# Add src to path
sys.path.insert(0, '/app/src')

from messaging import nats_client, publisher


async def test_nats_publish():
    """Test NATS publishing."""
    print("=" * 60)
    print("NATS Integration Test")
    print("=" * 60)

    # Connect to NATS
    print("\n1. Connecting to NATS...")
    try:
        await nats_client.connect()
        print(f"   ✅ Connected: {nats_client.connected}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return

    # Publish test entity registered event
    print("\n2. Publishing entity registered event...")
    try:
        await publisher.publish_entity_registered(
            entity_id=str(uuid4()),
            entity_name="test-strategy-alpha",
            entity_type="strategy",
            version="1.0.0",
            metadata={
                "author": "test-user",
                "description": "Test strategy for NATS verification",
                "test": True
            }
        )
        print("   ✅ Entity registered event published")
    except Exception as e:
        print(f"   ❌ Publish failed: {e}")

    # Publish test deployment completed event
    print("\n3. Publishing deployment completed event...")
    try:
        await publisher.publish_deployment_completed(
            deployment_id=str(uuid4()),
            entity_id=str(uuid4()),
            entity_name="test-strategy-alpha",
            entity_type="strategy",
            version="1.0.0",
            environment="test",
            status="success"
        )
        print("   ✅ Deployment completed event published")
    except Exception as e:
        print(f"   ❌ Publish failed: {e}")

    # Give subscriber time to receive
    print("\n4. Waiting for message propagation...")
    await asyncio.sleep(1)

    # Disconnect
    print("\n5. Disconnecting from NATS...")
    try:
        await nats_client.disconnect()
        print("   ✅ Disconnected")
    except Exception as e:
        print(f"   ❌ Disconnect failed: {e}")

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_nats_publish())
