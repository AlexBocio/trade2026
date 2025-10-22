# sentiment_divergence.py - Sentiment vs Price Divergence Detection
# Identifies when sentiment diverges from price action (contrarian signals)

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import logging
from sentiment_aggregator import SentimentAggregator

logger = logging.getLogger(__name__)


class SentimentDivergenceDetector:
    """
    Detects divergence between sentiment and price action.

    Divergence Types:
    1. Bullish Divergence - Price falling, sentiment improving (contrarian buy)
    2. Bearish Divergence - Price rising, sentiment deteriorating (contrarian sell)
    3. Extreme Sentiment - Sentiment at extremes (potential reversal)
    4. Sentiment Shift - Rapid sentiment change
    """

    def __init__(self, mock_mode: bool = False):
        self.sentiment_aggregator = SentimentAggregator(mock_mode=mock_mode)
        self.mock_mode = mock_mode

    def detect_divergence(self, symbol: str, lookback_days: int = 30) -> Dict:
        """
        Detect sentiment vs price divergence.

        Args:
            symbol: Stock symbol
            lookback_days: Days of history to analyze

        Returns:
            {
                'symbol': str,
                'divergence_detected': bool,
                'divergence_type': str ('bullish', 'bearish', 'none'),
                'divergence_strength': float (0-100),
                'price_trend': str ('up', 'down', 'neutral'),
                'sentiment_trend': str ('improving', 'deteriorating', 'stable'),
                'current_sentiment': float (-100 to 100),
                'sentiment_extreme': bool,
                'contrarian_signal': str,
                'interpretation': str
            }
        """
        try:
            # Get current sentiment
            sentiment_data = self.sentiment_aggregator.aggregate_sentiment(symbol, 7)
            current_sentiment = sentiment_data['aggregate_score']

            # Get price data
            price_data = self._fetch_price_data(symbol, lookback_days)
            if price_data is None:
                return self._default_result(symbol)

            # Analyze price trend
            price_trend = self._analyze_price_trend(price_data)

            # Analyze sentiment trend (compare current vs historical)
            sentiment_trend = self._analyze_sentiment_trend(symbol, current_sentiment)

            # Detect divergence
            divergence_type, divergence_strength = self._detect_divergence_pattern(
                price_trend, sentiment_trend, current_sentiment
            )

            divergence_detected = divergence_strength >= 60.0

            # Check for sentiment extremes
            sentiment_extreme = abs(current_sentiment) >= 70.0

            # Generate contrarian signal
            contrarian_signal = self._generate_contrarian_signal(
                divergence_type, divergence_strength, sentiment_extreme, current_sentiment
            )

            return {
                'symbol': symbol,
                'divergence_detected': divergence_detected,
                'divergence_type': divergence_type,
                'divergence_strength': divergence_strength,
                'price_trend': price_trend['trend'],
                'price_change_pct': price_trend['change_pct'],
                'sentiment_trend': sentiment_trend['trend'],
                'sentiment_change': sentiment_trend['change'],
                'current_sentiment': current_sentiment,
                'sentiment_extreme': sentiment_extreme,
                'contrarian_signal': contrarian_signal,
                'analysis_date': datetime.now().isoformat(),
                'interpretation': self._generate_interpretation(
                    divergence_detected, divergence_type, divergence_strength,
                    price_trend, sentiment_trend, current_sentiment
                )
            }

        except Exception as e:
            logger.error(f"Error detecting divergence for {symbol}: {e}")
            return self._default_result(symbol)

    def _fetch_price_data(self, symbol: str, lookback_days: int) -> Optional[pd.DataFrame]:
        """Fetch price data."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days + 10)

            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)

            if len(hist) < 10:
                return None

            return hist.tail(lookback_days)

        except Exception as e:
            logger.error(f"Error fetching price data for {symbol}: {e}")
            return None

    def _analyze_price_trend(self, price_data: pd.DataFrame) -> Dict:
        """
        Analyze price trend over the period.

        Returns:
            {
                'trend': str ('up', 'down', 'neutral'),
                'change_pct': float,
                'volatility': float
            }
        """
        try:
            closes = price_data['Close']

            # Calculate price change
            start_price = closes.iloc[0]
            end_price = closes.iloc[-1]
            change_pct = ((end_price - start_price) / start_price) * 100

            # Calculate trend
            if change_pct >= 5.0:
                trend = 'up'
            elif change_pct <= -5.0:
                trend = 'down'
            else:
                trend = 'neutral'

            # Calculate volatility
            returns = closes.pct_change().dropna()
            volatility = returns.std() * np.sqrt(252) * 100  # Annualized

            return {
                'trend': trend,
                'change_pct': float(change_pct),
                'volatility': float(volatility)
            }

        except Exception as e:
            logger.error(f"Error analyzing price trend: {e}")
            return {'trend': 'neutral', 'change_pct': 0.0, 'volatility': 0.0}

    def _analyze_sentiment_trend(self, symbol: str, current_sentiment: float) -> Dict:
        """
        Analyze sentiment trend by comparing current vs historical.

        For simplicity, we'll use a basic comparison. In production,
        you would track sentiment over time.
        """
        try:
            # For now, compare current sentiment to neutral (0)
            # In production, you would compare to historical sentiment average

            sentiment_change = current_sentiment - 0.0  # vs neutral baseline

            if sentiment_change >= 20.0:
                trend = 'improving'
            elif sentiment_change <= -20.0:
                trend = 'deteriorating'
            else:
                trend = 'stable'

            return {
                'trend': trend,
                'change': float(sentiment_change)
            }

        except Exception as e:
            logger.error(f"Error analyzing sentiment trend: {e}")
            return {'trend': 'stable', 'change': 0.0}

    def _detect_divergence_pattern(self, price_trend: Dict,
                                   sentiment_trend: Dict,
                                   current_sentiment: float) -> tuple:
        """
        Detect divergence pattern and calculate strength.

        Returns:
            (divergence_type, strength)
        """
        price_dir = price_trend['trend']
        sentiment_dir = sentiment_trend['trend']
        price_change = abs(price_trend['change_pct'])
        sentiment_change = abs(sentiment_trend['change'])

        # Bullish Divergence: Price down, sentiment improving or not as bearish
        if price_dir == 'down' and (sentiment_dir == 'improving' or current_sentiment > -30):
            strength = min(100, price_change * 2 + sentiment_change)
            return ('bullish', float(strength))

        # Bearish Divergence: Price up, sentiment deteriorating or not as bullish
        elif price_dir == 'up' and (sentiment_dir == 'deteriorating' or current_sentiment < 30):
            strength = min(100, price_change * 2 + abs(sentiment_change))
            return ('bearish', float(strength))

        # Extreme Sentiment Divergence
        elif abs(current_sentiment) >= 70:
            if current_sentiment >= 70 and price_dir == 'up':
                # Extreme bullish sentiment at highs - bearish divergence
                return ('bearish', 70.0)
            elif current_sentiment <= -70 and price_dir == 'down':
                # Extreme bearish sentiment at lows - bullish divergence
                return ('bullish', 70.0)

        return ('none', 0.0)

    def _generate_contrarian_signal(self, divergence_type: str,
                                   divergence_strength: float,
                                   sentiment_extreme: bool,
                                   current_sentiment: float) -> str:
        """Generate contrarian trading signal."""
        if divergence_strength < 60:
            return 'No signal'

        if divergence_type == 'bullish':
            if sentiment_extreme and current_sentiment < -70:
                return 'Strong contrarian BUY - extreme pessimism'
            else:
                return 'Contrarian BUY - bearish sentiment, declining price'

        elif divergence_type == 'bearish':
            if sentiment_extreme and current_sentiment > 70:
                return 'Strong contrarian SELL - extreme optimism'
            else:
                return 'Contrarian SELL - bullish sentiment, rising price'

        return 'No signal'

    def _generate_interpretation(self, divergence_detected: bool,
                                divergence_type: str,
                                divergence_strength: float,
                                price_trend: Dict,
                                sentiment_trend: Dict,
                                current_sentiment: float) -> str:
        """Generate human-readable interpretation."""
        if divergence_detected:
            price_dir = price_trend['trend']
            sentiment_dir = sentiment_trend['trend']

            if divergence_type == 'bullish':
                return (f"Bullish divergence detected (strength: {divergence_strength:.0f}/100). "
                       f"Price trending {price_dir} ({price_trend['change_pct']:.1f}%), "
                       f"but sentiment is {sentiment_dir} (score: {current_sentiment:.0f}). "
                       "Contrarian buy opportunity.")

            elif divergence_type == 'bearish':
                return (f"Bearish divergence detected (strength: {divergence_strength:.0f}/100). "
                       f"Price trending {price_dir} ({price_trend['change_pct']:.1f}%), "
                       f"but sentiment is {sentiment_dir} (score: {current_sentiment:.0f}). "
                       "Contrarian sell opportunity.")

        return (f"No significant divergence. Price {price_trend['trend']} "
               f"({price_trend['change_pct']:.1f}%), sentiment {sentiment_trend['trend']} "
               f"(score: {current_sentiment:.0f}).")

    def batch_analyze(self, symbols: List[str], lookback_days: int = 30) -> List[Dict]:
        """
        Analyze multiple symbols for sentiment divergence.

        Args:
            symbols: List of stock symbols
            lookback_days: Days of history to analyze

        Returns:
            List of divergence analyses, sorted by divergence strength
        """
        results = []

        for symbol in symbols:
            analysis = self.detect_divergence(symbol, lookback_days)
            results.append(analysis)

        # Sort by divergence strength
        results.sort(key=lambda x: x['divergence_strength'], reverse=True)

        return results

    def find_divergence_opportunities(self,
                                     symbols: List[str],
                                     min_strength: float = 60.0,
                                     divergence_type: str = None) -> List[Dict]:
        """
        Find stocks with significant sentiment divergence.

        Args:
            symbols: List of stock symbols
            min_strength: Minimum divergence strength (0-100)
            divergence_type: Filter by type ('bullish', 'bearish', or None for both)

        Returns:
            List of stocks with divergence detected
        """
        results = self.batch_analyze(symbols)

        opportunities = [
            r for r in results
            if r['divergence_detected']
            and r['divergence_strength'] >= min_strength
            and (divergence_type is None or r['divergence_type'] == divergence_type)
        ]

        return opportunities

    def _default_result(self, symbol: str) -> Dict:
        """Return default result when analysis fails."""
        return {
            'symbol': symbol,
            'divergence_detected': False,
            'divergence_type': 'none',
            'divergence_strength': 0.0,
            'price_trend': 'neutral',
            'price_change_pct': 0.0,
            'sentiment_trend': 'stable',
            'sentiment_change': 0.0,
            'current_sentiment': 0.0,
            'sentiment_extreme': False,
            'contrarian_signal': 'No signal',
            'analysis_date': datetime.now().isoformat(),
            'interpretation': 'Insufficient data for divergence analysis'
        }


# Module-level instance
_detector = SentimentDivergenceDetector()


def detect_sentiment_divergence(symbol: str, lookback_days: int = 30) -> Dict:
    """Convenience function for divergence detection."""
    return _detector.detect_divergence(symbol, lookback_days)


def find_contrarian_plays(symbols: List[str],
                          min_strength: float = 60.0,
                          divergence_type: str = None) -> List[Dict]:
    """Convenience function to find contrarian opportunities."""
    return _detector.find_divergence_opportunities(symbols, min_strength, divergence_type)
