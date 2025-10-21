"""
Default ML Alpha Strategy.

Trading strategy that uses XGBoost predictions from Feast features.
"""
import requests
from typing import Dict, Optional
from feast import FeatureStore
import pandas as pd
from pathlib import Path


class DefaultMLStrategy:
    """
    ML-based trading strategy using XGBoost predictions.

    Integrates:
    - Feast for online feature retrieval
    - Model serving endpoint for predictions
    - Signal generation with confidence thresholds
    """

    def __init__(
        self,
        model_endpoint: str = "http://localhost:3000",
        feast_repo_path: Optional[str] = None,
        position_size: float = 0.02,
        long_threshold: float = 0.6,
        short_threshold: float = 0.4
    ):
        """
        Initialize strategy.

        Args:
            model_endpoint: URL of model serving endpoint
            feast_repo_path: Path to Feast feature repository
            position_size: Position size as fraction (default 2%)
            long_threshold: Probability threshold for long signal (default 0.6)
            short_threshold: Probability threshold for short signal (default 0.4)
        """
        self.model_endpoint = model_endpoint
        self.position_size = position_size
        self.long_threshold = long_threshold
        self.short_threshold = short_threshold

        # Initialize Feast store
        if feast_repo_path is None:
            feast_repo_path = str(Path(__file__).parent.parent.parent.parent.parent / "feast" / "feature_repo")

        self.feature_store = FeatureStore(repo_path=feast_repo_path)

    def get_features(self, symbol: str) -> Dict[str, float]:
        """
        Get online features from Feast for given symbol.

        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")

        Returns:
            Dictionary of feature values
        """
        features = self.feature_store.get_online_features(
            features=[
                "technical_indicators:rsi",
                "technical_indicators:macd",
                "technical_indicators:macd_signal",
                "technical_indicators:macd_histogram",
                "technical_indicators:bb_upper",
                "technical_indicators:bb_middle",
                "technical_indicators:bb_lower",
                "technical_indicators:bb_bandwidth",
                "technical_indicators:bb_percent_b",
            ],
            entity_rows=[{"symbol": symbol}]
        ).to_dict()

        # Extract first row (single symbol)
        feature_dict = {
            "rsi": features["rsi"][0],
            "macd": features["macd"][0],
            "macd_signal": features["macd_signal"][0],
            "macd_histogram": features["macd_histogram"][0],
            "bb_upper": features["bb_upper"][0],
            "bb_middle": features["bb_middle"][0],
            "bb_lower": features["bb_lower"][0],
            "bb_bandwidth": features["bb_bandwidth"][0],
            "bb_percent_b": features["bb_percent_b"][0],
        }

        return feature_dict

    def get_prediction(self, features: Dict[str, float]) -> float:
        """
        Get model prediction from serving endpoint.

        Args:
            features: Dictionary of feature values

        Returns:
            Prediction probability (0-1)
        """
        # Convert features dict to list in correct order
        feature_vector = [
            features["rsi"],
            features["macd"],
            features["macd_signal"],
            features["macd_histogram"],
            features["bb_upper"],
            features["bb_middle"],
            features["bb_lower"],
            features["bb_bandwidth"],
            features["bb_percent_b"],
        ]

        # Call prediction endpoint
        response = requests.post(
            f"{self.model_endpoint}/predict",
            json={"features": [feature_vector]},
            timeout=5
        )

        response.raise_for_status()
        result = response.json()

        return result["predictions"][0]

    def generate_signal(self, symbol: str) -> Dict:
        """
        Generate trading signal for symbol.

        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")

        Returns:
            Signal dictionary with action, size, confidence, and features
        """
        # Get features from Feast
        features = self.get_features(symbol)

        # Get prediction from model
        prob = self.get_prediction(features)

        # Generate signal based on thresholds
        if prob > self.long_threshold:
            signal = {
                "symbol": symbol,
                "action": "BUY",
                "size": self.position_size,
                "confidence": prob,
                "features": features,
                "strategy": "default_ml_strategy",
                "version": "1.0.0"
            }
        elif prob < self.short_threshold:
            signal = {
                "symbol": symbol,
                "action": "SELL",
                "size": self.position_size,
                "confidence": 1 - prob,
                "features": features,
                "strategy": "default_ml_strategy",
                "version": "1.0.0"
            }
        else:
            signal = {
                "symbol": symbol,
                "action": "HOLD",
                "confidence": abs(prob - 0.5) / 0.5,  # Confidence in hold
                "features": features,
                "strategy": "default_ml_strategy",
                "version": "1.0.0"
            }

        return signal


def main():
    """Example usage of strategy."""
    print("=" * 70)
    print("DEFAULT ML STRATEGY - EXAMPLE")
    print("=" * 70)

    # Initialize strategy
    strategy = DefaultMLStrategy()

    # Generate signals for test symbols
    symbols = ["BTCUSDT", "ETHUSDT"]

    for symbol in symbols:
        print(f"\n[{symbol}]")
        try:
            signal = strategy.generate_signal(symbol)
            print(f"  Action: {signal['action']}")
            print(f"  Confidence: {signal['confidence']:.4f}")
            if signal['action'] != 'HOLD':
                print(f"  Size: {signal['size']:.2%}")
            print(f"  Features: RSI={signal['features']['rsi']:.2f}, "
                  f"MACD={signal['features']['macd']:.4f}")
        except Exception as e:
            print(f"  Error: {e}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
