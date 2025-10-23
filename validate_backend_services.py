#!/usr/bin/env python3
"""
Comprehensive Backend Services Validation Script
Tests all 8 backend services according to system guidelines
"""

import requests
import json
import time
from typing import Dict, List, Tuple
from datetime import datetime

# Service configuration
SERVICES = [
    {"name": "Portfolio Optimizer", "port": 5001, "health": "/api/health"},
    {"name": "RL Trading", "port": 5002, "health": "/api/health"},
    {"name": "Advanced Backtest", "port": 5003, "health": "/api/health"},
    {"name": "Factor Models", "port": 5004, "health": "/api/health"},
    {"name": "Simulation Engine", "port": 5005, "health": "/api/health"},
    {"name": "Fractional Diff", "port": 5006, "health": "/api/health"},
    {"name": "Meta-Labeling", "port": 5007, "health": "/api/health"},
    {"name": "Stock Screener", "port": 5008, "health": "/api/health"},
]

# Infrastructure dependencies
INFRASTRUCTURE = [
    {"name": "NATS", "url": "http://localhost:8222/healthz"},
    {"name": "QuestDB", "url": "http://localhost:9000"},
    {"name": "ClickHouse", "url": "http://localhost:8123/ping"},
    {"name": "Valkey", "check": "docker"},  # Special check via docker exec
]


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{'=' * 80}")
    print(f"  {text}")
    print(f"{'=' * 80}\n")


def print_result(name: str, status: bool, details: str = ""):
    """Print test result"""
    icon = "[OK]" if status else "[FAIL]"
    print(f"{icon} {name:40} {details}")


def check_valkey() -> Tuple[bool, str]:
    """Check Valkey via docker exec"""
    import subprocess
    try:
        result = subprocess.run(
            ["docker", "exec", "valkey", "valkey-cli", "PING"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and "PONG" in result.stdout:
            return True, "Healthy (PONG)"
        return False, f"Unhealthy: {result.stdout}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def validate_infrastructure() -> Dict[str, bool]:
    """Validate all infrastructure dependencies"""
    print_header("Infrastructure Validation")
    results = {}

    for service in INFRASTRUCTURE:
        name = service["name"]

        if name == "Valkey":
            status, details = check_valkey()
            results[name] = status
            print_result(name, status, details)
        else:
            try:
                response = requests.get(service["url"], timeout=5)
                status = response.status_code in [200, 204]
                details = f"HTTP {response.status_code}"
                results[name] = status
                print_result(name, status, details)
            except Exception as e:
                results[name] = False
                print_result(name, False, f"Error: {str(e)[:40]}")

    return results


def validate_backend_service(service: Dict) -> Dict:
    """Validate individual backend service"""
    name = service["name"]
    port = service["port"]
    health_endpoint = f"http://localhost:{port}{service['health']}"

    result = {
        "name": name,
        "port": port,
        "healthy": False,
        "response_time": None,
        "details": {}
    }

    try:
        start_time = time.time()
        response = requests.get(health_endpoint, timeout=10)
        response_time = (time.time() - start_time) * 1000  # ms

        if response.status_code == 200:
            result["healthy"] = True
            result["response_time"] = response_time
            result["details"] = response.json()
        else:
            result["details"] = {"error": f"HTTP {response.status_code}"}

    except requests.exceptions.Timeout:
        result["details"] = {"error": "Timeout (10s)"}
    except requests.exceptions.ConnectionError:
        result["details"] = {"error": "Connection refused (service not running?)"}
    except Exception as e:
        result["details"] = {"error": str(e)}

    return result


def validate_all_backend_services() -> List[Dict]:
    """Validate all backend services"""
    print_header("Backend Services Validation")
    results = []

    for service in SERVICES:
        result = validate_backend_service(service)
        results.append(result)

        status_text = f"{result['response_time']:.0f}ms" if result['response_time'] else "FAILED"
        print_result(
            f"{result['name']} (Port {result['port']})",
            result["healthy"],
            status_text
        )

    return results


def test_data_fetcher_integration() -> Dict:
    """Test that services are using the unified data fetcher"""
    print_header("Data Fetcher Integration Test")

    # Test Portfolio Optimizer with IBKR symbol
    test_payload = {
        "tickers": ["SPY", "QQQ"],  # IBKR symbols
        "weights": [0.5, 0.5],
        "method": "min_variance"
    }

    try:
        response = requests.post(
            "http://localhost:5001/api/optimize/min-variance",
            json=test_payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print_result("Portfolio Optimizer (SPY, QQQ)", True, f"Weights: {data.get('weights', {})}")
            return {"status": "success", "data": data}
        else:
            print_result("Portfolio Optimizer Test", False, f"HTTP {response.status_code}")
            return {"status": "failed", "error": f"HTTP {response.status_code}"}

    except Exception as e:
        print_result("Portfolio Optimizer Test", False, f"Error: {str(e)[:40]}")
        return {"status": "error", "error": str(e)}


def generate_report(infra_results: Dict, service_results: List[Dict], data_test: Dict):
    """Generate comprehensive validation report"""
    print_header("Validation Summary Report")

    # Infrastructure summary
    infra_healthy = sum(1 for v in infra_results.values() if v)
    infra_total = len(infra_results)
    print(f"Infrastructure: {infra_healthy}/{infra_total} healthy ({infra_healthy/infra_total*100:.0f}%)")

    # Backend services summary
    services_healthy = sum(1 for r in service_results if r["healthy"])
    services_total = len(service_results)
    print(f"Backend Services: {services_healthy}/{services_total} healthy ({services_healthy/services_total*100:.0f}%)")

    # Average response time
    response_times = [r["response_time"] for r in service_results if r["response_time"]]
    if response_times:
        avg_response = sum(response_times) / len(response_times)
        print(f"Avg Response Time: {avg_response:.0f}ms")

    # Data fetcher test
    data_status = "[PASSED]" if data_test.get("status") == "success" else "[FAILED]"
    print(f"Data Fetcher Test: {data_status}")

    # Overall status
    print(f"\n{'=' * 80}")
    overall_status = (
        infra_healthy == infra_total and
        services_healthy == services_total and
        data_test.get("status") == "success"
    )

    if overall_status:
        print("OVERALL STATUS: [OK] ALL SYSTEMS OPERATIONAL")
    else:
        print("OVERALL STATUS: [WARNING] SOME SYSTEMS DEGRADED")
    print(f"{'=' * 80}\n")

    # Save detailed report
    report = {
        "timestamp": datetime.now().isoformat(),
        "infrastructure": infra_results,
        "backend_services": service_results,
        "data_fetcher_test": data_test,
        "summary": {
            "infrastructure_health": f"{infra_healthy}/{infra_total}",
            "services_health": f"{services_healthy}/{services_total}",
            "overall_status": "operational" if overall_status else "degraded"
        }
    }

    with open("validation_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"Detailed report saved to: validation_report.json\n")


def main():
    """Main validation workflow"""
    print(f"\nTrade2026 Backend Services Validation")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Validate infrastructure
    infra_results = validate_infrastructure()

    # Step 2: Validate backend services
    service_results = validate_all_backend_services()

    # Step 3: Test data fetcher integration
    data_test = test_data_fetcher_integration()

    # Step 4: Generate report
    generate_report(infra_results, service_results, data_test)


if __name__ == "__main__":
    main()
