"""
XGBoost Training Pipeline for Trading Strategy.

Trains classification model to predict next-period price direction.
"""
import xgboost as xgb
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Optional MLflow integration
try:
    import mlflow
    import mlflow.xgboost
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    print("[WARNING] MLflow not available - metrics will not be logged")

# Optional ClickHouse integration
try:
    from clickhouse_driver import Client as ClickHouseClient
    CLICKHOUSE_AVAILABLE = True
except ImportError:
    CLICKHOUSE_AVAILABLE = False
    print("[WARNING] ClickHouse driver not available - cannot load from database")


class XGBoostTrainer:
    """
    XGBoost training pipeline for trading strategy.

    Trains a binary classification model to predict whether next-period
    price will be higher (1) or lower (0) than current price.
    """

    def __init__(
        self,
        mlflow_tracking_uri: Optional[str] = None,
        experiment_name: str = "default_ml_strategy",
        clickhouse_host: str = "localhost",
        clickhouse_port: int = 8123
    ):
        """
        Initialize XGBoost trainer.

        Args:
            mlflow_tracking_uri: MLflow tracking server URL (None = local)
            experiment_name: MLflow experiment name
            clickhouse_host: ClickHouse host
            clickhouse_port: ClickHouse HTTP port
        """
        self.model = None
        self.feature_columns = None
        self.mlflow_enabled = MLFLOW_AVAILABLE and mlflow_tracking_uri is not None

        if self.mlflow_enabled:
            # Convert Windows paths to proper file:// URI
            if mlflow_tracking_uri and not mlflow_tracking_uri.startswith(('http://', 'https://', 'file://')):
                from pathlib import Path
                import os
                # Convert to absolute path and format as URI
                abs_path = os.path.abspath(mlflow_tracking_uri)
                # Convert backslashes to forward slashes for URI
                abs_path = abs_path.replace('\\', '/')
                mlflow_tracking_uri = f"file:///{abs_path}"

            mlflow.set_tracking_uri(mlflow_tracking_uri)
            mlflow.set_experiment(experiment_name)
            print(f"[INFO] MLflow tracking enabled: {mlflow_tracking_uri}")
        else:
            print("[INFO] MLflow tracking disabled")

        self.clickhouse_host = clickhouse_host
        self.clickhouse_port = clickhouse_port

    def load_features_from_clickhouse(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Load features from ClickHouse.

        Args:
            symbol: Trading symbol (e.g. 'BTCUSDT')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame with features

        Raises:
            RuntimeError: If ClickHouse not available
        """
        if not CLICKHOUSE_AVAILABLE:
            raise RuntimeError("ClickHouse driver not installed")

        client = ClickHouseClient(
            host=self.clickhouse_host,
            port=self.clickhouse_port
        )

        query = f"""
        SELECT
            timestamp,
            symbol,
            close,
            rsi,
            macd,
            macd_signal,
            macd_histogram,
            bb_upper,
            bb_middle,
            bb_lower,
            bb_bandwidth,
            bb_percent_b
        FROM features
        WHERE symbol = '{symbol}'
          AND timestamp >= '{start_date}'
          AND timestamp <= '{end_date}'
        ORDER BY timestamp ASC
        """

        df = pd.DataFrame(
            client.execute(query),
            columns=['timestamp', 'symbol', 'close', 'rsi', 'macd', 'macd_signal',
                    'macd_histogram', 'bb_upper', 'bb_middle', 'bb_lower',
                    'bb_bandwidth', 'bb_percent_b']
        )

        print(f"[INFO] Loaded {len(df)} rows from ClickHouse for {symbol}")
        return df

    def generate_synthetic_data(
        self,
        n_samples: int = 1000,
        trend: str = 'mixed'
    ) -> pd.DataFrame:
        """
        Generate synthetic market data with features for testing.

        Args:
            n_samples: Number of samples to generate
            trend: 'up', 'down', 'sideways', or 'mixed'

        Returns:
            DataFrame with synthetic features
        """
        print(f"[INFO] Generating {n_samples} synthetic samples (trend={trend})")

        np.random.seed(42)

        # Generate base price series
        if trend == 'up':
            drift = 0.001
            volatility = 0.01
        elif trend == 'down':
            drift = -0.001
            volatility = 0.01
        elif trend == 'sideways':
            drift = 0.0
            volatility = 0.005
        else:  # mixed
            drift = 0.0
            volatility = 0.015

        returns = np.random.normal(drift, volatility, n_samples)
        prices = 100 * np.exp(np.cumsum(returns))

        # Generate features with realistic correlations
        rsi = 50 + 30 * np.sin(np.linspace(0, 20*np.pi, n_samples)) + \
              np.random.normal(0, 5, n_samples)
        rsi = np.clip(rsi, 0, 100)

        macd = np.random.normal(0, 0.5, n_samples) + \
               0.3 * (prices - np.roll(prices, 10)) / prices
        macd_signal = np.convolve(macd, np.ones(9)/9, mode='same')
        macd_histogram = macd - macd_signal

        bb_middle = np.convolve(prices, np.ones(20)/20, mode='same')
        bb_std = np.array([np.std(prices[max(0, i-20):i+1]) for i in range(n_samples)])
        bb_upper = bb_middle + 2 * bb_std
        bb_lower = bb_middle - 2 * bb_std
        bb_bandwidth = (bb_upper - bb_lower) / bb_middle
        bb_percent_b = (prices - bb_lower) / (bb_upper - bb_lower + 1e-10)

        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=n_samples, freq='h'),
            'symbol': 'SYNTHETIC',
            'close': prices,
            'rsi': rsi,
            'macd': macd,
            'macd_signal': macd_signal,
            'macd_histogram': macd_histogram,
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'bb_bandwidth': bb_bandwidth,
            'bb_percent_b': bb_percent_b
        })

        return df

    def prepare_data(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        prediction_horizon: int = 1
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Prepare features and labels for training.

        Args:
            df: DataFrame with features and close prices
            test_size: Fraction of data for test set
            prediction_horizon: Number of periods ahead to predict

        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        # Create label: 1 if price increases, 0 if decreases
        df['label'] = (df['close'].shift(-prediction_horizon) > df['close']).astype(int)

        # Remove rows with NaN labels
        df = df.dropna()

        # Define feature columns
        self.feature_columns = [
            'rsi', 'macd', 'macd_signal', 'macd_histogram',
            'bb_upper', 'bb_middle', 'bb_lower', 'bb_bandwidth', 'bb_percent_b'
        ]

        # Extract features and labels
        X = df[self.feature_columns]
        y = df['label']

        # Time-series split (no shuffle to preserve temporal order)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            shuffle=False  # Important for time series!
        )

        print(f"[INFO] Training set: {len(X_train)} samples")
        print(f"[INFO] Test set: {len(X_test)} samples")
        print(f"[INFO] Class distribution (train): {y_train.value_counts().to_dict()}")
        print(f"[INFO] Class distribution (test): {y_test.value_counts().to_dict()}")

        return X_train, X_test, y_train, y_test

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        hyperparams: Optional[Dict] = None
    ) -> xgb.XGBClassifier:
        """
        Train XGBoost model.

        Args:
            X_train: Training features
            y_train: Training labels
            X_test: Test features
            y_test: Test labels
            hyperparams: Model hyperparameters (None = defaults)

        Returns:
            Trained XGBoost model
        """
        # Default hyperparameters
        default_params = {
            'max_depth': 5,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'objective': 'binary:logistic',
            'eval_metric': 'logloss',
            'random_state': 42,
            'n_jobs': -1
        }

        if hyperparams:
            default_params.update(hyperparams)

        params = default_params

        print(f"\n[INFO] Training XGBoost with params:")
        for k, v in params.items():
            print(f"  {k}: {v}")

        # Start MLflow run if enabled
        if self.mlflow_enabled:
            mlflow.start_run()
            mlflow.log_params(params)

        # Train model
        start_time = datetime.now()

        self.model = xgb.XGBClassifier(**params)
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )

        training_time = (datetime.now() - start_time).total_seconds()

        # Evaluate
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)

        train_accuracy = accuracy_score(y_train, train_pred)
        test_accuracy = accuracy_score(y_test, test_pred)
        test_precision = precision_score(y_test, test_pred, zero_division=0)
        test_recall = recall_score(y_test, test_pred, zero_division=0)
        test_f1 = f1_score(y_test, test_pred, zero_division=0)

        # Print results
        print(f"\n[RESULTS]")
        print(f"Training time: {training_time:.2f}s")
        print(f"Train accuracy: {train_accuracy:.4f}")
        print(f"Test accuracy: {test_accuracy:.4f}")
        print(f"Test precision: {test_precision:.4f}")
        print(f"Test recall: {test_recall:.4f}")
        print(f"Test F1 score: {test_f1:.4f}")

        # Log metrics to MLflow
        if self.mlflow_enabled:
            mlflow.log_metric("training_time_seconds", training_time)
            mlflow.log_metric("train_accuracy", train_accuracy)
            mlflow.log_metric("test_accuracy", test_accuracy)
            mlflow.log_metric("test_precision", test_precision)
            mlflow.log_metric("test_recall", test_recall)
            mlflow.log_metric("test_f1", test_f1)

            # Log model
            mlflow.xgboost.log_model(self.model, "model")

            mlflow.end_run()
            print("[INFO] Metrics and model logged to MLflow")

        return self.model

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Generate predictions.

        Args:
            X: Features DataFrame

        Returns:
            Array of predicted probabilities for class 1 (price increase)
        """
        if self.model is None:
            raise RuntimeError("Model not trained yet")

        return self.model.predict_proba(X)[:, 1]

    def save_model(self, filepath: str):
        """Save model to disk."""
        if self.model is None:
            raise RuntimeError("No model to save")

        self.model.save_model(filepath)
        print(f"[INFO] Model saved to {filepath}")

    def load_model(self, filepath: str):
        """Load model from disk."""
        self.model = xgb.XGBClassifier()
        self.model.load_model(filepath)
        print(f"[INFO] Model loaded from {filepath}")


def main():
    """Example training pipeline execution."""
    print("="*70)
    print("XGBOOST TRAINING PIPELINE - DEFAULT ML STRATEGY")
    print("="*70)

    # Initialize trainer (MLflow disabled for local testing)
    trainer = XGBoostTrainer(
        mlflow_tracking_uri=None,  # Set to "http://mlflow:5000" when available
        experiment_name="default_ml_strategy"
    )

    # Generate synthetic data for testing
    df = trainer.generate_synthetic_data(n_samples=2000, trend='mixed')

    # Prepare data
    X_train, X_test, y_train, y_test = trainer.prepare_data(df, test_size=0.2)

    # Train model
    model = trainer.train(X_train, y_train, X_test, y_test)

    # Test prediction
    sample_features = X_test.iloc[:5]
    predictions = trainer.predict(sample_features)

    print(f"\n[SAMPLE PREDICTIONS]")
    print(f"Features shape: {sample_features.shape}")
    print(f"Predictions (probability of price increase):")
    for i, prob in enumerate(predictions):
        print(f"  Sample {i+1}: {prob:.4f}")

    print("\n" + "="*70)
    print("[SUCCESS] Training pipeline completed successfully!")
    print("="*70)


if __name__ == '__main__':
    main()
