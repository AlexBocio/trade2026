# monte_carlo_advanced.py - Advanced Monte Carlo simulation methods

import numpy as np
import pandas as pd
from typing import Dict, Tuple
import logging
from arch import arch_model
from scipy import stats
from scipy.optimize import minimize
from config import Config
from utils import validate_returns, ensure_positive_definite

logger = logging.getLogger(__name__)


def filtered_historical_simulation(
    returns: pd.Series,
    method: str = 'garch',
    n_simulations: int = 1000,
    forecast_horizon: int = None
) -> Dict:
    """
    Filtered Historical Simulation using GARCH(1,1).

    Fits a GARCH model, extracts standardized residuals,
    and simulates future returns by resampling residuals.

    Args:
        returns: Time series of returns
        method: Model type ('garch', 'egarch', 'gjr-garch')
        n_simulations: Number of simulation paths
        forecast_horizon: Number of periods to simulate (None = same as returns length)

    Returns:
        Dictionary with simulated paths, fitted parameters, and diagnostics

    Raises:
        ValueError: If returns is invalid
    """
    returns = validate_returns(returns)
    returns_pct = returns * 100  # arch library expects percentage returns

    if forecast_horizon is None:
        forecast_horizon = len(returns)

    # Fit GARCH model
    if method == 'garch':
        model = arch_model(returns_pct, vol='Garch', p=1, q=1)
    elif method == 'egarch':
        model = arch_model(returns_pct, vol='EGARCH', p=1, q=1)
    elif method == 'gjr-garch':
        model = arch_model(returns_pct, vol='GARCH', p=1, o=1, q=1)  # GJR-GARCH
    else:
        raise ValueError(f"Unknown GARCH method: {method}")

    # Fit model
    fitted = model.fit(disp='off')

    # Extract standardized residuals
    std_residuals = fitted.std_resid

    # Simulate paths
    simulated_paths = np.zeros((n_simulations, forecast_horizon))

    for i in range(n_simulations):
        # Resample standardized residuals
        resampled_residuals = np.random.choice(std_residuals, size=forecast_horizon)

        # Forecast volatility path
        volatility_forecast = fitted.forecast(horizon=forecast_horizon, start=0)
        vol_path = np.sqrt(volatility_forecast.variance.values[-1, :])

        # Reconstruct returns: return = mean + vol * std_residual
        mean_return = fitted.params['mu']
        simulated_paths[i, :] = mean_return + vol_path * resampled_residuals

    # Convert back from percentage
    simulated_paths = simulated_paths / 100

    logger.info(f"Generated {n_simulations} GARCH-filtered simulation paths")

    return {
        'simulated_paths': simulated_paths,
        'fitted_params': dict(fitted.params),
        'aic': fitted.aic,
        'bic': fitted.bic,
        'log_likelihood': fitted.loglikelihood,
        'model_type': method,
        'forecast_horizon': forecast_horizon
    }


def copula_simulation(
    returns_matrix: pd.DataFrame,
    copula_type: str = 'gaussian',
    n_simulations: int = 1000,
    forecast_horizon: int = None
) -> Dict:
    """
    Multi-asset simulation using copulas.

    Models marginal distributions and dependencies separately.
    Copula captures dependency structure.

    Args:
        returns_matrix: DataFrame of returns for multiple assets
        copula_type: Type of copula ('gaussian', 't', 'clayton', 'gumbel')
        n_simulations: Number of simulation paths
        forecast_horizon: Number of periods to simulate

    Returns:
        Dictionary with simulated paths and copula parameters

    Raises:
        ValueError: If returns_matrix is invalid
    """
    if forecast_horizon is None:
        forecast_horizon = len(returns_matrix)

    n_assets = returns_matrix.shape[1]

    # Fit marginal distributions (using empirical CDF)
    marginal_cdfs = {}
    for col in returns_matrix.columns:
        data = returns_matrix[col].dropna().values
        marginal_cdfs[col] = stats.rankdata(data) / (len(data) + 1)

    # Transform to uniform [0,1] using probability integral transform
    uniform_data = np.zeros((len(returns_matrix), n_assets))
    for i, col in enumerate(returns_matrix.columns):
        data = returns_matrix[col].dropna().values
        uniform_data[:len(data), i] = stats.rankdata(data) / (len(data) + 1)

    # Fit copula
    if copula_type == 'gaussian':
        # Estimate correlation matrix from normal quantiles
        normal_quantiles = stats.norm.ppf(np.clip(uniform_data, 1e-6, 1-1e-6))
        correlation_matrix = np.corrcoef(normal_quantiles.T)
        correlation_matrix = ensure_positive_definite(correlation_matrix)

        copula_params = {'correlation': correlation_matrix}

    elif copula_type == 't':
        # Student's t copula
        normal_quantiles = stats.norm.ppf(np.clip(uniform_data, 1e-6, 1-1e-6))
        correlation_matrix = np.corrcoef(normal_quantiles.T)
        correlation_matrix = ensure_positive_definite(correlation_matrix)

        # Estimate degrees of freedom (simplified)
        df = 5  # Default value

        copula_params = {'correlation': correlation_matrix, 'df': df}

    else:
        raise ValueError(f"Copula type {copula_type} not implemented")

    # Simulate from copula
    simulated_paths = np.zeros((n_simulations, forecast_horizon, n_assets))

    for i in range(n_simulations):
        if copula_type == 'gaussian':
            # Simulate from multivariate normal copula
            mvn_samples = np.random.multivariate_normal(
                mean=np.zeros(n_assets),
                cov=correlation_matrix,
                size=forecast_horizon
            )
            uniform_samples = stats.norm.cdf(mvn_samples)

        elif copula_type == 't':
            # Simulate from multivariate t copula
            mvt_samples = stats.multivariate_normal.rvs(
                mean=np.zeros(n_assets),
                cov=correlation_matrix,
                size=forecast_horizon
            )
            chi2_samples = np.random.chisquare(df, size=forecast_horizon)
            t_samples = mvt_samples / np.sqrt(chi2_samples[:, np.newaxis] / df)
            uniform_samples = stats.t.cdf(t_samples, df=df)

        # Transform back to original marginal distributions
        for j, col in enumerate(returns_matrix.columns):
            data = returns_matrix[col].dropna().values
            quantiles = np.quantile(data, uniform_samples[:, j])
            simulated_paths[i, :, j] = quantiles

    logger.info(f"Generated {n_simulations} copula simulation paths ({copula_type})")

    return {
        'simulated_paths': simulated_paths,
        'copula_type': copula_type,
        'copula_params': copula_params,
        'n_assets': n_assets,
        'asset_names': list(returns_matrix.columns)
    }


def jump_diffusion_simulation(
    returns: pd.Series,
    n_simulations: int = 1000,
    forecast_horizon: int = None
) -> Dict:
    """
    Merton Jump-Diffusion model simulation.

    Return process: dS/S = μ dt + σ dW + J dN
    where J is jump size and N is Poisson process.

    Args:
        returns: Time series of returns
        n_simulations: Number of simulation paths
        forecast_horizon: Number of periods to simulate

    Returns:
        Dictionary with simulated paths and estimated parameters

    Raises:
        ValueError: If returns is invalid
    """
    returns = validate_returns(returns)

    if forecast_horizon is None:
        forecast_horizon = len(returns)

    # Estimate parameters using method of moments
    mean_return = returns.mean()
    vol = returns.std()

    # Simple parameter estimation
    # Jump intensity (lambda)
    returns_sorted = np.sort(np.abs(returns.values))
    threshold = np.percentile(returns_sorted, 95)  # Top 5% are potential jumps
    jumps = returns[np.abs(returns) > threshold]
    lambda_jump = len(jumps) / len(returns)  # Jump intensity

    # Jump size distribution
    if len(jumps) > 0:
        mu_jump = jumps.mean()
        sigma_jump = jumps.std()
    else:
        mu_jump = 0
        sigma_jump = vol

    # Diffusion component
    sigma_diffusion = np.sqrt(vol**2 - lambda_jump * (mu_jump**2 + sigma_jump**2))
    sigma_diffusion = max(sigma_diffusion, vol * 0.5)  # Ensure positive

    # Simulate paths
    simulated_paths = np.zeros((n_simulations, forecast_horizon))

    for i in range(n_simulations):
        # Diffusion component
        diffusion = np.random.normal(mean_return, sigma_diffusion, size=forecast_horizon)

        # Jump component
        n_jumps = np.random.poisson(lambda_jump * forecast_horizon)
        jump_times = np.random.choice(forecast_horizon, size=min(n_jumps, forecast_horizon), replace=False)
        jump_sizes = np.random.normal(mu_jump, sigma_jump, size=len(jump_times))

        # Combine diffusion and jumps
        path = diffusion.copy()
        path[jump_times] += jump_sizes

        simulated_paths[i, :] = path

    logger.info(f"Generated {n_simulations} jump-diffusion simulation paths")

    return {
        'simulated_paths': simulated_paths,
        'parameters': {
            'mean_return': mean_return,
            'sigma_diffusion': sigma_diffusion,
            'lambda_jump': lambda_jump,
            'mu_jump': mu_jump,
            'sigma_jump': sigma_jump
        },
        'forecast_horizon': forecast_horizon
    }


def regime_switching_simulation(
    returns: pd.Series,
    n_regimes: int = 2,
    n_simulations: int = 1000,
    forecast_horizon: int = None
) -> Dict:
    """
    Markov Regime-Switching model simulation.

    Models returns as coming from different regimes (e.g., bull/bear markets).
    Each regime has its own return distribution.

    Args:
        returns: Time series of returns
        n_regimes: Number of regimes
        n_simulations: Number of simulation paths
        forecast_horizon: Number of periods to simulate

    Returns:
        Dictionary with simulated paths and regime parameters

    Raises:
        ValueError: If returns is invalid
    """
    returns = validate_returns(returns)

    if forecast_horizon is None:
        forecast_horizon = len(returns)

    # Simple regime identification using K-means on returns
    from sklearn.cluster import KMeans

    returns_array = returns.values.reshape(-1, 1)
    kmeans = KMeans(n_clusters=n_regimes, random_state=42)
    regime_labels = kmeans.fit_predict(returns_array)

    # Estimate regime parameters
    regime_params = []
    for regime in range(n_regimes):
        regime_returns = returns[regime_labels == regime]

        if len(regime_returns) > 0:
            regime_params.append({
                'mean': regime_returns.mean(),
                'std': regime_returns.std(),
                'probability': len(regime_returns) / len(returns)
            })
        else:
            regime_params.append({
                'mean': 0,
                'std': returns.std(),
                'probability': 0
            })

    # Estimate transition matrix
    transition_matrix = np.zeros((n_regimes, n_regimes))

    for i in range(len(regime_labels) - 1):
        current_regime = regime_labels[i]
        next_regime = regime_labels[i + 1]
        transition_matrix[current_regime, next_regime] += 1

    # Normalize rows
    for i in range(n_regimes):
        row_sum = transition_matrix[i, :].sum()
        if row_sum > 0:
            transition_matrix[i, :] /= row_sum
        else:
            transition_matrix[i, :] = 1.0 / n_regimes

    # Simulate paths
    simulated_paths = np.zeros((n_simulations, forecast_horizon))
    regime_paths = np.zeros((n_simulations, forecast_horizon), dtype=int)

    for i in range(n_simulations):
        # Initial regime (sampled from stationary distribution)
        probs = [p['probability'] for p in regime_params]
        current_regime = np.random.choice(n_regimes, p=probs)

        for t in range(forecast_horizon):
            # Record regime
            regime_paths[i, t] = current_regime

            # Sample return from current regime
            params = regime_params[current_regime]
            simulated_paths[i, t] = np.random.normal(params['mean'], params['std'])

            # Transition to next regime
            current_regime = np.random.choice(n_regimes, p=transition_matrix[current_regime, :])

    logger.info(f"Generated {n_simulations} regime-switching simulation paths")

    return {
        'simulated_paths': simulated_paths,
        'regime_paths': regime_paths,
        'regime_params': regime_params,
        'transition_matrix': transition_matrix.tolist(),
        'n_regimes': n_regimes,
        'forecast_horizon': forecast_horizon
    }


def compare_simulation_methods(
    returns: pd.Series,
    methods: list = None,
    n_simulations: int = 1000
) -> pd.DataFrame:
    """
    Compare different Monte Carlo simulation methods.

    Args:
        returns: Time series of returns
        methods: List of methods to compare (None = all methods)
        n_simulations: Number of simulations per method

    Returns:
        DataFrame comparing simulation methods
    """
    if methods is None:
        methods = ['garch', 'jump_diffusion', 'regime_switching']

    results = []

    for method in methods:
        try:
            if method == 'garch':
                sim_result = filtered_historical_simulation(returns, 'garch', n_simulations)
                paths = sim_result['simulated_paths']

            elif method == 'jump_diffusion':
                sim_result = jump_diffusion_simulation(returns, n_simulations)
                paths = sim_result['simulated_paths']

            elif method == 'regime_switching':
                sim_result = regime_switching_simulation(returns, n_regimes=2, n_simulations=n_simulations)
                paths = sim_result['simulated_paths']

            else:
                logger.warning(f"Unknown method: {method}")
                continue

            # Calculate statistics
            mean_simulated = paths.mean()
            std_simulated = paths.std()
            skew_simulated = stats.skew(paths.flatten())
            kurt_simulated = stats.kurtosis(paths.flatten())

            results.append({
                'method': method,
                'mean': mean_simulated,
                'std': std_simulated,
                'skewness': skew_simulated,
                'kurtosis': kurt_simulated,
                'actual_mean': returns.mean(),
                'actual_std': returns.std(),
                'actual_skew': returns.skew(),
                'actual_kurt': returns.kurtosis()
            })

        except Exception as e:
            logger.error(f"Error in {method} simulation: {str(e)}")

    return pd.DataFrame(results)
