# herc_vs_hrp.py - HERC vs HRP Comparison Framework
# Side-by-side comparison and analysis

import numpy as np
import pandas as pd
from typing import Dict
import logging
from herc import herc_portfolio
from hrp import hrp_portfolio
from risk_contribution import calculate_risk_contribution, calculate_cvar_contribution
from tail_risk_metrics import portfolio_tail_risk_analysis

logger = logging.getLogger(__name__)


def compare_herc_hrp(returns: pd.DataFrame,
                     cov_matrix: np.ndarray = None,
                     linkage_method: str = 'single',
                     risk_measure: str = 'volatility') -> dict:
    """
    Compare HERC and HRP side-by-side.

    Runs both algorithms and provides comprehensive comparison metrics
    to help decide which approach is better for the given data.

    Args:
        returns: Returns dataframe (T × N)
        cov_matrix: Covariance matrix (if None, computed from returns)
        linkage_method: Linkage method for both algorithms
        risk_measure: Risk measure for HERC ('volatility' or 'cvar')

    Returns:
        {
            'herc': HERC portfolio results,
            'hrp': HRP portfolio results,
            'comparison': Comparison metrics,
            'risk_contributions': RC comparison,
            'recommendation': Which method is better
        }
    """
    if cov_matrix is None:
        cov_matrix = returns.cov().values

    logger.info(f"Comparing HERC vs HRP on {len(returns.columns)} assets")

    # Run HERC
    herc_results = herc_portfolio(
        returns,
        cov_matrix,
        linkage_method=linkage_method,
        risk_measure=risk_measure
    )

    # Run HRP
    hrp_results = hrp_portfolio(
        returns,
        cov_matrix,
        linkage_method=linkage_method
    )

    # Calculate risk contributions for both
    herc_rc = calculate_risk_contribution(herc_results['weights'], cov_matrix)
    hrp_rc = calculate_risk_contribution(hrp_results['weights'], cov_matrix)

    # Calculate CVaR for both
    herc_cvar = calculate_cvar_contribution(herc_results['weights'], returns)
    hrp_cvar = calculate_cvar_contribution(hrp_results['weights'], returns)

    # Full tail risk analysis for both
    herc_tail = portfolio_tail_risk_analysis(herc_results['weights'], returns)
    hrp_tail = portfolio_tail_risk_analysis(hrp_results['weights'], returns)

    # Comparison metrics
    comparison = {
        # Volatility
        'herc_vol': float(herc_results['portfolio_metrics']['volatility']),
        'hrp_vol': float(hrp_results['portfolio_metrics']['volatility']),
        'vol_difference': float(herc_results['portfolio_metrics']['volatility'] -
                               hrp_results['portfolio_metrics']['volatility']),

        # CVaR (tail risk)
        'herc_cvar': float(herc_cvar['cvar']),
        'hrp_cvar': float(hrp_cvar['cvar']),
        'cvar_difference': float(herc_cvar['cvar'] - hrp_cvar['cvar']),

        # Diversification
        'herc_diversification': float(herc_results['portfolio_metrics']['diversification_ratio']),
        'hrp_diversification': float(hrp_results['portfolio_metrics']['diversification_ratio']),

        # Concentration
        'herc_max_weight': float(herc_results['portfolio_metrics']['concentration']),
        'hrp_max_weight': float(hrp_results['portfolio_metrics']['concentration']),

        # Weight difference (L1 norm)
        'weight_difference': float(np.sum(np.abs(herc_results['weights'] - hrp_results['weights']))),

        # Risk contribution concentration (lower is more equal)
        'herc_rc_concentration': float(np.std(herc_rc['percentage_rc'])),
        'hrp_rc_concentration': float(np.std(hrp_rc['percentage_rc'])),

        # Max drawdown
        'herc_max_drawdown': float(herc_tail['max_drawdown']),
        'hrp_max_drawdown': float(hrp_tail['max_drawdown']),

        # Sortino ratio
        'herc_sortino': float(herc_tail['sortino_ratio']),
        'hrp_sortino': float(hrp_tail['sortino_ratio']),

        # Calmar ratio
        'herc_calmar': float(herc_tail['calmar_ratio']),
        'hrp_calmar': float(hrp_tail['calmar_ratio'])
    }

    # Generate recommendations
    recommendations = []
    score_herc = 0
    score_hrp = 0

    # 1. Risk Contribution Equality
    if comparison['herc_rc_concentration'] < comparison['hrp_rc_concentration']:
        recommendations.append("HERC provides more equal risk contribution")
        score_herc += 2
    else:
        recommendations.append("HRP provides more equal risk contribution")
        score_hrp += 2

    # 2. Tail Risk (CVaR)
    if abs(comparison['herc_cvar']) < abs(comparison['hrp_cvar']):
        recommendations.append("HERC has lower tail risk (better CVaR)")
        score_herc += 2
    else:
        recommendations.append("HRP has lower tail risk (better CVaR)")
        score_hrp += 2

    # 3. Volatility
    if comparison['herc_vol'] < comparison['hrp_vol']:
        recommendations.append("HERC has lower volatility")
        score_herc += 1
    else:
        recommendations.append("HRP has lower volatility")
        score_hrp += 1

    # 4. Diversification
    if comparison['herc_diversification'] > comparison['hrp_diversification']:
        recommendations.append("HERC is more diversified")
        score_herc += 1
    else:
        recommendations.append("HRP is more diversified")
        score_hrp += 1

    # 5. Sortino Ratio
    if comparison['herc_sortino'] > comparison['hrp_sortino']:
        recommendations.append("HERC has better Sortino ratio")
        score_herc += 1
    else:
        recommendations.append("HRP has better Sortino ratio")
        score_hrp += 1

    # 6. Maximum Drawdown
    if abs(comparison['herc_max_drawdown']) < abs(comparison['hrp_max_drawdown']):
        recommendations.append("HERC has lower maximum drawdown")
        score_herc += 1
    else:
        recommendations.append("HRP has lower maximum drawdown")
        score_hrp += 1

    # Overall recommendation
    if score_herc > score_hrp:
        overall = f"HERC is recommended (score: {score_herc} vs {score_hrp})"
    elif score_hrp > score_herc:
        overall = f"HRP is recommended (score: {score_hrp} vs {score_herc})"
    else:
        overall = f"HERC and HRP are comparable (score: {score_herc} vs {score_hrp})"

    comparison['recommendations'] = recommendations
    comparison['overall_recommendation'] = overall
    comparison['score_herc'] = score_herc
    comparison['score_hrp'] = score_hrp

    logger.info(f"Comparison complete - {overall}")

    return {
        'herc': {
            'weights': herc_results['weights'].tolist(),
            'risk_contributions': herc_rc['percentage_rc'].tolist(),
            'portfolio_metrics': herc_results['portfolio_metrics'],
            'tail_metrics': herc_tail
        },
        'hrp': {
            'weights': hrp_results['weights'].tolist(),
            'risk_contributions': hrp_rc['percentage_rc'].tolist(),
            'portfolio_metrics': hrp_results['portfolio_metrics'],
            'tail_metrics': hrp_tail
        },
        'comparison': comparison,
        'asset_names': returns.columns.tolist()
    }


def backtest_comparison(returns: pd.DataFrame,
                       train_size: float = 0.7,
                       rebalance_frequency: int = 63) -> dict:
    """
    Backtest HERC vs HRP with periodic rebalancing.

    Args:
        returns: Returns dataframe
        train_size: Fraction of data for initial training
        rebalance_frequency: Days between rebalancing (63 = quarterly)

    Returns:
        Out-of-sample performance comparison
    """
    n_periods = len(returns)
    train_periods = int(n_periods * train_size)

    logger.info(f"Backtesting HERC vs HRP: {train_periods} train, "
                f"{n_periods - train_periods} test periods")

    # Lists to store portfolio values
    herc_values = [1.0]
    hrp_values = [1.0]
    dates = []

    # Rolling window backtest
    for start in range(train_periods, n_periods, rebalance_frequency):
        # Training data
        train_returns = returns.iloc[:start]

        # Test period
        end = min(start + rebalance_frequency, n_periods)
        test_returns = returns.iloc[start:end]

        if len(test_returns) == 0:
            break

        # Optimize on training data
        herc_weights = herc_portfolio(train_returns)['weights']
        hrp_weights = hrp_portfolio(train_returns)['weights']

        # Apply to test data
        herc_portfolio_returns = (test_returns @ herc_weights).values
        hrp_portfolio_returns = (test_returns @ hrp_weights).values

        # Update portfolio values
        for i in range(len(test_returns)):
            herc_values.append(herc_values[-1] * (1 + herc_portfolio_returns[i]))
            hrp_values.append(hrp_values[-1] * (1 + hrp_portfolio_returns[i]))
            dates.append(test_returns.index[i])

    # Calculate performance metrics
    herc_return = (herc_values[-1] - 1) * 100
    hrp_return = (hrp_values[-1] - 1) * 100

    herc_vol = np.std(np.diff(herc_values) / herc_values[:-1]) * np.sqrt(252) * 100
    hrp_vol = np.std(np.diff(hrp_values) / hrp_values[:-1]) * np.sqrt(252) * 100

    herc_sharpe = (herc_return / herc_vol) if herc_vol > 0 else 0
    hrp_sharpe = (hrp_return / hrp_vol) if hrp_vol > 0 else 0

    return {
        'herc_return': float(herc_return),
        'hrp_return': float(hrp_return),
        'herc_volatility': float(herc_vol),
        'hrp_volatility': float(hrp_vol),
        'herc_sharpe': float(herc_sharpe),
        'hrp_sharpe': float(hrp_sharpe),
        'herc_final_value': float(herc_values[-1]),
        'hrp_final_value': float(hrp_values[-1]),
        'n_rebalances': len(herc_values) // rebalance_frequency,
        'winner': 'HERC' if herc_sharpe > hrp_sharpe else 'HRP'
    }


def weight_stability_analysis(returns: pd.DataFrame,
                              n_simulations: int = 100) -> dict:
    """
    Analyze weight stability under bootstrap resampling.

    More stable weights indicate robustness to estimation error.

    Args:
        returns: Returns dataframe
        n_simulations: Number of bootstrap samples

    Returns:
        Weight stability metrics
    """
    n_periods = len(returns)
    n_assets = len(returns.columns)

    herc_weights_all = np.zeros((n_simulations, n_assets))
    hrp_weights_all = np.zeros((n_simulations, n_assets))

    logger.info(f"Running {n_simulations} bootstrap simulations")

    for i in range(n_simulations):
        # Bootstrap sample
        sample_idx = np.random.choice(n_periods, n_periods, replace=True)
        bootstrap_returns = returns.iloc[sample_idx]

        # Run both methods
        herc_weights_all[i] = herc_portfolio(bootstrap_returns)['weights']
        hrp_weights_all[i] = hrp_portfolio(bootstrap_returns)['weights']

    # Calculate weight stability (lower std = more stable)
    herc_weight_std = np.mean(np.std(herc_weights_all, axis=0))
    hrp_weight_std = np.mean(np.std(hrp_weights_all, axis=0))

    return {
        'herc_weight_stability': float(herc_weight_std),
        'hrp_weight_stability': float(hrp_weight_std),
        'more_stable': 'HERC' if herc_weight_std < hrp_weight_std else 'HRP',
        'stability_difference': float(abs(herc_weight_std - hrp_weight_std))
    }
