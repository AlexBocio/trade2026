# Simulation Engine

Advanced Monte Carlo simulation, walk-forward optimization, and cross-validation system for systematic trading strategies.

## Features

### 1. **Bootstrap Resampling Methods**
- **Standard Bootstrap**: IID resampling (independence assumption)
- **Block Bootstrap**: Preserves autocorrelation structure
- **Circular Block Bootstrap**: Treats data as circular
- **Stationary Bootstrap**: Random block lengths
- **Wild Bootstrap**: For heteroskedastic data

### 2. **Advanced Monte Carlo Simulations**
- **GARCH Filtered Historical Simulation**: Models volatility clustering
- **Jump-Diffusion**: Merton model with discontinuous jumps
- **Regime-Switching**: Markov switching models
- **Copula Simulation**: Multi-asset dependency modeling

### 3. **Walk-Forward Optimization Variants**
- **Anchored Walk-Forward**: Growing training window
- **Rolling Walk-Forward**: Fixed-size sliding window
- **Expanding Walk-Forward**: Both windows expand
- **Multi-Objective**: Pareto-optimal solutions
- **Reoptimization Tracking**: Parameter drift analysis

### 4. **Scenario Analysis**
- **Historical Scenarios**: 2008 crisis, COVID crash, etc.
- **Custom Stress Tests**: User-defined shocks
- **Multi-Factor Stress**: Factor-based stress testing
- **Reverse Stress Tests**: Find breaking point scenarios
- **Worst-Case Analysis**: Historical VaR estimation

### 5. **Synthetic Data Generation**
- **TimeSeriesGAN**: Generate realistic market data
- **TimeSeriesVAE**: Probabilistic latent representation
- **Statistical Validation**: KS tests, moment matching

### 6. **Advanced Cross-Validation**
- **Purged K-Fold**: Prevents time series data leakage
- **Nested CV**: Unbiased hyperparameter tuning
- **Walk-Forward CV Hybrid**: Combines WF with CV

## Installation

### PowerShell (Windows)
```powershell
cd backend/simulation_engine
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

Server runs on `http://localhost:5005`

## API Endpoints

### 1. Bootstrap Simulation

**POST** `/api/simulation/bootstrap`

```json
{
  "ticker": "SPY",
  "method": "block",
  "n_simulations": 1000,
  "block_size": 10
}
```

**Response:**
```json
{
  "ticker": "SPY",
  "method": "block",
  "n_simulations": 1000,
  "statistics": {
    "mean": {
      "point_estimate": 0.0008,
      "bootstrap_mean": 0.00082,
      "ci_lower": 0.00045,
      "ci_upper": 0.00115
    }
  }
}
```

### 2. Monte Carlo Simulation

**POST** `/api/simulation/monte-carlo`

```json
{
  "ticker": "SPY",
  "method": "garch",
  "n_simulations": 1000,
  "forecast_horizon": 252
}
```

Methods: `garch`, `jump_diffusion`, `regime_switching`

### 3. Walk-Forward Comparison

**POST** `/api/simulation/walk-forward/compare`

```json
{
  "ticker": "SPY",
  "strategy_params": {
    "fast": [10, 20, 30],
    "slow": [50, 100, 150]
  },
  "methods": ["anchored", "rolling", "expanding"]
}
```

### 4. Scenario Analysis

**POST** `/api/simulation/scenario`

```json
{
  "portfolio": {
    "SPY": 0.6,
    "TLT": 0.4
  },
  "scenarios": ["2008_crisis", "covid_crash"],
  "benchmark": "SPY"
}
```

**Available Scenarios:**
- `2008_crisis`: Sep 2008 - Mar 2009
- `covid_crash`: Feb 2020 - Apr 2020
- `dotcom_bubble`: Mar 2000 - Oct 2002
- `1987_crash`: Oct 1987 - Nov 1987
- `volmageddon`: Feb 2018
- `repo_crisis`: Sep 2019 - Oct 2019

### 5. Custom Stress Test

**POST** `/api/simulation/stress-test`

```json
{
  "portfolio": {
    "SPY": 0.6,
    "TLT": 0.4
  },
  "shocks": {
    "SPY": -0.20,
    "TLT": 0.10
  }
}
```

### 6. Synthetic Data Generation

**POST** `/api/simulation/synthetic`

```json
{
  "ticker": "SPY",
  "method": "gan",
  "n_samples": 1000,
  "epochs": 100
}
```

Methods: `gan`, `vae`

### 7. Cross-Validation

**POST** `/api/simulation/cross-validation`

```json
{
  "ticker": "SPY",
  "strategy_params": {
    "fast": [10, 20],
    "slow": [50, 100]
  },
  "method": "purged_kfold",
  "n_splits": 5
}
```

Methods: `purged_kfold`, `nested_cv`, `walk_forward_cv_hybrid`

### 8. Comprehensive Simulation

**POST** `/api/simulation/comprehensive`

```json
{
  "ticker": "SPY",
  "include_bootstrap": true,
  "include_monte_carlo": true,
  "include_scenario": false,
  "n_simulations": 1000
}
```

## Python Usage Examples

### Bootstrap Resampling

```python
import bootstrap
import pandas as pd

# Sample returns
returns = pd.Series([...])

# Block bootstrap
samples = bootstrap.block_bootstrap(returns, block_size=10, n_simulations=1000)

# Bootstrap confidence interval
def sharpe_ratio(r):
    return r.mean() / r.std() * np.sqrt(252)

ci = bootstrap.bootstrap_confidence_interval(
    returns,
    sharpe_ratio,
    bootstrap_method='block',
    n_simulations=1000
)

print(f"Sharpe 95% CI: [{ci['lower_bound']:.2f}, {ci['upper_bound']:.2f}]")
```

### GARCH Monte Carlo

```python
import monte_carlo_advanced

# Filtered historical simulation
result = monte_carlo_advanced.filtered_historical_simulation(
    returns,
    method='garch',
    n_simulations=1000,
    forecast_horizon=252
)

print(f"GARCH AIC: {result['aic']:.2f}")
print(f"Simulated paths shape: {result['simulated_paths'].shape}")
```

### Walk-Forward Optimization

```python
import walk_forward_variants

# Anchored walk-forward
result = walk_forward_variants.anchored_walk_forward(
    data,
    strategy_func,
    param_grid={'fast': [10, 20], 'slow': [50, 100]},
    train_size=252,
    test_size=63
)

print(f"Average Sharpe: {result['summary']['avg_sharpe']:.2f}")
print(f"Win Rate: {result['summary']['win_rate']:.1%}")
```

### Scenario Analysis

```python
import scenario_analysis

# Replay 2008 crisis
portfolio = {'SPY': 0.6, 'TLT': 0.4}
result = scenario_analysis.replay_historical_scenario(
    portfolio,
    '2008_crisis',
    benchmark='SPY'
)

print(f"Portfolio Return: {result['portfolio_metrics']['total_return']:.1%}")
print(f"Max Drawdown: {result['portfolio_metrics']['max_drawdown']:.1%}")
```

### Synthetic Data Generation

```python
import synthetic_data

# Generate synthetic data with GAN
result = synthetic_data.timeseries_gan(
    returns,
    n_samples=1000,
    epochs=100
)

# Validate synthetic data
validation = result['validation']
print(f"KS Test P-value: {validation['ks_pvalue']:.4f}")
print(f"Test Passed: {validation['ks_passed']}")
```

### Advanced Cross-Validation

```python
import cross_validation

# Purged K-Fold CV
result = cross_validation.purged_kfold_cv(
    data,
    strategy_func,
    param_grid,
    n_splits=5,
    embargo=5
)

print(f"Average Sharpe: {result['summary']['avg_sharpe']:.2f}")
print(f"Sharpe Std: {result['summary']['std_sharpe']:.2f}")
```

## Mathematical Background

### Bootstrap Methods

**Block Bootstrap**: For time series with autocorrelation
- Samples consecutive blocks instead of individual observations
- Block size determines balance between bias and variance
- Optimal block size ≈ n^(1/3)

**Stationary Bootstrap**: Random block lengths
- Block length ~ Geometric(p) where p = 1/avg_block_size
- Preserves stationarity properties
- Better for long-memory processes

### Monte Carlo Simulations

**GARCH(1,1) Model**:
```
σ²ₜ = ω + α·ε²ₜ₋₁ + β·σ²ₜ₋₁
rₜ = μ + σₜ·zₜ
```

**Jump-Diffusion**:
```
dS/S = μdt + σdW + JdN
```
where N is Poisson process, J is jump size

**Regime-Switching**:
```
rₜ = μ(sₜ) + σ(sₜ)·εₜ
P(sₜ = j | sₜ₋₁ = i) = pᵢⱼ
```

### Walk-Forward Optimization

**Anchored**: Training window grows from start
- Pros: Uses all available data
- Cons: Old data may not be relevant

**Rolling**: Fixed-size sliding window
- Pros: Adapts to recent conditions
- Cons: Discards historical data

**Expanding**: Both windows grow
- Pros: Balanced approach
- Cons: More computationally intensive

### Cross-Validation

**Purged K-Fold**: Prevents leakage in time series
1. Split data into K folds
2. For each test fold, purge overlapping training data
3. Embargo future observations
4. Average performance across folds

**Nested CV**: Unbiased hyperparameter selection
- Outer loop: Performance estimation
- Inner loop: Hyperparameter tuning
- Prevents optimistic bias

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run component tests
pytest tests/test_bootstrap.py -v
pytest tests/test_monte_carlo.py -v
pytest tests/test_walk_forward.py -v

# Run integration tests (requires running server)
python app.py &
pytest tests/test_integration.py -v
```

## Project Structure

```
simulation_engine/
├── app.py                      # Flask API server (Port 5005)
├── config.py                   # Configuration
├── utils.py                    # Utility functions
├── bootstrap.py                # Bootstrap methods
├── monte_carlo_advanced.py     # Advanced Monte Carlo
├── walk_forward_variants.py    # Walk-forward optimization
├── scenario_analysis.py        # Scenario analysis
├── synthetic_data.py           # GAN/VAE data generation
├── cross_validation.py         # Advanced CV methods
├── requirements.txt            # Dependencies
├── setup.ps1                   # Setup script
├── README.md                   # This file
└── tests/
    ├── test_bootstrap.py
    ├── test_monte_carlo.py
    ├── test_walk_forward.py
    └── test_integration.py
```

## Best Practices

1. **Bootstrap**: Use block bootstrap for time series data
2. **Monte Carlo**: Validate model fit before using simulations
3. **Walk-Forward**: Always test out-of-sample
4. **Scenarios**: Test across multiple market conditions
5. **Synthetic Data**: Validate against real data distribution
6. **Cross-Validation**: Use purged K-fold for time series

## Performance Considerations

- **GARCH fitting**: CPU-intensive, cache fitted models
- **GAN training**: GPU-accelerated (if available)
- **Bootstrap**: Parallelize across simulations
- **Walk-Forward**: Can be parallelized across windows

## Troubleshooting

**GARCH convergence issues**:
- Ensure sufficient data (>500 observations)
- Check for extreme outliers
- Try different starting values

**GAN training unstable**:
- Reduce learning rate
- Increase training epochs
- Use batch normalization

**Memory issues**:
- Reduce n_simulations
- Process in batches
- Use generators instead of arrays

## References

- **Bootstrap**: Politis & Romano (1994). "The Stationary Bootstrap"
- **GARCH**: Bollerslev (1986). "Generalized Autoregressive Conditional Heteroskedasticity"
- **Jump-Diffusion**: Merton (1976). "Option Pricing When Underlying Stock Returns Are Discontinuous"
- **Walk-Forward**: Pardo (2008). "The Evaluation and Optimization of Trading Strategies"
- **Purged CV**: López de Prado (2018). "Advances in Financial Machine Learning"

## License

MIT License - See main project LICENSE file

---

**Built for Trade2025** - Advanced simulation and validation for systematic trading
