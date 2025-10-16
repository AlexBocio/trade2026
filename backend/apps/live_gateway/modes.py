"""
Trading Mode Management
Phase 11: Live Trading Enablement
"""

import logging
from enum import Enum
from typing import Dict, Optional
from datetime import datetime
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class TradingMode(str, Enum):
    """Trading mode enumeration"""
    SHADOW = "SHADOW"  # Mirror orders without execution
    CANARY = "CANARY"  # Partial live execution
    LIVE = "LIVE"      # Full live execution


class VenueMode(BaseModel):
    """Per-venue mode configuration"""
    mode: TradingMode = TradingMode.SHADOW
    canary_pct: float = 0.0        # % of orders to execute live
    canary_max_qty: float = 0.0    # Max qty per order in canary


class ModeManager:
    """Manages trading modes across venues"""

    def __init__(self, config: Dict):
        self.config = config
        self.global_mode = TradingMode(config.get('modes', {}).get('global', 'SHADOW'))

        # Load venue modes
        self.venue_modes: Dict[str, VenueMode] = {}
        venue_configs = config.get('modes', {}).get('venues', {})

        for venue, venue_config in venue_configs.items():
            self.venue_modes[venue] = VenueMode(
                mode=TradingMode(venue_config.get('mode', 'SHADOW')),
                canary_pct=venue_config.get('canary_pct', 0.0),
                canary_max_qty=venue_config.get('canary_max_qty', 0.0)
            )

        logger.info(f"ModeManager initialized: global={self.global_mode}, venues={len(self.venue_modes)}")

    def get_mode(self, venue: str) -> VenueMode:
        """Get effective mode for a venue"""
        if venue in self.venue_modes:
            return self.venue_modes[venue]

        # Default to global mode
        return VenueMode(mode=self.global_mode)

    def update_global_mode(self, mode: TradingMode):
        """Update global trading mode"""
        logger.warning(f"Global mode changed: {self.global_mode} → {mode}")
        self.global_mode = mode

    def update_venue_mode(self, venue: str, mode_config: Dict):
        """Update venue-specific mode"""
        venue_mode = VenueMode(
            mode=TradingMode(mode_config.get('mode', 'SHADOW')),
            canary_pct=mode_config.get('canary_pct', 0.0),
            canary_max_qty=mode_config.get('canary_max_qty', 0.0)
        )

        old_mode = self.venue_modes.get(venue)
        self.venue_modes[venue] = venue_mode

        logger.warning(f"Venue {venue} mode changed: {old_mode} → {venue_mode}")

    def should_execute_live(self, venue: str, order_size: float) -> tuple[bool, float]:
        """
        Determine if order should execute live

        Returns:
            (should_execute, actual_size)
        """
        venue_mode = self.get_mode(venue)

        if venue_mode.mode == TradingMode.SHADOW:
            return False, 0.0

        if venue_mode.mode == TradingMode.CANARY:
            # Probabilistic canary selection
            import random
            if random.random() < venue_mode.canary_pct:
                # Cap at canary_max_qty
                actual_size = min(order_size, venue_mode.canary_max_qty)
                return True, actual_size
            return False, 0.0

        # LIVE mode
        return True, order_size

    def panic_mode(self):
        """Force all venues to SHADOW mode"""
        logger.critical("PANIC MODE ACTIVATED - All venues forced to SHADOW")
        self.global_mode = TradingMode.SHADOW
        for venue in self.venue_modes:
            self.venue_modes[venue].mode = TradingMode.SHADOW
