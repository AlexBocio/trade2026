# feature_engineering.py - Feature engineering for meta-model

import numpy as np
import pandas as pd
import logging
from primary_models import calculate_rsi
from config import Config

logger = logging.getLogger(__name__)


def create_meta_features(prices: pd.DataFrame,
                        primary_signals: pd.Series,
                        lookback: int = None) -> pd.DataFrame:
    """
    Create features for meta-model.

    Meta-features help predict when primary signals will work:
    - Market regime (volatility, trend strength)
    - Signal quality (consecutive signals, strength)
    - Context (recent performance)

    Args:
        prices: OHLCV dataframe with columns: open, high, low, close, volume
        primary_signals: Primary model signals
        lookback: Lookback window for features

    Returns:
        DataFrame with meta-features
    """
    if lookback is None:
        lookback = Config.FEATURE_LOOKBACK

    logger.info(f"Creating meta-features with lookback={lookback}")

    df = prices.copy()

    # Ensure we have close prices
    if 'close' not in df.columns:
        raise ValueError("prices DataFrame must have 'close' column")

    close = df['close']

    # === VOLATILITY FEATURES ===
    returns = close.pct_change()
    df['volatility_20'] = returns.rolling(20).std()
    df['volatility_5'] = returns.rolling(5).std()
    df['volatility_ratio'] = df['volatility_5'] / (df['volatility_20'] + 1e-10)

    # === TREND FEATURES ===
    df['sma_20'] = close.rolling(20).mean()
    df['sma_50'] = close.rolling(50).mean()
    df['trend_strength'] = (close - df['sma_50']) / (df['sma_50'] + 1e-10)
    df['above_sma'] = (close > df['sma_20']).astype(int)

    # === MOMENTUM FEATURES ===
    df['rsi'] = calculate_rsi(close, 14)
    df['momentum_5'] = close.pct_change(5)
    df['momentum_20'] = close.pct_change(20)

    # === VOLUME FEATURES (if available) ===
    if 'volume' in df.columns:
        df['volume_sma'] = df['volume'].rolling(20).mean()
        df['volume_ratio'] = df['volume'] / (df['volume_sma'] + 1e-10)
    else:
        df['volume_ratio'] = 1.0

    # === SIGNAL FEATURES ===
    # Align primary signals with price data
    df['primary_signal'] = primary_signals.reindex(df.index, fill_value=0)

    # Count consecutive signals
    signal_changes = (df['primary_signal'] != df['primary_signal'].shift()).cumsum()
    df['signal_consecutive'] = df.groupby(signal_changes).cumcount() + 1

    df['signal_strength'] = df['primary_signal'].abs()

    # === RECENT PERFORMANCE ===
    df['recent_return'] = close.pct_change(5)
    df['win_rate_20'] = returns.rolling(20).apply(
        lambda x: (x > 0).sum() / len(x) if len(x) > 0 else 0
    )

    # === PRICE PATTERNS ===
    # Distance from highs/lows
    df['dist_from_high_20'] = (close - close.rolling(20).max()) / (close.rolling(20).max() + 1e-10)
    df['dist_from_low_20'] = (close - close.rolling(20).min()) / (close.rolling(20).min() + 1e-10)

    # === MARKET REGIME (VIX proxy) ===
    df['returns_squared'] = returns ** 2
    df['realized_vol'] = df['returns_squared'].rolling(20).mean().apply(np.sqrt) * np.sqrt(252)

    # Drop NaN rows
    feature_cols = [
        'volatility_20', 'volatility_ratio', 'trend_strength',
        'above_sma', 'rsi', 'momentum_5', 'momentum_20',
        'volume_ratio', 'signal_consecutive', 'signal_strength',
        'win_rate_20', 'dist_from_high_20', 'dist_from_low_20',
        'realized_vol'
    ]

    features_df = df[feature_cols].copy()

    # Remove any remaining NaN or inf
    features_df = features_df.replace([np.inf, -np.inf], np.nan)
    features_df = features_df.dropna()

    logger.info(f"Created {len(feature_cols)} features, {len(features_df)} valid rows")

    return features_df


def select_features(features: pd.DataFrame,
                   target: pd.Series,
                   n_features: int = 10) -> list:
    """
    Select top N features using feature importance.

    Args:
        features: Feature dataframe
        target: Target labels
        n_features: Number of features to select

    Returns:
        List of selected feature names
    """
    from sklearn.ensemble import RandomForestClassifier

    # Align features and target
    common_idx = features.index.intersection(target.index)
    X = features.loc[common_idx]
    y = target.loc[common_idx]

    # Train quick RF to get feature importance
    rf = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
    rf.fit(X, y)

    # Get feature importances
    importances = pd.DataFrame({
        'feature': X.columns,
        'importance': rf.feature_importances_
    }).sort_values('importance', ascending=False)

    selected = importances.head(n_features)['feature'].tolist()

    logger.info(f"Selected top {n_features} features: {selected}")

    return selected


def create_lagged_features(features: pd.DataFrame,
                           lags: list = [1, 2, 3]) -> pd.DataFrame:
    """
    Create lagged versions of features.

    Args:
        features: Feature dataframe
        lags: List of lag periods

    Returns:
        DataFrame with original and lagged features
    """
    logger.info(f"Creating lagged features: {lags}")

    lagged_dfs = [features]

    for lag in lags:
        lagged = features.shift(lag)
        lagged.columns = [f"{col}_lag{lag}" for col in features.columns]
        lagged_dfs.append(lagged)

    combined = pd.concat(lagged_dfs, axis=1)
    combined = combined.dropna()

    logger.info(f"Created {len(combined.columns)} features (including lags)")

    return combined


def normalize_features(features: pd.DataFrame,
                      method: str = 'zscore') -> pd.DataFrame:
    """
    Normalize features.

    Args:
        features: Feature dataframe
        method: 'zscore' or 'minmax'

    Returns:
        Normalized features
    """
    if method == 'zscore':
        normalized = (features - features.mean()) / (features.std() + 1e-10)
    elif method == 'minmax':
        normalized = (features - features.min()) / (features.max() - features.min() + 1e-10)
    else:
        raise ValueError(f"Unknown normalization method: {method}")

    return normalized
