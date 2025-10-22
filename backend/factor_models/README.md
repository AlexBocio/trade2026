# Factor Models & Risk Attribution

Institutional-grade factor models and risk attribution system for portfolio analysis.

## Features

### 1. **Barra-Style Factor Model**
- Multi-factor risk decomposition
- Factor exposures (Size, Value, Momentum, Quality, Volatility, Growth)
- Factor covariance estimation
- Specific (idiosyncratic) risk calculation
- Portfolio risk decomposition (factor vs specific risk)

### 2. **Statistical Factor Extraction (PCA)**
- Principal Component Analysis
- Factor loadings and explained variance
- Factor beta calculation
- Factor-mimicking portfolios

### 3. **Risk Attribution**
- Marginal Contribution to Risk (MCR)
- Component Contribution to Risk (CCR)
- Factor risk contribution
- Risk budgeting analysis
- Diversification ratio

### 4. **Stress Testing**
- Factor shock scenarios
- Asset-level impact analysis
- Portfolio sensitivity to factor movements

## Installation

### PowerShell (Windows)
```powershell
.\setup.ps1
```

### Manual Setup
```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Server

```bash
python app.py
```

Server runs on `http://localhost:5004`

## API Endpoints

### 1. Barra Factor Model

**POST** `/api/factors/barra`

```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
  "weights": {
    "AAPL": 0.25,
    "MSFT": 0.25,
    "GOOGL": 0.25,
    "AMZN": 0.25
  },
  "start_date": "2022-01-01",
  "end_date": "2024-12-31"
}
```

**Response:**
```json
{
  "risk_decomposition": {
    "total_risk": 22.5,
    "factor_risk": 18.3,
    "specific_risk": 13.2,
    "factor_contribution": 81.4,
    "factor_exposures": {
      "Size": 0.45,
      "Value": -0.12,
      "Momentum": 0.68,
      "Quality": 0.23,
      "Volatility": -0.31,
      "Growth": 0.54
    }
  },
  "factor_tilts": {
    "Size": 0.45,
    "Value": -0.12,
    "Momentum": 0.68,
    "Quality": 0.23,
    "Volatility": -0.31,
    "Growth": 0.54
  }
}
```

### 2. PCA Factor Extraction

**POST** `/api/factors/pca`

```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
  "n_factors": 3,
  "start_date": "2022-01-01",
  "end_date": "2024-12-31"
}
```

**Response:**
```json
{
  "n_factors": 3,
  "explained_variance": [0.52, 0.23, 0.11],
  "total_explained": 0.86,
  "loadings": {
    "PC1": {
      "AAPL": 0.48,
      "MSFT": 0.51,
      "GOOGL": 0.49,
      "AMZN": 0.52
    },
    "PC2": {
      "AAPL": -0.23,
      "MSFT": 0.67,
      "GOOGL": -0.45,
      "AMZN": 0.54
    }
  }
}
```

### 3. Factor Betas

**POST** `/api/factors/factor-betas`

Calculate asset's exposure to statistical factors.

```json
{
  "benchmark_tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
  "asset_ticker": "TSLA",
  "n_factors": 3
}
```

**Response:**
```json
{
  "asset": "TSLA",
  "betas": {
    "PC1": 1.23,
    "PC2": -0.45,
    "PC3": 0.67
  },
  "alpha": 0.0012,
  "r_squared": 0.74
}
```

### 4. Factor-Mimicking Portfolio

**POST** `/api/factors/mimicking-portfolio`

Create a portfolio that replicates a specific factor.

```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
  "factor_index": 0,
  "n_factors": 3
}
```

**Response:**
```json
{
  "factor": "PC1",
  "weights": {
    "AAPL": 0.24,
    "MSFT": 0.26,
    "GOOGL": 0.25,
    "AMZN": 0.25
  }
}
```

### 5. Risk Attribution

**POST** `/api/risk/attribution`

Comprehensive risk attribution analysis.

```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
  "weights": {
    "AAPL": 0.25,
    "MSFT": 0.25,
    "GOOGL": 0.25,
    "AMZN": 0.25
  }
}
```

**Response:**
```json
{
  "marginal_contribution_to_risk": {
    "AAPL": 0.0045,
    "MSFT": 0.0038,
    "GOOGL": 0.0052,
    "AMZN": 0.0048
  },
  "component_contribution_to_risk": {
    "absolute": {
      "AAPL": 0.00112,
      "MSFT": 0.00095,
      "GOOGL": 0.00130,
      "AMZN": 0.00120
    },
    "percentage": {
      "AAPL": 24.5,
      "MSFT": 20.8,
      "GOOGL": 28.4,
      "AMZN": 26.3
    }
  },
  "factor_risk_contribution": {
    "factor_names": ["Size", "Value", "Momentum", "Quality", "Volatility", "Growth"],
    "exposures": [0.45, -0.12, 0.68, 0.23, -0.31, 0.54],
    "contribution_percentage": [15.2, -3.4, 28.9, 8.1, -10.2, 18.7]
  },
  "diversification_ratio": {
    "diversification_ratio": 1.34,
    "weighted_avg_volatility": 25.3,
    "portfolio_volatility": 18.9,
    "diversification_benefit": 25.4
  }
}
```

### 6. Stress Test

**POST** `/api/risk/stress-test`

Test portfolio under factor shocks.

```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
  "weights": {
    "AAPL": 0.25,
    "MSFT": 0.25,
    "GOOGL": 0.25,
    "AMZN": 0.25
  },
  "factor_shocks": {
    "Size": -0.02,
    "Value": 0.03,
    "Momentum": -0.01
  }
}
```

**Response:**
```json
{
  "total_impact": -1.23,
  "asset_contributions": {
    "AAPL": -0.31,
    "MSFT": -0.28,
    "GOOGL": -0.35,
    "AMZN": -0.29
  }
}
```

### 7. Risk Budgeting

**POST** `/api/risk/budget`

Analyze risk budgets vs targets.

```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
  "weights": {
    "AAPL": 0.25,
    "MSFT": 0.25,
    "GOOGL": 0.25,
    "AMZN": 0.25
  },
  "target_budgets": {
    "AAPL": 25.0,
    "MSFT": 25.0,
    "GOOGL": 25.0,
    "AMZN": 25.0
  }
}
```

**Response:**
```json
{
  "actual_budgets": {
    "AAPL": 24.5,
    "MSFT": 20.8,
    "GOOGL": 28.4,
    "AMZN": 26.3
  },
  "target_budgets": {
    "AAPL": 25.0,
    "MSFT": 25.0,
    "GOOGL": 25.0,
    "AMZN": 25.0
  },
  "deviations": {
    "AAPL": -0.5,
    "MSFT": -4.2,
    "GOOGL": 3.4,
    "AMZN": 1.3
  },
  "total_deviation": 5.87
}
```

### 8. Comprehensive Analysis

**POST** `/api/factors/comprehensive`

Run all analyses in one call.

```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
  "weights": {
    "AAPL": 0.25,
    "MSFT": 0.25,
    "GOOGL": 0.25,
    "AMZN": 0.25
  }
}
```

## Python Usage Examples

### Barra Factor Model

```python
from barra_model import BarraFactorModel

# Create model
model = BarraFactorModel(
    tickers=['AAPL', 'MSFT', 'GOOGL', 'AMZN'],
    start_date='2022-01-01',
    end_date='2024-12-31'
)

# Fetch data and calculate factors
model.fetch_data()
model.calculate_factors()
model.estimate_factor_returns()
model.calculate_factor_covariance()
model.calculate_specific_risk()

# Analyze portfolio
weights = {'AAPL': 0.25, 'MSFT': 0.25, 'GOOGL': 0.25, 'AMZN': 0.25}
risk_decomp = model.decompose_portfolio_risk(weights)

print(f"Total Risk: {risk_decomp['total_risk']:.2f}%")
print(f"Factor Risk: {risk_decomp['factor_risk']:.2f}%")
print(f"Specific Risk: {risk_decomp['specific_risk']:.2f}%")
print(f"Factor Contribution: {risk_decomp['factor_contribution']:.1f}%")

# Factor tilts
tilts = model.factor_tilts(weights)
print("\nFactor Tilts:")
for factor, tilt in tilts.items():
    print(f"  {factor}: {tilt:.2f}")
```

### PCA Factor Extraction

```python
from factor_analysis import FactorAnalyzer
import yfinance as yf

# Fetch returns
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
prices = yf.download(tickers, period='2y')['Adj Close']
returns = prices.pct_change().dropna()

# Extract factors
analyzer = FactorAnalyzer(returns)
result = analyzer.extract_pca_factors(n_factors=3)

print(f"Total Variance Explained: {result['total_explained']:.2%}")
print("\nFactor Loadings:")
print(result['loadings'])

# Calculate asset's factor betas
asset_returns = returns['AAPL']
betas = analyzer.calculate_factor_betas(asset_returns)
print(f"\nAAPL Factor Betas: {betas['betas']}")
print(f"Alpha: {betas['alpha']:.4f}")
print(f"R²: {betas['r_squared']:.2%}")

# Create factor-mimicking portfolio
weights = analyzer.factor_mimicking_portfolio('PC1')
print("\nPC1 Mimicking Portfolio:")
print(weights)
```

### Risk Attribution

```python
from barra_model import BarraFactorModel
from risk_attribution import RiskAttributor

# Create and fit model
model = BarraFactorModel(
    tickers=['AAPL', 'MSFT', 'GOOGL', 'AMZN'],
    start_date='2022-01-01',
    end_date='2024-12-31'
)
model.fetch_data()
model.calculate_factors()
model.estimate_factor_returns()
model.calculate_factor_covariance()
model.calculate_specific_risk()

# Create risk attributor
attributor = RiskAttributor(model)

weights = {'AAPL': 0.25, 'MSFT': 0.25, 'GOOGL': 0.25, 'AMZN': 0.25}

# Marginal contribution to risk
mcr = attributor.marginal_contribution_to_risk(weights)
print("Marginal Contribution to Risk:")
for ticker, contribution in mcr.items():
    print(f"  {ticker}: {contribution:.4f}")

# Component contribution to risk
ccr = attributor.component_contribution_to_risk(weights)
print("\nRisk Contribution (%):")
for ticker, pct in ccr['percentage'].items():
    print(f"  {ticker}: {pct:.1f}%")

# Factor risk contribution
factor_contrib = attributor.factor_risk_contribution(weights)
print("\nFactor Risk Contributions:")
for i, factor in enumerate(factor_contrib['factor_names']):
    print(f"  {factor}: {factor_contrib['contribution_percentage'][i]:.1f}%")

# Diversification ratio
div_ratio = attributor.diversification_ratio(weights)
print(f"\nDiversification Ratio: {div_ratio['diversification_ratio']:.2f}")
print(f"Diversification Benefit: {div_ratio['diversification_benefit']:.1f}%")

# Stress test
factor_shocks = {'Size': -0.02, 'Value': 0.03, 'Momentum': -0.01}
stress = attributor.stress_test(weights, factor_shocks)
print(f"\nStress Test Impact: {stress['total_impact']:.2f}%")
```

## Key Concepts

### Barra Factor Model

**Multi-factor risk decomposition:**
- Total Risk² = Factor Risk² + Specific Risk²
- Factor Risk: Risk from common factors (Size, Value, Momentum, etc.)
- Specific Risk: Idiosyncratic risk unique to each stock

**Factors:**
1. **Size**: Log of market cap (large vs small cap)
2. **Value**: Book-to-market ratio (value vs growth)
3. **Momentum**: 12-month return (winners vs losers)
4. **Quality**: ROE, profit margins (high vs low quality)
5. **Volatility**: Historical volatility (low vs high vol)
6. **Growth**: Revenue/earnings growth (high vs low growth)

### PCA (Principal Component Analysis)

**Statistical factor extraction:**
- Extract orthogonal factors that explain most variance
- PC1 typically explains 40-60% of variance (market factor)
- PC2, PC3 explain industry/sector rotations

**Benefits:**
- Data-driven (no need to specify factors)
- Captures hidden structure in returns
- Useful for dimensionality reduction

### Risk Attribution

**Marginal Contribution to Risk (MCR):**
- How much does portfolio risk increase if we add $1 to a position?
- MCR_i = ∂(Portfolio Risk) / ∂(Weight_i)

**Component Contribution to Risk (CCR):**
- How much of total portfolio risk comes from each position?
- CCR_i = Weight_i × MCR_i
- Sum of all CCR = Portfolio Risk

**Risk Budgeting:**
- Allocate risk instead of capital
- Target: Each position contributes equally to risk
- Useful for risk parity strategies

### Diversification Ratio

**Measure of diversification:**
- DR = (Weighted Avg Volatility) / (Portfolio Volatility)
- DR = 1: No diversification benefit
- DR > 1: Diversification benefit
- Typical portfolios: DR = 1.2 - 1.5

## Project Structure

```
factor_models/
├── app.py                  # Flask API server
├── barra_model.py          # Barra factor model
├── factor_analysis.py      # PCA factor extraction
├── risk_attribution.py     # Risk attribution & decomposition
├── requirements.txt        # Python dependencies
├── setup.ps1              # Automated setup script
└── README.md              # This file
```

## Integration with Frontend

The React frontend (`apps/console/web`) can call these APIs:

```javascript
// Example: Barra factor analysis
const response = await fetch('http://localhost:5004/api/factors/barra', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tickers: ['AAPL', 'MSFT', 'GOOGL', 'AMZN'],
    weights: { AAPL: 0.25, MSFT: 0.25, GOOGL: 0.25, AMZN: 0.25 }
  })
});

const results = await response.json();
console.log('Factor Risk:', results.risk_decomposition.factor_risk);
console.log('Factor Tilts:', results.factor_tilts);

// Example: Risk attribution
const riskAttr = await fetch('http://localhost:5004/api/risk/attribution', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tickers: ['AAPL', 'MSFT', 'GOOGL', 'AMZN'],
    weights: { AAPL: 0.25, MSFT: 0.25, GOOGL: 0.25, AMZN: 0.25 }
  })
});

const attrResults = await riskAttr.json();
console.log('Diversification Ratio:', attrResults.diversification_ratio.diversification_ratio);
```

## Use Cases

1. **Portfolio Construction**: Understand factor exposures when building portfolios
2. **Risk Management**: Decompose risk into factor and specific components
3. **Performance Attribution**: Identify which factors drove returns
4. **Stress Testing**: Model portfolio behavior under factor shocks
5. **Risk Budgeting**: Allocate risk optimally across positions
6. **Factor Timing**: Identify when to tilt toward/away from specific factors

## Best Practices

1. **Use sufficient history**: At least 2 years of data for reliable factor estimates
2. **Rebalance regularly**: Factor exposures drift over time
3. **Monitor factor concentration**: Avoid excessive exposure to any single factor
4. **Combine with optimization**: Use factor models to construct efficient portfolios
5. **Stress test**: Always test portfolios under adverse factor scenarios
6. **Track attribution**: Monitor whether performance comes from factors or stock selection

## Academic References

- **Barra Model**: Grinold & Kahn (2000). *Active Portfolio Management*
- **PCA**: Jolliffe (2002). *Principal Component Analysis*
- **Risk Attribution**: Meucci (2007). "Risk Contributions from Generic User-Defined Factors"
- **Risk Budgeting**: Qian (2006). "On the Financial Interpretation of Risk Contribution"

## License

MIT License - See main project LICENSE file

---

**Built for Trade2025** - Institutional-grade factor models for portfolio analysis
