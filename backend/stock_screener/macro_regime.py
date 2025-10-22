# macro_regime.py - Macro Economic Regime Detection
# Detects Fed policy, economic cycle, inflation, and geopolitical regimes

from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
import yfinance as yf
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class MacroRegimeDetector:
    """
    Detect macro economic regime.

    Components:
    1. Fed Policy Regime (TIGHTENING, EASING, NEUTRAL, PAUSE)
    2. Economic Cycle (EARLY_EXPANSION, LATE_EXPANSION, SLOWDOWN, RECESSION)
    3. Inflation Regime (LOW_INFLATION, MODERATE_INFLATION, HIGH_INFLATION, DEFLATION)
    4. Yield Curve Regime (STEEP, NORMAL, FLAT, INVERTED)
    5. Credit Regime (TIGHT, NORMAL, LOOSE)
    """

    # Fed funds rate thresholds
    FED_RATE_LOW = 2.0
    FED_RATE_MODERATE = 4.0
    FED_RATE_HIGH = 6.0

    # Inflation thresholds (CPI YoY %)
    INFLATION_LOW = 1.5
    INFLATION_TARGET = 2.0
    INFLATION_MODERATE = 3.0
    INFLATION_HIGH = 5.0

    # Yield curve thresholds (10Y - 2Y spread in bps)
    YC_INVERTED = -25
    YC_FLAT = 25
    YC_NORMAL = 100

    def __init__(self):
        self._cache = {}
        self._cache_time = None
        self._cache_duration = timedelta(hours=12)  # Cache macro data for 12 hours

    def detect_macro_regime(self, date: datetime = None) -> Dict:
        """
        Detect current macro regime.

        Args:
            date: Date to analyze (default: today)

        Returns:
            Macro regime dict
        """
        if date is None:
            date = datetime.now()

        # Use cached data if available and recent
        if self._cache_time and (datetime.now() - self._cache_time) < self._cache_duration:
            macro_data = self._cache
        else:
            macro_data = self._fetch_macro_data()
            self._cache = macro_data
            self._cache_time = datetime.now()

        # Detect individual regimes
        fed_regime = self._detect_fed_regime(macro_data)
        economic_regime = self._detect_economic_cycle(macro_data)
        inflation_regime = self._detect_inflation_regime(macro_data)
        yield_curve_regime = self._detect_yield_curve_regime(macro_data)
        credit_regime = self._detect_credit_regime(macro_data)

        # Calculate composite macro score
        macro_score = self._calculate_macro_score(
            fed_regime, economic_regime, inflation_regime,
            yield_curve_regime, credit_regime
        )

        # Determine overall macro regime
        overall_regime = self._determine_overall_regime(
            fed_regime, economic_regime, inflation_regime,
            yield_curve_regime, credit_regime
        )

        return {
            'date': date.strftime('%Y-%m-%d'),
            'overall_macro_regime': overall_regime,
            'macro_score': macro_score,  # -10 (crisis) to +10 (goldilocks)

            'fed_policy': fed_regime,
            'economic_cycle': economic_regime,
            'inflation_regime': inflation_regime,
            'yield_curve_regime': yield_curve_regime,
            'credit_regime': credit_regime,

            'macro_data': macro_data
        }

    def _fetch_macro_data(self) -> Dict:
        """
        Fetch macro economic data from market proxies.

        Since direct FRED API access requires setup, we use market ETFs as proxies:
        - TLT (20Y Treasury) for long-term rates
        - IEF (7-10Y Treasury) for medium-term rates
        - SHY (1-3Y Treasury) for short-term rates
        - HYG (High Yield Bonds) for credit spreads
        - TIP (TIPS) for inflation expectations
        - DXY via UUP (Dollar Index) for currency
        """
        try:
            # Fetch market data for macro proxies
            symbols = {
                'TLT': '20Y Treasury',
                'IEF': '10Y Treasury Proxy',
                'SHY': '2Y Treasury Proxy',
                'HYG': 'High Yield Credit',
                'LQD': 'Investment Grade Credit',
                'TIP': 'Inflation Protected',
                'UUP': 'Dollar Index'
            }

            data = {}
            for symbol, name in symbols.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='6mo')
                    if len(hist) > 0:
                        latest = hist['Close'].iloc[-1]
                        prev_month = hist['Close'].iloc[-22] if len(hist) > 22 else hist['Close'].iloc[0]
                        prev_3month = hist['Close'].iloc[-66] if len(hist) > 66 else hist['Close'].iloc[0]

                        data[symbol] = {
                            'price': float(latest),
                            '1m_return': float((latest / prev_month - 1) * 100),
                            '3m_return': float((latest / prev_3month - 1) * 100)
                        }
                except Exception as e:
                    logger.warning(f"Failed to fetch {symbol}: {e}")
                    data[symbol] = {'price': 0, '1m_return': 0, '3m_return': 0}

            # Calculate yield curve approximation
            # When rates rise, bond prices fall
            # TLT (long) vs SHY (short) spread indicates curve shape
            if 'TLT' in data and 'SHY' in data:
                # If TLT falls more than SHY, long rates rising faster = flattening
                # If TLT rises more than SHY, long rates falling faster = steepening
                yc_signal = data['SHY']['1m_return'] - data['TLT']['1m_return']
                data['yield_curve_signal'] = yc_signal
            else:
                data['yield_curve_signal'] = 0

            # Calculate credit spread approximation
            # HYG (high yield) vs LQD (investment grade) spread
            if 'HYG' in data and 'LQD' in data:
                # Widening spreads = HYG underperforms LQD
                credit_spread = data['LQD']['1m_return'] - data['HYG']['1m_return']
                data['credit_spread_signal'] = credit_spread
            else:
                data['credit_spread_signal'] = 0

            # Inflation expectations from TIP
            if 'TIP' in data:
                # Rising TIP = rising inflation expectations
                data['inflation_signal'] = data['TIP']['1m_return']
            else:
                data['inflation_signal'] = 0

            # Dollar strength
            if 'UUP' in data:
                data['dollar_strength'] = data['UUP']['1m_return']
            else:
                data['dollar_strength'] = 0

            return data

        except Exception as e:
            logger.error(f"Failed to fetch macro data: {e}")
            return {
                'yield_curve_signal': 0,
                'credit_spread_signal': 0,
                'inflation_signal': 0,
                'dollar_strength': 0
            }

    def _detect_fed_regime(self, macro_data: Dict) -> str:
        """
        Detect Fed policy regime based on rate direction.

        Returns: TIGHTENING | EASING | NEUTRAL | PAUSE
        """
        # Use short-term treasuries (SHY) as proxy for Fed policy
        # Falling SHY price = rising short rates = tightening
        # Rising SHY price = falling short rates = easing

        if 'SHY' not in macro_data:
            return 'NEUTRAL'

        shy_1m = macro_data['SHY']['1m_return']
        shy_3m = macro_data['SHY']['3m_return']

        # Tightening: short rates rising (SHY falling)
        if shy_1m < -1.5 and shy_3m < -3.0:
            return 'TIGHTENING'
        # Easing: short rates falling (SHY rising)
        elif shy_1m > 1.5 and shy_3m > 3.0:
            return 'EASING'
        # Pause: recent change different from 3-month trend
        elif abs(shy_1m) < 0.5:
            return 'PAUSE'
        else:
            return 'NEUTRAL'

    def _detect_economic_cycle(self, macro_data: Dict) -> str:
        """
        Detect economic cycle phase.

        Returns: EARLY_EXPANSION | LATE_EXPANSION | SLOWDOWN | RECESSION
        """
        # Use credit spreads and yield curve as proxies
        # - Tight credit + steepening curve = early expansion
        # - Tight credit + flattening curve = late expansion
        # - Widening credit + flat curve = slowdown
        # - Widening credit + inverted curve = recession

        credit_spread = macro_data.get('credit_spread_signal', 0)
        yc_signal = macro_data.get('yield_curve_signal', 0)

        credit_tight = credit_spread < -2.0
        credit_wide = credit_spread > 2.0
        curve_steepening = yc_signal < -2.0  # TLT outperforming SHY
        curve_flattening = yc_signal > 2.0   # SHY outperforming TLT

        if credit_tight and curve_steepening:
            return 'EARLY_EXPANSION'
        elif credit_tight and not curve_flattening:
            return 'LATE_EXPANSION'
        elif credit_wide and curve_flattening:
            return 'RECESSION'
        elif credit_wide or curve_flattening:
            return 'SLOWDOWN'
        else:
            return 'LATE_EXPANSION'

    def _detect_inflation_regime(self, macro_data: Dict) -> str:
        """
        Detect inflation regime.

        Returns: DEFLATION | LOW_INFLATION | MODERATE_INFLATION | HIGH_INFLATION
        """
        # Use TIP (inflation-protected bonds) as proxy
        # Rising TIP = rising inflation expectations

        inflation_signal = macro_data.get('inflation_signal', 0)

        if inflation_signal < -3.0:
            return 'DEFLATION'
        elif inflation_signal < 0:
            return 'LOW_INFLATION'
        elif inflation_signal < 3.0:
            return 'MODERATE_INFLATION'
        else:
            return 'HIGH_INFLATION'

    def _detect_yield_curve_regime(self, macro_data: Dict) -> str:
        """
        Detect yield curve regime.

        Returns: INVERTED | FLAT | NORMAL | STEEP
        """
        yc_signal = macro_data.get('yield_curve_signal', 0)

        # Positive signal = SHY outperforming TLT = curve flattening/inverting
        # Negative signal = TLT outperforming SHY = curve steepening

        if yc_signal > 5.0:
            return 'INVERTED'
        elif yc_signal > 2.0:
            return 'FLAT'
        elif yc_signal > -2.0:
            return 'NORMAL'
        else:
            return 'STEEP'

    def _detect_credit_regime(self, macro_data: Dict) -> str:
        """
        Detect credit regime.

        Returns: TIGHT | NORMAL | LOOSE
        """
        credit_spread = macro_data.get('credit_spread_signal', 0)

        if credit_spread > 3.0:
            return 'TIGHT'
        elif credit_spread < -3.0:
            return 'LOOSE'
        else:
            return 'NORMAL'

    def _calculate_macro_score(self, fed_regime: str, economic_regime: str,
                               inflation_regime: str, yc_regime: str,
                               credit_regime: str) -> float:
        """
        Calculate composite macro score (-10 to +10).

        Positive = supportive for equities
        Negative = headwinds for equities
        """
        score = 0.0

        # Fed policy contribution
        fed_scores = {
            'EASING': 4.0,
            'PAUSE': 2.0,
            'NEUTRAL': 0.0,
            'TIGHTENING': -3.0
        }
        score += fed_scores.get(fed_regime, 0)

        # Economic cycle contribution
        econ_scores = {
            'EARLY_EXPANSION': 3.0,
            'LATE_EXPANSION': 1.0,
            'SLOWDOWN': -2.0,
            'RECESSION': -4.0
        }
        score += econ_scores.get(economic_regime, 0)

        # Inflation contribution
        inflation_scores = {
            'LOW_INFLATION': 2.0,
            'MODERATE_INFLATION': 1.0,
            'HIGH_INFLATION': -2.0,
            'DEFLATION': -3.0
        }
        score += inflation_scores.get(inflation_regime, 0)

        # Yield curve contribution
        yc_scores = {
            'STEEP': 2.0,
            'NORMAL': 1.0,
            'FLAT': -1.0,
            'INVERTED': -3.0
        }
        score += yc_scores.get(yc_regime, 0)

        # Credit contribution
        credit_scores = {
            'LOOSE': 2.0,
            'NORMAL': 0.0,
            'TIGHT': -2.0
        }
        score += credit_scores.get(credit_regime, 0)

        # Clamp to [-10, 10]
        return max(-10.0, min(10.0, score))

    def _determine_overall_regime(self, fed_regime: str, economic_regime: str,
                                  inflation_regime: str, yc_regime: str,
                                  credit_regime: str) -> str:
        """
        Determine overall macro regime label.

        Returns: GOLDILOCKS | REFLATIONARY | STAGFLATION | DEFLATIONARY | CRISIS
        """
        # GOLDILOCKS: Growth + low inflation + accommodative Fed
        if (economic_regime in ['EARLY_EXPANSION', 'LATE_EXPANSION'] and
            inflation_regime in ['LOW_INFLATION', 'MODERATE_INFLATION'] and
            fed_regime in ['EASING', 'PAUSE', 'NEUTRAL']):
            return 'GOLDILOCKS'

        # REFLATIONARY: Recovery + rising inflation + easing Fed
        if (economic_regime == 'EARLY_EXPANSION' and
            inflation_regime in ['MODERATE_INFLATION', 'HIGH_INFLATION'] and
            fed_regime in ['EASING', 'NEUTRAL']):
            return 'REFLATIONARY'

        # STAGFLATION: Slowdown + high inflation
        if (economic_regime in ['SLOWDOWN', 'RECESSION'] and
            inflation_regime in ['HIGH_INFLATION', 'MODERATE_INFLATION']):
            return 'STAGFLATION'

        # DEFLATIONARY: Recession + deflation
        if (economic_regime == 'RECESSION' and
            inflation_regime in ['DEFLATION', 'LOW_INFLATION']):
            return 'DEFLATIONARY'

        # CRISIS: Inverted curve + wide spreads + recession
        if (yc_regime == 'INVERTED' and
            credit_regime == 'TIGHT' and
            economic_regime in ['RECESSION', 'SLOWDOWN']):
            return 'CRISIS'

        # Default: TRANSITIONAL
        return 'TRANSITIONAL'


# Module-level function for convenience
_detector = MacroRegimeDetector()


def detect_macro_regime(date: datetime = None) -> Dict:
    """Convenience function for macro regime detection."""
    return _detector.detect_macro_regime(date)
