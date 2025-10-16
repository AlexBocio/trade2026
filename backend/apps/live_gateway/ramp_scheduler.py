"""
Capital Ramp Scheduler
Phase 11: Live Trading Enablement
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class RampScheduleEntry(BaseModel):
    """Single ramp schedule entry"""
    at: datetime
    pct: float


class RampScheduler:
    """Manages capital ramp schedule"""

    def __init__(self, config: Dict):
        self.config = config.get('ramp', {})

        # Parse schedule
        self.schedule: List[RampScheduleEntry] = []
        for entry in self.config.get('schedule', []):
            self.schedule.append(RampScheduleEntry(
                at=datetime.fromisoformat(entry['at'].replace('Z', '+00:00')),
                pct=entry['pct']
            ))

        # Sort by time
        self.schedule.sort(key=lambda x: x.at)

        self.hard_daily_cap = self.config.get('hard_daily_notional_cap_usd', 50000)
        self.current_daily_notional = 0.0
        self.last_reset = datetime.utcnow().date()

        logger.info(f"RampScheduler initialized: {len(self.schedule)} schedule entries, daily cap=${self.hard_daily_cap}")

    def get_current_pct(self) -> float:
        """Get current ramp percentage based on schedule"""
        now = datetime.now(timezone.utc)

        # Find the most recent schedule entry
        current_pct = 0.0
        for entry in self.schedule:
            if now >= entry.at:
                current_pct = entry.pct
            else:
                break

        return current_pct

    def check_capacity(self, notional: float) -> tuple[bool, str]:
        """
        Check if order fits within ramp limits

        Returns:
            (approved, reason)
        """
        # Reset daily counter if new day
        today = datetime.utcnow().date()
        if today != self.last_reset:
            self.current_daily_notional = 0.0
            self.last_reset = today
            logger.info(f"Daily notional counter reset: {today}")

        # Check hard daily cap
        if self.current_daily_notional + notional > self.hard_daily_cap:
            return False, f"Daily notional cap reached: ${self.current_daily_notional:.2f} + ${notional:.2f} > ${self.hard_daily_cap}"

        return True, "OK"

    def record_notional(self, notional: float):
        """Record executed notional"""
        self.current_daily_notional += notional
        logger.info(f"Recorded notional: ${notional:.2f}, daily total: ${self.current_daily_notional:.2f}")

    def get_max_notional_for_account(self, account_capital: float) -> float:
        """Calculate max notional based on ramp % and account capital"""
        ramp_pct = self.get_current_pct()
        max_notional = account_capital * ramp_pct

        # Cap at daily limit
        remaining_daily = self.hard_daily_cap - self.current_daily_notional
        return min(max_notional, remaining_daily)
