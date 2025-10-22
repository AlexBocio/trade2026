# multi_horizon_predictor.py - Multi-Timeframe Prediction Engine
# Predict forward returns across multiple timeframes (1hr to 6 months)

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
import yfinance as yf
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MultiHorizonPredictor:
    """
    Predict forward returns across multiple timeframes for both long and short.

    Timeframes:
    - Intraday: 1hr, 4hr
    - Short-term: 1d, 2d, 3d, 4d, 5d
    - Medium-term: 1wk, 2wk, 3wk, 4wk, 5wk
    - Long-term: 1mo, 2mo, 3mo, 4mo, 5mo, 6mo
    """

    TIMEFRAMES = {
        'intraday': ['1h', '4h'],
        'short': ['1d', '2d', '3d', '4d', '5d'],
        'medium': ['1w', '2w', '3w', '4w', '5w'],
        'long': ['1mo', '2mo', '3mo', '4mo', '5mo', '6mo']
    }

    HORIZON_PERIODS = {
        # Intraday (in hours)
        '1h': 1 / 6.5,      # 1 hour / 6.5 trading hours per day
        '4h': 4 / 6.5,

        # Days
        '1d': 1,
        '2d': 2,
        '3d': 3,
        '4d': 4,
        '5d': 5,

        # Weeks (in days)
        '1w': 5,
        '2w': 10,
        '3w': 15,
        '4w': 20,
        '5w': 25,

        # Months (in days, trading days)
        '1mo': 21,
        '2mo': 42,
        '3mo': 63,
        '4mo': 84,
        '5mo': 105,
        '6mo': 126
    }

    def __init__(self):
        self.models = {}  # Store trained models per horizon
        self.feature_importance = {}
        self._price_cache = {}  # Cache current prices

    def predict_all_horizons(self,
                            ticker: str,
                            current_features: Dict[str, float]) -> Dict[str, Dict]:
        """
        Predict forward returns for all timeframes.

        Args:
            ticker: Stock symbol
            current_features: Current factor values for the stock

        Returns:
            {
                '1h': {
                    'predicted_return': 0.015,  # +1.5%
                    'confidence': 0.75,
                    'direction': 'long',
                    'strength': 'moderate'
                },
                '1d': {
                    'predicted_return': -0.025,  # -2.5%
                    'confidence': 0.85,
                    'direction': 'short',
                    'strength': 'strong'
                },
                ...
            }
        """
        logger.info(f"Predicting all horizons for {ticker}")

        predictions = {}

        # Fetch historical data
        hist_data = self._fetch_data(ticker, period='1y')

        if hist_data is None or hist_data.empty:
            logger.warning(f"No data for {ticker}, returning empty predictions")
            return self._empty_predictions()

        # Predict for each horizon
        for category, horizons in self.TIMEFRAMES.items():
            for horizon in horizons:
                pred = self._predict_single_horizon(
                    hist_data,
                    current_features,
                    horizon
                )
                predictions[horizon] = pred

        logger.info(f"Generated {len(predictions)} predictions for {ticker}")

        return predictions

    def _predict_single_horizon(self,
                                hist_data: pd.DataFrame,
                                current_features: Dict[str, float],
                                horizon: str) -> Dict:
        """
        Predict return for a single time horizon.

        Uses ensemble of methods:
        1. Linear regression on factors
        2. Random Forest
        3. Gradient Boosting
        4. Historical analogs (similar past patterns)
        """
        # Get forward returns for this horizon from historical data
        periods = int(self.HORIZON_PERIODS[horizon])

        if periods < 1:  # Intraday
            # For intraday, use simplified daily prediction
            forward_returns = hist_data['Close'].pct_change(1).shift(-1)
        else:
            forward_returns = hist_data['Close'].pct_change(periods).shift(-periods)

        # Create feature matrix from historical data
        X_hist = self._create_features(hist_data)
        y_hist = forward_returns

        # Remove NaN
        valid_mask = ~(X_hist.isna().any(axis=1) | y_hist.isna())
        X_train = X_hist[valid_mask]
        y_train = y_hist[valid_mask]

        if len(X_train) < 50:
            return {
                'predicted_return': 0.0,
                'confidence': 0.0,
                'direction': 'neutral',
                'strength': 'none',
                'ensemble_std': 0.0
            }

        # Train ensemble models
        models = [
            ('rf', RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)),
            ('gb', GradientBoostingRegressor(n_estimators=50, max_depth=3, random_state=42)),
            ('ridge', Ridge(alpha=1.0))
        ]

        predictions_ensemble = []

        for name, model in models:
            try:
                model.fit(X_train, y_train)

                # Predict for current features
                current_X = pd.DataFrame([current_features])
                # Align columns
                for col in X_train.columns:
                    if col not in current_X.columns:
                        current_X[col] = 0
                current_X = current_X[X_train.columns]

                pred = model.predict(current_X)[0]
                predictions_ensemble.append(pred)
            except Exception as e:
                logger.warning(f"Model {name} failed for {horizon}: {e}")
                continue

        if len(predictions_ensemble) == 0:
            return {
                'predicted_return': 0.0,
                'confidence': 0.0,
                'direction': 'neutral',
                'strength': 'none',
                'ensemble_std': 0.0
            }

        # Ensemble prediction (average)
        predicted_return = np.mean(predictions_ensemble)
        prediction_std = np.std(predictions_ensemble) if len(predictions_ensemble) > 1 else 0.1

        # Calculate confidence (inverse of std, normalized)
        confidence = 1.0 / (1.0 + prediction_std * 10)
        confidence = min(max(confidence, 0.0), 1.0)

        # Determine direction and strength
        abs_return = abs(predicted_return)

        if abs_return < 0.005:  # < 0.5%
            direction = 'neutral'
            strength = 'none'
        else:
            direction = 'long' if predicted_return > 0 else 'short'

            if abs_return < 0.02:  # 0.5-2%
                strength = 'weak'
            elif abs_return < 0.05:  # 2-5%
                strength = 'moderate'
            else:  # > 5%
                strength = 'strong'

        return {
            'predicted_return': float(predicted_return),
            'confidence': float(confidence),
            'direction': direction,
            'strength': strength,
            'ensemble_std': float(prediction_std)
        }

    def _create_features(self, hist_data: pd.DataFrame) -> pd.DataFrame:
        """
        Create feature matrix from price/volume data.

        Features:
        - Momentum (multiple lookbacks)
        - RSI
        - Volume ratios
        - Volatility
        - Price vs moving averages
        """
        features = pd.DataFrame(index=hist_data.index)

        close = hist_data['Close']
        volume = hist_data['Volume']

        # Momentum features
        features['momentum_5'] = close.pct_change(5)
        features['momentum_10'] = close.pct_change(10)
        features['momentum_20'] = close.pct_change(20)
        features['momentum_60'] = close.pct_change(60)

        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        features['rsi'] = 100 - (100 / (1 + rs))

        # Volume
        features['volume_ratio'] = volume / volume.rolling(20).mean()

        # Volatility
        features['volatility'] = close.pct_change().rolling(20).std()

        # Moving averages
        features['price_vs_sma20'] = (close / close.rolling(20).mean()) - 1
        features['price_vs_sma50'] = (close / close.rolling(50).mean()) - 1

        # Fill NaN with 0
        features = features.fillna(0)

        return features

    def _fetch_data(self, ticker: str, period: str = '1y') -> pd.DataFrame:
        """Fetch historical data."""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)

            # Cache current price
            if len(hist) > 0:
                self._price_cache[ticker] = float(hist['Close'].iloc[-1])

            return hist
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return None

    def get_cached_price(self, ticker: str) -> float:
        """Get cached current price."""
        return self._price_cache.get(ticker, 100.0)

    def _empty_predictions(self) -> Dict:
        """Return empty predictions if data unavailable."""
        empty = {}
        for category, horizons in self.TIMEFRAMES.items():
            for horizon in horizons:
                empty[horizon] = {
                    'predicted_return': 0.0,
                    'confidence': 0.0,
                    'direction': 'neutral',
                    'strength': 'none',
                    'ensemble_std': 0.0
                }
        return empty

    def batch_predict(self,
                     tickers: List[str],
                     features_by_ticker: Dict[str, Dict[str, float]]) -> Dict[str, Dict]:
        """
        Predict for multiple tickers in batch.

        Args:
            tickers: List of ticker symbols
            features_by_ticker: Dict mapping ticker -> current features

        Returns:
            Dict mapping ticker -> predictions
        """
        logger.info(f"Batch predicting for {len(tickers)} tickers")

        predictions_by_ticker = {}

        for ticker in tickers:
            features = features_by_ticker.get(ticker, {})
            predictions = self.predict_all_horizons(ticker, features)
            predictions_by_ticker[ticker] = predictions

        return predictions_by_ticker
