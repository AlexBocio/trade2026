# market_regime.py - Market-Level Regime Detection
# Detects regimes for major market indices using PROMPT 1 detector

from datetime import datetime
from typing import Dict, List
import logging
from regime_detection import RegimeDetector

logger = logging.getLogger(__name__)


class MarketRegimeDetector:
    """
    Detect regimes for major market indices.

    Indices:
    - SPY: S&P 500 (Large Cap Blend)
    - QQQ: Nasdaq 100 (Large Cap Growth/Tech)
    - IWM: Russell 2000 (Small Cap)
    - DIA: Dow Jones (Blue Chip)

    Analyzes:
    - Individual index regimes
    - Market breadth (alignment across indices)
    - Leadership (which index is leading)
    - Divergences
    """

    MARKET_INDICES = {
        'SPY': 'S&P 500',
        'QQQ': 'Nasdaq 100',
        'IWM': 'Russell 2000',
        'DIA': 'Dow Jones'
    }

    def __init__(self):
        self.regime_detector = RegimeDetector()

    def detect_market_regime(self, lookback_days: int = 60) -> Dict:
        """
        Detect market-level regime.

        Args:
            lookback_days: Lookback period for regime detection

        Returns:
            Market regime dict
        """
        # Detect regime for each major index
        index_regimes = {}
        for symbol, name in self.MARKET_INDICES.items():
            try:
                regime = self.regime_detector.detect_regime(symbol, lookback_days)
                index_regimes[symbol] = regime
            except Exception as e:
                logger.error(f"Failed to detect regime for {symbol}: {e}")
                index_regimes[symbol] = {
                    'primary_regime': 'UNKNOWN',
                    'confidence': 0.0
                }

        # Calculate market breadth
        market_breadth = self._calculate_market_breadth(index_regimes)

        # Determine market leadership
        market_leader = self._determine_market_leader(index_regimes)

        # Detect divergences
        divergences = self._detect_market_divergences(index_regimes)

        # Overall market regime (consensus)
        overall_regime = self._determine_overall_market_regime(index_regimes, market_breadth)

        # Market health score
        market_health = self._calculate_market_health(index_regimes, market_breadth)

        return {
            'timestamp': datetime.now().isoformat(),
            'overall_market_regime': overall_regime,
            'market_health_score': market_health,  # 0-100

            'market_breadth': market_breadth,
            'market_leader': market_leader,
            'divergences': divergences,

            'index_regimes': index_regimes,
            'interpretation': self._interpret_market_regime(
                overall_regime, market_breadth, market_leader
            )
        }

    def _calculate_market_breadth(self, index_regimes: Dict) -> Dict:
        """
        Calculate market breadth metrics.

        Returns:
            - regime_alignment: % of indices in same regime
            - bullish_count: # of bullish regimes
            - bearish_count: # of bearish regimes
            - trending_count: # of trending regimes
        """
        regimes = [r['primary_regime'] for r in index_regimes.values() if 'primary_regime' in r]

        if not regimes:
            return {
                'regime_alignment': 0.0,
                'bullish_count': 0,
                'bearish_count': 0,
                'trending_count': 0,
                'breadth_category': 'UNKNOWN'
            }

        # Count regime types
        bullish_regimes = {'BULL_TRENDING', 'MOMENTUM', 'LOW_VOLATILITY'}
        bearish_regimes = {'BEAR_TRENDING', 'HIGH_VOLATILITY', 'CRISIS'}
        trending_regimes = {'BULL_TRENDING', 'BEAR_TRENDING', 'MOMENTUM'}

        bullish_count = sum(1 for r in regimes if r in bullish_regimes)
        bearish_count = sum(1 for r in regimes if r in bearish_regimes)
        trending_count = sum(1 for r in regimes if r in trending_regimes)

        # Calculate alignment (most common regime %)
        from collections import Counter
        regime_counts = Counter(regimes)
        most_common_count = regime_counts.most_common(1)[0][1] if regime_counts else 0
        alignment = (most_common_count / len(regimes)) * 100 if regimes else 0

        # Determine breadth category
        if alignment >= 75:
            breadth_category = 'STRONG_ALIGNMENT'
        elif alignment >= 50:
            breadth_category = 'MODERATE_ALIGNMENT'
        elif bullish_count == bearish_count:
            breadth_category = 'MIXED'
        else:
            breadth_category = 'DIVERGENT'

        return {
            'regime_alignment': float(alignment),
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'trending_count': trending_count,
            'total_indices': len(regimes),
            'breadth_category': breadth_category
        }

    def _determine_market_leader(self, index_regimes: Dict) -> Dict:
        """Determine which index is leading the market."""
        leaders = []

        # Check confidence and strength
        for symbol, regime in index_regimes.items():
            if 'confidence' in regime and 'characteristics' in regime:
                strength = regime['characteristics'].get('trend_strength', 0)
                confidence = regime['confidence']
                leaders.append({
                    'symbol': symbol,
                    'name': self.MARKET_INDICES.get(symbol, symbol),
                    'regime': regime['primary_regime'],
                    'strength': strength,
                    'confidence': confidence,
                    'score': strength * confidence
                })

        if not leaders:
            return {'symbol': 'NONE', 'regime': 'UNKNOWN'}

        # Sort by score
        leaders.sort(key=lambda x: x['score'], reverse=True)
        leader = leaders[0]

        # Determine leadership type
        if leader['symbol'] == 'QQQ':
            leadership_type = 'GROWTH_LED'
        elif leader['symbol'] == 'IWM':
            leadership_type = 'SMALL_CAP_LED'
        elif leader['symbol'] == 'DIA':
            leadership_type = 'BLUE_CHIP_LED'
        else:
            leadership_type = 'BROAD_MARKET_LED'

        return {
            'symbol': leader['symbol'],
            'name': leader['name'],
            'regime': leader['regime'],
            'leadership_type': leadership_type,
            'strength': leader['strength'],
            'confidence': leader['confidence']
        }

    def _detect_market_divergences(self, index_regimes: Dict) -> List[Dict]:
        """Detect divergences between market indices."""
        divergences = []

        # Get regimes
        spy_regime = index_regimes.get('SPY', {}).get('primary_regime', 'UNKNOWN')
        qqq_regime = index_regimes.get('QQQ', {}).get('primary_regime', 'UNKNOWN')
        iwm_regime = index_regimes.get('IWM', {}).get('primary_regime', 'UNKNOWN')

        # SPY vs QQQ divergence (Growth vs Broad Market)
        if spy_regime != qqq_regime:
            bullish = {'BULL_TRENDING', 'MOMENTUM', 'LOW_VOLATILITY'}
            bearish = {'BEAR_TRENDING', 'HIGH_VOLATILITY', 'CRISIS'}

            if (spy_regime in bullish and qqq_regime in bearish) or \
               (spy_regime in bearish and qqq_regime in bullish):
                divergences.append({
                    'type': 'GROWTH_DIVERGENCE',
                    'description': f'Growth (QQQ: {qqq_regime}) diverging from broad market (SPY: {spy_regime})',
                    'severity': 'HIGH',
                    'indices': ['SPY', 'QQQ']
                })

        # SPY vs IWM divergence (Large vs Small Cap)
        if spy_regime != iwm_regime:
            bullish = {'BULL_TRENDING', 'MOMENTUM', 'LOW_VOLATILITY'}
            bearish = {'BEAR_TRENDING', 'HIGH_VOLATILITY', 'CRISIS'}

            if (spy_regime in bullish and iwm_regime in bearish) or \
               (spy_regime in bearish and iwm_regime in bullish):
                divergences.append({
                    'type': 'SIZE_DIVERGENCE',
                    'description': f'Small caps (IWM: {iwm_regime}) diverging from large caps (SPY: {spy_regime})',
                    'severity': 'MEDIUM',
                    'indices': ['SPY', 'IWM']
                })

        return divergences

    def _determine_overall_market_regime(self, index_regimes: Dict,
                                        market_breadth: Dict) -> str:
        """
        Determine overall market regime based on index consensus.

        Returns: Consensus regime or DIVERGENT/MIXED
        """
        regimes = [r['primary_regime'] for r in index_regimes.values() if 'primary_regime' in r]

        if not regimes:
            return 'UNKNOWN'

        # If strong alignment, use most common regime
        if market_breadth['regime_alignment'] >= 75:
            from collections import Counter
            return Counter(regimes).most_common(1)[0][0]

        # If moderate alignment, use SPY (most representative)
        if market_breadth['regime_alignment'] >= 50:
            return index_regimes.get('SPY', {}).get('primary_regime', 'MIXED')

        # Otherwise, it's divergent or mixed
        if market_breadth['bullish_count'] > market_breadth['bearish_count']:
            return 'MIXED_BULLISH'
        elif market_breadth['bearish_count'] > market_breadth['bullish_count']:
            return 'MIXED_BEARISH'
        else:
            return 'DIVERGENT'

    def _calculate_market_health(self, index_regimes: Dict,
                                 market_breadth: Dict) -> float:
        """
        Calculate overall market health score (0-100).

        Factors:
        - Regime alignment (breadth)
        - Bullish regime prevalence
        - Index confidence levels
        - Trend strength
        """
        score = 0.0

        # Alignment contribution (0-25 points)
        score += market_breadth['regime_alignment'] * 0.25

        # Bullish regime contribution (0-30 points)
        total = market_breadth['total_indices']
        if total > 0:
            bullish_pct = (market_breadth['bullish_count'] / total) * 100
            score += bullish_pct * 0.3

        # Average confidence contribution (0-25 points)
        confidences = [r['confidence'] for r in index_regimes.values() if 'confidence' in r]
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            score += avg_confidence * 25

        # Trend strength contribution (0-20 points)
        strengths = []
        for r in index_regimes.values():
            if 'characteristics' in r:
                strength = r['characteristics'].get('trend_strength', 0)
                strengths.append(strength)
        if strengths:
            avg_strength = sum(strengths) / len(strengths)
            score += avg_strength * 2  # 0-10 strength * 2 = 0-20 points

        return float(min(max(score, 0), 100))

    def _interpret_market_regime(self, overall_regime: str,
                                 market_breadth: Dict,
                                 market_leader: Dict) -> str:
        """Provide interpretation of market regime."""
        alignment = market_breadth['regime_alignment']
        breadth_cat = market_breadth['breadth_category']
        leader_type = market_leader.get('leadership_type', 'UNKNOWN')

        base_interpretations = {
            'BULL_TRENDING': 'Strong bullish trend across markets',
            'BEAR_TRENDING': 'Strong bearish trend across markets',
            'MOMENTUM': 'Momentum-driven market',
            'MEAN_REVERTING': 'Range-bound, mean-reverting market',
            'HIGH_VOLATILITY': 'High volatility environment',
            'LOW_VOLATILITY': 'Low volatility, grinding higher',
            'RANGE_BOUND': 'Sideways, choppy market',
            'CRISIS': 'Crisis conditions',
            'MIXED_BULLISH': 'Mixed signals with bullish bias',
            'MIXED_BEARISH': 'Mixed signals with bearish bias',
            'DIVERGENT': 'Significant divergences between indices'
        }

        base = base_interpretations.get(overall_regime, 'Complex market environment')

        if breadth_cat == 'STRONG_ALIGNMENT':
            alignment_str = f"Strong alignment ({alignment:.0f}%)"
        elif breadth_cat == 'MODERATE_ALIGNMENT':
            alignment_str = f"Moderate alignment ({alignment:.0f}%)"
        else:
            alignment_str = f"Low alignment ({alignment:.0f}%), rotation likely"

        leader_str = f"Led by {market_leader['name']} ({leader_type})"

        return f"{base}. {alignment_str}. {leader_str}."


# Module-level function for convenience
_detector = MarketRegimeDetector()


def detect_market_regime(lookback_days: int = 60) -> Dict:
    """Convenience function for market regime detection."""
    return _detector.detect_market_regime(lookback_days)
