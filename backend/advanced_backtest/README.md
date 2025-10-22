# Advanced Backtesting Engine

Sophisticated backtesting validation system that prevents overfitting and validates trading strategy robustness using institutional-grade techniques.

## Features

### 1. **Walk-Forward Optimization**
- Proper out-of-sample testing
- Sliding window approach
- Parameter stability analysis
- Prevents look-ahead bias

### 2. **Combinatorial Purged Cross-Validation (CPCV)**
- Time series-aware cross-validation
- Purging: removes overlapping observations
- Embargo: prevents information leakage
- Probability of Skill (POS) calculation

### 3. **Robustness Analysis**
- **Monte Carlo Simulation**: Tests if strategy exploits genuine patterns vs. luck
- **Parameter Sensitivity**: How stable is performance across parameter ranges?
- **Kolmogorov Complexity**: Simpler strategies generalize better
- **Regime Change Testing**: Does strategy work in different market conditions?

### 4. **Meta-Labeling**
- ML-based trade filtering
- Use ML to decide WHEN to trade, not what direction
- Improves Sharpe ratio by filtering low-conviction trades

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

Server runs on `http://localhost:5003`

## API Endpoints

### 1. Walk-Forward Optimization

**POST** `/api/backtest/walk-forward`

```json
{
  "ticker": "AAPL",
  "strategy": "ma_crossover",
  "param_grid": {
    "fast": [10, 20, 30],
    "slow": [50, 100, 150]
  },
  "train_period": 252,
  "test_period": 63,
  "start_date": "2020-01-01",
  "end_date": "2023-12-31"
}
```

**Response:**
```json
{
  "ticker": "AAPL",
  "results": [
    {
      "train_start": "2020-01-01",
      "train_end": "2020-12-31",
      "test_start": "2021-01-01",
      "test_end": "2021-03-31",
      "optimal_params": {"fast": 20, "slow": 50},
      "train_sharpe": 1.45,
      "test_sharpe": 1.23,
      "test_return": 0.085
    }
  ],
  "summary": {
    "num_windows": 8,
    "avg_test_sharpe": 1.15,
    "avg_test_return": 0.073,
    "total_return": 0.612,
    "total_sharpe": 1.28,
    "win_rate": 0.75,
    "parameter_stability": 0.82
  }
}
```

### 2. Combinatorial Purged Cross-Validation

**POST** `/api/backtest/cross-validation`

```json
{
  "ticker": "AAPL",
  "strategy": "ma_crossover",
  "param_grid": {
    "fast": [10, 20, 30],
    "slow": [50, 100, 150]
  },
  "n_splits": 5,
  "purge_pct": 0.05,
  "embargo_pct": 0.01
}
```

**Response:**
```json
{
  "ticker": "AAPL",
  "n_splits": 5,
  "mean_sharpe": 1.23,
  "std_sharpe": 0.18,
  "mean_return": 0.089,
  "probability_of_skill": 0.94
}
```

### 3. Robustness Analysis

**POST** `/api/backtest/robustness`

```json
{
  "ticker": "AAPL",
  "strategy": "ma_crossover",
  "params": {"fast": 20, "slow": 50},
  "tests": ["monte_carlo", "param_sensitivity", "regime_change"],
  "param_sensitivity": {
    "param_name": "fast",
    "variations": [10, 15, 20, 25, 30]
  }
}
```

**Response:**
```json
{
  "ticker": "AAPL",
  "params": {"fast": 20, "slow": 50},
  "tests_run": ["monte_carlo", "param_sensitivity", "regime_change"],
  "results": {
    "monte_carlo": {
      "baseline_sharpe": 1.45,
      "mean_random_sharpe": 0.12,
      "p_value": 0.018,
      "is_significant": true
    },
    "parameter_sensitivity": {
      "param_name": "fast",
      "results": [
        {"param_value": 10, "sharpe": 1.12, "return": 0.23},
        {"param_value": 15, "sharpe": 1.34, "return": 0.28},
        {"param_value": 20, "sharpe": 1.45, "return": 0.31}
      ],
      "sensitivity_score": 0.23,
      "is_robust": true
    },
    "regime_change": {
      "pre_regime_sharpe": 1.52,
      "post_regime_sharpe": 1.38,
      "stability_score": 0.91,
      "is_stable": true
    }
  }
}
```

### 4. Comprehensive Backtesting

**POST** `/api/backtest/comprehensive`

Runs all tests (walk-forward + CPCV + robustness) and generates a recommendation.

```json
{
  "ticker": "AAPL",
  "strategy": "ma_crossover",
  "param_grid": {
    "fast": [10, 20, 30],
    "slow": [50, 100, 150]
  }
}
```

**Response:**
```json
{
  "ticker": "AAPL",
  "best_params": {"fast": 20, "slow": 50},
  "walk_forward": {
    "total_sharpe": 1.28,
    "total_return": 0.612,
    "win_rate": 0.75,
    "parameter_stability": 0.82
  },
  "cross_validation": {
    "mean_sharpe": 1.23,
    "std_sharpe": 0.18,
    "probability_of_skill": 0.94
  },
  "robustness": {
    "monte_carlo": {
      "baseline_sharpe": 1.45,
      "p_value": 0.018,
      "is_significant": true
    },
    "complexity": {
      "complexity_score": 2.8,
      "is_simple": true
    },
    "regime_stability": {
      "stability_score": 0.91,
      "is_stable": true
    }
  },
  "recommendation": {
    "recommendation": "STRONG BUY",
    "score": 7,
    "max_score": 8,
    "reasons": [
      "Strong walk-forward Sharpe ratio",
      "Parameters are stable across time",
      "High probability of genuine skill",
      "Statistically significant performance",
      "Strategy is simple and generalizable",
      "Stable across market regimes"
    ]
  }
}
```

## Python Usage Examples

### Walk-Forward Optimization

```python
from walk_forward import WalkForwardOptimizer, moving_average_crossover_strategy
import pandas as pd
import yfinance as yf

# Fetch data
data = yf.download('AAPL', start='2020-01-01', end='2023-12-31')
data['returns'] = data['Close'].pct_change()

# Define parameter grid
param_grid = {
    'fast': [10, 20, 30],
    'slow': [50, 100, 150]
}

# Run walk-forward optimization
optimizer = WalkForwardOptimizer(
    data=data,
    strategy_func=moving_average_crossover_strategy,
    param_grid=param_grid,
    train_period=252,  # 1 year training
    test_period=63     # 3 months testing
)

results = optimizer.run()
summary = optimizer.get_summary()

print(f"Total Sharpe: {summary['total_sharpe']:.2f}")
print(f"Total Return: {summary['total_return']:.2%}")
print(f"Win Rate: {summary['win_rate']:.2%}")
print(f"Parameter Stability: {summary['parameter_stability']:.2f}")
```

### Combinatorial Purged Cross-Validation

```python
from cross_validation import CombinatorialPurgedCV
from walk_forward import moving_average_crossover_strategy

# Create CV instance
cv = CombinatorialPurgedCV(
    n_splits=5,
    purge_pct=0.05,    # Purge 5% around test set
    embargo_pct=0.01   # Embargo 1% after test set
)

# Evaluate strategy
results = cv.evaluate_strategy(
    data=data,
    strategy_func=moving_average_crossover_strategy,
    param_grid=param_grid
)

print(f"Mean Sharpe: {results['mean_sharpe']:.2f}")
print(f"Std Sharpe: {results['std_sharpe']:.2f}")
print(f"Probability of Skill: {results['probability_of_skill']:.2%}")
```

### Robustness Analysis

```python
from robustness import RobustnessAnalyzer
from walk_forward import moving_average_crossover_strategy

# Create analyzer
analyzer = RobustnessAnalyzer(
    data=data,
    strategy_func=moving_average_crossover_strategy,
    params={'fast': 20, 'slow': 50}
)

# 1. Monte Carlo simulation
mc_results = analyzer.monte_carlo_simulation(n_simulations=1000)
print(f"P-value: {mc_results['p_value']:.4f}")
print(f"Significant: {mc_results['is_significant']}")

# 2. Parameter sensitivity
sens_results = analyzer.parameter_sensitivity(
    param_name='fast',
    variations=[10, 15, 20, 25, 30]
)
print(f"Sensitivity Score: {sens_results['sensitivity_score']:.2f}")
print(f"Robust: {sens_results['is_robust']}")

# 3. Regime change test
regime_results = analyzer.regime_change_test()
print(f"Stability Score: {regime_results['stability_score']:.2f}")
print(f"Stable: {regime_results['is_stable']}")

# Comprehensive report
report = analyzer.comprehensive_report()
```

### Meta-Labeling

```python
from meta_labeling import MetaLabeler
from walk_forward import moving_average_crossover_strategy

# Primary model: MA crossover
def primary_model(data):
    return moving_average_crossover_strategy(data, {'fast': 20, 'slow': 50})

# Create meta-labeler
meta_labeler = MetaLabeler(primary_model_func=primary_model)

# Train meta-model
train_results = meta_labeler.train(data, holding_period=5)
print(f"CV Accuracy: {train_results['cv_accuracy']:.2%}")

# Backtest with meta-labeling
backtest_results = meta_labeler.backtest_with_meta_labeling(data)

print("\nPrimary Model Only:")
print(f"  Sharpe: {backtest_results['primary_only']['sharpe']:.2f}")
print(f"  Return: {backtest_results['primary_only']['total_return']:.2%}")

print("\nWith Meta-Labeling:")
print(f"  Sharpe: {backtest_results['with_meta_labeling']['sharpe']:.2f}")
print(f"  Return: {backtest_results['with_meta_labeling']['total_return']:.2%}")
print(f"  Trade Reduction: {backtest_results['trade_reduction_pct']:.2%}")
```

## Key Concepts

### Walk-Forward Optimization
Traditional backtesting optimizes parameters on historical data, then tests on the same data → overfitting!

Walk-forward:
1. Optimize on in-sample window (e.g., 1 year)
2. Test on out-of-sample window (e.g., 3 months)
3. Slide forward and repeat
4. Concatenate all out-of-sample results

This mimics real trading where you periodically re-optimize.

### Combinatorial Purged Cross-Validation

**Problem**: Traditional K-fold CV doesn't work for time series (data leakage).

**Solution**:
- **Purging**: Remove observations near the test set (they may overlap due to holding periods)
- **Embargo**: Remove observations immediately after test set (prevents look-ahead)
- **Combinatorial**: Test set can be anywhere in data, not just sequential chunks

### Monte Carlo Simulation

**Question**: Is your strategy genuinely profitable, or just lucky?

**Test**: Randomly shuffle returns and re-run strategy 1000 times.

If your real strategy outperforms >95% of random runs → statistically significant.

### Parameter Sensitivity

**Question**: Is your strategy fragile?

**Test**: Vary parameters ±20% and measure performance change.

Robust strategies have stable performance across parameter range.

### Kolmogorov Complexity

**Principle**: Simpler models generalize better (Occam's Razor).

**Proxy**: Count number of parameters and rules.

Strategies with fewer parameters and simpler logic are less likely to overfit.

### Meta-Labeling

**Traditional ML**: Predict direction (long vs. short).

**Meta-Labeling**:
1. Primary model predicts direction
2. Meta-model predicts whether primary's signal is worth taking

Meta-model features:
- Market regime (volatility, trend)
- Signal quality (strength, consistency)
- Risk factors (correlation, liquidity)

Result: Higher Sharpe ratio by filtering out low-quality trades.

## Project Structure

```
advanced_backtest/
├── app.py                  # Flask API server
├── walk_forward.py         # Walk-forward optimization
├── cross_validation.py     # Combinatorial purged CV
├── robustness.py           # Robustness analysis
├── meta_labeling.py        # Meta-labeling for trade filtering
├── requirements.txt        # Python dependencies
├── setup.ps1              # Automated setup script
└── README.md              # This file
```

## Integration with Frontend

The React frontend (`apps/console/web`) can call these APIs:

```javascript
// Example: Run comprehensive backtest
const response = await fetch('http://localhost:5003/api/backtest/comprehensive', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ticker: 'AAPL',
    strategy: 'ma_crossover',
    param_grid: {
      fast: [10, 20, 30],
      slow: [50, 100, 150]
    }
  })
});

const results = await response.json();
console.log('Recommendation:', results.recommendation.recommendation);
console.log('Sharpe Ratio:', results.walk_forward.total_sharpe);
```

## Best Practices

1. **Always use walk-forward optimization** - Never backtest on the same data you optimized on
2. **Check parameter stability** - If optimal parameters change drastically between windows, strategy may be overfit
3. **Verify statistical significance** - Use Monte Carlo to ensure results aren't due to luck
4. **Test multiple regimes** - Strategy should work in both bull and bear markets
5. **Keep it simple** - Complex strategies rarely generalize to live trading
6. **Use meta-labeling** - Improve Sharpe by filtering out low-conviction trades

## Academic References

- **Walk-Forward**: Pardo, R. (2008). *The Evaluation and Optimization of Trading Strategies*
- **Purged CV**: López de Prado, M. (2018). *Advances in Financial Machine Learning*
- **Meta-Labeling**: López de Prado, M. (2018). Chapter 3: Meta-Labeling
- **Probability of Skill**: Bailey, D. H., & López de Prado, M. (2014). "The Sharpe Ratio Efficient Frontier"

## License

MIT License - See main project LICENSE file

## Support

For issues or questions:
- Check the main project documentation
- Review API endpoint examples above
- Examine Python usage examples

---

**Built for Trade2025** - Institutional-grade backtesting for retail traders
