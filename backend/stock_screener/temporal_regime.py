# temporal_regime.py - Temporal/Calendar Regime Detection
# Detects seasonal patterns, calendar effects, and event-driven regimes

from datetime import datetime, timedelta
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class TemporalRegimeDetector:
    """
    Detect temporal/calendar-based market regimes.

    Patterns:
    - January Effect
    - Sell in May
    - Santa Rally
    - OpEx week volatility
    - Month-end rebalancing
    - Fed meeting weeks
    - Day-of-week patterns
    """

    # Fed meeting dates (approximate schedule - 8 meetings per year)
    FED_MEETING_MONTHS = [1, 3, 5, 6, 7, 9, 11, 12]

    # CPI release schedule (2nd week of each month)
    CPI_RELEASE_DAY = 13  # Approximate

    # OpEx (3rd Friday of each month)

    def __init__(self):
        pass

    def detect_temporal_context(self, date: datetime = None) -> Dict:
        """
        Detect temporal/calendar regime.

        Args:
            date: Date to analyze (default: today)

        Returns:
            Temporal context dict
        """
        if date is None:
            date = datetime.now()

        month = date.month
        day = date.day
        day_of_week = date.weekday()  # 0=Monday, 6=Sunday
        week_of_month = (day - 1) // 7 + 1

        # Detect seasonal regime
        seasonal_regime = self._detect_seasonal_regime(month)

        # Detect day regime
        day_regime = self._detect_day_regime(day_of_week)

        # Check for special events
        is_opex_week = self._is_opex_week(date)
        is_fed_week = self._is_fed_meeting_week(date)
        is_month_end = self._is_month_end(date)
        is_earnings_season = self._is_earnings_season(month)

        # Calculate days to next events
        days_to_next_fed = self._days_to_next_fed(date)
        days_to_next_cpi = self._days_to_next_cpi(date)
        days_to_month_end = self._days_to_month_end(date)

        # Historical performance
        historical_month_performance = self._get_historical_month_performance(month)

        return {
            'date': date.strftime('%Y-%m-%d'),
            'month': month,
            'month_name': date.strftime('%B'),
            'day': day,
            'day_of_week': day_of_week,
            'day_name': date.strftime('%A'),
            'week_of_month': week_of_month,

            'seasonal_regime': seasonal_regime,
            'day_regime': day_regime,

            'is_earnings_season': is_earnings_season,
            'is_opex_week': is_opex_week,
            'is_fed_week': is_fed_week,
            'is_month_end': is_month_end,

            'days_to_next_fed': days_to_next_fed,
            'days_to_next_cpi': days_to_next_cpi,
            'days_to_month_end': days_to_month_end,

            'historical_month_performance': historical_month_performance
        }

    def _detect_seasonal_regime(self, month: int) -> str:
        """Detect seasonal market regime."""
        if month == 1:
            return 'JANUARY_EFFECT'  # Small cap strength
        elif month == 10:
            return 'HISTORICALLY_VOLATILE'  # October effect
        elif month in [5, 6, 7, 8, 9]:
            return 'SUMMER_DOLDRUMS'  # Sell in May
        elif month == 12:
            return 'SANTA_RALLY'  # Year-end strength
        elif month in [11]:
            return 'THANKSGIVING_RALLY'  # Pre-holiday strength
        elif month in [2, 3, 4]:
            return 'SPRING_STRENGTH'  # Strong historical performance
        else:
            return 'NEUTRAL'

    def _detect_day_regime(self, day_of_week: int) -> str:
        """Detect day-of-week regime."""
        if day_of_week == 0:  # Monday
            return 'WEEKEND_GAP_RISK'
        elif day_of_week == 4:  # Friday
            return 'PROFIT_TAKING_LIKELY'
        elif day_of_week == 2:  # Wednesday
            return 'MID_WEEK_STRENGTH'
        else:
            return 'NEUTRAL_DAY'

    def _is_opex_week(self, date: datetime) -> bool:
        """Check if date is in OpEx week (3rd Friday of month)."""
        # Get 3rd Friday of this month
        first_day = date.replace(day=1)
        first_friday = (4 - first_day.weekday()) % 7 + 1
        third_friday = first_day.replace(day=first_friday + 14)

        # OpEx week is the week containing 3rd Friday
        week_start = third_friday - timedelta(days=third_friday.weekday())
        week_end = week_start + timedelta(days=6)

        return week_start <= date <= week_end

    def _is_fed_meeting_week(self, date: datetime) -> bool:
        """Check if date is in a Fed meeting week."""
        month = date.month

        if month not in self.FED_MEETING_MONTHS:
            return False

        # Fed meetings typically 2nd or 3rd week
        week_of_month = (date.day - 1) // 7 + 1
        return week_of_month in [2, 3]

    def _is_month_end(self, date: datetime) -> bool:
        """Check if date is near month end (last 3 trading days)."""
        # Get last day of month
        next_month = date.replace(day=28) + timedelta(days=4)
        last_day = (next_month - timedelta(days=next_month.day)).day

        # Month-end is last 3 days
        return date.day >= last_day - 2

    def _is_earnings_season(self, month: int) -> bool:
        """Check if month is earnings season."""
        # Earnings seasons: Jan, Apr, Jul, Oct (and following months)
        return month in [1, 2, 4, 5, 7, 8, 10, 11]

    def _days_to_next_fed(self, date: datetime) -> int:
        """Calculate days until next Fed meeting."""
        current_month = date.month

        # Find next Fed meeting month
        next_fed_months = [m for m in self.FED_MEETING_MONTHS if m > current_month]

        if not next_fed_months:
            # Next meeting is next year
            next_fed_month = self.FED_MEETING_MONTHS[0]
            next_fed_year = date.year + 1
        else:
            next_fed_month = next_fed_months[0]
            next_fed_year = date.year

        # Assume meeting is 15th of month
        next_fed_date = datetime(next_fed_year, next_fed_month, 15)

        return (next_fed_date - date).days

    def _days_to_next_cpi(self, date: datetime) -> int:
        """Calculate days until next CPI release."""
        # CPI releases on ~13th of each month
        if date.day < self.CPI_RELEASE_DAY:
            # This month
            next_cpi = date.replace(day=self.CPI_RELEASE_DAY)
        else:
            # Next month
            next_month = date.replace(day=28) + timedelta(days=4)
            next_cpi = next_month.replace(day=self.CPI_RELEASE_DAY)

        return (next_cpi - date).days

    def _days_to_month_end(self, date: datetime) -> int:
        """Calculate days until month end."""
        next_month = date.replace(day=28) + timedelta(days=4)
        last_day_of_month = next_month - timedelta(days=next_month.day)

        return (last_day_of_month - date).days

    def _get_historical_month_performance(self, month: int) -> Dict:
        """
        Get historical average performance for month.

        Based on S&P 500 historical data (1950-2024).
        """
        # Historical S&P 500 average monthly returns
        historical_returns = {
            1: 0.012,   # January: 1.2% (January Effect)
            2: 0.003,   # February: 0.3%
            3: 0.010,   # March: 1.0%
            4: 0.015,   # April: 1.5% (Best month historically)
            5: 0.005,   # May: 0.5%
            6: 0.001,   # June: 0.1%
            7: 0.008,   # July: 0.8%
            8: -0.002,  # August: -0.2% (Weak)
            9: -0.007,  # September: -0.7% (Worst month)
            10: 0.006,  # October: 0.6% (Volatile but positive)
            11: 0.014,  # November: 1.4% (Strong)
            12: 0.013   # December: 1.3% (Santa Rally)
        }

        # Volatility percentile (0-100)
        volatility_percentiles = {
            1: 55, 2: 50, 3: 52, 4: 45, 5: 50, 6: 48,
            7: 45, 8: 58, 9: 65, 10: 75, 11: 50, 12: 42
        }

        return {
            'SPY_avg_return': historical_returns.get(month, 0.0),
            'volatility_percentile': volatility_percentiles.get(month, 50)
        }


# Module-level function for convenience
_detector = TemporalRegimeDetector()


def detect_temporal_context(date: datetime = None) -> Dict:
    """Convenience function for temporal detection."""
    return _detector.detect_temporal_context(date)
