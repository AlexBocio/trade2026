# industry_regime.py - Industry-Level Regime Detection
# Detects regimes for ~30 industry-specific ETFs

from datetime import datetime
from typing import Dict, List, Optional
import logging
from regime_detection import RegimeDetector

logger = logging.getLogger(__name__)


class IndustryRegimeDetector:
    """
    Detect regimes for industry-specific ETFs.

    Industries (representative subset):
    Technology: SMH (Semis), SKYY (Cloud), HACK (Cyber), FINX (Fintech)
    Healthcare: IBB (Biotech), XBI (Small Biotech), IHI (Devices)
    Energy: XOP (Oil & Gas), TAN (Solar), ICLN (Clean Energy)
    Financials: KRE (Regional Banks), KBE (Banks), IAI (Brokers)
    Consumer: XRT (Retail), XHB (Homebuilders), PBJ (Food & Bev)
    Industrials: XAR (Aerospace), ITA (Defense), PAVE (Infrastructure)
    Materials: PICK (Metals & Mining), COPX (Copper), SLV (Silver)
    Communication: SOCL (Social Media), NXTG (5G)
    Real Estate: MORT (REIT), HOMZ (Housing)
    Utilities: RNRG (Renewables)
    Other: ARKK (Innovation), ROBO (Robotics), BOTZ (AI/Robotics)
    """

    INDUSTRIES = {
        # Technology
        'SMH': {'name': 'Semiconductors', 'sector': 'XLK'},
        'SKYY': {'name': 'Cloud Computing', 'sector': 'XLK'},
        'HACK': {'name': 'Cybersecurity', 'sector': 'XLK'},
        'FINX': {'name': 'Fintech', 'sector': 'XLK'},

        # Healthcare
        'IBB': {'name': 'Biotech', 'sector': 'XLV'},
        'XBI': {'name': 'Small Cap Biotech', 'sector': 'XLV'},
        'IHI': {'name': 'Medical Devices', 'sector': 'XLV'},

        # Energy
        'XOP': {'name': 'Oil & Gas Exploration', 'sector': 'XLE'},
        'TAN': {'name': 'Solar Energy', 'sector': 'XLE'},
        'ICLN': {'name': 'Clean Energy', 'sector': 'XLE'},

        # Financials
        'KRE': {'name': 'Regional Banks', 'sector': 'XLF'},
        'KBE': {'name': 'Banks', 'sector': 'XLF'},

        # Consumer
        'XRT': {'name': 'Retail', 'sector': 'XLY'},
        'XHB': {'name': 'Homebuilders', 'sector': 'XLY'},

        # Industrials
        'XAR': {'name': 'Aerospace & Defense', 'sector': 'XLI'},
        'ITA': {'name': 'Defense', 'sector': 'XLI'},

        # Materials
        'PICK': {'name': 'Metals & Mining', 'sector': 'XLB'},

        # Thematic/Other
        'ARKK': {'name': 'Innovation', 'sector': 'XLK'},
        'ROBO': {'name': 'Robotics', 'sector': 'XLK'},
    }

    def __init__(self):
        self.regime_detector = RegimeDetector()

    def detect_industry_regime(self, lookback_days: int = 60,
                               symbols: Optional[List[str]] = None) -> Dict:
        """
        Detect industry-level regime.

        Args:
            lookback_days: Lookback period for regime detection
            symbols: Specific industry symbols to analyze (default: all)

        Returns:
            Industry regime dict
        """
        # Use specified symbols or default to all
        if symbols is None:
            symbols = list(self.INDUSTRIES.keys())

        # Detect regime for each industry
        industry_regimes = {}
        for symbol in symbols:
            try:
                regime = self.regime_detector.detect_regime(symbol, lookback_days)
                industry_info = self.INDUSTRIES.get(symbol, {'name': symbol, 'sector': 'UNKNOWN'})
                regime['industry_name'] = industry_info['name']
                regime['parent_sector'] = industry_info['sector']
                industry_regimes[symbol] = regime
            except Exception as e:
                logger.warning(f"Failed to detect regime for {symbol}: {e}")
                # Don't include failed symbols

        # Analyze industry strength
        industry_analysis = self._analyze_industry_strength(industry_regimes)

        # Identify emerging trends
        emerging_trends = self._identify_emerging_trends(industry_regimes)

        # Detect industry divergences
        divergences = self._detect_industry_divergences(industry_regimes)

        # Top performers
        top_performers = self._get_top_performers(industry_regimes, count=5)

        # Bottom performers
        bottom_performers = self._get_bottom_performers(industry_regimes, count=5)

        return {
            'timestamp': datetime.now().isoformat(),
            'industry_count': len(industry_regimes),

            'industry_analysis': industry_analysis,
            'emerging_trends': emerging_trends,
            'divergences': divergences,

            'top_performers': top_performers,
            'bottom_performers': bottom_performers,

            'industry_regimes': industry_regimes,
            'interpretation': self._interpret_industry_regime(
                industry_analysis, emerging_trends
            )
        }

    def _analyze_industry_strength(self, industry_regimes: Dict) -> Dict:
        """Analyze overall industry strength patterns."""
        bullish_regimes = {'BULL_TRENDING', 'MOMENTUM', 'LOW_VOLATILITY'}
        bearish_regimes = {'BEAR_TRENDING', 'HIGH_VOLATILITY', 'CRISIS'}

        # Group by sector
        sector_strength = {}
        for symbol, regime in industry_regimes.items():
            sector = regime.get('parent_sector', 'UNKNOWN')
            if sector not in sector_strength:
                sector_strength[sector] = {'bullish': 0, 'bearish': 0, 'total': 0}

            sector_strength[sector]['total'] += 1
            if regime['primary_regime'] in bullish_regimes:
                sector_strength[sector]['bullish'] += 1
            elif regime['primary_regime'] in bearish_regimes:
                sector_strength[sector]['bearish'] += 1

        # Calculate percentages
        for sector in sector_strength:
            total = sector_strength[sector]['total']
            if total > 0:
                sector_strength[sector]['bullish_pct'] = (
                    sector_strength[sector]['bullish'] / total * 100
                )
                sector_strength[sector]['bearish_pct'] = (
                    sector_strength[sector]['bearish'] / total * 100
                )

        # Overall statistics
        total_industries = len(industry_regimes)
        bullish_count = sum(
            1 for r in industry_regimes.values()
            if r['primary_regime'] in bullish_regimes
        )
        bearish_count = sum(
            1 for r in industry_regimes.values()
            if r['primary_regime'] in bearish_regimes
        )

        return {
            'total_industries': total_industries,
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'bullish_pct': (bullish_count / total_industries * 100) if total_industries > 0 else 0,
            'sector_breakdown': sector_strength
        }

    def _identify_emerging_trends(self, industry_regimes: Dict) -> List[Dict]:
        """Identify emerging industry trends."""
        trends = []

        # High momentum industries
        momentum_industries = []
        for symbol, regime in industry_regimes.items():
            if regime['primary_regime'] == 'MOMENTUM':
                strength = regime['characteristics'].get('trend_strength', 0)
                confidence = regime['confidence']
                momentum_industries.append({
                    'symbol': symbol,
                    'name': regime.get('industry_name', symbol),
                    'strength': strength,
                    'confidence': confidence,
                    'score': strength * confidence
                })

        momentum_industries.sort(key=lambda x: x['score'], reverse=True)
        if momentum_industries:
            top_momentum = momentum_industries[0]
            trends.append({
                'type': 'MOMENTUM_BREAKOUT',
                'description': f"{top_momentum['name']} ({top_momentum['symbol']}) showing strong momentum",
                'strength': top_momentum['strength'],
                'confidence': top_momentum['confidence']
            })

        # Defensive rotation (utilities, staples, healthcare gaining)
        defensive_industries = {'XBI', 'IBB', 'IHI'}  # Healthcare as proxy
        defensive_bullish = sum(
            1 for s in defensive_industries
            if s in industry_regimes and
            industry_regimes[s]['primary_regime'] in {'BULL_TRENDING', 'MOMENTUM', 'LOW_VOLATILITY'}
        )
        if defensive_bullish >= 2:
            trends.append({
                'type': 'DEFENSIVE_ROTATION',
                'description': 'Defensive industries showing strength',
                'strength': (defensive_bullish / len(defensive_industries)) * 10,
                'confidence': 0.7
            })

        # Green energy trend
        green_energy = {'TAN', 'ICLN'}
        green_bullish = sum(
            1 for s in green_energy
            if s in industry_regimes and
            industry_regimes[s]['primary_regime'] in {'BULL_TRENDING', 'MOMENTUM'}
        )
        if green_bullish >= 1:
            trends.append({
                'type': 'GREEN_ENERGY_ROTATION',
                'description': 'Clean energy industries gaining momentum',
                'strength': (green_bullish / len(green_energy)) * 10,
                'confidence': 0.6
            })

        # Innovation/tech trend
        innovation = {'ARKK', 'ROBO', 'HACK', 'SKYY'}
        innovation_bullish = sum(
            1 for s in innovation
            if s in industry_regimes and
            industry_regimes[s]['primary_regime'] in {'BULL_TRENDING', 'MOMENTUM'}
        )
        if innovation_bullish >= 3:
            trends.append({
                'type': 'INNOVATION_ROTATION',
                'description': 'Innovation/disruptive tech showing strength',
                'strength': (innovation_bullish / len(innovation)) * 10,
                'confidence': 0.8
            })

        return trends

    def _detect_industry_divergences(self, industry_regimes: Dict) -> List[Dict]:
        """Detect divergences within same sector."""
        divergences = []

        # Check for intra-sector divergences
        sector_groups = {}
        for symbol, regime in industry_regimes.items():
            sector = regime.get('parent_sector', 'UNKNOWN')
            if sector not in sector_groups:
                sector_groups[sector] = []
            sector_groups[sector].append((symbol, regime))

        for sector, industries in sector_groups.items():
            if len(industries) < 2:
                continue

            # Check for divergent regimes within sector
            bullish_regimes = {'BULL_TRENDING', 'MOMENTUM', 'LOW_VOLATILITY'}
            bearish_regimes = {'BEAR_TRENDING', 'HIGH_VOLATILITY', 'CRISIS'}

            bullish_industries = [
                s for s, r in industries
                if r['primary_regime'] in bullish_regimes
            ]
            bearish_industries = [
                s for s, r in industries
                if r['primary_regime'] in bearish_regimes
            ]

            # If we have both bullish and bearish in same sector
            if bullish_industries and bearish_industries:
                divergences.append({
                    'type': 'INTRA_SECTOR_DIVERGENCE',
                    'sector': sector,
                    'description': f'{sector} sector divergence: some industries bullish, others bearish',
                    'bullish_industries': bullish_industries,
                    'bearish_industries': bearish_industries,
                    'severity': 'MEDIUM'
                })

        # Specific divergences
        # Traditional energy vs Clean energy
        if 'XOP' in industry_regimes and 'ICLN' in industry_regimes:
            xop_regime = industry_regimes['XOP']['primary_regime']
            icln_regime = industry_regimes['ICLN']['primary_regime']
            if xop_regime != icln_regime:
                divergences.append({
                    'type': 'ENERGY_DIVERGENCE',
                    'description': f'Traditional energy (XOP: {xop_regime}) vs Clean energy (ICLN: {icln_regime})',
                    'severity': 'LOW'
                })

        return divergences

    def _get_top_performers(self, industry_regimes: Dict, count: int = 5) -> List[Dict]:
        """Get top performing industries."""
        performers = []

        for symbol, regime in industry_regimes.items():
            strength = regime['characteristics'].get('trend_strength', 0)
            confidence = regime['confidence']
            performers.append({
                'symbol': symbol,
                'name': regime.get('industry_name', symbol),
                'regime': regime['primary_regime'],
                'strength': strength,
                'confidence': confidence,
                'score': strength * confidence,
                'sector': regime.get('parent_sector', 'UNKNOWN')
            })

        performers.sort(key=lambda x: x['score'], reverse=True)
        return performers[:count]

    def _get_bottom_performers(self, industry_regimes: Dict, count: int = 5) -> List[Dict]:
        """Get bottom performing industries."""
        performers = []

        for symbol, regime in industry_regimes.items():
            strength = regime['characteristics'].get('trend_strength', 0)
            confidence = regime['confidence']
            performers.append({
                'symbol': symbol,
                'name': regime.get('industry_name', symbol),
                'regime': regime['primary_regime'],
                'strength': strength,
                'confidence': confidence,
                'score': strength * confidence,
                'sector': regime.get('parent_sector', 'UNKNOWN')
            })

        performers.sort(key=lambda x: x['score'])
        return performers[:count]

    def _interpret_industry_regime(self, industry_analysis: Dict,
                                   emerging_trends: List[Dict]) -> str:
        """Provide interpretation of industry regime."""
        bullish_pct = industry_analysis['bullish_pct']
        bearish_pct = industry_analysis.get('bearish_pct', 0)

        # Overall sentiment
        if bullish_pct > 60:
            sentiment = 'Broad strength across industries'
        elif bullish_pct > 40:
            sentiment = 'Mixed industry performance'
        elif bearish_pct > 60:
            sentiment = 'Broad weakness across industries'
        else:
            sentiment = 'Highly selective environment'

        # Emerging trends summary
        if emerging_trends:
            trend_types = [t['type'] for t in emerging_trends]
            if 'MOMENTUM_BREAKOUT' in trend_types:
                trend_str = 'Momentum breakouts detected'
            elif 'DEFENSIVE_ROTATION' in trend_types:
                trend_str = 'Defensive rotation underway'
            elif 'INNOVATION_ROTATION' in trend_types:
                trend_str = 'Innovation sectors gaining'
            else:
                trend_str = 'Sector rotation active'
        else:
            trend_str = 'No clear emerging trends'

        return f"{sentiment}. {trend_str}. {industry_analysis['bullish_count']} of {industry_analysis['total_industries']} industries bullish."


# Module-level function for convenience
_detector = IndustryRegimeDetector()


def detect_industry_regime(lookback_days: int = 60,
                           symbols: Optional[List[str]] = None) -> Dict:
    """Convenience function for industry regime detection."""
    return _detector.detect_industry_regime(lookback_days, symbols)
