# config.py - Configuration for Meta-Labeling System

class Config:
    """Configuration settings for meta-labeling system."""

    # Server
    PORT = 5000
    HOST = '0.0.0.0'
    DEBUG = True

    # Meta-labeling
    DEFAULT_HOLDING_PERIOD = 5
    DEFAULT_LOOKBACK = 252  # 1 year of trading days
    MIN_DATA_POINTS = 100

    # Primary strategies
    MOMENTUM_FAST = 10
    MOMENTUM_SLOW = 30
    MEAN_REVERSION_LOOKBACK = 20
    MEAN_REVERSION_THRESHOLD = 2.0

    # Feature engineering
    FEATURE_LOOKBACK = 20
    RSI_PERIOD = 14

    # ML models
    RANDOM_FOREST_N_ESTIMATORS = 100
    RANDOM_FOREST_MAX_DEPTH = 10
    RANDOM_FOREST_MIN_SAMPLES_SPLIT = 50

    XGBOOST_N_ESTIMATORS = 100
    XGBOOST_MAX_DEPTH = 6
    XGBOOST_LEARNING_RATE = 0.1

    # Train/test split
    TEST_SIZE = 0.3
    RANDOM_STATE = 42

    # Meta-model prediction
    DEFAULT_CONFIDENCE_THRESHOLD = 0.5
    HIGH_CONFIDENCE_THRESHOLD = 0.7
    LOW_CONFIDENCE_THRESHOLD = 0.3

    # Backtesting
    REBALANCE_FREQ = 'D'  # 'D' daily, 'W' weekly, 'M' monthly
    TRANSACTION_COST = 0.001  # 10 bps

    # Data validation
    MAX_DATA_POINTS = 100000
