# backtesting.py - Backtest with and without meta-labeling

import numpy as np
import pandas as pd
import logging
from utils import calculate_strategy_returns, calculate_performance_metrics
from meta_labeler import create_meta_labels, train_meta_model, apply_meta_sizing, predict_meta_probability
from feature_engineering import create_meta_features
from config import Config

logger = logging.getLogger(__name__)


def backtest_with_meta_labeling(prices: pd.DataFrame,
                                primary_strategy: callable,
                                meta_model,
                                meta_features: pd.DataFrame,
                                threshold: float = None) -> dict:
    """
    Compare backtest results with and without meta-labeling.

    Args:
        prices: OHLCV price data
        primary_strategy: Function that returns primary signals
        meta_model: Trained meta-model
        meta_features: Features for meta-model
        threshold: Confidence threshold for meta-sizing

    Returns:
        {
            'without_meta': {...},  # Performance metrics
            'with_meta': {...},     # Performance metrics with meta-sizing
            'improvement': {...}    # Improvements in each metric
        }
    """
    if threshold is None:
        threshold = Config.DEFAULT_CONFIDENCE_THRESHOLD

    logger.info(f"Backtesting with meta-labeling, threshold={threshold}")

    # Generate primary signals
    primary_signals = primary_strategy(prices['close'])

    # Calculate returns
    market_returns = prices['close'].pct_change().dropna()

    # WITHOUT meta-labeling
    returns_no_meta = calculate_strategy_returns(market_returns, primary_signals)
    metrics_no_meta = calculate_performance_metrics(returns_no_meta)

    logger.info(f"Without meta - Sharpe: {metrics_no_meta['sharpe_ratio']:.3f}, "
                f"Return: {metrics_no_meta['annual_return']:.2%}")

    # WITH meta-labeling
    meta_proba = predict_meta_probability(meta_model, meta_features)
    sized_signals = apply_meta_sizing(primary_signals, meta_proba, threshold=threshold)
    returns_with_meta = calculate_strategy_returns(market_returns, sized_signals)
    metrics_with_meta = calculate_performance_metrics(returns_with_meta)

    logger.info(f"With meta - Sharpe: {metrics_with_meta['sharpe_ratio']:.3f}, "
                f"Return: {metrics_with_meta['annual_return']:.2%}")

    # Calculate improvement
    improvement = {
        'sharpe_improvement': metrics_with_meta['sharpe_ratio'] - metrics_no_meta['sharpe_ratio'],
        'return_improvement': metrics_with_meta['annual_return'] - metrics_no_meta['annual_return'],
        'max_dd_improvement': metrics_no_meta['max_drawdown'] - metrics_with_meta['max_drawdown'],
        'win_rate_improvement': metrics_with_meta['win_rate'] - metrics_no_meta['win_rate'],
        'profit_factor_improvement': metrics_with_meta['profit_factor'] - metrics_no_meta['profit_factor']
    }

    return {
        'without_meta': metrics_no_meta,
        'with_meta': metrics_with_meta,
        'improvement': improvement,
        'returns_no_meta': returns_no_meta,
        'returns_with_meta': returns_with_meta,
        'primary_signals': primary_signals,
        'sized_signals': sized_signals
    }


def walk_forward_backtest(prices: pd.DataFrame,
                         primary_strategy: callable,
                         train_window: int = 252,
                         test_window: int = 63,
                         model_type: str = 'random_forest') -> dict:
    """
    Walk-forward backtesting with meta-labeling.

    Args:
        prices: OHLCV price data
        primary_strategy: Function that returns primary signals
        train_window: Training window size (days)
        test_window: Test window size (days)
        model_type: Type of meta-model

    Returns:
        Aggregated results from all test periods
    """
    logger.info(f"Walk-forward backtest: train={train_window}, test={test_window}")

    all_results = []
    n_windows = (len(prices) - train_window) // test_window

    for i in range(n_windows):
        start_idx = i * test_window
        train_end_idx = start_idx + train_window
        test_end_idx = train_end_idx + test_window

        if test_end_idx > len(prices):
            break

        # Split data
        train_prices = prices.iloc[start_idx:train_end_idx]
        test_prices = prices.iloc[train_end_idx:test_end_idx]

        try:
            # Train on training period
            train_signals = primary_strategy(train_prices['close'])
            train_returns = train_prices['close'].pct_change()
            train_meta_labels = create_meta_labels(train_signals, train_returns)
            train_features = create_meta_features(train_prices, train_signals)

            # Train meta-model
            training_result = train_meta_model(
                train_features,
                train_meta_labels['meta_label'],
                model_type=model_type
            )

            # Test on test period
            test_signals = primary_strategy(test_prices['close'])
            test_features = create_meta_features(test_prices, test_signals)

            # Backtest
            backtest_result = backtest_with_meta_labeling(
                test_prices,
                primary_strategy,
                training_result['model'],
                test_features
            )

            all_results.append({
                'period': i + 1,
                'without_meta': backtest_result['without_meta'],
                'with_meta': backtest_result['with_meta'],
                'improvement': backtest_result['improvement']
            })

            logger.info(f"Period {i+1}/{n_windows}: Sharpe improvement = "
                       f"{backtest_result['improvement']['sharpe_improvement']:.3f}")

        except Exception as e:
            logger.error(f"Error in period {i+1}: {str(e)}")
            continue

    # Aggregate results
    if not all_results:
        raise ValueError("No successful walk-forward periods")

    # Average metrics
    avg_without_meta = {
        key: np.mean([r['without_meta'][key] for r in all_results])
        for key in all_results[0]['without_meta'].keys()
    }

    avg_with_meta = {
        key: np.mean([r['with_meta'][key] for r in all_results])
        for key in all_results[0]['with_meta'].keys()
    }

    avg_improvement = {
        key: np.mean([r['improvement'][key] for r in all_results])
        for key in all_results[0]['improvement'].keys()
    }

    logger.info(f"Walk-forward complete: {len(all_results)} periods")
    logger.info(f"Average Sharpe improvement: {avg_improvement['sharpe_improvement']:.3f}")

    return {
        'all_periods': all_results,
        'avg_without_meta': avg_without_meta,
        'avg_with_meta': avg_with_meta,
        'avg_improvement': avg_improvement,
        'n_periods': len(all_results)
    }


def compare_thresholds(prices: pd.DataFrame,
                      primary_strategy: callable,
                      meta_model,
                      meta_features: pd.DataFrame,
                      thresholds: list = None) -> pd.DataFrame:
    """
    Compare performance at different confidence thresholds.

    Args:
        prices: OHLCV price data
        primary_strategy: Function that returns primary signals
        meta_model: Trained meta-model
        meta_features: Features for meta-model
        thresholds: List of thresholds to test

    Returns:
        DataFrame with performance at each threshold
    """
    if thresholds is None:
        thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]

    logger.info(f"Comparing {len(thresholds)} thresholds")

    results = []

    for threshold in thresholds:
        backtest_result = backtest_with_meta_labeling(
            prices,
            primary_strategy,
            meta_model,
            meta_features,
            threshold=threshold
        )

        results.append({
            'threshold': threshold,
            **backtest_result['with_meta'],
            'sharpe_improvement': backtest_result['improvement']['sharpe_improvement']
        })

    df = pd.DataFrame(results)

    logger.info(f"Best threshold: {df.loc[df['sharpe_ratio'].idxmax(), 'threshold']:.2f}")

    return df


def calculate_cumulative_returns(returns: pd.Series) -> pd.Series:
    """
    Calculate cumulative returns.

    Args:
        returns: Returns series

    Returns:
        Cumulative returns series
    """
    return (1 + returns).cumprod()


def plot_comparison(returns_no_meta: pd.Series,
                   returns_with_meta: pd.Series) -> dict:
    """
    Prepare data for plotting comparison.

    Args:
        returns_no_meta: Returns without meta-labeling
        returns_with_meta: Returns with meta-labeling

    Returns:
        Dictionary with plot data
    """
    # Calculate cumulative returns
    cum_no_meta = calculate_cumulative_returns(returns_no_meta)
    cum_with_meta = calculate_cumulative_returns(returns_with_meta)

    # Align
    common_idx = cum_no_meta.index.intersection(cum_with_meta.index)

    return {
        'dates': common_idx.astype(str).tolist(),
        'cumulative_no_meta': cum_no_meta.loc[common_idx].tolist(),
        'cumulative_with_meta': cum_with_meta.loc[common_idx].tolist(),
        'daily_no_meta': returns_no_meta.loc[common_idx].tolist(),
        'daily_with_meta': returns_with_meta.loc[common_idx].tolist()
    }
