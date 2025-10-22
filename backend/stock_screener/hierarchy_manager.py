# hierarchy_manager.py - Hierarchical Regime Detection Manager
# Orchestrates all 7 layers of regime detection

from datetime import datetime
from typing import Dict, List, Optional
import logging
from regime_detection import RegimeDetector
from temporal_regime import detect_temporal_context
from macro_regime import detect_macro_regime
from cross_asset_regime import detect_cross_asset_regime
from market_regime import detect_market_regime
from sector_regime import detect_sector_regime
from industry_regime import detect_industry_regime

logger = logging.getLogger(__name__)


class HierarchyManager:
    """
    Manage hierarchical regime detection across 7 layers.

    Layer 0: Temporal/Calendar (seasonal patterns)
    Layer 1: Macro (Fed policy, economic cycle, inflation)
    Layer 2: Cross-Asset (bonds, commodities, currencies)
    Layer 3: Market (SPY, QQQ, IWM, DIA)
    Layer 4: Sector (11 SPDR sectors)
    Layer 5: Industry (30+ industry ETFs)
    Layer 6: Stock (individual stock using PROMPT 1)

    Analyzes:
    - Alignment across layers
    - Divergences between layers
    - Top-down vs bottom-up signals
    - Overall regime consensus
    """

    def __init__(self):
        self.regime_detector = RegimeDetector()

    def analyze_full_hierarchy(self, symbol: str = None,
                              lookback_days: int = 60) -> Dict:
        """
        Analyze full hierarchical regime.

        Args:
            symbol: Optional stock symbol for stock-level analysis
            lookback_days: Lookback period for regime detection

        Returns:
            Complete hierarchical analysis
        """
        logger.info(f"Analyzing full hierarchy for {symbol or 'market'}")

        # Layer 0: Temporal
        temporal = detect_temporal_context()

        # Layer 1: Macro
        macro = detect_macro_regime()

        # Layer 2: Cross-Asset
        cross_asset = detect_cross_asset_regime(lookback_days=30)

        # Layer 3: Market
        market = detect_market_regime(lookback_days)

        # Layer 4: Sector
        sector = detect_sector_regime(lookback_days)

        # Layer 5: Industry (sample of key industries)
        industry = detect_industry_regime(lookback_days)

        # Layer 6: Stock (if provided)
        stock_regime = None
        stock_sector = None
        if symbol:
            try:
                stock_regime = self.regime_detector.detect_regime(symbol, lookback_days)
                # Try to determine sector (simplified - in production use fundamentals API)
                stock_sector = self._infer_stock_sector(symbol)
            except Exception as e:
                logger.error(f"Failed to detect stock regime for {symbol}: {e}")

        # Calculate alignment scores
        alignment = self._calculate_alignment(
            temporal, macro, cross_asset, market, sector, industry, stock_regime
        )

        # Detect divergences
        divergences = self._detect_hierarchical_divergences(
            temporal, macro, cross_asset, market, sector, industry, stock_regime
        )

        # Overall assessment
        overall_regime = self._determine_overall_regime(
            macro, cross_asset, market, sector, alignment
        )

        # Risk assessment
        risk_assessment = self._assess_risk_environment(
            temporal, macro, cross_asset, market, sector, alignment
        )

        # Stock-specific assessment (if applicable)
        stock_assessment = None
        if symbol and stock_regime:
            stock_assessment = self._assess_stock_vs_hierarchy(
                symbol, stock_regime, stock_sector, market, sector, industry, alignment
            )

        return {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,

            'overall_regime': overall_regime,
            'risk_environment': risk_assessment,

            'alignment_scores': alignment,
            'divergences': divergences,

            'layers': {
                'layer_0_temporal': temporal,
                'layer_1_macro': macro,
                'layer_2_cross_asset': cross_asset,
                'layer_3_market': market,
                'layer_4_sector': sector,
                'layer_5_industry': industry,
                'layer_6_stock': stock_regime
            },

            'stock_assessment': stock_assessment,

            'interpretation': self._interpret_hierarchy(
                overall_regime, alignment, divergences, stock_assessment
            )
        }

    def analyze_stock_hierarchy(self, symbol: str, lookback_days: int = 60) -> Dict:
        """
        Analyze hierarchy specifically for a stock.

        Args:
            symbol: Stock symbol
            lookback_days: Lookback period

        Returns:
            Stock-focused hierarchical analysis
        """
        full_analysis = self.analyze_full_hierarchy(symbol, lookback_days)

        # Extract stock-relevant information
        stock_regime = full_analysis['layers']['layer_6_stock']
        market_regime = full_analysis['layers']['layer_3_market']
        sector_regime = full_analysis['layers']['layer_4_sector']
        alignment = full_analysis['alignment_scores']

        # Calculate stock-specific scores
        market_alignment_score = self._calculate_stock_market_alignment(
            stock_regime, market_regime
        )
        sector_alignment_score = self._calculate_stock_sector_alignment(
            stock_regime, sector_regime, full_analysis['stock_assessment']
        )

        # Trading signals
        trading_signals = self._generate_trading_signals(
            stock_regime, alignment, full_analysis['stock_assessment']
        )

        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),

            'stock_regime': stock_regime,
            'market_alignment': market_alignment_score,
            'sector_alignment': sector_alignment_score,

            'overall_alignment': alignment['overall_alignment_score'],
            'hierarchy_support': alignment['bullish_layers'] > alignment['bearish_layers'],

            'trading_signals': trading_signals,
            'stock_assessment': full_analysis['stock_assessment'],

            'summary': self._summarize_stock_position(
                symbol, stock_regime, alignment, trading_signals
            )
        }

    def _calculate_alignment(self, temporal: Dict, macro: Dict, cross_asset: Dict,
                            market: Dict, sector: Dict, industry: Dict,
                            stock_regime: Optional[Dict]) -> Dict:
        """Calculate alignment scores across hierarchy."""

        # Define bullish/bearish regime sets
        bullish_regimes = {'BULL_TRENDING', 'MOMENTUM', 'LOW_VOLATILITY', 'RISK_ON',
                          'GOLDILOCKS', 'REFLATIONARY', 'EARLY_EXPANSION', 'LATE_EXPANSION'}
        bearish_regimes = {'BEAR_TRENDING', 'HIGH_VOLATILITY', 'CRISIS', 'RISK_OFF',
                          'STAGFLATION', 'DEFLATIONARY', 'RECESSION', 'SLOWDOWN'}

        # Score each layer
        layer_scores = []

        # Layer 1: Macro (weight: 25%)
        macro_regime = macro.get('overall_macro_regime', 'TRANSITIONAL')
        macro_score = 1.0 if macro_regime in bullish_regimes else (-1.0 if macro_regime in bearish_regimes else 0.0)
        layer_scores.append(('macro', macro_score, 0.25))

        # Layer 2: Cross-Asset (weight: 20%)
        cross_asset_regime = cross_asset.get('cross_asset_regime', 'ROTATION')
        ca_score = 1.0 if cross_asset_regime in bullish_regimes else (-1.0 if cross_asset_regime in bearish_regimes else 0.0)
        layer_scores.append(('cross_asset', ca_score, 0.20))

        # Layer 3: Market (weight: 20%)
        market_regime = market.get('overall_market_regime', 'MIXED')
        mkt_score = 1.0 if market_regime in bullish_regimes else (-1.0 if market_regime in bearish_regimes else 0.0)
        layer_scores.append(('market', mkt_score, 0.20))

        # Layer 4: Sector (weight: 20%)
        sector_pattern = sector.get('rotation_pattern', 'MIXED_ROTATION')
        sec_score = 1.0 if 'RISK_ON' in sector_pattern or 'GROWTH' in sector_pattern else (
            -1.0 if 'RISK_OFF' in sector_pattern else 0.0
        )
        layer_scores.append(('sector', sec_score, 0.20))

        # Layer 5: Industry (weight: 15%)
        industry_analysis = industry.get('industry_analysis', {})
        ind_bullish_pct = industry_analysis.get('bullish_pct', 50)
        ind_score = (ind_bullish_pct - 50) / 50  # Convert to [-1, 1]
        layer_scores.append(('industry', ind_score, 0.15))

        # Calculate weighted alignment score
        weighted_sum = sum(score * weight for _, score, weight in layer_scores)
        alignment_score = (weighted_sum + 1) / 2 * 100  # Convert to [0, 100]

        # Count bullish/bearish layers
        bullish_layers = sum(1 for _, score, _ in layer_scores if score > 0.3)
        bearish_layers = sum(1 for _, score, _ in layer_scores if score < -0.3)
        neutral_layers = len(layer_scores) - bullish_layers - bearish_layers

        # Check stock alignment (if provided)
        stock_aligned = None
        if stock_regime:
            stock_regime_name = stock_regime.get('primary_regime', 'UNKNOWN')
            if stock_regime_name in bullish_regimes:
                stock_aligned = 'BULLISH' if bullish_layers > bearish_layers else 'DIVERGENT'
            elif stock_regime_name in bearish_regimes:
                stock_aligned = 'BEARISH' if bearish_layers > bullish_layers else 'DIVERGENT'
            else:
                stock_aligned = 'NEUTRAL'

        return {
            'overall_alignment_score': float(alignment_score),
            'alignment_category': self._categorize_alignment(alignment_score),
            'bullish_layers': bullish_layers,
            'bearish_layers': bearish_layers,
            'neutral_layers': neutral_layers,
            'layer_breakdown': {name: score for name, score, _ in layer_scores},
            'stock_alignment': stock_aligned
        }

    def _detect_hierarchical_divergences(self, temporal: Dict, macro: Dict,
                                        cross_asset: Dict, market: Dict,
                                        sector: Dict, industry: Dict,
                                        stock_regime: Optional[Dict]) -> List[Dict]:
        """Detect divergences across hierarchical layers."""
        divergences = []

        # Macro vs Market divergence
        macro_score = macro.get('macro_score', 0)
        market_health = market.get('market_health_score', 50)

        if macro_score > 5 and market_health < 40:
            divergences.append({
                'type': 'MACRO_MARKET_DIVERGENCE',
                'description': 'Macro environment supportive but market weak',
                'severity': 'HIGH',
                'layers': ['macro', 'market']
            })
        elif macro_score < -5 and market_health > 60:
            divergences.append({
                'type': 'MACRO_MARKET_DIVERGENCE',
                'description': 'Macro environment weak but market strong',
                'severity': 'HIGH',
                'layers': ['macro', 'market']
            })

        # Cross-asset vs Market divergence
        risk_sentiment = cross_asset.get('risk_sentiment', 0)
        market_breadth = market.get('market_breadth', {})
        regime_alignment = market_breadth.get('regime_alignment', 50)

        if risk_sentiment > 5 and regime_alignment < 40:
            divergences.append({
                'type': 'CROSS_ASSET_MARKET_DIVERGENCE',
                'description': 'Cross-asset signals bullish but market divergent',
                'severity': 'MEDIUM',
                'layers': ['cross_asset', 'market']
            })

        # Market vs Sector divergence
        market_regime = market.get('overall_market_regime', 'MIXED')
        sector_pattern = sector.get('rotation_pattern', 'MIXED_ROTATION')

        bullish_market = market_regime in {'BULL_TRENDING', 'MOMENTUM', 'MIXED_BULLISH'}
        bullish_sector = 'RISK_ON' in sector_pattern or 'GROWTH' in sector_pattern

        if bullish_market and not bullish_sector:
            divergences.append({
                'type': 'MARKET_SECTOR_DIVERGENCE',
                'description': 'Market bullish but sector rotation defensive',
                'severity': 'MEDIUM',
                'layers': ['market', 'sector']
            })

        # Sector vs Industry divergence
        risk_appetite = sector.get('risk_appetite_score', 50)
        industry_analysis = industry.get('industry_analysis', {})
        ind_bullish_pct = industry_analysis.get('bullish_pct', 50)

        if abs(risk_appetite - ind_bullish_pct) > 30:
            divergences.append({
                'type': 'SECTOR_INDUSTRY_DIVERGENCE',
                'description': 'Sector and industry signals diverging',
                'severity': 'LOW',
                'layers': ['sector', 'industry']
            })

        return divergences

    def _determine_overall_regime(self, macro: Dict, cross_asset: Dict,
                                  market: Dict, sector: Dict,
                                  alignment: Dict) -> str:
        """Determine overall hierarchical regime."""

        alignment_score = alignment['overall_alignment_score']
        bullish_layers = alignment['bullish_layers']
        bearish_layers = alignment['bearish_layers']

        # Strong alignment scenarios
        if alignment_score > 75 and bullish_layers >= 4:
            return 'STRONG_BULL_REGIME'
        elif alignment_score < 25 and bearish_layers >= 4:
            return 'STRONG_BEAR_REGIME'

        # Moderate alignment
        elif alignment_score > 60:
            return 'MODERATE_BULL_REGIME'
        elif alignment_score < 40:
            return 'MODERATE_BEAR_REGIME'

        # Mixed/divergent
        elif bullish_layers == bearish_layers:
            return 'NEUTRAL_MIXED_REGIME'
        else:
            return 'DIVERGENT_REGIME'

    def _assess_risk_environment(self, temporal: Dict, macro: Dict,
                                cross_asset: Dict, market: Dict,
                                sector: Dict, alignment: Dict) -> Dict:
        """Assess overall risk environment."""

        risk_factors = []
        risk_score = 50  # Neutral baseline (0=min risk, 100=max risk)

        # Macro risk
        macro_regime = macro.get('overall_macro_regime', 'TRANSITIONAL')
        if macro_regime in {'CRISIS', 'STAGFLATION', 'DEFLATIONARY'}:
            risk_score += 20
            risk_factors.append('Macro environment deteriorating')
        elif macro_regime in {'GOLDILOCKS', 'REFLATIONARY'}:
            risk_score -= 15

        # Market risk
        market_health = market.get('market_health_score', 50)
        risk_score += (50 - market_health) * 0.3

        # Volatility risk
        cross_asset_regime = cross_asset.get('cross_asset_regime', 'ROTATION')
        if cross_asset_regime == 'FLIGHT_TO_QUALITY':
            risk_score += 15
            risk_factors.append('Flight to quality underway')

        # Temporal risk (calendar effects)
        seasonal_regime = temporal.get('seasonal_regime', 'NEUTRAL')
        if seasonal_regime in {'HISTORICALLY_VOLATILE', 'SUMMER_DOLDRUMS'}:
            risk_score += 5
            risk_factors.append(f'Seasonal pattern: {seasonal_regime}')

        # Divergence risk
        if len(alignment.get('layer_breakdown', {})) > 0:
            layer_std = sum(abs(v) for v in alignment['layer_breakdown'].values()) / len(alignment['layer_breakdown'])
            if layer_std > 0.5:
                risk_score += 10
                risk_factors.append('High divergence across layers')

        # Clamp risk score
        risk_score = max(0, min(100, risk_score))

        # Categorize risk
        if risk_score < 30:
            risk_category = 'LOW_RISK'
        elif risk_score < 50:
            risk_category = 'MODERATE_LOW_RISK'
        elif risk_score < 70:
            risk_category = 'MODERATE_HIGH_RISK'
        else:
            risk_category = 'HIGH_RISK'

        return {
            'risk_score': float(risk_score),
            'risk_category': risk_category,
            'risk_factors': risk_factors
        }

    def _assess_stock_vs_hierarchy(self, symbol: str, stock_regime: Dict,
                                   stock_sector: Optional[str], market: Dict,
                                   sector: Dict, industry: Dict,
                                   alignment: Dict) -> Dict:
        """Assess how stock compares to hierarchy."""

        stock_regime_name = stock_regime['primary_regime']
        stock_confidence = stock_regime['confidence']
        stock_strength = stock_regime['characteristics'].get('trend_strength', 0)

        # Compare to market
        market_regime = market['overall_market_regime']
        market_aligned = self._regimes_aligned(stock_regime_name, market_regime)

        # Compare to sector (if known)
        sector_aligned = None
        if stock_sector and stock_sector in sector.get('sector_regimes', {}):
            sector_regime_name = sector['sector_regimes'][stock_sector]['primary_regime']
            sector_aligned = self._regimes_aligned(stock_regime_name, sector_regime_name)

        # Overall hierarchy alignment
        hierarchy_bullish = alignment['bullish_layers'] > alignment['bearish_layers']
        stock_bullish = stock_regime_name in {'BULL_TRENDING', 'MOMENTUM', 'LOW_VOLATILITY'}

        stock_vs_hierarchy = 'ALIGNED' if stock_bullish == hierarchy_bullish else 'DIVERGENT'

        # Relative strength
        if stock_strength > 7 and not hierarchy_bullish:
            relative_strength = 'OUTPERFORMING'
        elif stock_strength < 3 and hierarchy_bullish:
            relative_strength = 'UNDERPERFORMING'
        else:
            relative_strength = 'INLINE'

        return {
            'market_aligned': market_aligned,
            'sector_aligned': sector_aligned,
            'hierarchy_alignment': stock_vs_hierarchy,
            'relative_strength': relative_strength,
            'stock_confidence': stock_confidence,
            'stock_strength': stock_strength
        }

    def _regimes_aligned(self, regime1: str, regime2: str) -> bool:
        """Check if two regimes are aligned."""
        bullish = {'BULL_TRENDING', 'MOMENTUM', 'LOW_VOLATILITY', 'RISK_ON', 'GOLDILOCKS', 'REFLATIONARY'}
        bearish = {'BEAR_TRENDING', 'HIGH_VOLATILITY', 'CRISIS', 'RISK_OFF', 'STAGFLATION', 'DEFLATIONARY'}

        r1_bullish = regime1 in bullish
        r2_bullish = regime2 in bullish
        r1_bearish = regime1 in bearish
        r2_bearish = regime2 in bearish

        return (r1_bullish and r2_bullish) or (r1_bearish and r2_bearish)

    def _infer_stock_sector(self, symbol: str) -> Optional[str]:
        """Infer stock sector (simplified - in production use fundamentals API)."""
        # Simplified sector mapping (in production, use yfinance info or fundamentals API)
        # This is just for demonstration
        tech_stocks = {'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'META', 'TSLA', 'AMD', 'INTC'}
        finance_stocks = {'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C'}
        healthcare_stocks = {'JNJ', 'UNH', 'PFE', 'ABBV', 'LLY', 'MRK'}

        if symbol in tech_stocks:
            return 'XLK'
        elif symbol in finance_stocks:
            return 'XLF'
        elif symbol in healthcare_stocks:
            return 'XLV'
        else:
            return None

    def _categorize_alignment(self, score: float) -> str:
        """Categorize alignment score."""
        if score > 75:
            return 'STRONG_ALIGNMENT'
        elif score > 60:
            return 'MODERATE_ALIGNMENT'
        elif score > 40:
            return 'WEAK_ALIGNMENT'
        else:
            return 'DIVERGENT'

    def _calculate_stock_market_alignment(self, stock_regime: Dict,
                                         market_regime: Dict) -> float:
        """Calculate stock-market alignment score."""
        if not stock_regime:
            return 50.0

        stock_name = stock_regime['primary_regime']
        market_name = market_regime['overall_market_regime']

        if self._regimes_aligned(stock_name, market_name):
            return 80.0
        else:
            return 20.0

    def _calculate_stock_sector_alignment(self, stock_regime: Dict,
                                         sector_regime: Dict,
                                         stock_assessment: Optional[Dict]) -> float:
        """Calculate stock-sector alignment score."""
        if not stock_assessment or stock_assessment.get('sector_aligned') is None:
            return 50.0

        return 80.0 if stock_assessment['sector_aligned'] else 20.0

    def _generate_trading_signals(self, stock_regime: Dict, alignment: Dict,
                                  stock_assessment: Optional[Dict]) -> Dict:
        """Generate trading signals based on hierarchical analysis."""
        signals = {
            'primary_signal': 'NEUTRAL',
            'conviction': 'LOW',
            'supporting_factors': [],
            'risk_factors': []
        }

        if not stock_regime:
            return signals

        stock_name = stock_regime['primary_regime']
        stock_confidence = stock_regime['confidence']
        alignment_score = alignment['overall_alignment_score']

        # Bullish signals
        bullish_regimes = {'BULL_TRENDING', 'MOMENTUM', 'LOW_VOLATILITY'}
        if stock_name in bullish_regimes:
            if alignment_score > 70 and stock_confidence > 0.7:
                signals['primary_signal'] = 'STRONG_BUY'
                signals['conviction'] = 'HIGH'
                signals['supporting_factors'].append('Stock and hierarchy aligned bullish')
            elif alignment_score > 60:
                signals['primary_signal'] = 'BUY'
                signals['conviction'] = 'MEDIUM'
                signals['supporting_factors'].append('Stock bullish with moderate hierarchy support')
            else:
                signals['primary_signal'] = 'HOLD'
                signals['conviction'] = 'LOW'
                signals['risk_factors'].append('Stock bullish but hierarchy divergent')

        # Bearish signals
        bearish_regimes = {'BEAR_TRENDING', 'HIGH_VOLATILITY', 'CRISIS'}
        if stock_name in bearish_regimes:
            if alignment_score < 30 and stock_confidence > 0.7:
                signals['primary_signal'] = 'STRONG_SELL'
                signals['conviction'] = 'HIGH'
                signals['supporting_factors'].append('Stock and hierarchy aligned bearish')
            elif alignment_score < 40:
                signals['primary_signal'] = 'SELL'
                signals['conviction'] = 'MEDIUM'
                signals['supporting_factors'].append('Stock bearish with hierarchy confirmation')
            else:
                signals['primary_signal'] = 'HOLD'
                signals['conviction'] = 'LOW'
                signals['risk_factors'].append('Stock bearish but hierarchy divergent')

        # Check for divergence opportunities
        if stock_assessment:
            if stock_assessment.get('relative_strength') == 'OUTPERFORMING':
                signals['supporting_factors'].append('Stock outperforming despite weak market')
            elif stock_assessment.get('relative_strength') == 'UNDERPERFORMING':
                signals['risk_factors'].append('Stock underperforming despite strong market')

        return signals

    def _summarize_stock_position(self, symbol: str, stock_regime: Dict,
                                  alignment: Dict, trading_signals: Dict) -> str:
        """Summarize stock position in hierarchy."""
        regime = stock_regime['primary_regime']
        confidence = stock_regime['confidence']
        signal = trading_signals['primary_signal']
        conviction = trading_signals['conviction']
        alignment_score = alignment['overall_alignment_score']

        return (f"{symbol} in {regime} regime (confidence: {confidence:.2f}). "
                f"Hierarchy alignment: {alignment_score:.0f}%. "
                f"Signal: {signal} ({conviction} conviction).")

    def _interpret_hierarchy(self, overall_regime: str, alignment: Dict,
                            divergences: List[Dict], stock_assessment: Optional[Dict]) -> str:
        """Provide interpretation of hierarchical analysis."""

        regime_interpretations = {
            'STRONG_BULL_REGIME': 'Strong bullish alignment across all layers - favorable environment',
            'MODERATE_BULL_REGIME': 'Moderate bullish bias - selective opportunities',
            'NEUTRAL_MIXED_REGIME': 'Neutral/mixed environment - stock-specific approach',
            'MODERATE_BEAR_REGIME': 'Moderate bearish bias - defensive positioning',
            'STRONG_BEAR_REGIME': 'Strong bearish alignment - risk-off environment',
            'DIVERGENT_REGIME': 'Significant divergences across layers - complex environment'
        }

        base = regime_interpretations.get(overall_regime, 'Complex market environment')

        alignment_score = alignment['overall_alignment_score']
        alignment_str = f"Alignment: {alignment_score:.0f}%"

        if divergences:
            div_count = len(divergences)
            div_str = f"{div_count} divergence{'s' if div_count > 1 else ''} detected"
        else:
            div_str = "No major divergences"

        if stock_assessment:
            stock_str = f"Stock {stock_assessment['hierarchy_alignment'].lower()} with hierarchy"
        else:
            stock_str = ""

        return f"{base}. {alignment_str}. {div_str}. {stock_str}".strip()


# Module-level function for convenience
_manager = HierarchyManager()


def analyze_full_hierarchy(symbol: str = None, lookback_days: int = 60) -> Dict:
    """Convenience function for full hierarchy analysis."""
    return _manager.analyze_full_hierarchy(symbol, lookback_days)


def analyze_stock_hierarchy(symbol: str, lookback_days: int = 60) -> Dict:
    """Convenience function for stock-focused hierarchy analysis."""
    return _manager.analyze_stock_hierarchy(symbol, lookback_days)
