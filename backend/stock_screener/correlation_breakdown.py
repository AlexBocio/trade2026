# correlation_breakdown.py - Stock-Sector Correlation Breakdown Detection
# Identifies when stocks decorrelate from their sector (potential breakout opportunities)

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from scipy.stats import pearsonr
import logging

logger = logging.getLogger(__name__)


class CorrelationBreakdownDetector:
    """
    Detects correlation breakdowns between stocks and their sectors.

    When a stock decorrelates from its sector while outperforming,
    it may signal a significant breakout opportunity.
    """

    TIMEFRAMES = {
        'short': 20,   # 20 days
        'medium': 60,  # 60 days
        'long': 120    # 120 days
    }

    SECTOR_ETFS = {
        'Technology': 'XLK',
        'Healthcare': 'XLV',
        'Financials': 'XLF',
        'Consumer Discretionary': 'XLY',
        'Communication Services': 'XLC',
        'Industrials': 'XLI',
        'Consumer Staples': 'XLP',
        'Energy': 'XLE',
        'Utilities': 'XLU',
        'Real Estate': 'XLRE',
        'Materials': 'XLB'
    }

    def __init__(self):
        pass

    def analyze_correlation_breakdown(self,
                                      symbol: str,
                                      sector: str = None,
                                      lookback_days: int = 120) -> Dict:
        """
        Analyze correlation breakdown between stock and sector.

        Args:
            symbol: Stock symbol
            sector: Sector name (auto-detected if None)
            lookback_days: Days of history to analyze

        Returns:
            Dict with correlation analysis results
        """
        try:
            # Determine sector ETF
            if sector is None:
                sector_etf = 'SPY'  # Default to market
                sector = 'Market'
            else:
                sector_etf = self.SECTOR_ETFS.get(sector, 'SPY')

            # Fetch price data
            stock_data, sector_data = self._fetch_correlation_data(
                symbol, sector_etf, lookback_days
            )

            if stock_data is None or sector_data is None:
                return self._default_result(symbol, sector)

            # Calculate multi-timeframe correlations
            correlations = self._calculate_timeframe_correlations(
                stock_data, sector_data
            )

            # Detect breakdown
            breakdown_detected, breakdown_strength = self._detect_breakdown(
                correlations
            )

            # Calculate relative performance
            relative_performance = self._calculate_relative_performance(
                stock_data, sector_data
            )

            # Determine breakdown type
            breakdown_type = self._classify_breakdown(
                correlations, relative_performance, breakdown_detected
            )

            # Calculate opportunity score
            opportunity_score = self._calculate_opportunity_score(
                breakdown_strength, relative_performance, correlations
            )

            return {
                'symbol': symbol,
                'sector': sector,
                'sector_etf': sector_etf,
                'breakdown_detected': breakdown_detected,
                'breakdown_type': breakdown_type,
                'breakdown_strength': breakdown_strength,
                'opportunity_score': opportunity_score,
                'correlations': correlations,
                'relative_performance': relative_performance,
                'analysis_date': datetime.now().isoformat(),
                'interpretation': self._generate_interpretation(
                    breakdown_detected, breakdown_type,
                    opportunity_score, relative_performance
                )
            }

        except Exception as e:
            logger.error(f"Error analyzing correlation breakdown for {symbol}: {e}")
            return self._default_result(symbol, sector or 'Unknown')

    def _fetch_correlation_data(self,
                                symbol: str,
                                sector_etf: str,
                                lookback_days: int) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """Fetch aligned price data for stock and sector."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days + 30)

            # Fetch stock data
            stock_ticker = yf.Ticker(symbol)
            stock_hist = stock_ticker.history(start=start_date, end=end_date)

            # Fetch sector data
            sector_ticker = yf.Ticker(sector_etf)
            sector_hist = sector_ticker.history(start=start_date, end=end_date)

            if len(stock_hist) < 20 or len(sector_hist) < 20:
                return None, None

            # Align dates
            common_dates = stock_hist.index.intersection(sector_hist.index)
            if len(common_dates) < 20:
                return None, None

            stock_aligned = stock_hist.loc[common_dates, 'Close']
            sector_aligned = sector_hist.loc[common_dates, 'Close']

            return stock_aligned, sector_aligned

        except Exception as e:
            logger.error(f"Error fetching correlation data: {e}")
            return None, None

    def _calculate_timeframe_correlations(self,
                                         stock_data: pd.Series,
                                         sector_data: pd.Series) -> Dict[str, float]:
        """Calculate rolling correlations across multiple timeframes."""
        correlations = {}

        # Calculate returns
        stock_returns = stock_data.pct_change().dropna()
        sector_returns = sector_data.pct_change().dropna()

        for timeframe, days in self.TIMEFRAMES.items():
            if len(stock_returns) >= days:
                # Use last N days
                stock_tf = stock_returns.tail(days)
                sector_tf = sector_returns.tail(days)

                if len(stock_tf) >= 10 and len(sector_tf) >= 10:
                    try:
                        corr, _ = pearsonr(stock_tf, sector_tf)
                        correlations[timeframe] = float(corr)
                    except:
                        correlations[timeframe] = 0.0
                else:
                    correlations[timeframe] = 0.0
            else:
                correlations[timeframe] = 0.0

        # Calculate full period correlation
        if len(stock_returns) >= 20 and len(sector_returns) >= 20:
            try:
                full_corr, _ = pearsonr(stock_returns, sector_returns)
                correlations['full_period'] = float(full_corr)
            except:
                correlations['full_period'] = 0.0
        else:
            correlations['full_period'] = 0.0

        return correlations

    def _detect_breakdown(self, correlations: Dict[str, float]) -> Tuple[bool, float]:
        """
        Detect if correlation breakdown is occurring.

        Breakdown occurs when:
        1. Short-term correlation drops significantly below long-term
        2. Short-term correlation is low (<0.5)

        Returns:
            (breakdown_detected: bool, strength: float 0-100)
        """
        short_corr = correlations.get('short', 0.5)
        medium_corr = correlations.get('medium', 0.5)
        long_corr = correlations.get('long', 0.5)

        # Calculate correlation drop
        corr_drop_medium = long_corr - medium_corr
        corr_drop_short = long_corr - short_corr

        # Breakdown detection criteria
        breakdown_detected = (
            short_corr < 0.5 and
            corr_drop_short > 0.3
        )

        # Calculate strength (0-100)
        if breakdown_detected:
            # Strength based on:
            # 1. How low the short-term correlation is
            # 2. How much it dropped from long-term
            low_corr_score = (0.8 - min(short_corr, 0.8)) / 0.8 * 50  # 0-50 points
            drop_score = min(corr_drop_short / 0.8, 1.0) * 50  # 0-50 points
            strength = low_corr_score + drop_score
        else:
            # Weak breakdown or no breakdown
            if corr_drop_short > 0.2:
                strength = min(corr_drop_short / 0.3 * 40, 40)  # Partial breakdown
            else:
                strength = 0.0

        return breakdown_detected, float(np.clip(strength, 0, 100))

    def _calculate_relative_performance(self,
                                       stock_data: pd.Series,
                                       sector_data: pd.Series) -> Dict[str, float]:
        """Calculate stock performance relative to sector."""
        performance = {}

        for timeframe, days in self.TIMEFRAMES.items():
            if len(stock_data) >= days and len(sector_data) >= days:
                stock_return = (stock_data.iloc[-1] / stock_data.iloc[-days] - 1) * 100
                sector_return = (sector_data.iloc[-1] / sector_data.iloc[-days] - 1) * 100

                performance[f'{timeframe}_stock'] = float(stock_return)
                performance[f'{timeframe}_sector'] = float(sector_return)
                performance[f'{timeframe}_relative'] = float(stock_return - sector_return)
            else:
                performance[f'{timeframe}_stock'] = 0.0
                performance[f'{timeframe}_sector'] = 0.0
                performance[f'{timeframe}_relative'] = 0.0

        return performance

    def _classify_breakdown(self,
                           correlations: Dict[str, float],
                           relative_performance: Dict[str, float],
                           breakdown_detected: bool) -> str:
        """
        Classify the type of breakdown.

        Types:
        - BULLISH_BREAKOUT: Decorrelation + outperformance (best signal)
        - BEARISH_BREAKDOWN: Decorrelation + underperformance
        - NEUTRAL_DIVERGENCE: Decorrelation + neutral performance
        - NO_BREAKDOWN: Normal correlation maintained
        """
        if not breakdown_detected:
            return 'NO_BREAKDOWN'

        short_relative = relative_performance.get('short_relative', 0)
        medium_relative = relative_performance.get('medium_relative', 0)

        # Average relative performance
        avg_relative = (short_relative + medium_relative) / 2

        if avg_relative > 5:
            return 'BULLISH_BREAKOUT'  # Decorrelating upward
        elif avg_relative < -5:
            return 'BEARISH_BREAKDOWN'  # Decorrelating downward
        else:
            return 'NEUTRAL_DIVERGENCE'  # Decorrelating sideways

    def _calculate_opportunity_score(self,
                                    breakdown_strength: float,
                                    relative_performance: Dict[str, float],
                                    correlations: Dict[str, float]) -> float:
        """
        Calculate opportunity score (0-100).

        High scores indicate strong bullish breakout opportunities.
        """
        short_relative = relative_performance.get('short_relative', 0)
        medium_relative = relative_performance.get('medium_relative', 0)

        # Score components
        breakdown_score = breakdown_strength * 0.4  # 40% weight

        # Relative performance score (0-40 points)
        avg_relative = (short_relative + medium_relative) / 2
        if avg_relative > 0:
            performance_score = min(avg_relative / 20 * 40, 40)  # Cap at 40
        else:
            performance_score = 0  # No points for underperformance

        # Momentum score (0-20 points)
        if short_relative > medium_relative:
            momentum_score = 20  # Accelerating outperformance
        elif short_relative > 0:
            momentum_score = 10  # Still outperforming but decelerating
        else:
            momentum_score = 0

        opportunity_score = breakdown_score + performance_score + momentum_score

        return float(np.clip(opportunity_score, 0, 100))

    def _generate_interpretation(self,
                                breakdown_detected: bool,
                                breakdown_type: str,
                                opportunity_score: float,
                                relative_performance: Dict[str, float]) -> str:
        """Generate human-readable interpretation."""
        if breakdown_type == 'BULLISH_BREAKOUT':
            short_rel = relative_performance.get('short_relative', 0)
            return (
                f"Strong bullish breakout detected. Stock is decorrelating from "
                f"sector while outperforming by {short_rel:.1f}% (20d). "
                f"Opportunity score: {opportunity_score:.0f}/100."
            )
        elif breakdown_type == 'BEARISH_BREAKDOWN':
            return (
                f"Bearish breakdown detected. Stock is decorrelating while "
                f"underperforming sector. Caution advised."
            )
        elif breakdown_type == 'NEUTRAL_DIVERGENCE':
            return (
                f"Neutral divergence from sector. Stock moving independently "
                f"but without clear directional edge."
            )
        else:
            short_corr = relative_performance.get('short_relative', 0)
            return (
                f"No significant breakdown detected. Stock maintains normal "
                f"correlation with sector. Relative performance: {short_corr:.1f}%."
            )

    def batch_analyze(self,
                     symbols: List[str],
                     sector_map: Dict[str, str] = None) -> List[Dict]:
        """Analyze correlation breakdown for multiple stocks."""
        results = []

        for symbol in symbols:
            sector = sector_map.get(symbol) if sector_map else None
            analysis = self.analyze_correlation_breakdown(symbol, sector)
            results.append(analysis)

        # Sort by opportunity score
        results.sort(key=lambda x: x['opportunity_score'], reverse=True)

        return results

    def find_breakout_opportunities(self,
                                   symbols: List[str],
                                   min_opportunity_score: float = 60.0,
                                   breakdown_type: str = 'BULLISH_BREAKOUT') -> List[Dict]:
        """
        Find stocks with high-probability breakout opportunities.

        Args:
            symbols: List of stock symbols to analyze
            min_opportunity_score: Minimum opportunity score (0-100)
            breakdown_type: Type of breakdown to filter for

        Returns:
            List of stocks meeting criteria, sorted by opportunity score
        """
        results = self.batch_analyze(symbols)

        # Filter by criteria
        opportunities = [
            r for r in results
            if r['opportunity_score'] >= min_opportunity_score
            and r['breakdown_type'] == breakdown_type
        ]

        return opportunities

    def _default_result(self, symbol: str, sector: str) -> Dict:
        """Return default result when analysis fails."""
        return {
            'symbol': symbol,
            'sector': sector,
            'sector_etf': 'SPY',
            'breakdown_detected': False,
            'breakdown_type': 'NO_BREAKDOWN',
            'breakdown_strength': 0.0,
            'opportunity_score': 0.0,
            'correlations': {
                'short': 0.0,
                'medium': 0.0,
                'long': 0.0,
                'full_period': 0.0
            },
            'relative_performance': {
                'short_stock': 0.0,
                'short_sector': 0.0,
                'short_relative': 0.0,
                'medium_stock': 0.0,
                'medium_sector': 0.0,
                'medium_relative': 0.0,
                'long_stock': 0.0,
                'long_sector': 0.0,
                'long_relative': 0.0
            },
            'analysis_date': datetime.now().isoformat(),
            'interpretation': 'Insufficient data for correlation analysis'
        }


# Module-level instance
_detector = CorrelationBreakdownDetector()


def analyze_correlation_breakdown(symbol: str, sector: str = None,
                                  lookback_days: int = 120) -> Dict:
    """Convenience function for correlation breakdown analysis."""
    return _detector.analyze_correlation_breakdown(symbol, sector, lookback_days)


def find_breakout_opportunities(symbols: List[str],
                               min_opportunity_score: float = 60.0) -> List[Dict]:
    """Convenience function to find breakout opportunities."""
    return _detector.find_breakout_opportunities(
        symbols, min_opportunity_score, 'BULLISH_BREAKOUT'
    )


def batch_correlation_analysis(symbols: List[str],
                               sector_map: Dict[str, str] = None) -> List[Dict]:
    """Convenience function for batch analysis."""
    return _detector.batch_analyze(symbols, sector_map)
