"""
Venue Health Monitoring & Circuit Breakers
Phase 11: Live Trading Enablement
"""

import logging
import asyncio
from enum import Enum
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Circuit tripped, fail fast
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker for a single venue"""

    def __init__(self, venue: str, config: Dict):
        self.venue = venue
        self.consecutive_failures_threshold = config.get('consecutive_failures', 5)
        self.cooldown_seconds = config.get('cooldown_seconds', 60)
        self.half_open_max_calls = config.get('half_open_max_calls', 3)

        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_successes = 0
        self.half_open_attempts = 0

        logger.info(f"CircuitBreaker for {venue}: threshold={self.consecutive_failures_threshold}, cooldown={self.cooldown_seconds}s")

    def record_success(self):
        """Record successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_successes += 1
            self.half_open_attempts += 1

            if self.half_open_successes >= self.half_open_max_calls:
                # Close circuit
                logger.info(f"Circuit CLOSED for {self.venue} after {self.half_open_successes} successes")
                self.state = CircuitState.CLOSED
                self.consecutive_failures = 0
                self.half_open_successes = 0
                self.half_open_attempts = 0
        else:
            self.consecutive_failures = 0

    def record_failure(self):
        """Record failed call"""
        self.last_failure_time = datetime.utcnow()

        if self.state == CircuitState.HALF_OPEN:
            # Failure in half-open → reopen circuit
            logger.warning(f"Circuit reopened for {self.venue} - failure in half-open state")
            self.state = CircuitState.OPEN
            self.consecutive_failures = self.consecutive_failures_threshold
            self.half_open_successes = 0
            self.half_open_attempts = 0
            return

        self.consecutive_failures += 1

        if self.consecutive_failures >= self.consecutive_failures_threshold and self.state == CircuitState.CLOSED:
            logger.critical(f"Circuit OPENED for {self.venue} after {self.consecutive_failures} consecutive failures")
            self.state = CircuitState.OPEN

    def can_attempt(self) -> bool:
        """Check if call can be attempted"""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if cooldown elapsed
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed >= self.cooldown_seconds:
                    logger.info(f"Circuit entering HALF_OPEN for {self.venue} after {elapsed:.1f}s cooldown")
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_attempts = 0
                    self.half_open_successes = 0
                    return True
            return False

        # HALF_OPEN
        return self.half_open_attempts < self.half_open_max_calls


class VenueHealthMonitor:
    """Monitors health of all venues"""

    def __init__(self, config: Dict):
        self.config = config
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

        cb_config = config.get('circuit_breakers', {})
        for venue in ['IBKR', 'ALPACA', 'CCXT']:
            self.circuit_breakers[venue] = CircuitBreaker(venue, cb_config)

        logger.info(f"VenueHealthMonitor initialized for {len(self.circuit_breakers)} venues")

    def get_circuit_breaker(self, venue: str) -> CircuitBreaker:
        """Get circuit breaker for venue"""
        if venue not in self.circuit_breakers:
            cb_config = self.config.get('circuit_breakers', {})
            self.circuit_breakers[venue] = CircuitBreaker(venue, cb_config)
        return self.circuit_breakers[venue]

    def record_success(self, venue: str):
        """Record successful operation"""
        cb = self.get_circuit_breaker(venue)
        cb.record_success()

    def record_failure(self, venue: str):
        """Record failed operation"""
        cb = self.get_circuit_breaker(venue)
        cb.record_failure()

    def can_execute(self, venue: str) -> bool:
        """Check if venue can execute orders"""
        cb = self.get_circuit_breaker(venue)
        return cb.can_attempt()

    def get_status(self) -> Dict:
        """Get status of all circuits"""
        return {
            venue: {
                'state': cb.state,
                'consecutive_failures': cb.consecutive_failures,
                'last_failure': cb.last_failure_time.isoformat() if cb.last_failure_time else None
            }
            for venue, cb in self.circuit_breakers.items()
        }
