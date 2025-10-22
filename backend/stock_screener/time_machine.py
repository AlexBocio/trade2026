# time_machine.py - Time Machine Pattern Matching using DTW
# Matches current price patterns against historical winners using Dynamic Time Warping

from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import yfinance as yf
from datetime import datetime, timedelta
import logging
from pattern_database import get_database, PricePattern

logger = logging.getLogger(__name__)


class TimeMachine:
    """
    Time Machine pattern matcher.

    Uses Dynamic Time Warping (DTW) to find similar historical patterns
    and predict outcomes based on historical performance.
    """

    def __init__(self):
        self.pattern_db = get_database()

    def find_matches(self,
                    symbol: str,
                    lookback_days: int = 30,
                    top_n: int = 5,
                    min_similarity: float = 0.7) -> List[Dict]:
        """
        Find similar historical patterns for a stock.

        Args:
            symbol: Stock symbol
            lookback_days: Days of price history to match
            top_n: Number of top matches to return
            min_similarity: Minimum similarity score (0-1)

        Returns:
            List of pattern matches with similarity scores and expected outcomes
        """
        # Fetch current price data
        current_pattern = self._fetch_current_pattern(symbol, lookback_days)
        if not current_pattern:
            logger.error(f"Could not fetch data for {symbol}")
            return []

        # Compare against all historical patterns
        matches = []
        for pattern in self.pattern_db.patterns.values():
            similarity = self._calculate_similarity(current_pattern, pattern.price_series)

            if similarity >= min_similarity:
                matches.append({
                    'pattern_id': pattern.pattern_id,
                    'pattern_name': pattern.pattern_name,
                    'category': pattern.category,
                    'similarity_score': similarity,
                    'expected_return_5d': pattern.forward_return_5d,
                    'expected_return_10d': pattern.forward_return_10d,
                    'expected_return_20d': pattern.forward_return_20d,
                    'success_rate': pattern.success_rate,
                    'description': pattern.description,
                    'confidence': similarity * pattern.success_rate / 100
                })

        # Sort by similarity score
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)

        return matches[:top_n]

    def predict_outcome(self,
                       symbol: str,
                       lookback_days: int = 30,
                       horizon: str = '10d') -> Dict:
        """
        Predict outcome based on pattern matching.

        Args:
            symbol: Stock symbol
            lookback_days: Days of history to match
            horizon: '5d', '10d', or '20d'

        Returns:
            Prediction dict with expected return and confidence
        """
        matches = self.find_matches(symbol, lookback_days, top_n=10, min_similarity=0.6)

        if not matches:
            return {
                'symbol': symbol,
                'horizon': horizon,
                'expected_return': 0.0,
                'confidence': 0.0,
                'method': 'time_machine_dtw',
                'matches_found': 0
            }

        # Weight predictions by similarity
        total_weight = sum(m['similarity_score'] for m in matches)
        weighted_return = 0.0
        weighted_confidence = 0.0

        return_key = f'expected_return_{horizon}'
        for match in matches:
            weight = match['similarity_score'] / total_weight
            weighted_return += match[return_key] * weight
            weighted_confidence += match['confidence'] * weight

        return {
            'symbol': symbol,
            'horizon': horizon,
            'expected_return': weighted_return,
            'confidence': weighted_confidence,
            'method': 'time_machine_dtw',
            'matches_found': len(matches),
            'top_matches': matches[:3]  # Include top 3 for transparency
        }

    def _fetch_current_pattern(self, symbol: str, lookback_days: int) -> Optional[List[float]]:
        """Fetch and normalize current price pattern."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days + 10)

            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)

            if len(hist) < lookback_days:
                return None

            # Get last N days
            prices = hist['Close'].tail(lookback_days).values

            # Normalize to start at 1.0
            normalized = prices / prices[0]

            return list(normalized)

        except Exception as e:
            logger.error(f"Error fetching pattern for {symbol}: {e}")
            return None

    def _calculate_similarity(self, series1: List[float], series2: List[float]) -> float:
        """
        Calculate similarity between two price series using DTW.

        Returns similarity score 0-1 (1 = identical)
        """
        try:
            # Convert to numpy arrays
            s1 = np.array(series1).reshape(-1, 1)
            s2 = np.array(series2).reshape(-1, 1)

            # Calculate DTW distance
            distance, _ = fastdtw(s1, s2, dist=euclidean)

            # Normalize distance to similarity score
            # Lower distance = higher similarity
            max_possible_distance = len(series1) * 2  # Rough estimate
            similarity = 1.0 / (1.0 + distance / max_possible_distance)

            return float(np.clip(similarity, 0, 1))

        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def batch_analyze(self, symbols: List[str], lookback_days: int = 30) -> List[Dict]:
        """Analyze multiple symbols for pattern matches."""
        results = []

        for symbol in symbols:
            try:
                matches = self.find_matches(symbol, lookback_days, top_n=3)
                prediction = self.predict_outcome(symbol, lookback_days)

                results.append({
                    'symbol': symbol,
                    'best_match': matches[0] if matches else None,
                    'prediction': prediction,
                    'total_matches': len(matches)
                })
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                continue

        return results

    def get_pattern_distribution(self, symbol: str, lookback_days: int = 30) -> Dict:
        """Get distribution of matched pattern categories."""
        matches = self.find_matches(symbol, lookback_days, top_n=20, min_similarity=0.5)

        if not matches:
            return {'categories': {}, 'dominant_category': None}

        # Count by category
        categories = {}
        for match in matches:
            cat = match['category']
            categories[cat] = categories.get(cat, 0) + 1

        # Find dominant category
        dominant = max(categories.items(), key=lambda x: x[1])[0] if categories else None

        return {
            'categories': categories,
            'dominant_category': dominant,
            'total_matches': len(matches)
        }


# Module-level instance
_time_machine = TimeMachine()


def find_pattern_matches(symbol: str, lookback_days: int = 30,
                         top_n: int = 5, min_similarity: float = 0.7) -> List[Dict]:
    """Convenience function for pattern matching."""
    return _time_machine.find_matches(symbol, lookback_days, top_n, min_similarity)


def predict_from_patterns(symbol: str, lookback_days: int = 30,
                          horizon: str = '10d') -> Dict:
    """Convenience function for pattern-based prediction."""
    return _time_machine.predict_outcome(symbol, lookback_days, horizon)
