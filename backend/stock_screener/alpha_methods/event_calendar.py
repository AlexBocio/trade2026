# event_calendar.py - Event Calendar Aggregation
# Aggregates earnings dates, FDA decisions, economic events

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class EventCalendar:
    """
    Aggregates upcoming catalyst events.

    Event Types:
    1. Earnings - Quarterly earnings releases
    2. FDA Decisions - Drug approvals (biotech)
    3. Economic Events - Fed meetings, CPI, jobs reports
    4. Product Launches - Major product releases
    """

    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode

    def get_upcoming_events(self, symbol: str, days_ahead: int = 60) -> Dict:
        """
        Get upcoming catalyst events for a symbol.

        Args:
            symbol: Stock symbol
            days_ahead: Days to look ahead

        Returns:
            {
                'symbol': str,
                'events': List[Dict],
                'earnings_date': str or None,
                'days_to_earnings': int or None,
                'has_upcoming_catalyst': bool,
                'next_catalyst_type': str,
                'days_to_next_catalyst': int
            }
        """
        try:
            events = []

            # Get earnings date
            earnings_event = self._get_earnings_date(symbol, days_ahead)
            if earnings_event:
                events.append(earnings_event)

            # Get FDA events (if biotech)
            fda_events = self._get_fda_events(symbol, days_ahead)
            events.extend(fda_events)

            # Get product launch events
            product_events = self._get_product_events(symbol, days_ahead)
            events.extend(product_events)

            # Sort events by date
            events.sort(key=lambda x: x['date'])

            # Determine next catalyst
            has_catalyst = len(events) > 0
            next_catalyst_type = events[0]['type'] if has_catalyst else None
            days_to_next = events[0]['days_until'] if has_catalyst else None

            return {
                'symbol': symbol,
                'events': events,
                'earnings_date': earnings_event['date_str'] if earnings_event else None,
                'days_to_earnings': earnings_event['days_until'] if earnings_event else None,
                'has_upcoming_catalyst': has_catalyst,
                'next_catalyst_type': next_catalyst_type,
                'days_to_next_catalyst': days_to_next,
                'analysis_date': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting events for {symbol}: {e}")
            return self._default_result(symbol)

    def _get_earnings_date(self, symbol: str, days_ahead: int) -> Optional[Dict]:
        """Get next earnings date."""
        try:
            if self.mock_mode:
                return self._mock_earnings_event(symbol)

            ticker = yf.Ticker(symbol)
            calendar = ticker.calendar

            if calendar is None or 'Earnings Date' not in calendar:
                return None

            earnings_date = calendar['Earnings Date']

            # Handle various return types from yfinance
            if isinstance(earnings_date, list):
                # Sometimes yfinance returns a list
                earnings_date = earnings_date[0] if len(earnings_date) > 0 else None
            elif isinstance(earnings_date, pd.Series):
                # Sometimes it's a pandas Series
                earnings_date = earnings_date.iloc[0] if len(earnings_date) > 0 else None

            if earnings_date is None:
                return None

            # Convert to datetime if needed
            if isinstance(earnings_date, str):
                earnings_date = pd.to_datetime(earnings_date)
            elif not isinstance(earnings_date, (datetime, pd.Timestamp)):
                # Try to convert unknown types
                try:
                    earnings_date = pd.to_datetime(earnings_date)
                except:
                    logger.warning(f"Could not parse earnings date for {symbol}: {type(earnings_date)}")
                    return None

            # Convert pd.Timestamp to datetime for consistent handling
            if isinstance(earnings_date, pd.Timestamp):
                earnings_date = earnings_date.to_pydatetime()

            today = datetime.now()
            days_until = (earnings_date - today).days

            if 0 <= days_until <= days_ahead:
                return {
                    'type': 'earnings',
                    'date': earnings_date,
                    'date_str': earnings_date.strftime('%Y-%m-%d'),
                    'days_until': days_until,
                    'description': f'Earnings release'
                }

            return None

        except Exception as e:
            logger.error(f"Error getting earnings date for {symbol}: {e}")
            return None

    def _get_fda_events(self, symbol: str, days_ahead: int) -> List[Dict]:
        """Get FDA decision dates (mock for now)."""
        # In production, would integrate with FDA calendar API
        return []

    def _get_product_events(self, symbol: str, days_ahead: int) -> List[Dict]:
        """Get product launch events (mock for now)."""
        # In production, would integrate with company announcements
        return []

    def _mock_earnings_event(self, symbol: str) -> Dict:
        """Mock earnings event for testing."""
        days_until = np.random.randint(5, 45)
        earnings_date = datetime.now() + timedelta(days=days_until)

        return {
            'type': 'earnings',
            'date': earnings_date,
            'date_str': earnings_date.strftime('%Y-%m-%d'),
            'days_until': days_until,
            'description': 'Earnings release'
        }

    def batch_analyze(self, symbols: List[str], days_ahead: int = 60) -> List[Dict]:
        """
        Get events for multiple symbols.

        Returns:
            List of event analyses, sorted by next catalyst date
        """
        results = []

        for symbol in symbols:
            analysis = self.get_upcoming_events(symbol, days_ahead)
            results.append(analysis)

        # Sort by days to next catalyst
        results.sort(key=lambda x: x['days_to_next_catalyst'] if x['days_to_next_catalyst'] is not None else 999)

        return results

    def _default_result(self, symbol: str) -> Dict:
        """Return default result when analysis fails."""
        return {
            'symbol': symbol,
            'events': [],
            'earnings_date': None,
            'days_to_earnings': None,
            'has_upcoming_catalyst': False,
            'next_catalyst_type': None,
            'days_to_next_catalyst': None,
            'analysis_date': datetime.now().isoformat()
        }


# Module-level instance
_calendar = EventCalendar()


def get_upcoming_events(symbol: str, days_ahead: int = 60) -> Dict:
    """Convenience function for event calendar."""
    return _calendar.get_upcoming_events(symbol, days_ahead)
