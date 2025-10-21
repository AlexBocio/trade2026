"""Quick performance test for PRISM"""
import requests
import time

BASE_URL = "http://localhost:8360"
NUM_ORDERS = 50

print("=== Quick PRISM Performance Test ===\n")

# Test order throughput
print(f"Submitting {NUM_ORDERS} market orders...")
start = time.time()
successful = 0

for i in range(NUM_ORDERS):
    try:
        response = requests.post(
            f"{BASE_URL}/orders",
            json={
                "symbol": "BTCUSDT",
                "side": "buy" if i % 2 == 0 else "sell",
                "order_type": "market",
                "quantity": 0.01
            },
            timeout=5
        )
        if response.status_code == 200:
            successful += 1
    except:
        pass

end = time.time()
duration = end - start

print(f"\nResults:")
print(f"  Orders Submitted: {NUM_ORDERS}")
print(f"  Successful: {successful}")
print(f"  Duration: {duration:.2f}s")
print(f"  Throughput: {successful/duration:.2f} orders/sec")
print(f"  Avg Latency: {(duration/successful)*1000:.2f}ms per order")
