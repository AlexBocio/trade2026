# utils.py - Utility functions for Simulation Engine

import numpy as np
import pandas as pd
from typing import Union, Callable, Dict, Any
import logging
from config import Config

logger = logging.getLogger(__name__)


def validate_returns(returns: pd.Series) -> pd.Series:
    """
    Validate and clean returns data.

    Args:
        returns: Time series of returns

    Returns:
        Cleaned returns series

    Raises:
        ValueError: If returns data is invalid
    """
    if not isinstance(returns, pd.Series):
        raise ValueError("Returns must be a pandas Series")

    if len(returns) < Config.MIN_DATA_POINTS:
        raise ValueError(f"Insufficient data points. Minimum: {Config.MIN_DATA_POINTS}")

    # Remove NaN values
    returns_clean = returns.dropna()

    if len(returns_clean) < Config.MIN_DATA_POINTS:
        raise ValueError(f"Too many NaN values. Valid points: {len(returns_clean)}")

    # Check for infinite values
    if np.any(np.isinf(returns_clean)):
        logger.warning("Infinite values detected, removing them")
        returns_clean = returns_clean[~np.isinf(returns_clean)]

    return returns_clean


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    Calculate annualized Sharpe ratio.

    Args:
        returns: Time series of returns
        risk_free_rate: Annual risk-free rate (default: 2%)

    Returns:
        Annualized Sharpe ratio
    """
    if returns.std() == 0:
        return 0.0

    excess_returns = returns - risk_free_rate / 252
    return np.sqrt(252) * excess_returns.mean() / excess_returns.std()


def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    Calculate annualized Sortino ratio.

    Args:
        returns: Time series of returns
        risk_free_rate: Annual risk-free rate (default: 2%)

    Returns:
        Annualized Sortino ratio
    """
    excess_returns = returns - risk_free_rate / 252
    downside_returns = excess_returns[excess_returns < 0]

    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return 0.0

    downside_deviation = np.sqrt((downside_returns ** 2).mean())
    return np.sqrt(252) * excess_returns.mean() / downside_deviation


def calculate_calmar_ratio(returns: pd.Series) -> float:
    """
    Calculate Calmar ratio (return / max drawdown).

    Args:
        returns: Time series of returns

    Returns:
        Calmar ratio
    """
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = abs(drawdown.min())

    if max_drawdown == 0:
        return 0.0

    annual_return = (1 + returns).prod() ** (252 / len(returns)) - 1
    return annual_return / max_drawdown


def calculate_max_drawdown(returns: pd.Series) -> float:
    """
    Calculate maximum drawdown.

    Args:
        returns: Time series of returns

    Returns:
        Maximum drawdown (positive number)
    """
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return abs(drawdown.min())


def calculate_metrics(returns: pd.Series) -> Dict[str, float]:
    """
    Calculate comprehensive performance metrics.

    Args:
        returns: Time series of returns

    Returns:
        Dictionary of performance metrics
    """
    return {
        'total_return': (1 + returns).prod() - 1,
        'annual_return': (1 + returns).prod() ** (252 / len(returns)) - 1,
        'volatility': returns.std() * np.sqrt(252),
        'sharpe_ratio': calculate_sharpe_ratio(returns),
        'sortino_ratio': calculate_sortino_ratio(returns),
        'calmar_ratio': calculate_calmar_ratio(returns),
        'max_drawdown': calculate_max_drawdown(returns),
        'win_rate': (returns > 0).sum() / len(returns),
        'avg_win': returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0,
        'avg_loss': returns[returns < 0].mean() if len(returns[returns < 0]) > 0 else 0,
        'skewness': returns.skew(),
        'kurtosis': returns.kurtosis()
    }


def generate_price_path(returns: np.ndarray, initial_price: float = 100.0) -> np.ndarray:
    """
    Convert returns to price path.

    Args:
        returns: Array of returns
        initial_price: Starting price (default: 100)

    Returns:
        Array of prices
    """
    prices = np.zeros(len(returns) + 1)
    prices[0] = initial_price

    for i in range(len(returns)):
        prices[i + 1] = prices[i] * (1 + returns[i])

    return prices


def price_to_returns(prices: np.ndarray) -> np.ndarray:
    """
    Convert prices to returns.

    Args:
        prices: Array of prices

    Returns:
        Array of returns
    """
    return np.diff(prices) / prices[:-1]


def ensure_positive_definite(matrix: np.ndarray, epsilon: float = 1e-8) -> np.ndarray:
    """
    Ensure matrix is positive definite (for covariance matrices).

    Args:
        matrix: Input matrix
        epsilon: Small value to add to diagonal

    Returns:
        Positive definite matrix
    """
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)

    # Ensure all eigenvalues are positive
    eigenvalues = np.maximum(eigenvalues, epsilon)

    # Reconstruct matrix
    return eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T


def bootstrap_confidence_interval(
    data: np.ndarray,
    statistic_func: Callable,
    alpha: float = 0.05,
    n_bootstrap: int = 1000
) -> Dict[str, float]:
    """
    Calculate bootstrap confidence interval for a statistic.

    Args:
        data: Input data
        statistic_func: Function to calculate statistic
        alpha: Significance level (default: 0.05 for 95% CI)
        n_bootstrap: Number of bootstrap samples

    Returns:
        Dictionary with point estimate and confidence interval
    """
    n = len(data)
    bootstrap_stats = np.zeros(n_bootstrap)

    for i in range(n_bootstrap):
        sample = np.random.choice(data, size=n, replace=True)
        bootstrap_stats[i] = statistic_func(sample)

    point_estimate = statistic_func(data)
    lower = np.percentile(bootstrap_stats, 100 * alpha / 2)
    upper = np.percentile(bootstrap_stats, 100 * (1 - alpha / 2))

    return {
        'point_estimate': point_estimate,
        'lower_bound': lower,
        'upper_bound': upper,
        'confidence_level': 1 - alpha
    }


def time_series_train_test_split(
    data: pd.DataFrame,
    train_size: Union[int, float]
) -> tuple:
    """
    Split time series data into train and test sets.

    Args:
        data: Time series DataFrame
        train_size: Size of training set (int for absolute, float for proportion)

    Returns:
        Tuple of (train_data, test_data)
    """
    if isinstance(train_size, float):
        train_size = int(len(data) * train_size)

    train_data = data.iloc[:train_size]
    test_data = data.iloc[train_size:]

    return train_data, test_data


def fetch_data(ticker: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    Fetch price data for a ticker.

    Args:
        ticker: Stock ticker symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        DataFrame with price data and returns
    """
    import yfinance as yf
    from datetime import datetime, timedelta

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')

    data = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if data.empty:
        raise ValueError(f"No data found for ticker: {ticker}")

    # Calculate returns
    data['returns'] = data['Adj Close'].pct_change()
    data = data.dropna()

    return data


def validate_simulation_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate simulation parameters.

    Args:
        params: Dictionary of parameters

    Returns:
        Validated parameters

    Raises:
        ValueError: If parameters are invalid
    """
    validated = params.copy()

    # Validate n_simulations
    if 'n_simulations' in validated:
        n_sim = validated['n_simulations']
        if n_sim <= 0:
            raise ValueError("n_simulations must be positive")
        if n_sim > Config.MAX_SIMULATIONS:
            raise ValueError(f"n_simulations cannot exceed {Config.MAX_SIMULATIONS}")

    # Validate block_size
    if 'block_size' in validated:
        block_size = validated['block_size']
        if block_size < Config.MIN_BLOCK_SIZE:
            raise ValueError(f"block_size must be >= {Config.MIN_BLOCK_SIZE}")
        if block_size > Config.MAX_BLOCK_SIZE:
            raise ValueError(f"block_size cannot exceed {Config.MAX_BLOCK_SIZE}")

    return validated
