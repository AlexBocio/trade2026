# meta_labeling.py - Meta-labeling for strategy filtering

import numpy as np
import pandas as pd
from typing import Callable
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

class MetaLabeler:
    """
    Meta-Labeling - Use ML to decide WHEN to trade, not what direction.

    Primary model predicts direction (side).
    Meta-model predicts whether primary model's signal is worth taking.

    This improves Sharpe ratio by filtering out low-conviction trades.
    """

    def __init__(self, primary_model_func: Callable):
        """
        Args:
            primary_model_func: Function that generates primary signals
        """
        self.primary_model_func = primary_model_func
        self.meta_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )

    def create_meta_labels(self, data: pd.DataFrame, returns: pd.Series,
                          holding_period: int = 5):
        """
        Create meta-labels: 1 if trade would be profitable, 0 otherwise.

        Args:
            data: Price data
            returns: Future returns
            holding_period: How many periods to hold position

        Returns:
            Binary labels (1 = profitable, 0 = unprofitable)
        """
        # Get primary model signals
        primary_signals = self.primary_model_func(data)

        # Calculate forward returns for holding period
        forward_returns = returns.shift(-holding_period).fillna(0)

        # Meta-label: 1 if (signal direction * forward return) > 0
        meta_labels = ((primary_signals * forward_returns) > 0).astype(int)

        return meta_labels

    def create_features(self, data: pd.DataFrame):
        """
        Create features for meta-model.

        Features should capture:
        - Market regime (volatility, trend strength)
        - Signal quality (strength, consistency)
        - Risk factors (correlation, liquidity)
        """
        features = pd.DataFrame(index=data.index)

        # Volatility features
        features['volatility_5d'] = data['returns'].rolling(5).std()
        features['volatility_20d'] = data['returns'].rolling(20).std()
        features['volatility_ratio'] = features['volatility_5d'] / features['volatility_20d']

        # Trend strength
        features['sma_10'] = data['Close'].rolling(10).mean()
        features['sma_50'] = data['Close'].rolling(50).mean()
        features['trend_strength'] = (features['sma_10'] - features['sma_50']) / features['sma_50']

        # Momentum
        features['rsi'] = self._calculate_rsi(data['Close'], period=14)
        features['macd'] = self._calculate_macd(data['Close'])

        # Volume (if available)
        if 'Volume' in data.columns:
            features['volume_ratio'] = data['Volume'] / data['Volume'].rolling(20).mean()

        # Autocorrelation (signal persistence)
        features['autocorr_5'] = data['returns'].rolling(20).apply(
            lambda x: x.autocorr(lag=5), raw=False
        )

        return features.dropna()

    def train(self, data: pd.DataFrame, holding_period: int = 5):
        """Train meta-model."""
        # Create labels
        meta_labels = self.create_meta_labels(
            data,
            data['returns'],
            holding_period
        )

        # Create features
        features = self.create_features(data)

        # Align labels and features
        common_idx = features.index.intersection(meta_labels.index)
        X = features.loc[common_idx]
        y = meta_labels.loc[common_idx]

        # Train
        self.meta_model.fit(X, y)

        # Cross-validation score
        cv_score = cross_val_score(
            self.meta_model, X, y,
            cv=5, scoring='accuracy'
        ).mean()

        return {
            'cv_accuracy': cv_score,
            'feature_importance': dict(zip(
                X.columns,
                self.meta_model.feature_importances_
            ))
        }

    def predict(self, data: pd.DataFrame):
        """
        Predict whether to take primary model's signals.

        Returns:
            1 = Take signal, 0 = Skip signal
        """
        features = self.create_features(data)
        predictions = self.meta_model.predict(features)

        return pd.Series(predictions, index=features.index)

    def backtest_with_meta_labeling(self, data: pd.DataFrame):
        """
        Backtest strategy with meta-labeling filter.

        Compare:
        1. Primary model alone
        2. Primary model + meta-labeling filter
        """
        # Primary signals
        primary_signals = self.primary_model_func(data)

        # Meta predictions
        meta_predictions = self.predict(data)

        # Filtered signals: only take trades where meta-model agrees
        filtered_signals = primary_signals.copy()
        filtered_signals[meta_predictions == 0] = 0

        # Calculate returns
        primary_returns = data['returns'] * primary_signals.shift(1)
        filtered_returns = data['returns'] * filtered_signals.shift(1)

        primary_returns = primary_returns.dropna()
        filtered_returns = filtered_returns.dropna()

        # Metrics
        def calc_metrics(returns):
            return {
                'total_return': (1 + returns).prod() - 1,
                'sharpe': np.sqrt(252) * returns.mean() / returns.std() if returns.std() > 0 else 0,
                'max_drawdown': (returns.cumsum() - returns.cumsum().cummax()).min(),
                'win_rate': (returns > 0).sum() / len(returns)
            }

        return {
            'primary_only': calc_metrics(primary_returns),
            'with_meta_labeling': calc_metrics(filtered_returns),
            'num_trades_primary': (primary_signals != 0).sum(),
            'num_trades_filtered': (filtered_signals != 0).sum(),
            'trade_reduction_pct': 1 - (filtered_signals != 0).sum() / (primary_signals != 0).sum()
        }

    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _calculate_macd(self, prices, fast=12, slow=26):
        """Calculate MACD indicator."""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow

        return macd
