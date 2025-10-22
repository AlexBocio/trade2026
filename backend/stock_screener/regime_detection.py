# regime_detection.py - Advanced 8-Regime Market Detection
# Implements 15 technical indicators across 5 categories
# Returns comprehensive regime analysis with scoring

import numpy as np
import pandas as pd
import yfinance as yf
from typing import Dict, List, Tuple, Optional
from scipy import stats
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RegimeDetector:
    """
    Advanced regime detector with 8 distinct market regimes.

    Regimes:
    1. BULL_TRENDING: Strong upward trend
    2. BEAR_TRENDING: Strong downward trend
    3. MOMENTUM: Persistent directional movement
    4. MEAN_REVERTING: Oscillating around mean
    5. HIGH_VOLATILITY: Elevated uncertainty
    6. LOW_VOLATILITY: Compressed ranges
    7. RANGE_BOUND: Sideways consolidation
    8. CRISIS: Extreme stress conditions
    """

    REGIMES = [
        'BULL_TRENDING',
        'BEAR_TRENDING',
        'MOMENTUM',
        'MEAN_REVERTING',
        'HIGH_VOLATILITY',
        'LOW_VOLATILITY',
        'RANGE_BOUND',
        'CRISIS'
    ]

    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes

    def detect_regime(self, symbol: str, lookback_days: int = 60) -> Dict:
        """
        Detect market regime for given symbol.

        Args:
            symbol: Ticker symbol (e.g., 'SPY')
            lookback_days: Number of days to analyze

        Returns:
            Comprehensive regime analysis
        """
        try:
            # Fetch data
            data = self._fetch_data(symbol, lookback_days)
            if data is None or len(data) < 20:
                logger.error(f"Insufficient data for {symbol}")
                return self._default_regime(symbol)

            # Calculate all 15 indicators
            indicators = self._calculate_indicators(data)

            # Calculate regime scores
            regime_scores = self._score_regimes(indicators)

            # Determine primary and secondary regimes
            sorted_regimes = sorted(regime_scores.items(), key=lambda x: x[1], reverse=True)
            primary_regime = sorted_regimes[0][0]
            secondary_regime = sorted_regimes[1][0]

            # Calculate confidence
            confidence = self._calculate_confidence(regime_scores, indicators)

            return {
                'symbol': symbol,
                'primary_regime': primary_regime,
                'secondary_regime': secondary_regime,
                'confidence': round(confidence, 2),
                'regime_strength': round(regime_scores[primary_regime], 1),
                'regime_scores': {k: round(v, 1) for k, v in regime_scores.items()},
                'characteristics': {
                    'trend_strength': round(indicators['adx'], 1),
                    'volatility': round(indicators['realized_volatility'], 3),
                    'hurst_exponent': round(indicators['hurst'], 2),
                    'price_vs_sma20': round(indicators['price_vs_sma20'], 3),
                    'adx': round(indicators['adx'], 1),
                    'rsi': round(indicators['rsi'], 1)
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error detecting regime for {symbol}: {e}")
            return self._default_regime(symbol)

    def _fetch_data(self, symbol: str, lookback_days: int) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data."""
        try:
            ticker = yf.Ticker(symbol)
            # Add buffer for indicator calculation
            period = f"{lookback_days + 30}d"
            hist = ticker.history(period=period)

            if len(hist) < 20:
                return None

            return hist

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    def _calculate_indicators(self, data: pd.DataFrame) -> Dict:
        """
        Calculate all 15 technical indicators.

        Categories:
        A. TREND (4 indicators)
        B. VOLATILITY (4 indicators)
        C. MEAN REVERSION (3 indicators)
        D. MOMENTUM (3 indicators)
        E. VOLUME (1 indicator)
        """
        close = data['Close']
        high = data['High']
        low = data['Low']
        volume = data['Volume']

        indicators = {}

        # === A. TREND INDICATORS (4) ===

        # 1. price_vs_sma20
        sma20 = close.rolling(20).mean()
        indicators['price_vs_sma20'] = (close.iloc[-1] / sma20.iloc[-1]) - 1 if len(sma20) > 0 else 0

        # 2. sma20_slope
        if len(sma20) >= 5:
            indicators['sma20_slope'] = (sma20.iloc[-1] - sma20.iloc[-5]) / sma20.iloc[-5]
        else:
            indicators['sma20_slope'] = 0

        # 3. ADX (Average Directional Index)
        indicators['adx'] = self._calculate_adx(high, low, close)

        # 4. linear_trend
        if len(close) >= 20:
            x = np.arange(len(close[-20:]))
            slope, _ = np.polyfit(x, close[-20:].values, 1)
            indicators['linear_trend'] = slope / close.iloc[-1]  # Normalized
        else:
            indicators['linear_trend'] = 0

        # === B. VOLATILITY INDICATORS (4) ===

        # 5. atr_pct
        atr = self._calculate_atr(high, low, close)
        indicators['atr_pct'] = (atr / close.iloc[-1]) * 100 if close.iloc[-1] > 0 else 0

        # 6. realized_volatility
        returns = close.pct_change().dropna()
        if len(returns) >= 20:
            indicators['realized_volatility'] = returns.rolling(20).std().iloc[-1] * np.sqrt(252)
        else:
            indicators['realized_volatility'] = 0

        # 7. bb_width (Bollinger Band width)
        if len(sma20) >= 20:
            std20 = close.rolling(20).std()
            bb_upper = sma20 + (2 * std20)
            bb_lower = sma20 - (2 * std20)
            indicators['bb_width'] = ((bb_upper.iloc[-1] - bb_lower.iloc[-1]) / sma20.iloc[-1]) if sma20.iloc[-1] > 0 else 0
        else:
            indicators['bb_width'] = 0

        # 8. vol_vs_avg
        if len(returns) >= 20:
            current_vol = returns.iloc[-5:].std() * np.sqrt(252)
            vol_sma20 = returns.rolling(20).std().iloc[-1] * np.sqrt(252)
            indicators['vol_vs_avg'] = (current_vol / vol_sma20) - 1 if vol_sma20 > 0 else 0
        else:
            indicators['vol_vs_avg'] = 0

        # === C. MEAN REVERSION INDICATORS (3) ===

        # 9. hurst_exponent (R/S analysis)
        indicators['hurst'] = self._calculate_hurst(close)

        # 10. half_life
        indicators['half_life'] = self._calculate_half_life(close)

        # 11. zscore
        if len(sma20) >= 20 and len(close) >= 20:
            std20 = close.rolling(20).std()
            indicators['zscore'] = (close.iloc[-1] - sma20.iloc[-1]) / std20.iloc[-1] if std20.iloc[-1] > 0 else 0
        else:
            indicators['zscore'] = 0

        # === D. MOMENTUM INDICATORS (3) ===

        # 12. rsi (14-period)
        indicators['rsi'] = self._calculate_rsi(close, period=14)

        # 13. macd_histogram
        macd, signal = self._calculate_macd(close)
        indicators['macd_histogram'] = macd - signal

        # 14. roc_20 (Rate of Change)
        if len(close) >= 20:
            indicators['roc_20'] = (close.iloc[-1] / close.iloc[-20]) - 1
        else:
            indicators['roc_20'] = 0

        # === E. VOLUME INDICATORS (1) ===

        # 15. volume_trend
        if len(volume) >= 20:
            vol_5d = volume.iloc[-5:].mean()
            vol_20d = volume.iloc[-20:].mean()
            indicators['volume_trend'] = (vol_5d / vol_20d) - 1 if vol_20d > 0 else 0
        else:
            indicators['volume_trend'] = 0

        # Calculate autocorrelation for regime scoring
        if len(returns) >= 20:
            indicators['autocorr_lag1'] = returns.autocorr(lag=1)
        else:
            indicators['autocorr_lag1'] = 0

        return indicators

    def _score_regimes(self, ind: Dict) -> Dict[str, float]:
        """
        Score all 8 regimes based on indicator values.

        Returns scores 0-10 for each regime.
        """
        scores = {regime: 0.0 for regime in self.REGIMES}

        # === BULL_TRENDING ===
        if ind['price_vs_sma20'] > 0.02:
            scores['BULL_TRENDING'] += 2
        if ind['sma20_slope'] > 0.01:
            scores['BULL_TRENDING'] += 2
        if ind['adx'] > 25:
            scores['BULL_TRENDING'] += 1
        if 50 < ind['rsi'] < 70:
            scores['BULL_TRENDING'] += 1
        if ind['macd_histogram'] > 0:
            scores['BULL_TRENDING'] += 1

        # === BEAR_TRENDING ===
        if ind['price_vs_sma20'] < -0.02:
            scores['BEAR_TRENDING'] += 2
        if ind['sma20_slope'] < -0.01:
            scores['BEAR_TRENDING'] += 2
        if ind['adx'] > 25:
            scores['BEAR_TRENDING'] += 1
        if 30 < ind['rsi'] < 50:
            scores['BEAR_TRENDING'] += 1
        if ind['macd_histogram'] < 0:
            scores['BEAR_TRENDING'] += 1

        # === MOMENTUM ===
        if ind['hurst'] > 0.55:
            scores['MOMENTUM'] += 3
        if abs(ind['roc_20']) > 0.10:
            scores['MOMENTUM'] += 2
        if ind['autocorr_lag1'] > 0.3:
            scores['MOMENTUM'] += 2
        if ind['volume_trend'] > 0.2:
            scores['MOMENTUM'] += 1

        # === MEAN_REVERTING ===
        if ind['hurst'] < 0.45:
            scores['MEAN_REVERTING'] += 3
        if abs(ind['zscore']) > 2:
            scores['MEAN_REVERTING'] += 2
        if ind['autocorr_lag1'] < 0:
            scores['MEAN_REVERTING'] += 2
        if ind['half_life'] < 10:
            scores['MEAN_REVERTING'] += 1

        # === HIGH_VOLATILITY ===
        if ind['realized_volatility'] > 0.30:
            scores['HIGH_VOLATILITY'] += 3
        if ind['atr_pct'] > 2.5:
            scores['HIGH_VOLATILITY'] += 2
        if ind['vol_vs_avg'] > 0.5:
            scores['HIGH_VOLATILITY'] += 2

        # === LOW_VOLATILITY ===
        if ind['realized_volatility'] < 0.15:
            scores['LOW_VOLATILITY'] += 3
        if ind['atr_pct'] < 1.0:
            scores['LOW_VOLATILITY'] += 2
        if ind['bb_width'] < 0.03:
            scores['LOW_VOLATILITY'] += 1

        # === RANGE_BOUND ===
        if abs(ind['linear_trend']) < 0.001:
            scores['RANGE_BOUND'] += 2
        if ind['adx'] < 20:
            scores['RANGE_BOUND'] += 2
        if abs(ind['zscore']) < 0.5:
            scores['RANGE_BOUND'] += 1

        # === CRISIS ===
        if ind['realized_volatility'] > 0.50:
            scores['CRISIS'] += 3
        if ind['roc_20'] < -0.10:
            scores['CRISIS'] += 3
        if ind['vol_vs_avg'] > 1.0:
            scores['CRISIS'] += 2

        return scores

    def _calculate_confidence(self, regime_scores: Dict[str, float], indicators: Dict) -> float:
        """Calculate confidence in primary regime (0-1)."""
        scores = list(regime_scores.values())
        scores_sorted = sorted(scores, reverse=True)

        if len(scores_sorted) < 2:
            return 0.5

        # Gap between 1st and 2nd place
        gap = scores_sorted[0] - scores_sorted[1]

        # Normalize to 0-1
        confidence = min(gap / 10.0, 1.0)

        # Adjust by data quality
        if indicators['realized_volatility'] > 0.40:
            confidence *= 0.8  # Lower confidence in extreme volatility

        return max(0.0, min(confidence, 1.0))

    # === INDICATOR CALCULATION HELPERS ===

    def _calculate_adx(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> float:
        """Calculate Average Directional Index."""
        try:
            # True Range
            high_low = high - low
            high_close = np.abs(high - close.shift())
            low_close = np.abs(low - close.shift())
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

            # Directional Movement
            plus_dm = high.diff()
            minus_dm = -low.diff()
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm < 0] = 0

            # Smoothed indicators
            tr_smooth = tr.rolling(period).mean()
            plus_di = 100 * (plus_dm.rolling(period).mean() / tr_smooth)
            minus_di = 100 * (minus_dm.rolling(period).mean() / tr_smooth)

            # ADX
            dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(period).mean().iloc[-1]

            return float(adx) if not np.isnan(adx) else 0.0

        except:
            return 0.0

    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> float:
        """Calculate Average True Range."""
        try:
            high_low = high - low
            high_close = np.abs(high - close.shift())
            low_close = np.abs(low - close.shift())
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = tr.rolling(period).mean().iloc[-1]
            return float(atr) if not np.isnan(atr) else 0.0
        except:
            return 0.0

    def _calculate_rsi(self, close: pd.Series, period: int = 14) -> float:
        """Calculate Relative Strength Index."""
        try:
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1]) if not np.isnan(rsi.iloc[-1]) else 50.0
        except:
            return 50.0

    def _calculate_macd(self, close: pd.Series) -> Tuple[float, float]:
        """Calculate MACD and Signal line."""
        try:
            ema12 = close.ewm(span=12).mean()
            ema26 = close.ewm(span=26).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9).mean()
            return float(macd.iloc[-1]), float(signal.iloc[-1])
        except:
            return 0.0, 0.0

    def _calculate_hurst(self, close: pd.Series, max_lag: int = 20) -> float:
        """
        Calculate Hurst Exponent using R/S analysis.

        H < 0.5: Mean-reverting
        H = 0.5: Random walk
        H > 0.5: Trending/momentum
        """
        try:
            if len(close) < max_lag * 2:
                return 0.5

            lags = range(2, max_lag)
            tau = []

            for lag in lags:
                # Calculate std dev for this lag
                pp = np.array([close.iloc[i:i+lag].values for i in range(0, len(close)-lag, lag)])

                if len(pp) == 0:
                    continue

                # Calculate range and std
                ranges = []
                stds = []
                for p in pp:
                    if len(p) > 1:
                        ranges.append(np.max(p) - np.min(p))
                        stds.append(np.std(p))

                if len(ranges) > 0 and len(stds) > 0:
                    rs = np.mean(ranges) / (np.mean(stds) + 1e-10)
                    tau.append(rs)

            if len(tau) < 2:
                return 0.5

            # Fit log-log plot
            log_lags = np.log(list(lags[:len(tau)]))
            log_tau = np.log(tau)

            slope, _ = np.polyfit(log_lags, log_tau, 1)
            hurst = float(slope)

            # Clamp to reasonable range
            return max(0.0, min(hurst, 1.0))

        except:
            return 0.5

    def _calculate_half_life(self, close: pd.Series) -> float:
        """
        Calculate mean reversion half-life.

        Lower half-life = faster mean reversion.
        """
        try:
            if len(close) < 20:
                return 999.0

            # AR(1) regression
            y = close.diff().dropna()
            x = close.shift(1).dropna()

            # Align
            common_idx = y.index.intersection(x.index)
            y = y.loc[common_idx]
            x = x.loc[common_idx]

            if len(y) < 10:
                return 999.0

            # Regression
            slope, _ = np.polyfit(x, y, 1)

            # Half-life
            if slope >= 0:
                return 999.0

            half_life = -np.log(2) / np.log(1 + slope)

            return float(half_life) if half_life > 0 else 999.0

        except:
            return 999.0

    def _default_regime(self, symbol: str) -> Dict:
        """Return default regime on error."""
        return {
            'symbol': symbol,
            'primary_regime': 'RANGE_BOUND',
            'secondary_regime': 'MEAN_REVERTING',
            'confidence': 0.3,
            'regime_strength': 3.0,
            'regime_scores': {regime: 0.0 for regime in self.REGIMES},
            'characteristics': {
                'trend_strength': 0.0,
                'volatility': 0.0,
                'hurst_exponent': 0.5,
                'price_vs_sma20': 0.0,
                'adx': 0.0,
                'rsi': 50.0
            },
            'timestamp': datetime.now().isoformat()
        }


# === MODULE-LEVEL FUNCTIONS (for backward compatibility) ===

_detector = RegimeDetector()


def detect_market_regime(ticker: str = 'SPY', period: str = '6mo') -> str:
    """
    Detect market regime (backward compatible function).

    Maps new 8-regime system to old 4-regime system for compatibility.

    Returns:
        One of: 'trending', 'mean_reverting', 'volatile', 'choppy'
    """
    try:
        # Use new detector
        result = _detector.detect_regime(ticker, lookback_days=120)
        primary = result['primary_regime']

        # Map to old regime names
        mapping = {
            'BULL_TRENDING': 'trending',
            'BEAR_TRENDING': 'trending',
            'MOMENTUM': 'trending',
            'MEAN_REVERTING': 'mean_reverting',
            'HIGH_VOLATILITY': 'volatile',
            'LOW_VOLATILITY': 'choppy',
            'RANGE_BOUND': 'choppy',
            'CRISIS': 'volatile'
        }

        return mapping.get(primary, 'mean_reverting')

    except Exception as e:
        logger.error(f"Error in detect_market_regime: {e}")
        return 'mean_reverting'


def get_regime_characteristics(regime: str) -> Dict:
    """
    Get regime characteristics (backward compatible).

    Supports both old (4) and new (8) regime names.
    """
    # Old regime characteristics
    old_chars = {
        'trending': {
            'description': 'Strong directional movement',
            'best_strategies': ['momentum', 'trend_following'],
            'prediction_reliability': 'high',
            'recommended_timeframes': ['medium', 'long'],
            'risk_level': 'moderate'
        },
        'mean_reverting': {
            'description': 'Oscillating around mean',
            'best_strategies': ['mean_reversion', 'range_trading'],
            'prediction_reliability': 'moderate',
            'recommended_timeframes': ['short', 'medium'],
            'risk_level': 'low'
        },
        'volatile': {
            'description': 'High volatility, large swings',
            'best_strategies': ['volatility_arbitrage', 'options'],
            'prediction_reliability': 'low',
            'recommended_timeframes': ['short'],
            'risk_level': 'high'
        },
        'choppy': {
            'description': 'Low volatility, sideways movement',
            'best_strategies': ['range_trading', 'theta_decay'],
            'prediction_reliability': 'low',
            'recommended_timeframes': ['short'],
            'risk_level': 'low'
        }
    }

    # New regime characteristics
    new_chars = {
        'BULL_TRENDING': old_chars['trending'],
        'BEAR_TRENDING': old_chars['trending'],
        'MOMENTUM': old_chars['trending'],
        'MEAN_REVERTING': old_chars['mean_reverting'],
        'HIGH_VOLATILITY': old_chars['volatile'],
        'LOW_VOLATILITY': old_chars['choppy'],
        'RANGE_BOUND': old_chars['choppy'],
        'CRISIS': old_chars['volatile']
    }

    # Try both old and new regime names
    if regime in old_chars:
        return old_chars[regime]
    elif regime in new_chars:
        return new_chars[regime]
    else:
        return old_chars['mean_reverting']
