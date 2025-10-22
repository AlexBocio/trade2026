# smart_money.py - Smart Money Tracker
# Detects institutional accumulation via dark pool, options flow, and insider buying

from typing import Dict, List, Optional
import numpy as np
from datetime import datetime, timedelta
import logging
from data_providers import get_provider

logger = logging.getLogger(__name__)


class SmartMoneyTracker:
    """
    Tracks smart money (institutional) activity.

    Signals:
    1. Dark Pool Accumulation - Large block trades off-exchange
    2. Unusual Options Flow - Big premium bets on calls
    3. Insider Buying - Corporate insiders buying stock
    4. Aggregate Score - Combined confidence of institutional interest
    """

    def __init__(self, mock_mode: bool = False):
        self.data_provider = get_provider(mock_mode=mock_mode)

    def track_smart_money(self,
                         symbol: str,
                         lookback_days: int = 30) -> Dict:
        """
        Track smart money activity for a symbol.

        Args:
            symbol: Stock symbol
            lookback_days: Days of history to analyze

        Returns:
            {
                'symbol': str,
                'smart_money_detected': bool,
                'aggregate_score': float (0-100),
                'dark_pool_score': float (0-100),
                'options_flow_score': float (0-100),
                'insider_score': float (0-100),
                'confidence': float (0-100),
                'signals': List[str],
                'interpretation': str
            }
        """
        try:
            # Track dark pool activity
            dark_pool_data = self._analyze_dark_pool(symbol, lookback_days)

            # Track options flow
            options_data = self._analyze_options_flow(symbol)

            # Track insider activity
            insider_data = self._analyze_insider_activity(symbol, lookback_days)

            # Calculate component scores
            dark_pool_score = dark_pool_data['score']
            options_score = options_data['score']
            insider_score = insider_data['score']

            # Calculate aggregate score
            aggregate_score = self._calculate_aggregate_score(
                dark_pool_score,
                options_score,
                insider_score
            )

            # Determine if smart money detected
            smart_money_detected = aggregate_score >= 60.0

            # Generate signals
            signals = []
            if dark_pool_score >= 60:
                signals.append(dark_pool_data['signal'])
            if options_score >= 60:
                signals.append(options_data['signal'])
            if insider_score >= 60:
                signals.append(insider_data['signal'])

            # Calculate confidence
            confidence = self._calculate_confidence(
                dark_pool_data, options_data, insider_data
            )

            return {
                'symbol': symbol,
                'smart_money_detected': smart_money_detected,
                'aggregate_score': aggregate_score,
                'dark_pool_score': dark_pool_score,
                'options_flow_score': options_score,
                'insider_score': insider_score,
                'confidence': confidence,
                'signals': signals,
                'dark_pool_details': dark_pool_data['details'],
                'options_details': options_data['details'],
                'insider_details': insider_data['details'],
                'analysis_date': datetime.now().isoformat(),
                'interpretation': self._generate_interpretation(
                    smart_money_detected, aggregate_score, signals, confidence
                )
            }

        except Exception as e:
            logger.error(f"Error tracking smart money for {symbol}: {e}")
            return self._default_result(symbol)

    def _analyze_dark_pool(self, symbol: str, lookback_days: int) -> Dict:
        """
        Analyze dark pool activity.

        High score indicates:
        - High dark pool volume relative to total volume
        - Large average trade sizes (institutional blocks)
        - Bullish sentiment from dark pool trades
        """
        try:
            dark_pool_data = self.data_provider.get_dark_pool_trades(symbol, lookback_days)

            if dark_pool_data is None:
                return {
                    'score': 0.0,
                    'signal': '',
                    'details': {'available': False}
                }

            dark_pool_pct = dark_pool_data['dark_pool_pct']
            sentiment = dark_pool_data['sentiment']
            avg_trade_size = dark_pool_data['avg_trade_size']

            # Score calculation
            score = 0.0

            # Component 1: Dark pool percentage (0-40 points)
            # 30%+ dark pool = high institutional activity
            if dark_pool_pct >= 40:
                pct_score = 40
            elif dark_pool_pct >= 30:
                pct_score = 30 + (dark_pool_pct - 30) * 1.0
            elif dark_pool_pct >= 20:
                pct_score = 20 + (dark_pool_pct - 20) * 1.0
            else:
                pct_score = dark_pool_pct * 1.0

            # Component 2: Average trade size (0-30 points)
            # Larger trades = institutional
            if avg_trade_size >= 50000:
                size_score = 30
            elif avg_trade_size >= 10000:
                size_score = 15 + (avg_trade_size - 10000) / 40000 * 15
            else:
                size_score = avg_trade_size / 10000 * 15

            # Component 3: Sentiment (0-30 points)
            if sentiment == 'bullish':
                sentiment_score = 30
            elif sentiment == 'neutral':
                sentiment_score = 15
            else:
                sentiment_score = 0

            score = pct_score + size_score + sentiment_score

            signal = f"Dark Pool: {dark_pool_pct:.1f}% of volume, {sentiment} sentiment"

            return {
                'score': float(np.clip(score, 0, 100)),
                'signal': signal,
                'details': {
                    'available': True,
                    'dark_pool_pct': dark_pool_pct,
                    'avg_trade_size': avg_trade_size,
                    'sentiment': sentiment,
                    'total_volume': dark_pool_data['total_volume'],
                    'dark_pool_volume': dark_pool_data['dark_pool_volume']
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing dark pool for {symbol}: {e}")
            return {'score': 0.0, 'signal': '', 'details': {'available': False}}

    def _analyze_options_flow(self, symbol: str) -> Dict:
        """
        Analyze unusual options flow.

        High score indicates:
        - Unusual call volume (bullish bets)
        - Large premium trades (big money)
        - High volume/OI ratio (new positions)
        """
        try:
            options_data = self.data_provider.get_unusual_options_activity(symbol)

            if options_data is None:
                return {
                    'score': 0.0,
                    'signal': '',
                    'details': {'available': False}
                }

            sentiment = options_data['aggregate_sentiment']
            total_premium = options_data['total_premium']
            unusual_calls = options_data['unusual_calls']
            unusual_puts = options_data['unusual_puts']

            # Score calculation
            score = 0.0

            # Component 1: Sentiment (0-40 points)
            if sentiment == 'bullish':
                sentiment_score = 40
            elif sentiment == 'neutral':
                sentiment_score = 20
            else:
                sentiment_score = 0

            # Component 2: Total premium (0-40 points)
            # $1M+ = significant smart money
            if total_premium >= 5000000:
                premium_score = 40
            elif total_premium >= 1000000:
                premium_score = 20 + (total_premium - 1000000) / 4000000 * 20
            elif total_premium >= 100000:
                premium_score = 10 + (total_premium - 100000) / 900000 * 10
            else:
                premium_score = total_premium / 100000 * 10

            # Component 3: Number of unusual trades (0-20 points)
            num_unusual = len(unusual_calls) + len(unusual_puts)
            unusual_score = min(num_unusual * 5, 20)

            score = sentiment_score + premium_score + unusual_score

            signal = f"Options Flow: {sentiment}, ${total_premium/1000000:.2f}M premium"

            return {
                'score': float(np.clip(score, 0, 100)),
                'signal': signal,
                'details': {
                    'available': True,
                    'sentiment': sentiment,
                    'total_premium': total_premium,
                    'unusual_calls_count': len(unusual_calls),
                    'unusual_puts_count': len(unusual_puts),
                    'top_call': unusual_calls[0] if unusual_calls else None,
                    'top_put': unusual_puts[0] if unusual_puts else None
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing options flow for {symbol}: {e}")
            return {'score': 0.0, 'signal': '', 'details': {'available': False}}

    def _analyze_insider_activity(self, symbol: str, lookback_days: int) -> Dict:
        """
        Analyze insider buying activity.

        High score indicates:
        - Net insider buying (more buys than sells)
        - Large transaction values
        - Multiple insiders buying
        """
        try:
            insider_data = self.data_provider.get_insider_transactions(symbol, lookback_days)

            if insider_data is None:
                return {
                    'score': 0.0,
                    'signal': '',
                    'details': {'available': False}
                }

            sentiment = insider_data['insider_sentiment']
            net_buying = insider_data['net_buying']
            net_value = insider_data['net_value']
            transactions = insider_data['transactions']

            # Score calculation
            score = 0.0

            # Component 1: Sentiment (0-40 points)
            if sentiment == 'bullish':
                sentiment_score = 40
            elif sentiment == 'neutral':
                sentiment_score = 20
            else:
                sentiment_score = 0

            # Component 2: Net value (0-40 points)
            # $1M+ net buying = strong signal
            if net_value >= 5000000:
                value_score = 40
            elif net_value >= 1000000:
                value_score = 20 + (net_value - 1000000) / 4000000 * 20
            elif net_value >= 100000:
                value_score = 10 + (net_value - 100000) / 900000 * 10
            elif net_value > 0:
                value_score = net_value / 100000 * 10
            else:
                value_score = 0

            # Component 3: Number of buying transactions (0-20 points)
            buy_count = sum(1 for t in transactions if 'Purchase' in t['type'] or 'Buy' in t['type'])
            buy_score = min(buy_count * 5, 20)

            score = sentiment_score + value_score + buy_score

            signal = f"Insider Activity: {sentiment}, ${abs(net_value)/1000000:.2f}M net"

            return {
                'score': float(np.clip(score, 0, 100)),
                'signal': signal,
                'details': {
                    'available': True,
                    'sentiment': sentiment,
                    'net_buying_shares': net_buying,
                    'net_value': net_value,
                    'transaction_count': len(transactions),
                    'recent_transactions': transactions[:5]
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing insider activity for {symbol}: {e}")
            return {'score': 0.0, 'signal': '', 'details': {'available': False}}

    def _calculate_aggregate_score(self,
                                   dark_pool: float,
                                   options: float,
                                   insider: float) -> float:
        """
        Calculate aggregate smart money score (0-100).

        Weights:
        - Dark pool: 35%
        - Options flow: 35%
        - Insider activity: 30%
        """
        aggregate = (
            dark_pool * 0.35 +
            options * 0.35 +
            insider * 0.30
        )

        return float(np.clip(aggregate, 0, 100))

    def _calculate_confidence(self,
                             dark_pool_data: Dict,
                             options_data: Dict,
                             insider_data: Dict) -> float:
        """
        Calculate confidence score (0-100).

        Higher confidence when multiple signals confirm.
        """
        signals_available = sum([
            dark_pool_data['details'].get('available', False),
            options_data['details'].get('available', False),
            insider_data['details'].get('available', False)
        ])

        signals_strong = sum([
            dark_pool_data['score'] >= 60,
            options_data['score'] >= 60,
            insider_data['score'] >= 60
        ])

        if signals_available == 0:
            return 0.0

        # Base confidence from data availability
        base_confidence = (signals_available / 3) * 40

        # Boost from strong signals
        signal_boost = (signals_strong / max(signals_available, 1)) * 60

        confidence = base_confidence + signal_boost

        return float(np.clip(confidence, 0, 100))

    def _generate_interpretation(self,
                                detected: bool,
                                score: float,
                                signals: List[str],
                                confidence: float) -> str:
        """Generate human-readable interpretation."""
        if detected:
            signal_str = '; '.join(signals) if signals else 'Multiple indicators'
            return (f"Smart money activity detected (score: {score:.0f}/100, "
                   f"confidence: {confidence:.0f}%). {signal_str}. "
                   "Institutional accumulation likely underway.")
        else:
            return (f"No significant smart money activity (score: {score:.0f}/100). "
                   "Limited institutional interest detected.")

    def batch_analyze(self, symbols: List[str], lookback_days: int = 30) -> List[Dict]:
        """
        Analyze multiple symbols for smart money activity.

        Args:
            symbols: List of stock symbols
            lookback_days: Days of history to analyze

        Returns:
            List of smart money analyses, sorted by aggregate score
        """
        results = []

        for symbol in symbols:
            analysis = self.track_smart_money(symbol, lookback_days)
            results.append(analysis)

        # Sort by aggregate score
        results.sort(key=lambda x: x['aggregate_score'], reverse=True)

        return results

    def find_accumulation_opportunities(self,
                                       symbols: List[str],
                                       min_score: float = 60.0,
                                       min_confidence: float = 50.0) -> List[Dict]:
        """
        Find stocks with strong smart money accumulation.

        Args:
            symbols: List of stock symbols
            min_score: Minimum aggregate score (0-100)
            min_confidence: Minimum confidence (0-100)

        Returns:
            List of stocks with smart money detected
        """
        results = self.batch_analyze(symbols)

        opportunities = [
            r for r in results
            if r['smart_money_detected']
            and r['aggregate_score'] >= min_score
            and r['confidence'] >= min_confidence
        ]

        return opportunities

    def _default_result(self, symbol: str) -> Dict:
        """Return default result when analysis fails."""
        return {
            'symbol': symbol,
            'smart_money_detected': False,
            'aggregate_score': 0.0,
            'dark_pool_score': 0.0,
            'options_flow_score': 0.0,
            'insider_score': 0.0,
            'confidence': 0.0,
            'signals': [],
            'dark_pool_details': {'available': False},
            'options_details': {'available': False},
            'insider_details': {'available': False},
            'analysis_date': datetime.now().isoformat(),
            'interpretation': 'Insufficient data for smart money analysis'
        }


# Module-level instance
_tracker = SmartMoneyTracker()


def track_smart_money(symbol: str, lookback_days: int = 30) -> Dict:
    """Convenience function for smart money tracking."""
    return _tracker.track_smart_money(symbol, lookback_days)


def find_smart_money_plays(symbols: List[str],
                           min_score: float = 60.0,
                           min_confidence: float = 50.0) -> List[Dict]:
    """Convenience function to find smart money opportunities."""
    return _tracker.find_accumulation_opportunities(symbols, min_score, min_confidence)
