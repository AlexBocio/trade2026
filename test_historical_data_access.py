#!/usr/bin/env python
"""Test historical data access from Portfolio Optimizer"""

import requests
import json
import time

print("Testing Historical Data Access from Backend Services")
print("=" * 80)

# Test 1: Portfolio Optimizer with sector ETFs (have historical data)
print("\nTest 1: Portfolio Optimizer - Sector ETFs (XLE, XLF, XLI)")
print("-" * 80)

payload1 = {
    "symbols": ["XLE", "XLF", "XLI"],  # Sector ETFs with ~40-50 days of data
    "start_date": "2025-09-01",
    "end_date": "2025-10-23"
}

try:
    response = requests.post(
        "http://localhost:5001/api/portfolio/optimize",
        json=payload1,
        timeout=30
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"SUCCESS: Got {len(result.get('weights', {}))} weights")
        print(f"Weights: {json.dumps(result.get('weights', {}), indent=2)}")
    else:
        print(f"Response: {response.text}")

except Exception as e:
    print(f"ERROR: {e}")

# Test 2: Portfolio Optimizer with SPY, QQQ, TLT (have 93 days of data)
print("\n\nTest 2: Portfolio Optimizer - Major ETFs (SPY, QQQ, TLT)")
print("-" * 80)

payload2 = {
    "symbols": ["SPY", "QQQ", "TLT"],  # Major ETFs with 93 days of data
    "start_date": "2025-08-01",
    "end_date": "2025-10-23"
}

try:
    response = requests.post(
        "http://localhost:5001/api/portfolio/optimize",
        json=payload2,
        timeout=30
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"SUCCESS: Got {len(result.get('weights', {}))} weights")
        print(f"Weights: {json.dumps(result.get('weights', {}), indent=2)}")
        print(f"Expected Return: {result.get('expected_return', 'N/A')}")
        print(f"Volatility: {result.get('volatility', 'N/A')}")
        print(f"Sharpe Ratio: {result.get('sharpe_ratio', 'N/A')}")
    else:
        print(f"Response: {response.text}")

except Exception as e:
    print(f"ERROR: {e}")

# Test 3: Stock Screener health check
print("\n\nTest 3: Stock Screener - Health Check")
print("-" * 80)

try:
    response = requests.get("http://localhost:5008/health", timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"SUCCESS: {response.json()}")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 80)
print("Test Complete")
