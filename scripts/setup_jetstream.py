#!/usr/bin/env python3
"""
Setup JetStream streams for Trade2026
"""
import asyncio
import nats
from nats.js.api import StreamConfig

async def setup_streams():
    """Create required JetStream streams"""
    # Connect to NATS
    nc = await nats.connect("nats://localhost:4222")
    js = nc.jetstream()

    # Stream 1: Market Ticks
    try:
        stream_config = StreamConfig(
            name="MARKET_TICKS",
            subjects=["market.tick.>"],
            max_age=86400 * 1_000_000_000,  # 24 hours in nanoseconds
            storage="file",
            retention="limits",
            discard="old"
        )
        await js.add_stream(stream_config)
        print("✓ Created MARKET_TICKS stream")
    except Exception as e:
        print(f"MARKET_TICKS stream: {e}")

    # Stream 2: Alt Data
    try:
        stream_config = StreamConfig(
            name="ALT_DATA",
            subjects=["alt.norm.>"],
            max_age=86400 * 1_000_000_000,  # 24 hours
            storage="file",
            retention="limits",
            discard="old"
        )
        await js.add_stream(stream_config)
        print("✓ Created ALT_DATA stream")
    except Exception as e:
        print(f"ALT_DATA stream: {e}")

    # List streams
    print("\nExisting streams:")
    async for stream in js.streams_info():
        print(f"  - {stream.config.name}: {stream.config.subjects}")

    await nc.close()
    print("\n✓ JetStream setup complete")

if __name__ == "__main__":
    asyncio.run(setup_streams())
