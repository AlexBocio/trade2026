#!/usr/bin/env python3
"""
Simplified Load Test for OMS
Tests throughput and stability
"""

import requests
import time
import concurrent.futures
import statistics
from datetime import datetime

def submit_order(order_num):
    """Submit a single order"""
    order = {
        "account": f"test_account_{order_num % 10}",
        "symbol": "BTCUSDT",
        "side": "buy" if order_num % 2 == 0 else "sell",
        "type": "limit",
        "quantity": 0.001,
        "price": 45000.0 + (order_num % 100),
        "order_type": "LIMIT"
    }

    try:
        start = time.perf_counter()
        response = requests.post('http://localhost:8099/orders', json=order, timeout=5)
        elapsed = time.perf_counter() - start

        return {
            'success': response.status_code == 200,
            'elapsed': elapsed,
            'order_num': order_num
        }
    except Exception as e:
        return {
            'success': False,
            'elapsed': 5.0,
            'order_num': order_num,
            'error': str(e)
        }

def run_load_test(total_orders=100, workers=10):
    """Run load test with specified number of orders and workers"""
    print(f"=== Load Test: {total_orders} orders with {workers} workers ===")
    print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit all orders
        futures = [executor.submit(submit_order, i) for i in range(total_orders)]

        # Collect results with progress
        results = []
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            results.append(future.result())
            if (i + 1) % 10 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                print(f"  Progress: {i + 1}/{total_orders} orders, Rate: {rate:.1f} orders/sec")

    # Calculate statistics
    total_time = time.time() - start_time
    successful = sum(1 for r in results if r['success'])
    failed = total_orders - successful
    latencies = [r['elapsed'] * 1000 for r in results if r['success']]

    print(f"\n=== Load Test Results ===")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Total orders: {total_orders}")
    print(f"Successful: {successful} ({successful/total_orders*100:.1f}%)")
    print(f"Failed: {failed}")
    print(f"Throughput: {total_orders/total_time:.1f} orders/sec")

    if latencies:
        print(f"\nLatency Statistics (ms):")
        print(f"  Min: {min(latencies):.2f}")
        print(f"  Max: {max(latencies):.2f}")
        print(f"  Avg: {statistics.mean(latencies):.2f}")
        print(f"  P50: {statistics.median(latencies):.2f}")
        if len(latencies) > 10:
            print(f"  P95: {statistics.quantiles(latencies, n=20)[18]:.2f}")
        if len(latencies) > 100:
            print(f"  P99: {statistics.quantiles(latencies, n=100)[98]:.2f}")

    return successful, total_time, total_orders/total_time

if __name__ == "__main__":
    print("Task 04 - Simplified Load Test\n")

    # Warm up with a few orders
    print("Warming up...")
    for i in range(5):
        submit_order(i)

    print("\n")

    # Test with increasing load
    tests = [
        (10, 2),     # 10 orders, 2 workers
        (50, 5),     # 50 orders, 5 workers
        (100, 10),   # 100 orders, 10 workers
        (200, 20),   # 200 orders, 20 workers
    ]

    for total, workers in tests:
        successful, duration, rate = run_load_test(total, workers)
        print(f"\n{'='*50}\n")
        time.sleep(2)  # Brief pause between tests

    print("Load testing complete!")