# liquidity_vacuum.py - Liquidity Vacuum Detection
# Identifies tight consolidation patterns before catalysts (spring-loaded setups)

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import logging
from data_providers import get_provider

logger = logging.getLogger(__name__)


class LiquidityVacuumDetector:
    """
    Detects liquidity vacuum conditions.

    A liquidity vacuum occurs when:
    1. Price consolidates tightly (low volatility)
    2. Volume contracts significantly
    3. Bid-ask spread narrows or remains tight
    4. ATR compresses to low levels
    5. A catalyst is approaching (earnings, FDA decision, etc.)

    These setups are "spring-loaded" - small buying pressure can
    trigger explosive moves due to lack of liquidity.
    """

    def __init__(self, mock_mode: bool = False):
        self.data_provider = get_provider(mock_mode=mock_mode)

    def detect_vacuum(self,
                     symbol: str,
                     lookback_days: int = 30,
                     catalyst_date: str = None) -> Dict:
        """
        Detect liquidity vacuum conditions for a symbol.

        Args:
            symbol: Stock symbol
            lookback_days: Days of history to analyze
            catalyst_date: Optional catalyst date (YYYY-MM-DD)

        Returns:
            {
                'symbol': str,
                'vacuum_detected': bool,
                'vacuum_strength': float (0-100),
                'consolidation_score': float (0-100),
                'volume_contraction_score': float (0-100),
                'spread_score': float (0-100),
                'atr_compression_score': float (0-100),
                'catalyst_proximity_score': float (0-100),
                'days_to_catalyst': int or None,
                'interpretation': str
            }
        """
        try:
            # Fetch price and volume data
            price_data = self._fetch_price_data(symbol, lookback_days)
            if price_data is None:
                return self._default_result(symbol)

            # Calculate component scores
            consolidation_score = self._calculate_consolidation_score(price_data)
            volume_score = self._calculate_volume_contraction_score(price_data)
            atr_score = self._calculate_atr_compression_score(price_data)

            # Get spread score from current market data
            spread_score = self._calculate_spread_score(symbol)

            # Calculate catalyst proximity score
            catalyst_score, days_to_catalyst = self._calculate_catalyst_proximity(catalyst_date)

            # Calculate overall vacuum strength
            vacuum_strength = self._calculate_vacuum_strength(
                consolidation_score,
                volume_score,
                spread_score,
                atr_score,
                catalyst_score
            )

            # Determine if vacuum detected
            vacuum_detected = vacuum_strength >= 60.0

            return {
                'symbol': symbol,
                'vacuum_detected': vacuum_detected,
                'vacuum_strength': vacuum_strength,
                'consolidation_score': consolidation_score,
                'volume_contraction_score': volume_score,
                'spread_score': spread_score,
                'atr_compression_score': atr_score,
                'catalyst_proximity_score': catalyst_score,
                'days_to_catalyst': days_to_catalyst,
                'current_price': float(price_data['Close'].iloc[-1]),
                'avg_volume': float(price_data['Volume'].mean()),
                'analysis_date': datetime.now().isoformat(),
                'interpretation': self._generate_interpretation(
                    vacuum_detected, vacuum_strength, days_to_catalyst
                )
            }

        except Exception as e:
            logger.error(f"Error detecting vacuum for {symbol}: {e}")
            return self._default_result(symbol)

    def _fetch_price_data(self, symbol: str, lookback_days: int) -> Optional[pd.DataFrame]:
        """Fetch price and volume data."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days + 10)

            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)

            if len(hist) < 20:
                return None

            return hist.tail(lookback_days)

        except Exception as e:
            logger.error(f"Error fetching price data for {symbol}: {e}")
            return None

    def _calculate_consolidation_score(self, price_data: pd.DataFrame) -> float:
        """
        Calculate consolidation tightness score (0-100).

        Higher score = tighter consolidation.
        Measured by:
        - Bollinger Band width
        - High-low range compression
        """
        try:
            closes = price_data['Close']
            highs = price_data['High']
            lows = price_data['Low']

            # Calculate Bollinger Band width
            sma_20 = closes.rolling(20).mean()
            std_20 = closes.rolling(20).std()

            bb_width = (2 * std_20) / sma_20
            current_bb_width = bb_width.iloc[-1]
            avg_bb_width = bb_width.mean()

            # BB width compression (lower width = tighter = higher score)
            bb_score = max(0, (1 - current_bb_width / avg_bb_width)) * 100

            # Calculate range compression
            recent_range = (highs.tail(10) - lows.tail(10)) / closes.tail(10)
            avg_range = recent_range.mean()

            historical_range = (highs - lows) / closes
            hist_avg_range = historical_range.mean()

            # Range compression score
            range_score = max(0, (1 - avg_range / hist_avg_range)) * 100

            # Combined consolidation score
            consolidation_score = (bb_score * 0.6 + range_score * 0.4)

            return float(np.clip(consolidation_score, 0, 100))

        except Exception as e:
            logger.error(f"Error calculating consolidation score: {e}")
            return 0.0

    def _calculate_volume_contraction_score(self, price_data: pd.DataFrame) -> float:
        """
        Calculate volume contraction score (0-100).

        Higher score = more volume contraction.
        """
        try:
            volume = price_data['Volume']

            # Recent volume (last 5 days) vs historical average
            recent_volume = volume.tail(5).mean()
            hist_volume = volume.mean()

            if hist_volume == 0:
                return 0.0

            volume_ratio = recent_volume / hist_volume

            # Score: lower ratio = higher score
            # If recent volume is 50% of historical, score = 50
            # If recent volume is 30% of historical, score = 70
            score = max(0, (1 - volume_ratio) * 100)

            return float(np.clip(score, 0, 100))

        except Exception as e:
            logger.error(f"Error calculating volume score: {e}")
            return 0.0

    def _calculate_atr_compression_score(self, price_data: pd.DataFrame) -> float:
        """
        Calculate ATR compression score (0-100).

        Higher score = more ATR compression (lower volatility).
        """
        try:
            highs = price_data['High']
            lows = price_data['Low']
            closes = price_data['Close']

            # Calculate True Range
            tr1 = highs - lows
            tr2 = abs(highs - closes.shift(1))
            tr3 = abs(lows - closes.shift(1))

            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

            # Calculate ATR(14)
            atr_14 = tr.rolling(14).mean()

            current_atr = atr_14.iloc[-1]
            avg_atr = atr_14.mean()

            if avg_atr == 0:
                return 0.0

            atr_ratio = current_atr / avg_atr

            # Score: lower ATR ratio = higher score
            score = max(0, (1 - atr_ratio) * 100)

            return float(np.clip(score, 0, 100))

        except Exception as e:
            logger.error(f"Error calculating ATR score: {e}")
            return 0.0

    def _calculate_spread_score(self, symbol: str) -> float:
        """
        Calculate bid-ask spread score (0-100).

        Lower spread = higher score (better liquidity baseline).
        """
        try:
            spread_data = self.data_provider.get_bid_ask_spread(symbol)

            if spread_data is None:
                return 50.0  # Neutral score if unavailable

            spread_pct = spread_data['spread_pct']

            # Score: lower spread = higher score
            # 0.05% spread = 95 points
            # 0.30% spread = 70 points
            # 1.0% spread = 0 points
            if spread_pct <= 0.05:
                score = 95.0
            elif spread_pct <= 0.30:
                score = 95 - ((spread_pct - 0.05) / 0.25) * 25
            else:
                score = max(0, 70 - (spread_pct - 0.30) * 70)

            return float(np.clip(score, 0, 100))

        except Exception as e:
            logger.error(f"Error calculating spread score: {e}")
            return 50.0

    def _calculate_catalyst_proximity(self, catalyst_date: str = None) -> tuple:
        """
        Calculate catalyst proximity score (0-100).

        Optimal window: 7-30 days before catalyst.
        """
        if catalyst_date is None:
            return 0.0, None

        try:
            catalyst = datetime.strptime(catalyst_date, '%Y-%m-%d')
            today = datetime.now()

            days_to_catalyst = (catalyst - today).days

            if days_to_catalyst < 0:
                # Catalyst has passed
                score = 0.0
            elif days_to_catalyst <= 7:
                # Too close (1-7 days) - moderate score
                score = 50.0
            elif days_to_catalyst <= 30:
                # Optimal window (7-30 days) - high score
                score = 100.0
            elif days_to_catalyst <= 60:
                # Decent window (30-60 days) - moderate score
                score = 70.0
            else:
                # Too far out (60+ days) - low score
                score = 30.0

            return float(score), int(days_to_catalyst)

        except Exception as e:
            logger.error(f"Error calculating catalyst proximity: {e}")
            return 0.0, None

    def _calculate_vacuum_strength(self,
                                  consolidation: float,
                                  volume: float,
                                  spread: float,
                                  atr: float,
                                  catalyst: float) -> float:
        """
        Calculate overall vacuum strength (0-100).

        Weights:
        - Consolidation: 30%
        - Volume contraction: 25%
        - ATR compression: 25%
        - Spread: 10%
        - Catalyst proximity: 10%
        """
        strength = (
            consolidation * 0.30 +
            volume * 0.25 +
            atr * 0.25 +
            spread * 0.10 +
            catalyst * 0.10
        )

        return float(np.clip(strength, 0, 100))

    def _generate_interpretation(self,
                                vacuum_detected: bool,
                                vacuum_strength: float,
                                days_to_catalyst: int = None) -> str:
        """Generate human-readable interpretation."""
        if vacuum_detected:
            base_msg = f"Liquidity vacuum detected (strength: {vacuum_strength:.0f}/100). "

            if days_to_catalyst is not None:
                if 7 <= days_to_catalyst <= 30:
                    return (base_msg +
                           f"Stock is tightly consolidated with {days_to_catalyst} days to catalyst. "
                           "High probability spring-loaded setup.")
                else:
                    return (base_msg +
                           f"Tight consolidation detected ({days_to_catalyst} days to catalyst). "
                           "Monitor for expansion.")
            else:
                return (base_msg +
                       "Tight consolidation with low volume. Monitor for catalyst announcement.")
        else:
            return (f"No significant vacuum detected (strength: {vacuum_strength:.0f}/100). "
                   "Stock not in tight consolidation phase.")

    def batch_analyze(self,
                     symbols: List[str],
                     catalyst_map: Dict[str, str] = None) -> List[Dict]:
        """
        Analyze multiple symbols for liquidity vacuums.

        Args:
            symbols: List of stock symbols
            catalyst_map: Optional dict of {symbol: catalyst_date}

        Returns:
            List of vacuum analyses, sorted by vacuum strength
        """
        results = []

        for symbol in symbols:
            catalyst_date = catalyst_map.get(symbol) if catalyst_map else None
            analysis = self.detect_vacuum(symbol, catalyst_date=catalyst_date)
            results.append(analysis)

        # Sort by vacuum strength
        results.sort(key=lambda x: x['vacuum_strength'], reverse=True)

        return results

    def find_vacuum_opportunities(self,
                                 symbols: List[str],
                                 min_strength: float = 60.0,
                                 catalyst_map: Dict[str, str] = None) -> List[Dict]:
        """
        Find stocks with strong liquidity vacuum setups.

        Args:
            symbols: List of stock symbols
            min_strength: Minimum vacuum strength (0-100)
            catalyst_map: Optional dict of {symbol: catalyst_date}

        Returns:
            List of stocks with vacuum detected, sorted by strength
        """
        results = self.batch_analyze(symbols, catalyst_map)

        opportunities = [
            r for r in results
            if r['vacuum_detected'] and r['vacuum_strength'] >= min_strength
        ]

        return opportunities

    def _default_result(self, symbol: str) -> Dict:
        """Return default result when analysis fails."""
        return {
            'symbol': symbol,
            'vacuum_detected': False,
            'vacuum_strength': 0.0,
            'consolidation_score': 0.0,
            'volume_contraction_score': 0.0,
            'spread_score': 0.0,
            'atr_compression_score': 0.0,
            'catalyst_proximity_score': 0.0,
            'days_to_catalyst': None,
            'current_price': 0.0,
            'avg_volume': 0.0,
            'analysis_date': datetime.now().isoformat(),
            'interpretation': 'Insufficient data for vacuum analysis'
        }


# Module-level instance
_detector = LiquidityVacuumDetector()


def detect_liquidity_vacuum(symbol: str,
                            lookback_days: int = 30,
                            catalyst_date: str = None) -> Dict:
    """Convenience function for vacuum detection."""
    return _detector.detect_vacuum(symbol, lookback_days, catalyst_date)


def find_vacuum_setups(symbols: List[str],
                       min_strength: float = 60.0,
                       catalyst_map: Dict[str, str] = None) -> List[Dict]:
    """Convenience function to find vacuum opportunities."""
    return _detector.find_vacuum_opportunities(symbols, min_strength, catalyst_map)
