# catalyst_calendar.py - Catalyst Setup Scanner
# Scores stocks with upcoming catalysts

from typing import Dict, List
import numpy as np
from datetime import datetime
import logging
from event_calendar import EventCalendar
import yfinance as yf
import sys
sys.path.append('.')
from liquidity_vacuum import LiquidityVacuumDetector

logger = logging.getLogger(__name__)


class CatalystScanner:
    """Scans for catalyst setups - stocks with catalysts + favorable technical setup."""

    def __init__(self, mock_mode: bool = False):
        self.event_calendar = EventCalendar(mock_mode=mock_mode)
        self.vacuum_detector = LiquidityVacuumDetector(mock_mode=mock_mode)

    def scan_catalyst_setup(self, symbol: str) -> Dict:
        """
        Score catalyst setup for a symbol.

        Returns:
            {
                'symbol': str,
                'setup_detected': bool,
                'setup_score': float (0-100),
                'catalyst_score': float,
                'technical_score': float,
                'days_to_catalyst': int,
                'catalyst_type': str,
                'interpretation': str
            }
        """
        try:
            # Get upcoming events
            events = self.event_calendar.get_upcoming_events(symbol, days_ahead=60)

            # Get technical setup (liquidity vacuum)
            vacuum = self.vacuum_detector.detect_vacuum(symbol, catalyst_date=events.get('earnings_date'))

            # Calculate scores
            catalyst_score = self._score_catalyst(events)
            technical_score = vacuum['vacuum_strength']

            # Combined setup score
            setup_score = (catalyst_score * 0.4 + technical_score * 0.6)

            setup_detected = setup_score >= 60.0

            return {
                'symbol': symbol,
                'setup_detected': setup_detected,
                'setup_score': setup_score,
                'catalyst_score': catalyst_score,
                'technical_score': technical_score,
                'days_to_catalyst': events['days_to_next_catalyst'],
                'catalyst_type': events['next_catalyst_type'],
                'earnings_date': events['earnings_date'],
                'analysis_date': datetime.now().isoformat(),
                'interpretation': self._generate_interpretation(
                    setup_detected, setup_score, events, vacuum
                )
            }

        except Exception as e:
            logger.error(f"Error scanning catalyst setup for {symbol}: {e}")
            return self._default_result(symbol)

    def _score_catalyst(self, events: Dict) -> float:
        """Score catalyst timing (0-100)."""
        if not events['has_upcoming_catalyst']:
            return 0.0

        days = events['days_to_next_catalyst']

        # Optimal: 7-30 days before catalyst
        if 7 <= days <= 30:
            return 100.0
        elif 3 <= days < 7:
            return 70.0
        elif 30 < days <= 60:
            return 50.0
        else:
            return 20.0

    def _generate_interpretation(self, detected: bool, score: float, events: Dict, vacuum: Dict) -> str:
        """Generate interpretation."""
        if detected:
            return (f"Catalyst setup detected (score: {score:.0f}/100). "
                   f"{events['next_catalyst_type']} in {events['days_to_next_catalyst']} days. "
                   f"Technical setup: {vacuum['vacuum_strength']:.0f}/100.")
        return f"No significant setup (score: {score:.0f}/100)."

    def batch_scan(self, symbols: List[str]) -> List[Dict]:
        """Scan multiple symbols."""
        results = []
        for symbol in symbols:
            results.append(self.scan_catalyst_setup(symbol))
        results.sort(key=lambda x: x['setup_score'], reverse=True)
        return results

    def _default_result(self, symbol: str) -> Dict:
        return {
            'symbol': symbol,
            'setup_detected': False,
            'setup_score': 0.0,
            'catalyst_score': 0.0,
            'technical_score': 0.0,
            'days_to_catalyst': None,
            'catalyst_type': None,
            'earnings_date': None,
            'analysis_date': datetime.now().isoformat(),
            'interpretation': 'Insufficient data'
        }


_scanner = CatalystScanner()

def scan_catalyst_setup(symbol: str) -> Dict:
    return _scanner.scan_catalyst_setup(symbol)

def find_catalyst_setups(symbols: List[str], min_score: float = 60.0) -> List[Dict]:
    results = _scanner.batch_scan(symbols)
    return [r for r in results if r['setup_detected'] and r['setup_score'] >= min_score]
