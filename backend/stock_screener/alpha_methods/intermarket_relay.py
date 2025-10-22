# intermarket_relay.py - Intermarket Lead-Lag Relationships
# Detects when one market leads another (eg. commodities → stocks)

from typing import Dict, List
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class IntermarketRelay:
    """Detects lead-lag relationships between markets."""

    MARKET_PAIRS = [
        ('GLD', 'GDX'),  # Gold → Gold miners
        ('USO', 'XLE'),  # Oil → Energy stocks
        ('TLT', 'XLF'),  # Bonds → Financials
        ('UUP', 'EEM'),  # Dollar (via UUP ETF) → Emerging markets
    ]

    def detect_relay(self, leader_symbol: str, follower_symbol: str, lookback_days: int = 60) -> Dict:
        """
        Detect lead-lag relationship.

        Returns:
            {
                'leader': str,
                'follower': str,
                'relay_detected': bool,
                'correlation': float,
                'lag_days': int,
                'leader_signal': str ('bullish', 'bearish', 'neutral'),
                'relay_strength': float (0-100),
                'interpretation': str
            }
        """
        try:
            # Fetch data
            leader_data = self._fetch_data(leader_symbol, lookback_days)
            follower_data = self._fetch_data(follower_symbol, lookback_days)

            if leader_data is None or follower_data is None:
                return self._default_result(leader_symbol, follower_symbol)

            # Calculate correlation
            correlation = self._calculate_correlation(leader_data, follower_data)

            # Detect lag
            lag_days = self._detect_lag(leader_data, follower_data)

            # Determine leader signal
            leader_signal = self._get_leader_signal(leader_data)

            # Calculate relay strength
            relay_strength = abs(correlation) * 100

            relay_detected = relay_strength >= 60.0 and abs(lag_days) <= 5

            return {
                'leader': leader_symbol,
                'follower': follower_symbol,
                'relay_detected': relay_detected,
                'correlation': correlation,
                'lag_days': lag_days,
                'leader_signal': leader_signal,
                'relay_strength': relay_strength,
                'analysis_date': datetime.now().isoformat(),
                'interpretation': self._generate_interpretation(
                    relay_detected, leader_signal, correlation, lag_days
                )
            }

        except Exception as e:
            logger.error(f"Error detecting relay {leader_symbol} → {follower_symbol}: {e}")
            return self._default_result(leader_symbol, follower_symbol)

    def _fetch_data(self, symbol: str, lookback_days: int) -> pd.DataFrame:
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days + 20)
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            return hist['Close'] if len(hist) >= 20 else None
        except:
            return None

    def _calculate_correlation(self, leader: pd.Series, follower: pd.Series) -> float:
        try:
            # Align by index
            combined = pd.concat([leader, follower], axis=1).dropna()
            if len(combined) < 20:
                return 0.0
            return float(combined.iloc[:, 0].corr(combined.iloc[:, 1]))
        except:
            return 0.0

    def _detect_lag(self, leader: pd.Series, follower: pd.Series) -> int:
        """Detect lag in days (positive = leader leads, negative = leader lags)."""
        try:
            max_lag = 5
            correlations = []

            for lag in range(-max_lag, max_lag + 1):
                if lag == 0:
                    corr = leader.corr(follower)
                elif lag > 0:
                    corr = leader[:-lag].corr(follower[lag:])
                else:
                    corr = leader[-lag:].corr(follower[:lag])

                correlations.append((lag, abs(corr)))

            best_lag = max(correlations, key=lambda x: x[1])[0]
            return int(best_lag)

        except:
            return 0

    def _get_leader_signal(self, leader_data: pd.Series) -> str:
        """Determine current leader trend."""
        try:
            recent = leader_data.tail(10)
            change_pct = ((recent.iloc[-1] - recent.iloc[0]) / recent.iloc[0]) * 100

            if change_pct >= 2.0:
                return 'bullish'
            elif change_pct <= -2.0:
                return 'bearish'
            return 'neutral'

        except:
            return 'neutral'

    def _generate_interpretation(self, detected: bool, signal: str, corr: float, lag: int) -> str:
        if detected:
            return (f"Relay detected: {signal} leader signal, {corr:.2f} correlation, "
                   f"{abs(lag)}-day lag. Expect follower to move {'up' if signal == 'bullish' else 'down'}.")
        return f"No significant relay (correlation: {corr:.2f})."

    def scan_all_pairs(self) -> List[Dict]:
        """Scan all market pairs."""
        results = []
        for leader, follower in self.MARKET_PAIRS:
            results.append(self.detect_relay(leader, follower))
        return results

    def _default_result(self, leader: str, follower: str) -> Dict:
        return {
            'leader': leader,
            'follower': follower,
            'relay_detected': False,
            'correlation': 0.0,
            'lag_days': 0,
            'leader_signal': 'neutral',
            'relay_strength': 0.0,
            'analysis_date': datetime.now().isoformat(),
            'interpretation': 'Insufficient data'
        }


_relay = IntermarketRelay()

def detect_intermarket_relay(leader: str, follower: str) -> Dict:
    return _relay.detect_relay(leader, follower)

def scan_market_relays() -> List[Dict]:
    return _relay.scan_all_pairs()
