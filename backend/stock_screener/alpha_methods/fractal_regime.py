# fractal_regime.py - Multi-Timeframe Regime Detection
# Analyzes market regime across multiple timeframes (5d, 20d, 60d, 252d)

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FractalRegimeDetector:
    """
    Detects market regime across multiple timeframes.

    Timeframes analyzed:
    1. Ultra-short (5 days) - Microstructure
    2. Short (20 days) - Swing trend
    3. Medium (60 days) - Intermediate trend
    4. Long (252 days) - Primary trend

    Regime Types:
    - Trending Up: Consistent upward momentum
    - Trending Down: Consistent downward momentum
    - Range-bound: Sideways consolidation
    - Volatile: High volatility, no clear direction
    """

    def __init__(self):
        self.timeframes = {
            'ultra_short': 5,
            'short': 20,
            'medium': 60,
            'long': 252
        }

    def detect_regime(self, symbol: str) -> Dict:
        """
        Detect market regime across all timeframes.

        Args:
            symbol: Stock symbol

        Returns:
            {
                'symbol': str,
                'alignment_detected': bool,
                'alignment_type': str ('bullish', 'bearish', 'mixed'),
                'alignment_strength': float (0-100),
                'regimes': {
                    'ultra_short': {...},
                    'short': {...},
                    'medium': {...},
                    'long': {...}
                },
                'fractal_score': float (0-100),
                'interpretation': str
            }
        """
        try:
            # Fetch price data for longest timeframe
            price_data = self._fetch_price_data(symbol, self.timeframes['long'] + 50)
            if price_data is None:
                return self._default_result(symbol)

            # Analyze regime for each timeframe
            regimes = {}
            for tf_name, tf_days in self.timeframes.items():
                regime = self._analyze_timeframe_regime(price_data, tf_days, tf_name)
                regimes[tf_name] = regime

            # Detect alignment across timeframes
            alignment_detected, alignment_type, alignment_strength = self._detect_alignment(regimes)

            # Calculate fractal score (multi-timeframe confluence)
            fractal_score = self._calculate_fractal_score(regimes)

            return {
                'symbol': symbol,
                'alignment_detected': alignment_detected,
                'alignment_type': alignment_type,
                'alignment_strength': alignment_strength,
                'regimes': regimes,
                'fractal_score': fractal_score,
                'analysis_date': datetime.now().isoformat(),
                'interpretation': self._generate_interpretation(
                    alignment_detected, alignment_type, alignment_strength, regimes
                )
            }

        except Exception as e:
            logger.error(f"Error detecting regime for {symbol}: {e}")
            return self._default_result(symbol)

    def _fetch_price_data(self, symbol: str, lookback_days: int) -> Optional[pd.DataFrame]:
        """Fetch price data."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days + 30)

            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)

            if len(hist) < 50:
                return None

            return hist

        except Exception as e:
            logger.error(f"Error fetching price data for {symbol}: {e}")
            return None

    def _analyze_timeframe_regime(self, price_data: pd.DataFrame,
                                  lookback_days: int,
                                  timeframe_name: str) -> Dict:
        """
        Analyze regime for a specific timeframe.

        Returns:
            {
                'regime': str ('trending_up', 'trending_down', 'range_bound', 'volatile'),
                'trend_strength': float (0-100),
                'volatility': float,
                'price_change_pct': float,
                'above_ma': bool
            }
        """
        try:
            # Get data for this timeframe
            data = price_data.tail(lookback_days)

            if len(data) < lookback_days * 0.8:  # Need at least 80% of data
                return self._default_regime()

            closes = data['Close']
            highs = data['High']
            lows = data['Low']

            # Calculate price change
            start_price = closes.iloc[0]
            end_price = closes.iloc[-1]
            price_change_pct = ((end_price - start_price) / start_price) * 100

            # Calculate moving average
            ma_period = max(int(lookback_days * 0.5), 5)
            ma = closes.rolling(ma_period).mean()
            current_price = closes.iloc[-1]
            current_ma = ma.iloc[-1]
            above_ma = current_price > current_ma

            # Calculate volatility (ATR-based)
            tr1 = highs - lows
            tr2 = abs(highs - closes.shift(1))
            tr3 = abs(lows - closes.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(min(14, len(data))).mean().iloc[-1]
            atr_pct = (atr / current_price) * 100

            # Calculate trend strength using linear regression
            x = np.arange(len(closes))
            y = closes.values
            slope, _ = np.polyfit(x, y, 1)
            trend_strength = abs(slope / start_price) * 100 * len(closes)  # Normalize

            # Determine regime
            regime = self._classify_regime(price_change_pct, atr_pct, trend_strength, above_ma)

            return {
                'regime': regime,
                'trend_strength': float(np.clip(trend_strength, 0, 100)),
                'volatility': float(atr_pct),
                'price_change_pct': float(price_change_pct),
                'above_ma': bool(above_ma),
                'ma_distance_pct': float(((current_price - current_ma) / current_ma) * 100)
            }

        except Exception as e:
            logger.error(f"Error analyzing timeframe regime: {e}")
            return self._default_regime()

    def _classify_regime(self, price_change: float, volatility: float,
                        trend_strength: float, above_ma: bool) -> str:
        """
        Classify market regime based on metrics.
        """
        # High volatility regime
        if volatility > 5.0:
            return 'volatile'

        # Trending regimes
        if abs(price_change) >= 10.0 and trend_strength >= 30:
            if price_change > 0 and above_ma:
                return 'trending_up'
            elif price_change < 0 and not above_ma:
                return 'trending_down'

        # Moderate trend
        if abs(price_change) >= 5.0:
            if price_change > 0:
                return 'trending_up'
            else:
                return 'trending_down'

        # Range-bound (low price change, low volatility)
        return 'range_bound'

    def _detect_alignment(self, regimes: Dict) -> tuple:
        """
        Detect alignment across timeframes.

        Returns:
            (alignment_detected, alignment_type, alignment_strength)
        """
        # Count regimes by type
        trending_up_count = sum(1 for r in regimes.values() if r['regime'] == 'trending_up')
        trending_down_count = sum(1 for r in regimes.values() if r['regime'] == 'trending_down')

        total_timeframes = len(regimes)

        # Bullish alignment: 3+ timeframes trending up
        if trending_up_count >= 3:
            strength = (trending_up_count / total_timeframes) * 100
            return (True, 'bullish', float(strength))

        # Bearish alignment: 3+ timeframes trending down
        if trending_down_count >= 3:
            strength = (trending_down_count / total_timeframes) * 100
            return (True, 'bearish', float(strength))

        # Partial alignment: 2 timeframes in same direction
        if trending_up_count == 2 and trending_down_count == 0:
            return (True, 'bullish', 50.0)

        if trending_down_count == 2 and trending_up_count == 0:
            return (True, 'bearish', 50.0)

        # Mixed or no alignment
        return (False, 'mixed', 0.0)

    def _calculate_fractal_score(self, regimes: Dict) -> float:
        """
        Calculate fractal score based on multi-timeframe confluence.

        Higher score = stronger alignment across timeframes.
        """
        try:
            # Weight timeframes (longer = more important)
            weights = {
                'ultra_short': 0.15,
                'short': 0.25,
                'medium': 0.30,
                'long': 0.30
            }

            # Calculate weighted score based on trend strength and regime consistency
            score = 0.0

            # Get primary regime from long timeframe
            primary_regime = regimes['long']['regime']

            for tf_name, regime_data in regimes.items():
                weight = weights[tf_name]
                trend_strength = regime_data['trend_strength']

                # Bonus if regime matches primary regime
                regime_match = 1.5 if regime_data['regime'] == primary_regime else 0.5

                score += trend_strength * weight * regime_match

            return float(np.clip(score, 0, 100))

        except Exception as e:
            logger.error(f"Error calculating fractal score: {e}")
            return 0.0

    def _generate_interpretation(self, alignment_detected: bool,
                                alignment_type: str,
                                alignment_strength: float,
                                regimes: Dict) -> str:
        """Generate human-readable interpretation."""
        if alignment_detected:
            aligned_tfs = sum(1 for r in regimes.values()
                            if r['regime'] in ['trending_up', 'trending_down'])

            if alignment_type == 'bullish':
                return (f"Bullish fractal alignment detected ({alignment_strength:.0f}% strength). "
                       f"{aligned_tfs}/4 timeframes in bullish regime. "
                       "Strong multi-timeframe uptrend confirmation.")

            elif alignment_type == 'bearish':
                return (f"Bearish fractal alignment detected ({alignment_strength:.0f}% strength). "
                       f"{aligned_tfs}/4 timeframes in bearish regime. "
                       "Strong multi-timeframe downtrend confirmation.")

        # No alignment
        regime_summary = ', '.join([f"{tf}: {r['regime']}" for tf, r in regimes.items()])
        return f"No significant alignment. Mixed regimes across timeframes: {regime_summary}"

    def batch_analyze(self, symbols: List[str]) -> List[Dict]:
        """
        Analyze multiple symbols for fractal regime alignment.

        Args:
            symbols: List of stock symbols

        Returns:
            List of regime analyses, sorted by fractal score
        """
        results = []

        for symbol in symbols:
            analysis = self.detect_regime(symbol)
            results.append(analysis)

        # Sort by fractal score
        results.sort(key=lambda x: x['fractal_score'], reverse=True)

        return results

    def find_aligned_opportunities(self,
                                  symbols: List[str],
                                  alignment_type: str = None,
                                  min_strength: float = 60.0) -> List[Dict]:
        """
        Find stocks with strong fractal alignment.

        Args:
            symbols: List of stock symbols
            alignment_type: Filter by type ('bullish', 'bearish', or None for both)
            min_strength: Minimum alignment strength (0-100)

        Returns:
            List of stocks with alignment detected
        """
        results = self.batch_analyze(symbols)

        opportunities = [
            r for r in results
            if r['alignment_detected']
            and r['alignment_strength'] >= min_strength
            and (alignment_type is None or r['alignment_type'] == alignment_type)
        ]

        return opportunities

    def _default_regime(self) -> Dict:
        """Return default regime when analysis fails."""
        return {
            'regime': 'unknown',
            'trend_strength': 0.0,
            'volatility': 0.0,
            'price_change_pct': 0.0,
            'above_ma': False,
            'ma_distance_pct': 0.0
        }

    def _default_result(self, symbol: str) -> Dict:
        """Return default result when analysis fails."""
        return {
            'symbol': symbol,
            'alignment_detected': False,
            'alignment_type': 'mixed',
            'alignment_strength': 0.0,
            'regimes': {
                'ultra_short': self._default_regime(),
                'short': self._default_regime(),
                'medium': self._default_regime(),
                'long': self._default_regime()
            },
            'fractal_score': 0.0,
            'analysis_date': datetime.now().isoformat(),
            'interpretation': 'Insufficient data for regime analysis'
        }


# Module-level instance
_detector = FractalRegimeDetector()


def detect_fractal_regime(symbol: str) -> Dict:
    """Convenience function for regime detection."""
    return _detector.detect_regime(symbol)


def find_fractal_setups(symbols: List[str],
                        alignment_type: str = None,
                        min_strength: float = 60.0) -> List[Dict]:
    """Convenience function to find aligned opportunities."""
    return _detector.find_aligned_opportunities(symbols, alignment_type, min_strength)
