# meta_labeler.py - Core meta-labeling logic

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, precision_score, recall_score, accuracy_score
import logging
from typing import Tuple
from config import Config

logger = logging.getLogger(__name__)


def create_meta_labels(primary_signals: pd.Series,
                      returns: pd.Series,
                      holding_period: int = None) -> pd.DataFrame:
    """
    Create meta-labels: Binary labels for whether primary signal is profitable.

    Args:
        primary_signals: Series of +1 (long), -1 (short), 0 (no position)
        returns: Forward returns
        holding_period: How many periods to hold

    Returns:
        DataFrame with columns:
            - primary_signal: Original signal
            - meta_label: 1 if signal profitable, 0 otherwise
            - forward_return: Actual return achieved
            - signal_strength: Absolute value of primary signal
    """
    if holding_period is None:
        holding_period = Config.DEFAULT_HOLDING_PERIOD

    logger.info(f"Creating meta-labels with holding_period={holding_period}")

    # Align signals and returns
    common_idx = primary_signals.index.intersection(returns.index)
    primary_signals = primary_signals.loc[common_idx]
    returns = returns.loc[common_idx]

    df = pd.DataFrame({
        'primary_signal': primary_signals,
        'returns': returns
    })

    # Calculate forward returns over holding period
    df['forward_return'] = df['returns'].rolling(holding_period).sum().shift(-holding_period)

    # Meta-label: Did the signal make money?
    # Long signal (>0) profitable if forward return > 0
    # Short signal (<0) profitable if forward return < 0
    # No signal (=0) is always labeled as 0 (no trade)

    conditions = [
        (df['primary_signal'] > 0) & (df['forward_return'] > 0),  # Long and profitable
        (df['primary_signal'] < 0) & (df['forward_return'] < 0),  # Short and profitable
    ]

    df['meta_label'] = np.select(conditions, [1, 1], default=0)

    df['signal_strength'] = df['primary_signal'].abs()

    # Drop rows with NaN (end of series)
    df_clean = df.dropna()

    logger.info(f"Created {len(df_clean)} meta-labels, positive rate: {df_clean['meta_label'].mean():.2%}")

    return df_clean


def train_meta_model(features: pd.DataFrame,
                    meta_labels: pd.Series,
                    model_type: str = 'random_forest',
                    test_size: float = None,
                    random_state: int = None) -> dict:
    """
    Train meta-model to predict when primary signals will be profitable.

    Args:
        features: Meta-features (volatility, momentum, volume, etc.)
        meta_labels: Binary labels (1=signal works, 0=signal fails)
        model_type: 'random_forest' | 'xgboost' | 'logistic'
        test_size: Fraction for test set
        random_state: Random seed

    Returns:
        {
            'model': Trained model,
            'feature_importance': DataFrame,
            'train_accuracy': float,
            'test_accuracy': float,
            'precision': float,
            'recall': float,
            'predictions': array,
            'probabilities': array
        }
    """
    if test_size is None:
        test_size = Config.TEST_SIZE
    if random_state is None:
        random_state = Config.RANDOM_STATE

    logger.info(f"Training meta-model: {model_type}, test_size={test_size}")

    # Align features and labels
    common_idx = features.index.intersection(meta_labels.index)
    X = features.loc[common_idx]
    y = meta_labels.loc[common_idx]

    # Train/test split (time series, so no shuffle)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, shuffle=False, random_state=random_state
    )

    logger.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

    # Train model
    if model_type == 'random_forest':
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier(
            n_estimators=Config.RANDOM_FOREST_N_ESTIMATORS,
            max_depth=Config.RANDOM_FOREST_MAX_DEPTH,
            min_samples_split=Config.RANDOM_FOREST_MIN_SAMPLES_SPLIT,
            random_state=random_state,
            n_jobs=-1
        )
    elif model_type == 'xgboost':
        from xgboost import XGBClassifier
        model = XGBClassifier(
            n_estimators=Config.XGBOOST_N_ESTIMATORS,
            max_depth=Config.XGBOOST_MAX_DEPTH,
            learning_rate=Config.XGBOOST_LEARNING_RATE,
            random_state=random_state,
            n_jobs=-1
        )
    elif model_type == 'logistic':
        from sklearn.linear_model import LogisticRegression
        model = LogisticRegression(max_iter=1000, random_state=random_state)
    else:
        raise ValueError(f"Unknown model_type: {model_type}")

    # Fit model
    model.fit(X_train, y_train)

    # Predictions
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    y_test_proba = model.predict_proba(X_test)[:, 1]

    # Metrics
    train_accuracy = accuracy_score(y_train, y_train_pred)
    test_accuracy = accuracy_score(y_test, y_test_pred)
    precision = precision_score(y_test, y_test_pred, zero_division=0)
    recall = recall_score(y_test, y_test_pred, zero_division=0)

    logger.info(f"Train accuracy: {train_accuracy:.3f}, Test accuracy: {test_accuracy:.3f}")
    logger.info(f"Precision: {precision:.3f}, Recall: {recall:.3f}")

    # Feature importance
    feature_importance = None
    if hasattr(model, 'feature_importances_'):
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)

    return {
        'model': model,
        'feature_importance': feature_importance,
        'train_accuracy': float(train_accuracy),
        'test_accuracy': float(test_accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'predictions': y_test_pred,
        'probabilities': y_test_proba,
        'y_test': y_test,
        'X_train': X_train,
        'X_test': X_test
    }


def apply_meta_sizing(primary_signals: pd.Series,
                     meta_probabilities: pd.Series,
                     base_size: float = 1.0,
                     threshold: float = None) -> pd.Series:
    """
    Apply position sizing based on meta-model confidence.

    Args:
        primary_signals: Original signals (+1, -1, 0)
        meta_probabilities: P(signal is profitable) from meta-model
        base_size: Base position size
        threshold: Minimum confidence to take position

    Returns:
        Sized positions: direction × size × confidence

    Example:
        Primary signal: +1 (long)
        Meta probability: 0.8 (80% confident)
        Base size: 1.0
        Result: +0.8 (long 80% of base size)
    """
    if threshold is None:
        threshold = Config.DEFAULT_CONFIDENCE_THRESHOLD

    logger.info(f"Applying meta-sizing: threshold={threshold}, base_size={base_size}")

    # Align signals and probabilities
    common_idx = primary_signals.index.intersection(meta_probabilities.index)
    primary_signals = primary_signals.loc[common_idx]
    meta_probabilities = meta_probabilities.loc[common_idx]

    # Only take positions when confidence > threshold
    take_position = meta_probabilities > threshold

    # Size = direction × confidence (if above threshold)
    sized_positions = np.where(
        take_position,
        primary_signals * meta_probabilities * base_size,
        0
    )

    sized_series = pd.Series(sized_positions, index=common_idx)

    # Log statistics
    n_positions = (sized_series != 0).sum()
    avg_size = sized_series[sized_series != 0].abs().mean() if n_positions > 0 else 0

    logger.info(f"Meta-sizing complete: {n_positions} positions, avg size: {avg_size:.3f}")

    return sized_series


def predict_meta_probability(model,
                             features: pd.DataFrame) -> pd.Series:
    """
    Predict probability that signals will be profitable.

    Args:
        model: Trained meta-model
        features: Current features

    Returns:
        Series of probabilities (0-1)
    """
    probabilities = model.predict_proba(features)[:, 1]

    return pd.Series(probabilities, index=features.index)


def evaluate_meta_model(model,
                       X_test: pd.DataFrame,
                       y_test: pd.Series) -> dict:
    """
    Comprehensive evaluation of meta-model.

    Args:
        model: Trained model
        X_test: Test features
        y_test: Test labels

    Returns:
        Dictionary of evaluation metrics
    """
    from sklearn.metrics import confusion_matrix, roc_auc_score, f1_score

    # Predictions
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    # ROC AUC
    try:
        roc_auc = roc_auc_score(y_test, y_proba)
    except:
        roc_auc = 0.0

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)

    return {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'roc_auc': float(roc_auc),
        'confusion_matrix': cm.tolist(),
        'n_test': len(y_test),
        'positive_rate': float(y_test.mean())
    }


def meta_label_pipeline(prices: pd.DataFrame,
                       primary_strategy: callable,
                       holding_period: int = 5,
                       model_type: str = 'random_forest') -> dict:
    """
    Complete meta-labeling pipeline.

    Args:
        prices: OHLCV price data
        primary_strategy: Function that returns signals
        holding_period: Holding period for meta-labels
        model_type: Type of meta-model

    Returns:
        Complete results including model, features, labels, performance
    """
    from feature_engineering import create_meta_features

    logger.info("Running complete meta-labeling pipeline")

    # Step 1: Generate primary signals
    primary_signals = primary_strategy(prices['close'])

    # Step 2: Create meta-labels
    returns = prices['close'].pct_change()
    meta_labels_df = create_meta_labels(primary_signals, returns, holding_period)

    # Step 3: Create features
    features = create_meta_features(prices, primary_signals)

    # Step 4: Train meta-model
    training_result = train_meta_model(
        features,
        meta_labels_df['meta_label'],
        model_type=model_type
    )

    # Step 5: Generate sized positions
    meta_proba = predict_meta_probability(training_result['model'], features)
    sized_positions = apply_meta_sizing(primary_signals, meta_proba)

    logger.info("Meta-labeling pipeline complete")

    return {
        'model': training_result['model'],
        'feature_importance': training_result['feature_importance'],
        'train_accuracy': training_result['train_accuracy'],
        'test_accuracy': training_result['test_accuracy'],
        'precision': training_result['precision'],
        'recall': training_result['recall'],
        'primary_signals': primary_signals,
        'meta_labels': meta_labels_df,
        'features': features,
        'sized_positions': sized_positions
    }
