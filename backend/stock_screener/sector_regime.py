# sector_regime.py - Sector-Level Regime Detection
# Detects regimes for 11 SPDR sector ETFs

from datetime import datetime
from typing import Dict, List
import logging
from regime_detection import RegimeDetector

logger = logging.getLogger(__name__)


class SectorRegimeDetector:
    """
    Detect regimes for 11 SPDR sector ETFs.

    Sectors:
    - XLK: Technology
    - XLF: Financials
    - XLV: Healthcare
    - XLE: Energy
    - XLY: Consumer Discretionary
    - XLP: Consumer Staples
    - XLI: Industrials
    - XLB: Materials
    - XLRE: Real Estate
    - XLU: Utilities
    - XLC: Communication Services

    Analyzes:
    - Individual sector regimes
    - Sector rotation patterns
    - Defensive vs Cyclical leadership
    - Sector divergences
    """

    SECTORS = {
        'XLK': 'Technology',
        'XLF': 'Financials',
        'XLV': 'Healthcare',
        'XLE': 'Energy',
        'XLY': 'Consumer Discretionary',
        'XLP': 'Consumer Staples',
        'XLI': 'Industrials',
        'XLB': 'Materials',
        'XLRE': 'Real Estate',
        'XLU': 'Utilities',
        'XLC': 'Communication Services'
    }

    # Sector classifications
    CYCLICAL_SECTORS = {'XLY', 'XLF', 'XLE', 'XLI', 'XLB'}
    DEFENSIVE_SECTORS = {'XLP', 'XLU', 'XLV'}
    GROWTH_SECTORS = {'XLK', 'XLC', 'XLY'}
    VALUE_SECTORS = {'XLF', 'XLE', 'XLU'}

    def __init__(self):
        self.regime_detector = RegimeDetector()

    def detect_sector_regime(self, lookback_days: int = 60) -> Dict:
        """
        Detect sector-level regime.

        Args:
            lookback_days: Lookback period for regime detection

        Returns:
            Sector regime dict
        """
        # Detect regime for each sector
        sector_regimes = {}
        for symbol, name in self.SECTORS.items():
            try:
                regime = self.regime_detector.detect_regime(symbol, lookback_days)
                sector_regimes[symbol] = regime
            except Exception as e:
                logger.error(f"Failed to detect regime for {symbol}: {e}")
                sector_regimes[symbol] = {
                    'primary_regime': 'UNKNOWN',
                    'confidence': 0.0
                }

        # Analyze sector rotation
        rotation_analysis = self._analyze_sector_rotation(sector_regimes)

        # Determine sector leadership
        sector_leaders = self._determine_sector_leaders(sector_regimes)

        # Detect sector divergences
        divergences = self._detect_sector_divergences(sector_regimes)

        # Overall sector regime (rotation pattern)
        overall_pattern = self._determine_rotation_pattern(rotation_analysis)

        # Risk appetite score
        risk_appetite = self._calculate_risk_appetite(sector_regimes, rotation_analysis)

        return {
            'timestamp': datetime.now().isoformat(),
            'rotation_pattern': overall_pattern,
            'risk_appetite_score': risk_appetite,  # 0-100

            'rotation_analysis': rotation_analysis,
            'sector_leaders': sector_leaders,
            'divergences': divergences,

            'sector_regimes': sector_regimes,
            'interpretation': self._interpret_sector_regime(
                overall_pattern, rotation_analysis, sector_leaders
            )
        }

    def _analyze_sector_rotation(self, sector_regimes: Dict) -> Dict:
        """Analyze sector rotation patterns."""
        # Count bullish sectors by category
        bullish_regimes = {'BULL_TRENDING', 'MOMENTUM', 'LOW_VOLATILITY'}

        cyclical_bullish = sum(
            1 for s in self.CYCLICAL_SECTORS
            if sector_regimes.get(s, {}).get('primary_regime') in bullish_regimes
        )
        defensive_bullish = sum(
            1 for s in self.DEFENSIVE_SECTORS
            if sector_regimes.get(s, {}).get('primary_regime') in bullish_regimes
        )
        growth_bullish = sum(
            1 for s in self.GROWTH_SECTORS
            if sector_regimes.get(s, {}).get('primary_regime') in bullish_regimes
        )
        value_bullish = sum(
            1 for s in self.VALUE_SECTORS
            if sector_regimes.get(s, {}).get('primary_regime') in bullish_regimes
        )

        # Calculate percentages
        cyclical_pct = (cyclical_bullish / len(self.CYCLICAL_SECTORS)) * 100
        defensive_pct = (defensive_bullish / len(self.DEFENSIVE_SECTORS)) * 100
        growth_pct = (growth_bullish / len(self.GROWTH_SECTORS)) * 100
        value_pct = (value_bullish / len(self.VALUE_SECTORS)) * 100

        # Determine dominant style
        if cyclical_pct > defensive_pct + 30:
            style = 'RISK_ON_CYCLICAL'
        elif defensive_pct > cyclical_pct + 30:
            style = 'RISK_OFF_DEFENSIVE'
        elif growth_pct > value_pct + 30:
            style = 'GROWTH_DOMINANCE'
        elif value_pct > growth_pct + 30:
            style = 'VALUE_DOMINANCE'
        else:
            style = 'BALANCED_ROTATION'

        return {
            'cyclical_strength': cyclical_pct,
            'defensive_strength': defensive_pct,
            'growth_strength': growth_pct,
            'value_strength': value_pct,
            'dominant_style': style,
            'cyclical_bullish_count': cyclical_bullish,
            'defensive_bullish_count': defensive_bullish
        }

    def _determine_sector_leaders(self, sector_regimes: Dict) -> List[Dict]:
        """Determine leading sectors."""
        leaders = []

        for symbol, regime in sector_regimes.items():
            if 'confidence' in regime and 'characteristics' in regime:
                strength = regime['characteristics'].get('trend_strength', 0)
                confidence = regime['confidence']
                leaders.append({
                    'symbol': symbol,
                    'name': self.SECTORS.get(symbol, symbol),
                    'regime': regime['primary_regime'],
                    'strength': strength,
                    'confidence': confidence,
                    'score': strength * confidence,
                    'category': self._categorize_sector(symbol)
                })

        # Sort by score
        leaders.sort(key=lambda x: x['score'], reverse=True)

        # Return top 3
        return leaders[:3]

    def _categorize_sector(self, symbol: str) -> str:
        """Categorize sector as cyclical/defensive/growth/value."""
        categories = []
        if symbol in self.CYCLICAL_SECTORS:
            categories.append('CYCLICAL')
        if symbol in self.DEFENSIVE_SECTORS:
            categories.append('DEFENSIVE')
        if symbol in self.GROWTH_SECTORS:
            categories.append('GROWTH')
        if symbol in self.VALUE_SECTORS:
            categories.append('VALUE')
        return '/'.join(categories) if categories else 'OTHER'

    def _detect_sector_divergences(self, sector_regimes: Dict) -> List[Dict]:
        """Detect significant sector divergences."""
        divergences = []

        # Tech vs Financials (Growth vs Value)
        xlk_regime = sector_regimes.get('XLK', {}).get('primary_regime', 'UNKNOWN')
        xlf_regime = sector_regimes.get('XLF', {}).get('primary_regime', 'UNKNOWN')

        if xlk_regime != xlf_regime:
            bullish = {'BULL_TRENDING', 'MOMENTUM', 'LOW_VOLATILITY'}
            bearish = {'BEAR_TRENDING', 'HIGH_VOLATILITY', 'CRISIS'}

            if (xlk_regime in bullish and xlf_regime in bearish) or \
               (xlk_regime in bearish and xlf_regime in bullish):
                divergences.append({
                    'type': 'GROWTH_VALUE_DIVERGENCE',
                    'description': f'Tech (XLK: {xlk_regime}) diverging from Financials (XLF: {xlf_regime})',
                    'severity': 'HIGH',
                    'sectors': ['XLK', 'XLF']
                })

        # Cyclical vs Defensive divergence
        cyclical_regimes = [
            sector_regimes.get(s, {}).get('primary_regime', 'UNKNOWN')
            for s in self.CYCLICAL_SECTORS
        ]
        defensive_regimes = [
            sector_regimes.get(s, {}).get('primary_regime', 'UNKNOWN')
            for s in self.DEFENSIVE_SECTORS
        ]

        bullish = {'BULL_TRENDING', 'MOMENTUM', 'LOW_VOLATILITY'}
        cyclical_bullish = sum(1 for r in cyclical_regimes if r in bullish)
        defensive_bullish = sum(1 for r in defensive_regimes if r in bullish)

        # Strong divergence if one is mostly bullish and other is mostly bearish
        if cyclical_bullish >= 4 and defensive_bullish == 0:
            divergences.append({
                'type': 'CYCLICAL_DEFENSIVE_DIVERGENCE',
                'description': 'Cyclicals bullish, defensives bearish (strong risk-on)',
                'severity': 'MEDIUM',
                'sectors': list(self.CYCLICAL_SECTORS) + list(self.DEFENSIVE_SECTORS)
            })
        elif defensive_bullish >= 2 and cyclical_bullish <= 1:
            divergences.append({
                'type': 'CYCLICAL_DEFENSIVE_DIVERGENCE',
                'description': 'Defensives bullish, cyclicals bearish (strong risk-off)',
                'severity': 'MEDIUM',
                'sectors': list(self.CYCLICAL_SECTORS) + list(self.DEFENSIVE_SECTORS)
            })

        return divergences

    def _determine_rotation_pattern(self, rotation_analysis: Dict) -> str:
        """
        Determine overall rotation pattern.

        Returns: Rotation pattern name
        """
        style = rotation_analysis['dominant_style']
        cyclical_str = rotation_analysis['cyclical_strength']
        defensive_str = rotation_analysis['defensive_strength']

        if style == 'RISK_ON_CYCLICAL':
            return 'RISK_ON_ROTATION'
        elif style == 'RISK_OFF_DEFENSIVE':
            return 'RISK_OFF_ROTATION'
        elif style == 'GROWTH_DOMINANCE':
            return 'GROWTH_ROTATION'
        elif style == 'VALUE_DOMINANCE':
            return 'VALUE_ROTATION'
        elif abs(cyclical_str - defensive_str) < 20:
            return 'BALANCED_ROTATION'
        else:
            return 'MIXED_ROTATION'

    def _calculate_risk_appetite(self, sector_regimes: Dict,
                                 rotation_analysis: Dict) -> float:
        """
        Calculate market risk appetite score (0-100).

        Higher score = more risk appetite (cyclicals leading)
        Lower score = less risk appetite (defensives leading)
        """
        score = 50.0  # Neutral baseline

        # Cyclical vs Defensive contribution (±25 points)
        cyclical_str = rotation_analysis['cyclical_strength']
        defensive_str = rotation_analysis['defensive_strength']
        score += (cyclical_str - defensive_str) * 0.25

        # Growth vs Value contribution (±15 points)
        growth_str = rotation_analysis['growth_strength']
        value_str = rotation_analysis['value_strength']
        score += (growth_str - value_str) * 0.15

        # High beta sector performance (±10 points)
        high_beta_sectors = {'XLK', 'XLY', 'XLE'}
        bullish_regimes = {'BULL_TRENDING', 'MOMENTUM', 'LOW_VOLATILITY'}
        high_beta_bullish = sum(
            1 for s in high_beta_sectors
            if sector_regimes.get(s, {}).get('primary_regime') in bullish_regimes
        )
        score += (high_beta_bullish / len(high_beta_sectors)) * 10

        return float(min(max(score, 0), 100))

    def _interpret_sector_regime(self, rotation_pattern: str,
                                 rotation_analysis: Dict,
                                 sector_leaders: List[Dict]) -> str:
        """Provide interpretation of sector regime."""
        pattern_interpretations = {
            'RISK_ON_ROTATION': 'Risk-on rotation: cyclicals outperforming',
            'RISK_OFF_ROTATION': 'Risk-off rotation: defensives outperforming',
            'GROWTH_ROTATION': 'Growth rotation: tech and growth sectors leading',
            'VALUE_ROTATION': 'Value rotation: financials and energy leading',
            'BALANCED_ROTATION': 'Balanced rotation across sectors',
            'MIXED_ROTATION': 'Mixed rotation, no clear pattern'
        }

        base = pattern_interpretations.get(rotation_pattern, 'Complex sector dynamics')

        if sector_leaders:
            leader_names = [l['name'] for l in sector_leaders[:2]]
            leaders_str = f"Led by {' and '.join(leader_names)}"
        else:
            leaders_str = "No clear leaders"

        style = rotation_analysis['dominant_style']

        return f"{base}. {leaders_str}. Style: {style}."


# Module-level function for convenience
_detector = SectorRegimeDetector()


def detect_sector_regime(lookback_days: int = 60) -> Dict:
    """Convenience function for sector regime detection."""
    return _detector.detect_sector_regime(lookback_days)
