# Fractional Differentiation Engine

**Port: 5006**

A production-ready backend service that implements fractional differentiation for time series, achieving stationarity while preserving memory (autocorrelation). Based on techniques from Marcos Lopez de Prado's "Advances in Financial Machine Learning".

---

## Overview

### What is Fractional Differentiation?

Traditional time series analysis faces a dilemma:
- **Price data** is non-stationary (violates ML assumptions) but has full memory (predictive power)
- **Returns** (d=1) are stationary but have no memory (no autocorrelation)

**Fractional differentiation** solves this by differentiating to degree **d** (0 < d < 1):
- **d=0**: Original series (non-stationary, full memory)
- **d=1**: Returns (stationary, no memory)
- **d=0.4-0.6**: Sweet spot (stationary + memory retention)

This enables machine learning models to work with stationary features that still retain predictive autocorrelation.

---

## Features

### Core Algorithms
- **FFD (Fixed-Width Window)**: Fast fractional differentiation with weight truncation
- **Standard Method**: Full binomial expansion without truncation
- **Weight calculation**: Efficient recursive binomial coefficient computation

### Stationarity Testing
- **ADF (Augmented Dickey-Fuller)**: H0: non-stationary
- **KPSS (Kwiatkowski-Phillips-Schmidt-Shin)**: H0: stationary
- **PP (Phillips-Perron)**: Robust to heteroskedasticity
- **Combined Test**: Consensus from all three tests with confidence scoring

### Optimization
- **Optimal d Finder**: Find minimum d that achieves stationarity (maximum memory)
- **Grid Search**: Test multiple d values with different objectives
- **Comparison Tool**: Side-by-side comparison of transformations

### Memory Metrics
- **Autocorrelation Function (ACF)**: Temporal dependency measurement
- **Hurst Exponent**: Long-term memory indicator (R/S analysis)
- **Memory Retention Score**: Correlation between original and transformed ACF

---

## Installation

### Prerequisites
- Python 3.9+
- pip

### Quick Setup

#### Using setup.ps1 (Windows)
```powershell
.\setup.ps1
```

#### Manual Setup
```bash
cd backend/fractional_diff

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
python app.py
```

Server starts on: `http://localhost:5006`

---

## API Endpoints

### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "fractional-diff-engine",
  "port": 5006,
  "version": "1.0.0"
}
```

---

### 2. Transform Series
```http
POST /api/fracdiff/transform
```

Apply fractional differentiation to a time series.

**Request Body:**
```json
{
  "ticker": "SPY",           // OR "values": [...]
  "d": 0.5,
  "method": "ffd",           // "ffd" or "standard"
  "threshold": 1e-5,
  "start_date": "2020-01-01",  // optional
  "end_date": "2023-01-01"     // optional
}
```

**Alternative (raw values):**
```json
{
  "values": [100, 102, 101, 103, ...],
  "index": ["2020-01-01", "2020-01-02", ...],  // optional
  "d": 0.5
}
```

**Response:**
```json
{
  "success": true,
  "original": {
    "data": {
      "values": [...],
      "index": [...],
      "length": 500
    },
    "statistics": {
      "mean": 145.32,
      "std": 15.67,
      "min": 120.45,
      "max": 178.90
    },
    "hurst_exponent": 0.65
  },
  "transformed": {
    "data": {
      "values": [...],
      "index": [...],
      "length": 485
    },
    "statistics": {...},
    "hurst_exponent": 0.52
  },
  "stationarity": {
    "consensus": "stationary",
    "confidence": "high",
    "adf": {
      "p_value": 0.001,
      "is_stationary": true
    },
    "kpss": {...},
    "pp": {...}
  },
  "memory": {
    "retention_score": 0.73,
    "interpretation": "High"
  },
  "config": {
    "d": 0.5,
    "method": "ffd",
    "threshold": 1e-5
  }
}
```

---

### 3. Find Optimal d
```http
POST /api/fracdiff/find-optimal-d
```

Find minimum d that achieves stationarity (maximum memory retention).

**Request Body:**
```json
{
  "ticker": "SPY",         // OR "values": [...]
  "d_range": [0.0, 1.0],
  "step": 0.05,
  "method": "combined",    // "adf", "kpss", "pp", "combined"
  "alpha": 0.05
}
```

**Response:**
```json
{
  "success": true,
  "optimal_d": 0.45,
  "memory_retained": 0.73,
  "original_memory": 0.98,
  "stationarity_results": [
    {
      "d": 0.0,
      "is_stationary": false,
      "p_value": 0.85,
      "memory_retained": 1.0,
      "series_length": 500
    },
    {
      "d": 0.05,
      "is_stationary": false,
      "p_value": 0.72,
      "memory_retained": 0.95,
      "series_length": 495
    },
    ...
  ],
  "method": "combined",
  "alpha": 0.05,
  "recommendation": "Use d=0.45 for stationarity with 73% memory retention. This balances stationarity and predictive power.",
  "visualization_data": {
    "d_values": [0.0, 0.05, 0.1, ...],
    "is_stationary": [false, false, true, ...],
    "p_values": [0.85, 0.72, 0.03, ...],
    "memory_scores": [1.0, 0.95, 0.89, ...]
  }
}
```

---

### 4. Compare d Values
```http
POST /api/fracdiff/compare
```

Compare multiple d values side-by-side.

**Request Body:**
```json
{
  "ticker": "SPY",         // OR "values": [...]
  "d_values": [0.0, 0.3, 0.5, 0.7, 1.0]
}
```

**Response:**
```json
{
  "success": true,
  "comparison": [
    {
      "label": "Original (d=0)",
      "d": 0.0,
      "is_stationary": false,
      "confidence": "high",
      "adf_p_value": 0.95,
      "memory_retained": 1.0,
      "mean": 145.32,
      "std": 15.67
    },
    {
      "label": "d=0.5",
      "d": 0.5,
      "is_stationary": true,
      "confidence": "high",
      "adf_p_value": 0.001,
      "memory_retained": 0.73,
      "mean": 0.05,
      "std": 1.2
    },
    ...
  ],
  "memory_comparison": [
    {
      "label": "Original",
      "autocorr_lag1": 0.98,
      "autocorr_lag5": 0.87,
      "autocorr_lag10": 0.76,
      "hurst_exponent": 0.65,
      "memory_score": 1.0
    },
    ...
  ],
  "summary": {
    "total_tested": 5,
    "stationary_count": 3,
    "best_d_for_memory": 0.3
  }
}
```

---

### 5. Batch Transform
```http
POST /api/fracdiff/batch
```

Transform multiple tickers in batch.

**Request Body:**
```json
{
  "tickers": ["SPY", "QQQ", "IWM"],
  "d": 0.5,
  "method": "ffd",
  "start_date": "2020-01-01",
  "end_date": "2023-01-01"
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "SPY": {
      "success": true,
      "original_length": 500,
      "transformed_length": 485,
      "is_stationary": true,
      "stationarity_confidence": "high",
      "memory_retained": 0.73,
      "transformed_data": {...}
    },
    "QQQ": {...},
    "IWM": {...}
  },
  "summary": {
    "total": 3,
    "success": 3,
    "failure": 0,
    "config": {
      "d": 0.5,
      "method": "ffd",
      "threshold": 1e-5
    }
  }
}
```

---

### 6. Stationarity Test
```http
POST /api/fracdiff/stationarity-test
```

Test stationarity of a time series.

**Request Body:**
```json
{
  "ticker": "SPY",         // OR "values": [...]
  "test": "combined",      // "adf", "kpss", "pp", "combined"
  "alpha": 0.05
}
```

**Response:**
```json
{
  "success": true,
  "test_results": {
    "adf": {
      "statistic": -3.45,
      "p_value": 0.01,
      "is_stationary": true
    },
    "kpss": {...},
    "pp": {...},
    "consensus": "stationary",
    "confidence": "high",
    "summary": "All 3 tests indicate stationarity"
  },
  "is_stationary": true,
  "conclusion": "All 3 tests indicate stationarity"
}
```

---

## Usage Examples

### Python Client

```python
import requests
import json

BASE_URL = "http://localhost:5006"

# Example 1: Transform a ticker
def transform_ticker(ticker, d=0.5):
    payload = {
        "ticker": ticker,
        "d": d,
        "method": "ffd"
    }

    response = requests.post(
        f"{BASE_URL}/api/fracdiff/transform",
        json=payload
    )

    result = response.json()

    if result['success']:
        print(f"Transformed {ticker} with d={d}")
        print(f"Stationary: {result['stationarity']['consensus']}")
        print(f"Memory retained: {result['memory']['retention_score']:.2%}")
        return result['transformed']['data']['values']
    else:
        print(f"Error: {result['error']}")

# Example 2: Find optimal d
def find_optimal_d(ticker):
    payload = {
        "ticker": ticker,
        "d_range": [0.0, 1.0],
        "step": 0.05,
        "method": "combined"
    }

    response = requests.post(
        f"{BASE_URL}/api/fracdiff/find-optimal-d",
        json=payload
    )

    result = response.json()

    if result['success']:
        print(f"Optimal d: {result['optimal_d']}")
        print(f"Memory retained: {result['memory_retained']:.2%}")
        print(f"Recommendation: {result['recommendation']}")
        return result['optimal_d']

# Example 3: Compare multiple d values
def compare_d_values(ticker):
    payload = {
        "ticker": ticker,
        "d_values": [0.0, 0.3, 0.5, 0.7, 1.0]
    }

    response = requests.post(
        f"{BASE_URL}/api/fracdiff/compare",
        json=payload
    )

    result = response.json()

    if result['success']:
        print("\nComparison Results:")
        for item in result['comparison']:
            print(f"d={item['d']:.1f}: Stationary={item['is_stationary']}, "
                  f"Memory={item['memory_retained']:.2%}")

# Run examples
if __name__ == '__main__':
    ticker = "SPY"

    # Transform
    transformed = transform_ticker(ticker, d=0.5)

    # Find optimal d
    optimal_d = find_optimal_d(ticker)

    # Compare
    compare_d_values(ticker)
```

### cURL Examples

```bash
# Health check
curl http://localhost:5006/health

# Transform with values
curl -X POST http://localhost:5006/api/fracdiff/transform \
  -H "Content-Type: application/json" \
  -d '{
    "values": [100, 102, 101, 103, 105, 104, 106],
    "d": 0.5
  }'

# Find optimal d
curl -X POST http://localhost:5006/api/fracdiff/find-optimal-d \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "SPY",
    "d_range": [0.0, 1.0],
    "step": 0.05,
    "method": "combined"
  }'

# Compare d values
curl -X POST http://localhost:5006/api/fracdiff/compare \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "SPY",
    "d_values": [0.0, 0.3, 0.5, 0.7, 1.0]
  }'
```

---

## Testing

### Run All Tests
```bash
# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_fractional_diff.py -v
```

### Test Suite

#### Component Tests
- `test_fractional_diff.py`: Core algorithms (FFD, standard, weights)
- `test_stationarity.py`: Stationarity tests (ADF, KPSS, PP)

#### Integration Tests
- `test_integration.py`: Flask API endpoints

### Expected Coverage
- Core algorithms: >85%
- Stationarity tests: >80%
- API endpoints: >75%
- Overall: >80%

---

## Configuration

### Default Settings (config.py)

```python
class Config:
    PORT = 5006

    # Fractional differentiation
    DEFAULT_D = 0.5
    MIN_D = 0.0
    MAX_D = 1.0
    DEFAULT_THRESHOLD = 1e-5
    DEFAULT_D_STEP = 0.05

    # Stationarity tests
    DEFAULT_ALPHA = 0.05
    ADF_REGRESSION = 'c'
    KPSS_REGRESSION = 'c'
    ADF_MAXLAG = None
    KPSS_NLAGS = 'auto'

    # Memory metrics
    DEFAULT_LAGS = 20
    HURST_LAG_RANGE = (10, 100)

    # Data validation
    MIN_DATA_POINTS = 100
    MAX_DATA_POINTS = 100000
```

To customize, edit `config.py` or override in API requests.

---

## Mathematical Background

### Fractional Differentiation Formula

**Weight Calculation:**
```
w_k = (-1)^k * binom(d, k)
    = -w_{k-1} / k * (d - k + 1)
```

**Transformation:**
```
X̃_t = Σ(k=0 to K) w_k * X_{t-k}
```

Where:
- `d`: Differentiation order (0 < d < 1)
- `w_k`: Binomial weights
- `K`: Window width (FFD truncates at |w_k| < threshold)

### Stationarity Tests

**ADF (Augmented Dickey-Fuller):**
- H0: Series has unit root (non-stationary)
- H1: Series is stationary
- p-value < α → Reject H0 → Stationary

**KPSS:**
- H0: Series IS stationary (opposite of ADF!)
- H1: Series is non-stationary
- p-value ≥ α → Fail to reject H0 → Stationary

**PP (Phillips-Perron):**
- Similar to ADF but robust to heteroskedasticity

### Hurst Exponent (R/S Analysis)

```
H = slope of log(R/S) vs log(lag)
```

Interpretation:
- H = 0.5: Random walk (no memory)
- H > 0.5: Persistent (trending, positive autocorrelation)
- H < 0.5: Mean-reverting (negative autocorrelation)

---

## Directory Structure

```
backend/fractional_diff/
├── app.py                      # Flask API server (Port 5006)
├── config.py                   # Configuration
├── utils.py                    # Validation & helpers
├── fractional_diff.py          # Core FFD algorithms
├── stationarity_tests.py       # ADF, KPSS, PP tests
├── optimal_d_finder.py         # Optimal d search
├── memory_metrics.py           # Memory retention metrics
├── requirements.txt            # Dependencies
├── setup.ps1                   # Automated setup script
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
├── tests/
│   ├── __init__.py
│   ├── test_fractional_diff.py     # Core algorithm tests
│   ├── test_stationarity.py        # Stationarity test tests
│   └── test_integration.py         # API integration tests
└── venv/                       # Virtual environment (created by setup)
```

---

## Dependencies

Core dependencies (see requirements.txt):
- Flask >= 2.3.0: Web framework
- flask-cors >= 4.0.0: CORS support
- numpy >= 1.24.0: Numerical computing
- pandas >= 2.0.0: Time series data structures
- statsmodels >= 0.14.0: Statistical tests (ADF, KPSS)
- yfinance >= 0.2.0: Market data fetching
- pytest >= 7.4.0: Testing framework

---

## Error Handling

### Common Errors

**1. Invalid d value:**
```json
{
  "success": false,
  "error": "d must be between 0.0 and 1.0, got: 1.5"
}
```

**2. Insufficient data:**
```json
{
  "success": false,
  "error": "Insufficient data points. Minimum: 100, got: 50"
}
```

**3. Invalid ticker:**
```json
{
  "success": false,
  "error": "No data found for ticker: INVALID"
}
```

**4. Missing data:**
```json
{
  "success": false,
  "error": "Must provide either 'ticker' or 'values' in request"
}
```

---

## Performance

### Benchmarks (Intel i7, 16GB RAM)

- **FFD (d=0.5, n=1000)**: ~10ms
- **Standard (d=0.5, n=1000)**: ~50ms
- **ADF Test**: ~30ms
- **Combined Stationarity Check**: ~100ms
- **Find Optimal d (20 steps)**: ~2s

### Optimization Tips

1. **Use FFD over standard**: 5x faster, minimal accuracy loss
2. **Increase threshold**: Larger threshold = fewer weights = faster
3. **Reduce search steps**: Use step=0.1 instead of 0.05 for quick results
4. **Cache results**: Optimal d doesn't change frequently for same ticker

---

## Production Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5006

CMD ["python", "app.py"]
```

### Build and Run
```bash
docker build -t fracdiff-engine .
docker run -p 5006:5006 fracdiff-engine
```

### Environment Variables

```bash
export FLASK_ENV=production
export FLASK_DEBUG=0
export FRACDIFF_PORT=5006
```

---

## Troubleshooting

### Server won't start on port 5006
```bash
# Check if port is in use
netstat -ano | findstr :5006  # Windows
lsof -i :5006                 # Linux/Mac

# Kill process or change port in config.py
```

### Import errors
```bash
# Ensure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Tests failing
```bash
# Ensure test dependencies are installed
pip install pytest pytest-cov

# Run tests with verbose output
pytest tests/ -v -s
```

---

## References

1. **Advances in Financial Machine Learning** by Marcos Lopez de Prado (2018)
   - Chapter 5: Fractional Differentiation

2. **Augmented Dickey-Fuller Test**
   - Said, S. E., & Dickey, D. A. (1984)

3. **KPSS Test**
   - Kwiatkowski, Phillips, Schmidt, & Shin (1992)

4. **Hurst Exponent**
   - Hurst, H. E. (1951). Long-term storage capacity of reservoirs

---

## License

MIT License - See LICENSE file for details

---

## Support

For issues and questions:
- GitHub Issues: [Create issue](https://github.com/your-repo/issues)
- Documentation: This README
- Email: support@yourcompany.com

---

## Changelog

### v1.0.0 (2024-01-15)
- Initial release
- FFD and standard fractional differentiation
- ADF, KPSS, PP stationarity tests
- Optimal d finder
- Memory retention metrics
- Complete REST API
- Comprehensive test suite

---

**Fractional Differentiation Engine - Port 5006**

*Achieve stationarity while preserving memory*
