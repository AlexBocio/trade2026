#!/usr/bin/env python3
"""
Real-Time IBKR Data Testing Script
Tests all backend services with IBKR real-time data symbols
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List

# IBKR symbols available in QuestDB (15 total)
IBKR_SYMBOLS = [
    # Sector ETFs (7)
    "XLE",  # Energy
    "XLF",  # Financials
    "XLI",  # Industrials
    "XLK",  # Technology
    "XLP",  # Consumer Staples
    "XLV",  # Healthcare
    "XLY",  # Consumer Discretionary

    # Benchmark ETFs (8)
    "SPY",  # S&P 500
    "QQQ",  # NASDAQ 100
    "IWM",  # Russell 2000
    "DIA",  # Dow Jones
    "VTI",  # Total Stock Market
    "GLD",  # Gold
    "TLT",  # 20+ Year Treasury
    "SHY",  # 1-3 Year Treasury
]


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{'=' * 80}")
    print(f"  {text}")
    print(f"{'=' * 80}\n")


def print_test(service: str, symbol: str, status: bool, details: str):
    """Print test result"""
    icon = "[OK]" if status else "[FAIL]"
    print(f"{icon} {service:25} {symbol:8} {details}")


def check_questdb_data():
    """Check if QuestDB has IBKR data"""
    print_header("QuestDB Data Availability Check")

    query = "SELECT symbol, COUNT(*) as count FROM market_data_l1 GROUP BY symbol ORDER BY symbol"

    try:
        response = requests.get(
            "http://localhost:9000/exec",
            params={"query": query},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if "dataset" in data and len(data["dataset"]) > 0:
                print("IBKR Data in QuestDB:")
                for row in data["dataset"]:
                    symbol, count = row
                    print(f"  {symbol}: {count:,} ticks")
                return True
            else:
                print("❌ No IBKR data found in QuestDB")
                return False
        else:
            print(f"❌ QuestDB query failed: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error checking QuestDB: {str(e)}")
        return False


def test_portfolio_optimizer(symbols: List[str]):
    """Test Portfolio Optimizer with IBKR symbols"""
    print_header(f"Testing Portfolio Optimizer with {len(symbols)} IBKR Symbols")

    payload = {
        "tickers": symbols[:4],  # Use first 4 symbols
        "weights": {symbol: 1/4 for symbol in symbols[:4]},
        "method": "min_variance"
    }

    try:
        start = time.time()
        response = requests.post(
            "http://localhost:5001/api/optimize/min-variance",
            json=payload,
            timeout=60
        )
        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            weights = data.get("weights", {})
            print_test(
                "Portfolio Optimizer",
                ", ".join(symbols[:4]),
                True,
                f"{elapsed:.2f}s - Weights: {weights}"
            )
            return True
        else:
            print_test(
                "Portfolio Optimizer",
                ", ".join(symbols[:4]),
                False,
                f"HTTP {response.status_code}"
            )
            return False

    except Exception as e:
        print_test("Portfolio Optimizer", ", ".join(symbols[:4]), False, f"Error: {str(e)[:50]}")
        return False


def test_factor_models(symbols: List[str]):
    """Test Factor Models with IBKR symbols"""
    print_header(f"Testing Factor Models with {len(symbols)} IBKR Symbols")

    payload = {
        "tickers": symbols[:4],
        "n_factors": 2
    }

    try:
        start = time.time()
        response = requests.post(
            "http://localhost:5004/api/factors/pca",
            json=payload,
            timeout=60
        )
        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            variance = data.get("total_explained", 0)
            print_test(
                "Factor Models (PCA)",
                ", ".join(symbols[:4]),
                True,
                f"{elapsed:.2f}s - Variance: {variance:.2%}"
            )
            return True
        else:
            print_test(
                "Factor Models (PCA)",
                ", ".join(symbols[:4]),
                False,
                f"HTTP {response.status_code}"
            )
            return False

    except Exception as e:
        print_test("Factor Models (PCA)", ", ".join(symbols[:4]), False, f"Error: {str(e)[:50]}")
        return False


def test_simulation_engine(symbol: str):
    """Test Simulation Engine with single IBKR symbol"""
    print_header(f"Testing Simulation Engine with {symbol}")

    payload = {
        "ticker": symbol,
        "n_simulations": 100,
        "n_days": 21,
        "method": "geometric_brownian"
    }

    try:
        start = time.time()
        response = requests.post(
            "http://localhost:5005/api/simulate/monte-carlo",
            json=payload,
            timeout=60
        )
        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            mean_return = data.get("mean_final_return", 0)
            print_test(
                "Simulation Engine (MC)",
                symbol,
                True,
                f"{elapsed:.2f}s - Mean Return: {mean_return:.2%}"
            )
            return True
        else:
            print_test(
                "Simulation Engine (MC)",
                symbol,
                False,
                f"HTTP {response.status_code}"
            )
            return False

    except Exception as e:
        print_test("Simulation Engine (MC)", symbol, False, f"Error: {str(e)[:50]}")
        return False


def test_advanced_backtest(symbol: str):
    """Test Advanced Backtest with IBKR symbol"""
    print_header(f"Testing Advanced Backtest with {symbol}")

    payload = {
        "ticker": symbol,
        "strategy": "ma_crossover",
        "param_grid": {
            "fast": [10, 20],
            "slow": [50, 100]
        },
        "train_period": 126,  # 6 months
        "test_period": 21     # 1 month
    }

    try:
        start = time.time()
        response = requests.post(
            "http://localhost:5003/api/backtest/walk-forward",
            json=payload,
            timeout=120
        )
        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            sharpe = data.get("summary", {}).get("total_sharpe", 0)
            print_test(
                "Advanced Backtest (WF)",
                symbol,
                True,
                f"{elapsed:.2f}s - Sharpe: {sharpe:.2f}"
            )
            return True
        else:
            print_test(
                "Advanced Backtest (WF)",
                symbol,
                False,
                f"HTTP {response.status_code}"
            )
            return False

    except Exception as e:
        print_test("Advanced Backtest (WF)", symbol, False, f"Error: {str(e)[:50]}")
        return False


def test_stock_screener(symbols: List[str]):
    """Test Stock Screener with IBKR symbols"""
    print_header(f"Testing Stock Screener with {len(symbols)} IBKR Symbols")

    payload = {
        "tickers": symbols[:5],
        "min_price": 100,
        "max_price": 500,
        "min_volume": 1000000
    }

    try:
        start = time.time()
        response = requests.post(
            "http://localhost:5008/api/screen/basic",
            json=payload,
            timeout=60
        )
        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            matches = len(data.get("results", []))
            print_test(
                "Stock Screener",
                ", ".join(symbols[:5]),
                True,
                f"{elapsed:.2f}s - {matches} matches"
            )
            return True
        else:
            print_test(
                "Stock Screener",
                ", ".join(symbols[:5]),
                False,
                f"HTTP {response.status_code}"
            )
            return False

    except Exception as e:
        print_test("Stock Screener", ", ".join(symbols[:5]), False, f"Error: {str(e)[:50]}")
        return False


def generate_report(results: Dict):
    """Generate test report"""
    print_header("Real-Time IBKR Data Testing Summary")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    print(f"Tests Passed: {passed}/{total} ({passed/total*100:.0f}%)")
    print(f"\nResults:")
    for test_name, status in results.items():
        icon = "[OK]" if status else "[FAIL]"
        print(f"  {icon} {test_name}")

    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "ibkr_symbols": IBKR_SYMBOLS,
        "tests": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": f"{passed/total*100:.0f}%"
        }
    }

    with open("ibkr_data_test_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nDetailed report saved to: ibkr_data_test_report.json")


def main():
    """Main testing workflow"""
    print(f"\nTrade2026 Real-Time IBKR Data Testing")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing with {len(IBKR_SYMBOLS)} IBKR symbols: {', '.join(IBKR_SYMBOLS)}")

    results = {}

    # Check QuestDB data availability
    questdb_ok = check_questdb_data()
    results["QuestDB Data Check"] = questdb_ok

    if not questdb_ok:
        print("\n[WARNING] No IBKR data in QuestDB. Services will fall back to yfinance.")
        print("          Consider starting the Data Ingestion Service for real-time data.\n")

    # Run tests
    results["Portfolio Optimizer"] = test_portfolio_optimizer(IBKR_SYMBOLS)
    results["Factor Models"] = test_factor_models(IBKR_SYMBOLS)
    results["Simulation Engine"] = test_simulation_engine("SPY")
    results["Advanced Backtest"] = test_advanced_backtest("SPY")
    results["Stock Screener"] = test_stock_screener(IBKR_SYMBOLS)

    # Generate report
    generate_report(results)


if __name__ == "__main__":
    main()
