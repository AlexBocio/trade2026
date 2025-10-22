# confidence_scoring.py - Prediction Confidence Scoring
# Adjust confidence based on market regime, historical accuracy, and model agreement

import numpy as np
import pandas as pd
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


def calculate_prediction_confidence(predictions: Dict,
                                   historical_accuracy: Dict = None,
                                   regime: str = 'trending') -> Dict[str, float]:
    """
    Calculate confidence scores for predictions.

    Factors affecting confidence:
    1. Model ensemble agreement (low std = high confidence)
    2. Historical accuracy for this timeframe
    3. Current market regime (predictions better in trending vs choppy)
    4. Data quality and recency

    Args:
        predictions: Raw predictions from models
        historical_accuracy: Past accuracy for each horizon
        regime: 'trending' | 'mean_reverting' | 'volatile' | 'choppy'

    Returns:
        Confidence scores per timeframe
    """
    if historical_accuracy is None:
        historical_accuracy = _get_default_accuracy()

    confidence_scores = {}

    # Regime adjustments (supports both old 4-regime and new 8-regime systems)
    regime_multipliers = {
        # Old 4-regime system (for backward compatibility)
        'trending': {
            '1h': 0.7, '4h': 0.75,
            '1d': 0.8, '2d': 0.85, '3d': 0.9, '4d': 0.9, '5d': 0.9,
            '1w': 0.9, '2w': 0.95, '3w': 0.95, '4w': 0.95, '5w': 0.95,
            '1mo': 1.0, '2mo': 1.0, '3mo': 1.0, '4mo': 1.0, '5mo': 1.0, '6mo': 1.0
        },
        'mean_reverting': {
            '1h': 0.9, '4h': 0.85,
            '1d': 0.8, '2d': 0.75, '3d': 0.7, '4d': 0.7, '5d': 0.7,
            '1w': 0.6, '2w': 0.6, '3w': 0.6, '4w': 0.6, '5w': 0.6,
            '1mo': 0.5, '2mo': 0.5, '3mo': 0.5, '4mo': 0.5, '5mo': 0.5, '6mo': 0.5
        },
        'volatile': {
            '1h': 0.5, '4h': 0.55,
            '1d': 0.6, '2d': 0.65, '3d': 0.65, '4d': 0.65, '5d': 0.65,
            '1w': 0.7, '2w': 0.75, '3w': 0.75, '4w': 0.75, '5w': 0.75,
            '1mo': 0.8, '2mo': 0.8, '3mo': 0.8, '4mo': 0.8, '5mo': 0.8, '6mo': 0.8
        },
        'choppy': {
            '1h': 0.4, '4h': 0.45,
            '1d': 0.5, '2d': 0.55, '3d': 0.55, '4d': 0.55, '5d': 0.55,
            '1w': 0.6, '2w': 0.65, '3w': 0.65, '4w': 0.65, '5w': 0.65,
            '1mo': 0.7, '2mo': 0.7, '3mo': 0.7, '4mo': 0.7, '5mo': 0.7, '6mo': 0.7
        },

        # New 8-regime system
        'BULL_TRENDING': {
            '1h': 0.75, '4h': 0.80,
            '1d': 0.85, '2d': 0.90, '3d': 0.92, '4d': 0.92, '5d': 0.92,
            '1w': 0.95, '2w': 1.0, '3w': 1.0, '4w': 1.0, '5w': 1.0,
            '1mo': 1.0, '2mo': 1.0, '3mo': 1.0, '4mo': 0.95, '5mo': 0.95, '6mo': 0.95
        },
        'BEAR_TRENDING': {
            '1h': 0.75, '4h': 0.80,
            '1d': 0.85, '2d': 0.90, '3d': 0.92, '4d': 0.92, '5d': 0.92,
            '1w': 0.95, '2w': 1.0, '3w': 1.0, '4w': 1.0, '5w': 1.0,
            '1mo': 1.0, '2mo': 1.0, '3mo': 1.0, '4mo': 0.95, '5mo': 0.95, '6mo': 0.95
        },
        'MOMENTUM': {
            '1h': 0.65, '4h': 0.70,
            '1d': 0.75, '2d': 0.80, '3d': 0.85, '4d': 0.85, '5d': 0.85,
            '1w': 0.90, '2w': 0.95, '3w': 0.95, '4w': 0.95, '5w': 0.95,
            '1mo': 0.95, '2mo': 0.95, '3mo': 0.90, '4mo': 0.85, '5mo': 0.80, '6mo': 0.75
        },
        'MEAN_REVERTING': {
            '1h': 0.90, '4h': 0.85,
            '1d': 0.80, '2d': 0.75, '3d': 0.70, '4d': 0.70, '5d': 0.70,
            '1w': 0.60, '2w': 0.60, '3w': 0.60, '4w': 0.60, '5w': 0.60,
            '1mo': 0.50, '2mo': 0.50, '3mo': 0.50, '4mo': 0.50, '5mo': 0.50, '6mo': 0.50
        },
        'HIGH_VOLATILITY': {
            '1h': 0.45, '4h': 0.50,
            '1d': 0.55, '2d': 0.60, '3d': 0.60, '4d': 0.60, '5d': 0.60,
            '1w': 0.65, '2w': 0.70, '3w': 0.70, '4w': 0.70, '5w': 0.70,
            '1mo': 0.75, '2mo': 0.75, '3mo': 0.75, '4mo': 0.75, '5mo': 0.75, '6mo': 0.75
        },
        'LOW_VOLATILITY': {
            '1h': 0.55, '4h': 0.60,
            '1d': 0.65, '2d': 0.70, '3d': 0.70, '4d': 0.70, '5d': 0.70,
            '1w': 0.75, '2w': 0.80, '3w': 0.80, '4w': 0.80, '5w': 0.80,
            '1mo': 0.85, '2mo': 0.85, '3mo': 0.85, '4mo': 0.85, '5mo': 0.85, '6mo': 0.85
        },
        'RANGE_BOUND': {
            '1h': 0.40, '4h': 0.45,
            '1d': 0.50, '2d': 0.55, '3d': 0.55, '4d': 0.55, '5d': 0.55,
            '1w': 0.60, '2w': 0.65, '3w': 0.65, '4w': 0.65, '5w': 0.65,
            '1mo': 0.70, '2mo': 0.70, '3mo': 0.70, '4mo': 0.70, '5mo': 0.70, '6mo': 0.70
        },
        'CRISIS': {
            '1h': 0.30, '4h': 0.35,
            '1d': 0.40, '2d': 0.45, '3d': 0.45, '4d': 0.45, '5d': 0.45,
            '1w': 0.50, '2w': 0.55, '3w': 0.55, '4w': 0.55, '5w': 0.55,
            '1mo': 0.60, '2mo': 0.60, '3mo': 0.60, '4mo': 0.60, '5mo': 0.60, '6mo': 0.60
        }
    }

    for horizon, pred in predictions.items():
        base_confidence = pred.get('confidence', 0.5)

        # Adjust for regime
        regime_mult = regime_multipliers.get(regime, {}).get(horizon, 0.7)

        # Adjust for historical accuracy
        hist_acc = historical_accuracy.get(horizon, 0.5)

        # Combined confidence
        final_confidence = base_confidence * regime_mult * hist_acc
        final_confidence = min(max(final_confidence, 0.0), 1.0)

        confidence_scores[horizon] = final_confidence

    return confidence_scores


def _get_default_accuracy() -> Dict[str, float]:
    """
    Get default historical accuracy estimates.

    Generally:
    - Short-term predictions are less accurate
    - Medium-term predictions are most accurate
    - Long-term predictions have more uncertainty
    """
    return {
        # Intraday (low accuracy due to noise)
        '1h': 0.5,
        '4h': 0.55,

        # Short-term (moderate accuracy)
        '1d': 0.6,
        '2d': 0.65,
        '3d': 0.7,
        '4d': 0.7,
        '5d': 0.7,

        # Medium-term (highest accuracy)
        '1w': 0.75,
        '2w': 0.8,
        '3w': 0.8,
        '4w': 0.8,
        '5w': 0.8,

        # Long-term (decreasing accuracy)
        '1mo': 0.75,
        '2mo': 0.7,
        '3mo': 0.65,
        '4mo': 0.6,
        '5mo': 0.55,
        '6mo': 0.5
    }


def adjust_confidence_by_volatility(confidence_scores: Dict[str, float],
                                    volatility: float,
                                    baseline_vol: float = 0.02) -> Dict[str, float]:
    """
    Adjust confidence scores based on current volatility.

    Higher volatility = lower confidence (more unpredictable).

    Args:
        confidence_scores: Base confidence scores
        volatility: Current annualized volatility
        baseline_vol: Baseline "normal" volatility

    Returns:
        Adjusted confidence scores
    """
    # Calculate volatility multiplier
    # If vol = baseline, mult = 1.0
    # If vol = 2 × baseline, mult = 0.7
    # If vol = 0.5 × baseline, mult = 1.2
    vol_ratio = volatility / baseline_vol if baseline_vol > 0 else 1.0
    vol_multiplier = 1.0 / np.sqrt(vol_ratio)
    vol_multiplier = min(max(vol_multiplier, 0.5), 1.5)  # Clamp to [0.5, 1.5]

    adjusted = {}
    for horizon, confidence in confidence_scores.items():
        adjusted[horizon] = min(confidence * vol_multiplier, 1.0)

    return adjusted


def calculate_ensemble_agreement(predictions_ensemble: List[float]) -> float:
    """
    Calculate agreement score from ensemble predictions.

    High agreement (low std) = high confidence.

    Args:
        predictions_ensemble: List of predictions from different models

    Returns:
        Agreement score (0-1)
    """
    if len(predictions_ensemble) < 2:
        return 0.5

    std = np.std(predictions_ensemble)

    # Convert std to agreement score
    # Low std → high agreement
    # We expect returns in range -0.2 to 0.2, so std of 0.05 is moderate
    agreement = 1.0 / (1.0 + std * 20)
    agreement = min(max(agreement, 0.0), 1.0)

    return float(agreement)


def get_confidence_category(confidence: float) -> str:
    """
    Categorize confidence score.

    Args:
        confidence: Confidence score (0-1)

    Returns:
        Category: 'very_low' | 'low' | 'moderate' | 'high' | 'very_high'
    """
    if confidence < 0.3:
        return 'very_low'
    elif confidence < 0.5:
        return 'low'
    elif confidence < 0.7:
        return 'moderate'
    elif confidence < 0.9:
        return 'high'
    else:
        return 'very_high'


def filter_predictions_by_confidence(predictions: Dict[str, Dict],
                                    min_confidence: float = 0.6) -> Dict[str, Dict]:
    """
    Filter predictions to only include those above minimum confidence.

    Args:
        predictions: Predictions dict
        min_confidence: Minimum confidence threshold

    Returns:
        Filtered predictions
    """
    filtered = {}

    for horizon, pred in predictions.items():
        if pred.get('confidence', 0) >= min_confidence:
            filtered[horizon] = pred

    return filtered
