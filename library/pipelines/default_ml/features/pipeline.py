"""
Feature Pipeline - Integrates all technical indicators.

This pipeline calculates multiple technical indicators from price data
and returns a clean DataFrame ready for ML model training or inference.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

from .rsi import calculate_rsi, calculate_rsi_smoothed
from .macd import calculate_macd, macd_crossover_signal
from .bollinger_bands import (
    calculate_bollinger_bands,
    bollinger_squeeze,
    bollinger_breakout_signal
)


class FeaturePipeline:
    """
    Feature engineering pipeline for trading strategies.

    Calculates technical indicators and prepares features for ML models.
    """

    def __init__(
        self,
        rsi_period: int = 14,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        bb_period: int = 20,
        bb_std: float = 2.0
    ):
        """
        Initialize feature pipeline with indicator parameters.

        Args:
            rsi_period: RSI lookback period
            macd_fast: MACD fast EMA period
            macd_slow: MACD slow EMA period
            macd_signal: MACD signal line period
            bb_period: Bollinger Bands SMA period
            bb_std: Bollinger Bands standard deviation multiplier
        """
        self.rsi_period = rsi_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.bb_period = bb_period
        self.bb_std = bb_std

    def calculate_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators for the given price data.

        Args:
            df: DataFrame with at least a 'close' column

        Returns:
            DataFrame with all original columns plus calculated features

        Raises:
            ValueError: If required columns are missing
        """
        if 'close' not in df.columns:
            raise ValueError("DataFrame must contain 'close' column")

        # Create a copy to avoid modifying original
        result = df.copy()

        # Calculate RSI
        result['rsi'] = calculate_rsi(result['close'], period=self.rsi_period)

        # Calculate MACD
        macd_features = calculate_macd(
            result['close'],
            fast=self.macd_fast,
            slow=self.macd_slow,
            signal=self.macd_signal
        )
        result['macd'] = macd_features['macd']
        result['macd_signal'] = macd_features['signal']
        result['macd_histogram'] = macd_features['histogram']

        # Calculate MACD crossover signals
        result['macd_crossover'] = macd_crossover_signal(macd_features)

        # Calculate Bollinger Bands
        bbands = calculate_bollinger_bands(
            result['close'],
            period=self.bb_period,
            std_dev=self.bb_std
        )
        result['bb_upper'] = bbands['upper']
        result['bb_middle'] = bbands['middle']
        result['bb_lower'] = bbands['lower']
        result['bb_bandwidth'] = bbands['bandwidth']
        result['bb_percent_b'] = bbands['percent_b']

        # Calculate Bollinger squeeze indicator
        result['bb_squeeze'] = bollinger_squeeze(bbands).astype(int)

        # Calculate Bollinger breakout signals
        result['bb_breakout'] = bollinger_breakout_signal(result['close'], bbands)

        # Drop NaN rows from rolling window calculations
        # Keep track of how many rows were dropped
        original_len = len(result)
        result = result.dropna()
        dropped_rows = original_len - len(result)

        if dropped_rows > 0:
            print(f"Dropped {dropped_rows} rows due to NaN values from rolling windows")

        return result

    def calculate_feature_subset(
        self,
        df: pd.DataFrame,
        features: List[str]
    ) -> pd.DataFrame:
        """
        Calculate only a subset of features.

        Args:
            df: DataFrame with price data
            features: List of feature names to calculate
                     Valid: 'rsi', 'macd', 'bollinger_bands'

        Returns:
            DataFrame with requested features only
        """
        result = df.copy()

        if 'rsi' in features:
            result['rsi'] = calculate_rsi(result['close'], period=self.rsi_period)

        if 'macd' in features:
            macd_features = calculate_macd(
                result['close'],
                fast=self.macd_fast,
                slow=self.macd_slow,
                signal=self.macd_signal
            )
            result['macd'] = macd_features['macd']
            result['macd_signal'] = macd_features['signal']
            result['macd_histogram'] = macd_features['histogram']

        if 'bollinger_bands' in features:
            bbands = calculate_bollinger_bands(
                result['close'],
                period=self.bb_period,
                std_dev=self.bb_std
            )
            result['bb_upper'] = bbands['upper']
            result['bb_middle'] = bbands['middle']
            result['bb_lower'] = bbands['lower']

        result = result.dropna()
        return result

    def get_feature_names(self) -> List[str]:
        """
        Get list of all feature column names that will be generated.

        Returns:
            List of feature column names
        """
        return [
            'rsi',
            'macd',
            'macd_signal',
            'macd_histogram',
            'macd_crossover',
            'bb_upper',
            'bb_middle',
            'bb_lower',
            'bb_bandwidth',
            'bb_percent_b',
            'bb_squeeze',
            'bb_breakout'
        ]

    def validate_data(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Validate input data quality.

        Returns:
            Dictionary with validation results
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }

        # Check required columns
        if 'close' not in df.columns:
            validation['valid'] = False
            validation['errors'].append("Missing 'close' column")

        # Check for sufficient data
        min_required = max(self.rsi_period, self.macd_slow, self.bb_period)
        if len(df) < min_required:
            validation['valid'] = False
            validation['errors'].append(
                f"Insufficient data: need at least {min_required} rows, got {len(df)}"
            )

        # Check for missing values
        if df['close'].isna().any():
            na_count = df['close'].isna().sum()
            validation['warnings'].append(f"{na_count} missing values in 'close' column")

        # Calculate stats
        validation['stats'] = {
            'rows': len(df),
            'min_price': df['close'].min(),
            'max_price': df['close'].max(),
            'mean_price': df['close'].mean()
        }

        return validation
