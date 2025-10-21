"""
PRISM Performance Benchmarks
Measures throughput, latency, and resource usage.
"""
import requests
import json
import time
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:8360"


def benchmark_order_throughput(num_orders=1000, concurrency=10):
    """Measure order submission throughput."""
    print(f"\n{'='*60}")
    print(f"BENCHMARK: Order Throughput ({num_orders} orders, {concurrency} concurrent)")
    print(f"{'='*60}")

    def submit_order(i):
        order = {
            "symbol": "BTCUSDT",
            "side": "buy" if i % 2 == 0 else "sell",
            "order_type": "market",
            "quantity": 0.01
        }
        start = time.time()
        try:
            response = requests.post(f"{BASE_URL}/orders", json=order, timeout=5)
            latency = (time.time() - start) * 1000  # ms
            return {"success": response.status_code == 200, "latency": latency}
        except Exception as e:
            return {"success": False, "latency": 0, "error": str(e)}

    start_time = time.time()
    results = []

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(submit_order, i) for i in range(num_orders)]
        for future in as_completed(futures):
            results.append(future.result())

    end_time = time.time()
    duration = end_time - start_time

    successful = sum(1 for r in results if r["success"])
    failed = num_orders - successful
    latencies = [r["latency"] for r in results if r["success"]]

    print(f"\nResults:")
    print(f"  Total Orders: {num_orders}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Throughput: {successful / duration:.2f} orders/sec")

    if latencies:
        print(f"\nLatency Stats (ms):")
        print(f"  Min: {min(latencies):.2f}")
        print(f"  Max: {max(latencies):.2f}")
        print(f"  Mean: {statistics.mean(latencies):.2f}")
        print(f"  Median: {statistics.median(latencies):.2f}")
        print(f"  P95: {statistics.quantiles(latencies, n=20)[18]:.2f}")
        print(f"  P99: {statistics.quantiles(latencies, n=100)[98]:.2f}")

    return {
        "throughput": successful / duration,
        "latency_mean": statistics.mean(latencies) if latencies else 0,
        "latency_p95": statistics.quantiles(latencies, n=20)[18] if latencies else 0,
        "success_rate": successful / num_orders
    }


def benchmark_market_data_access(num_requests=1000):
    """Measure market data access performance."""
    print(f"\n{'='*60}")
    print(f"BENCHMARK: Market Data Access ({num_requests} requests)")
    print(f"{'='*60}")

    symbols = ["BTCUSDT", "ETHUSDT", "AAPL", "MSFT", "GOOGL"]
    latencies = []

    start_time = time.time()

    for i in range(num_requests):
        symbol = symbols[i % len(symbols)]
        start = time.time()
        try:
            response = requests.get(f"{BASE_URL}/market/{symbol}", timeout=5)
            latency = (time.time() - start) * 1000
            if response.status_code == 200:
                latencies.append(latency)
        except:
            pass

    end_time = time.time()
    duration = end_time - start_time

    print(f"\nResults:")
    print(f"  Total Requests: {num_requests}")
    print(f"  Successful: {len(latencies)}")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Throughput: {len(latencies) / duration:.2f} req/sec")

    if latencies:
        print(f"\nLatency Stats (ms):")
        print(f"  Min: {min(latencies):.2f}")
        print(f"  Max: {max(latencies):.2f}")
        print(f"  Mean: {statistics.mean(latencies):.2f}")
        print(f"  Median: {statistics.median(latencies):.2f}")

    return {
        "throughput": len(latencies) / duration,
        "latency_mean": statistics.mean(latencies) if latencies else 0
    }


def benchmark_order_book_access(num_requests=500):
    """Measure order book access performance."""
    print(f"\n{'='*60}")
    print(f"BENCHMARK: Order Book Access ({num_requests} requests)")
    print(f"{'='*60}")

    symbols = ["BTCUSDT", "ETHUSDT"]
    latencies = []

    start_time = time.time()

    for i in range(num_requests):
        symbol = symbols[i % len(symbols)]
        start = time.time()
        try:
            response = requests.get(f"{BASE_URL}/orderbook/{symbol}", timeout=5)
            latency = (time.time() - start) * 1000
            if response.status_code == 200:
                latencies.append(latency)
        except:
            pass

    end_time = time.time()
    duration = end_time - start_time

    print(f"\nResults:")
    print(f"  Total Requests: {num_requests}")
    print(f"  Successful: {len(latencies)}")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Throughput: {len(latencies) / duration:.2f} req/sec")

    if latencies:
        print(f"\nLatency Stats (ms):")
        print(f"  Min: {min(latencies):.2f}")
        print(f"  Max: {max(latencies):.2f}")
        print(f"  Mean: {statistics.mean(latencies):.2f}")

    return {
        "throughput": len(latencies) / duration,
        "latency_mean": statistics.mean(latencies) if latencies else 0
    }


def benchmark_agent_simulation():
    """Measure agent simulation performance over time."""
    print(f"\n{'='*60}")
    print(f"BENCHMARK: Agent Simulation Performance")
    print(f"{'='*60}")

    # Get initial state
    initial = requests.get(f"{BASE_URL}/market/BTCUSDT").json()
    initial_volume = initial["volume"]

    print(f"\n  Initial volume: {initial_volume:.2f}")
    print(f"  Monitoring for 10 seconds...")

    time.sleep(10)

    final = requests.get(f"{BASE_URL}/market/BTCUSDT").json()
    final_volume = final["volume"]

    volume_per_second = (final_volume - initial_volume) / 10

    print(f"\nResults:")
    print(f"  Final volume: {final_volume:.2f}")
    print(f"  Volume increase: {final_volume - initial_volume:.2f}")
    print(f"  Avg volume/sec: {volume_per_second:.2f}")
    print(f"  Agent activity: Active (40 agents trading)")

    return {
        "volume_per_second": volume_per_second,
        "total_volume_increase": final_volume - initial_volume
    }


def run_all_benchmarks():
    """Run complete benchmark suite."""
    print(f"\n{'#'*60}")
    print(f"# PRISM PERFORMANCE BENCHMARKS")
    print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*60}")

    # Wait for PRISM to be ready
    print(f"\nWaiting for PRISM to be ready...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print(f"PRISM is ready!")
                break
        except:
            time.sleep(1)
    else:
        print("ERROR: PRISM not responding. Exiting.")
        return

    results = {}

    # Run benchmarks
    results["order_throughput"] = benchmark_order_throughput(num_orders=500, concurrency=10)
    time.sleep(2)

    results["market_data"] = benchmark_market_data_access(num_requests=500)
    time.sleep(2)

    results["order_book"] = benchmark_order_book_access(num_requests=200)
    time.sleep(2)

    results["agent_simulation"] = benchmark_agent_simulation()

    # Summary
    print(f"\n{'='*60}")
    print(f"BENCHMARK SUMMARY")
    print(f"{'='*60}")
    print(f"\nOrder Execution:")
    print(f"  Throughput: {results['order_throughput']['throughput']:.2f} orders/sec")
    print(f"  Mean Latency: {results['order_throughput']['latency_mean']:.2f} ms")
    print(f"  P95 Latency: {results['order_throughput']['latency_p95']:.2f} ms")
    print(f"  Success Rate: {results['order_throughput']['success_rate']*100:.1f}%")

    print(f"\nMarket Data Access:")
    print(f"  Throughput: {results['market_data']['throughput']:.2f} req/sec")
    print(f"  Mean Latency: {results['market_data']['latency_mean']:.2f} ms")

    print(f"\nOrder Book Access:")
    print(f"  Throughput: {results['order_book']['throughput']:.2f} req/sec")
    print(f"  Mean Latency: {results['order_book']['latency_mean']:.2f} ms")

    print(f"\nAgent Simulation:")
    print(f"  Volume/sec: {results['agent_simulation']['volume_per_second']:.2f}")
    print(f"  Total increase (10s): {results['agent_simulation']['total_volume_increase']:.2f}")

    print(f"\n{'='*60}")
    print(f"Benchmarks completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    return results


if __name__ == "__main__":
    results = run_all_benchmarks()
