#!/usr/bin/env python3
"""
Latency Test for Risk and OMS Services
Tests SLA requirements:
- Risk service: P50 <= 1.5ms
- OMS: P50 <= 10ms, P99 <= 50ms
"""

import requests
import time
import statistics

def test_oms_latency(num_requests=100):
    """Test OMS latency with order submission"""
    print("=== Testing OMS Latency ===")
    print(f"Running {num_requests} requests...")

    latencies = []
    errors = 0

    for i in range(num_requests):
        order = {
            "account": "test_account",
            "symbol": "BTCUSDT",
            "side": "buy" if i % 2 == 0 else "sell",
            "type": "limit",
            "quantity": 0.001,
            "price": 45000.0 + (i % 100),
            "order_type": "LIMIT"
        }

        try:
            start = time.perf_counter()
            response = requests.post('http://localhost:8099/orders', json=order, timeout=1)
            elapsed_ms = (time.perf_counter() - start) * 1000

            if response.status_code == 200:
                latencies.append(elapsed_ms)
            else:
                errors += 1

            # Progress indicator
            if (i + 1) % 20 == 0:
                print(f"  Processed {i + 1}/{num_requests} requests...")

        except Exception as e:
            errors += 1
            print(f"  Error on request {i}: {e}")

    if latencies:
        # Calculate statistics
        p50 = statistics.median(latencies)
        p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else max(latencies)
        p99 = statistics.quantiles(latencies, n=100)[98] if len(latencies) > 100 else max(latencies)

        print(f"\nOMS Latency Results ({len(latencies)} successful requests):")
        print(f"  P50: {p50:.2f}ms (SLA: <= 10ms) {'PASS' if p50 <= 10 else 'FAIL'}")
        print(f"  P95: {p95:.2f}ms")
        print(f"  P99: {p99:.2f}ms (SLA: <= 50ms) {'PASS' if p99 <= 50 else 'FAIL'}")
        print(f"  Min: {min(latencies):.2f}ms")
        print(f"  Max: {max(latencies):.2f}ms")
        print(f"  Avg: {statistics.mean(latencies):.2f}ms")
        print(f"  Errors: {errors}")

        # Check SLAs
        oms_sla_passed = p50 <= 10 and p99 <= 50
        return oms_sla_passed, p50, p99
    else:
        print("  No successful requests!")
        return False, 0, 0

def test_risk_latency(num_requests=100):
    """Test Risk service latency directly"""
    print("\n=== Testing Risk Service Latency ===")
    print(f"Running {num_requests} requests...")

    latencies = []
    errors = 0

    for i in range(num_requests):
        risk_check = {
            "account": f"test_account_{i % 10}",
            "symbol": "BTCUSDT",
            "side": "buy",
            "quantity": 0.001,
            "price": 45000.0
        }

        try:
            start = time.perf_counter()
            response = requests.post('http://localhost:8103/check', json=risk_check, timeout=0.01)
            elapsed_ms = (time.perf_counter() - start) * 1000

            if response.status_code == 200:
                latencies.append(elapsed_ms)
            else:
                errors += 1

            # Progress indicator
            if (i + 1) % 20 == 0:
                print(f"  Processed {i + 1}/{num_requests} requests...")

        except requests.Timeout:
            errors += 1
            # Timeout means it's too slow
            latencies.append(10.0)  # Add penalty for timeout
        except Exception as e:
            errors += 1

    if latencies:
        # Calculate statistics
        p50 = statistics.median(latencies)
        p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else max(latencies)
        p99 = statistics.quantiles(latencies, n=100)[98] if len(latencies) > 100 else max(latencies)

        print(f"\nRisk Service Latency Results ({len(latencies)} measurements):")
        print(f"  P50: {p50:.2f}ms (SLA: <= 1.5ms) {'PASS' if p50 <= 1.5 else 'FAIL'}")
        print(f"  P95: {p95:.2f}ms")
        print(f"  P99: {p99:.2f}ms")
        print(f"  Min: {min(latencies):.2f}ms")
        print(f"  Max: {max(latencies):.2f}ms")
        print(f"  Avg: {statistics.mean(latencies):.2f}ms")
        print(f"  Errors/Timeouts: {errors}")

        # Check SLA
        risk_sla_passed = p50 <= 1.5
        return risk_sla_passed, p50
    else:
        print("  No successful requests!")
        return False, 0

if __name__ == "__main__":
    print("Task 04 Critical Validation - Latency Testing\n")

    # Test OMS latency (includes risk checks)
    oms_passed, oms_p50, oms_p99 = test_oms_latency(100)

    # Test Risk service directly
    risk_passed, risk_p50 = test_risk_latency(100)

    # Summary
    print("\n" + "="*50)
    print("LATENCY TEST SUMMARY")
    print("="*50)

    if oms_passed and risk_passed:
        print("RESULT: ALL SLAs PASSED")
        print("  - OMS: P50={:.2f}ms (<=10ms), P99={:.2f}ms (<=50ms)".format(oms_p50, oms_p99))
        print("  - Risk: P50={:.2f}ms (<=1.5ms)".format(risk_p50))
    else:
        print("RESULT: SLA VIOLATION DETECTED")
        if not oms_passed:
            print("  - OMS failed SLA requirements")
        if not risk_passed:
            print("  - Risk service failed SLA requirements (P50 > 1.5ms)")
        print("\nNote: Risk service may need optimization or the /check endpoint may not be implemented yet.")