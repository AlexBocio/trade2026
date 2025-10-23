#!/usr/bin/env python
"""Test yfinance fallback fix for Portfolio Optimizer"""

import requests
import json

print("Testing yfinance fallback fix...")
print("=" * 60)

# Test 1: Non-IBKR symbols (should use yfinance)
print("\nTest 1: Non-IBKR symbols (AAPL, MSFT, GOOGL)")
print("-" * 60)

payload = {
    "symbols": ["AAPL", "MSFT", "GOOGL"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
}

try:
    response = requests.post(
        "http://localhost:5001/api/portfolio/optimize",
        json=payload,
        timeout=30
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))

except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 60)
print("Test Complete")
