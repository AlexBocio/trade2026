# Trade2025 Portfolio Optimizer Backend

Advanced portfolio optimization backend service with institutional-grade algorithms.

## Features

### Optimization Methods
- **Mean-Variance Optimization** (Markowitz) - Classic portfolio optimization
- **Black-Litterman** - Combines market equilibrium with investor views
- **Risk Parity** - Equal risk contribution from each asset
- **Hierarchical Risk Parity (HRP)** - Clustering-based optimization
- **Minimum Variance** - Lowest risk portfolio
- **Maximum Diversification** - Maximizes diversification ratio
- **Transaction Cost-Aware** - Optimization with realistic trading costs

### Covariance Estimation
- **Ledoit-Wolf Shrinkage** - Better for high-dimensional data
- **Oracle Approximating Shrinkage (OAS)** - Alternative shrinkage method
- **EWMA** - Exponentially weighted moving average
- **Constant Correlation** - Simplified correlation structure
- **Denoised** - Random Matrix Theory noise filtering

## Quick Start

### 1. Setup Environment

```powershell
# Navigate to project
cd C:\trade2025\backend\portfolio_optimizer

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Server

```powershell
python app.py
```

Server will start on: **http://localhost:5001**

### 3. Test API

```powershell
# Health check
curl http://localhost:5001/health

# View all endpoints
curl http://localhost:5001/
```

## API Endpoints

### Optimization

**POST /api/optimize/mean-variance**
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "target_return": 0.15,
  "risk_free_rate": 0.02
}
```

**POST /api/optimize/black-litterman**
```json
{
  "tickers": ["AAPL", "MSFT"],
  "market_caps": {
    "AAPL": 3000000000000,
    "MSFT": 2800000000000
  },
  "views": {
    "AAPL": 0.15,
    "MSFT": 0.12
  },
  "confidence": {
    "AAPL": 0.8,
    "MSFT": 0.6
  }
}
```

**POST /api/optimize/risk-parity**
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"]
}
```

**POST /api/optimize/hrp**
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL"]
}
```

**POST /api/optimize/efficient-frontier**
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "n_points": 50
}
```

### Covariance

**POST /api/covariance/compare**
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL"]
}
```

**POST /api/covariance/ledoit-wolf**
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL"]
}
```

## Example Usage

### Python

```python
import requests

# Optimize portfolio using Mean-Variance
response = requests.post('http://localhost:5001/api/optimize/mean-variance', json={
    'tickers': ['AAPL', 'MSFT', 'GOOGL'],
    'risk_free_rate': 0.02
})

result = response.json()
print(f"Optimal Weights: {result['weights']}")
print(f"Expected Return: {result['expected_return']:.2%}")
print(f"Volatility: {result['volatility']:.2%}")
print(f"Sharpe Ratio: {result['sharpe_ratio']:.2f}")
```

### JavaScript/React

```javascript
const optimizePortfolio = async () => {
  const response = await fetch('http://localhost:5001/api/optimize/mean-variance', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      tickers: ['AAPL', 'MSFT', 'GOOGL'],
      risk_free_rate: 0.02
    })
  });

  const result = await response.json();
  console.log('Optimal Weights:', result.weights);
  console.log('Sharpe Ratio:', result.sharpe_ratio);
};
```

### cURL

```bash
curl -X POST http://localhost:5001/api/optimize/mean-variance \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL", "MSFT", "GOOGL"],
    "risk_free_rate": 0.02
  }'
```

## Response Format

All optimization endpoints return:

```json
{
  "weights": {
    "AAPL": 0.35,
    "MSFT": 0.40,
    "GOOGL": 0.25
  },
  "expected_return": 0.15,
  "volatility": 0.20,
  "sharpe_ratio": 0.75,
  "method": "mean_variance"
}
```

## Architecture

```
backend/portfolio_optimizer/
├── app.py              # Flask API server
├── optimizers.py       # Portfolio optimization algorithms
├── covariance.py       # Covariance estimation methods
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── venv/              # Virtual environment
```

## Dependencies

- **numpy** - Numerical computing
- **pandas** - Data manipulation
- **scipy** - Scientific computing
- **cvxpy** - Convex optimization
- **PyPortfolioOpt** - Portfolio optimization library
- **riskfolio-lib** - Advanced portfolio optimization
- **scikit-learn** - Machine learning (covariance estimation)
- **flask** - Web framework
- **yfinance** - Market data

## Integration with Frontend

Your React frontend can call these APIs:

```javascript
// services/portfolioOptimizer.js
export const portfolioOptimizerAPI = {
  baseURL: 'http://localhost:5001/api',

  async optimizeMeanVariance(tickers, targetReturn = null) {
    const response = await fetch(`${this.baseURL}/optimize/mean-variance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tickers,
        target_return: targetReturn,
        risk_free_rate: 0.02
      })
    });
    return response.json();
  },

  async optimizeRiskParity(tickers) {
    const response = await fetch(`${this.baseURL}/optimize/risk-parity`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tickers })
    });
    return response.json();
  },

  async getEfficientFrontier(tickers, nPoints = 50) {
    const response = await fetch(`${this.baseURL}/optimize/efficient-frontier`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tickers, n_points: nPoints })
    });
    return response.json();
  }
};
```

## Troubleshooting

### ModuleNotFoundError

If you get import errors:
```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Port Already in Use

If port 5001 is already in use, edit `app.py` line 233:
```python
app.run(host='0.0.0.0', port=5002, debug=True)  # Change to 5002
```

### CVXPY Installation Issues

On Windows, if CVXPY fails to install:
```powershell
pip install cvxpy --no-build-isolation
```

## Production Deployment

For production:

1. **Disable Debug Mode**
   ```python
   app.run(host='0.0.0.0', port=5001, debug=False)
   ```

2. **Use Production Server**
   ```powershell
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5001 app:app
   ```

3. **Add Authentication**
   ```python
   from flask_httpauth import HTTPBasicAuth
   auth = HTTPBasicAuth()
   ```

4. **Enable HTTPS**
   Use nginx or Apache as reverse proxy with SSL

5. **Add Rate Limiting**
   ```powershell
   pip install flask-limiter
   ```

## Testing

Test all endpoints:

```powershell
# Mean-Variance
curl -X POST http://localhost:5001/api/optimize/mean-variance -H "Content-Type: application/json" -d "{\"tickers\": [\"AAPL\", \"MSFT\"]}"

# Risk Parity
curl -X POST http://localhost:5001/api/optimize/risk-parity -H "Content-Type: application/json" -d "{\"tickers\": [\"AAPL\", \"MSFT\", \"GOOGL\"]}"

# Efficient Frontier
curl -X POST http://localhost:5001/api/optimize/efficient-frontier -H "Content-Type: application/json" -d "{\"tickers\": [\"AAPL\", \"MSFT\"], \"n_points\": 30}"
```

## Support

- Documentation: See this README
- API Reference: http://localhost:5001/ (when server is running)
- Issues: Create GitHub issue

---

**Ready to optimize portfolios!** 🚀📊
