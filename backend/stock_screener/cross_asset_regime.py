# cross_asset_regime.py - Cross-Asset Regime Detection
# Detects correlations and divergences across asset classes

from datetime import datetime, timedelta
from typing import Dict, List
import logging
import yfinance as yf
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class CrossAssetRegimeDetector:
    """
    Detect cross-asset correlations and regime.

    Asset Classes:
    - Equities (SPY, QQQ, IWM)
    - Bonds (TLT, IEF, SHY)
    - Commodities (GLD, USO, DBC)
    - Currencies (UUP - Dollar Index)
    - Volatility (VIX via ^VIX)
    - Credit (HYG, LQD)

    Regimes:
    - RISK_ON: Equities up, bonds down, commodities up, VIX down
    - RISK_OFF: Equities down, bonds up, commodities down, VIX up
    - FLIGHT_TO_QUALITY: Everything into treasuries
    - COMMODITY_DRIVEN: Commodities leading
    - ROTATION: Mixed signals, sector rotation
    - DIVERGENT: Major asset class divergences
    """

    ASSET_CLASSES = {
        'equities': ['SPY', 'QQQ', 'IWM'],
        'bonds': ['TLT', 'IEF', 'SHY'],
        'commodities': ['GLD', 'USO', 'DBC'],
        'currencies': ['UUP'],
        'volatility': ['^VIX']
    }

    def __init__(self):
        self._cache = {}
        self._cache_time = None
        self._cache_duration = timedelta(hours=6)

    def detect_cross_asset_regime(self, lookback_days: int = 30) -> Dict:
        """
        Detect cross-asset regime.

        Args:
            lookback_days: Lookback period for correlation

        Returns:
            Cross-asset regime dict
        """
        # Fetch asset class data
        asset_data = self._fetch_asset_data(lookback_days)

        # Calculate correlations
        correlations = self._calculate_correlations(asset_data)

        # Calculate asset class momentum
        momentum = self._calculate_asset_momentum(asset_data)

        # Detect regime
        regime = self._detect_regime(momentum, correlations)

        # Calculate divergences
        divergences = self._detect_divergences(momentum, correlations)

        # Risk sentiment score
        risk_sentiment = self._calculate_risk_sentiment(momentum)

        return {
            'timestamp': datetime.now().isoformat(),
            'cross_asset_regime': regime,
            'risk_sentiment': risk_sentiment,  # -10 (max fear) to +10 (max greed)

            'asset_momentum': momentum,
            'correlations': correlations,
            'divergences': divergences,

            'interpretation': self._interpret_regime(regime, risk_sentiment)
        }

    def _fetch_asset_data(self, lookback_days: int) -> Dict:
        """Fetch data for all asset classes."""
        all_symbols = []
        for symbols in self.ASSET_CLASSES.values():
            all_symbols.extend(symbols)

        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days + 10)

        data = {}
        for symbol in all_symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_date, end=end_date)
                if len(hist) > 0:
                    data[symbol] = hist['Close']
            except Exception as e:
                logger.warning(f"Failed to fetch {symbol}: {e}")

        return data

    def _calculate_correlations(self, asset_data: Dict) -> Dict:
        """Calculate key cross-asset correlations."""
        correlations = {}

        try:
            # Create DataFrame
            df = pd.DataFrame(asset_data)
            if df.empty:
                return correlations

            # Calculate returns
            returns = df.pct_change().dropna()

            # Key correlations
            if 'SPY' in returns.columns and 'TLT' in returns.columns:
                correlations['stocks_bonds'] = float(returns['SPY'].corr(returns['TLT']))

            if 'SPY' in returns.columns and 'GLD' in returns.columns:
                correlations['stocks_gold'] = float(returns['SPY'].corr(returns['GLD']))

            if 'SPY' in returns.columns and 'UUP' in returns.columns:
                correlations['stocks_dollar'] = float(returns['SPY'].corr(returns['UUP']))

            if 'TLT' in returns.columns and 'GLD' in returns.columns:
                correlations['bonds_gold'] = float(returns['TLT'].corr(returns['GLD']))

            if 'GLD' in returns.columns and 'USO' in returns.columns:
                correlations['gold_oil'] = float(returns['GLD'].corr(returns['USO']))

            # Equity market correlations
            if all(s in returns.columns for s in ['SPY', 'QQQ', 'IWM']):
                correlations['spy_qqq'] = float(returns['SPY'].corr(returns['QQQ']))
                correlations['spy_iwm'] = float(returns['SPY'].corr(returns['IWM']))
                correlations['equity_correlation_avg'] = float(
                    (correlations['spy_qqq'] + correlations['spy_iwm']) / 2
                )

        except Exception as e:
            logger.error(f"Correlation calculation failed: {e}")

        return correlations

    def _calculate_asset_momentum(self, asset_data: Dict) -> Dict:
        """Calculate momentum for each asset class."""
        momentum = {}

        for asset_class, symbols in self.ASSET_CLASSES.items():
            returns = []
            for symbol in symbols:
                if symbol in asset_data:
                    series = asset_data[symbol]
                    if len(series) > 1:
                        # Calculate 1-month return
                        ret = (series.iloc[-1] / series.iloc[0] - 1) * 100
                        returns.append(float(ret))

            if returns:
                momentum[asset_class] = {
                    'return_1m': float(np.mean(returns)),
                    'direction': 'UP' if np.mean(returns) > 0 else 'DOWN',
                    'strength': abs(float(np.mean(returns)))
                }
            else:
                momentum[asset_class] = {
                    'return_1m': 0.0,
                    'direction': 'NEUTRAL',
                    'strength': 0.0
                }

        return momentum

    def _detect_regime(self, momentum: Dict, correlations: Dict) -> str:
        """
        Detect overall cross-asset regime.

        Returns: RISK_ON | RISK_OFF | FLIGHT_TO_QUALITY | COMMODITY_DRIVEN | ROTATION | DIVERGENT
        """
        # Extract momentum directions
        eq_up = momentum.get('equities', {}).get('direction') == 'UP'
        eq_down = momentum.get('equities', {}).get('direction') == 'DOWN'
        bonds_up = momentum.get('bonds', {}).get('direction') == 'UP'
        bonds_down = momentum.get('bonds', {}).get('direction') == 'DOWN'
        comm_up = momentum.get('commodities', {}).get('direction') == 'UP'

        # Extract key correlations
        stocks_bonds_corr = correlations.get('stocks_bonds', 0)
        equity_corr = correlations.get('equity_correlation_avg', 0.8)

        # RISK_ON: Equities up, bonds down, negative stock-bond correlation
        if eq_up and bonds_down and stocks_bonds_corr < -0.3:
            return 'RISK_ON'

        # RISK_OFF: Equities down, bonds up, negative stock-bond correlation
        if eq_down and bonds_up and stocks_bonds_corr < -0.3:
            return 'RISK_OFF'

        # FLIGHT_TO_QUALITY: Everything down except bonds
        if eq_down and bonds_up and not comm_up:
            return 'FLIGHT_TO_QUALITY'

        # COMMODITY_DRIVEN: Commodities leading
        if comm_up and momentum.get('commodities', {}).get('strength', 0) > 5:
            return 'COMMODITY_DRIVEN'

        # DIVERGENT: Low equity correlation (sector rotation)
        if equity_corr < 0.5:
            return 'DIVERGENT'

        # ROTATION: Mixed signals
        return 'ROTATION'

    def _detect_divergences(self, momentum: Dict, correlations: Dict) -> List[Dict]:
        """Detect unusual asset class divergences."""
        divergences = []

        # Stocks-bonds correlation break
        sb_corr = correlations.get('stocks_bonds', -0.5)
        if sb_corr > 0.5:
            divergences.append({
                'type': 'STOCKS_BONDS_CORRELATION',
                'description': 'Stocks and bonds moving together (unusual)',
                'severity': 'HIGH',
                'value': sb_corr
            })

        # Growth-value divergence (QQQ vs IWM)
        spy_qqq = correlations.get('spy_qqq', 0.9)
        spy_iwm = correlations.get('spy_iwm', 0.9)
        if abs(spy_qqq - spy_iwm) > 0.4:
            divergences.append({
                'type': 'GROWTH_VALUE_DIVERGENCE',
                'description': 'Large cap growth diverging from small cap value',
                'severity': 'MEDIUM',
                'value': abs(spy_qqq - spy_iwm)
            })

        # Gold-oil divergence
        gold_oil = correlations.get('gold_oil', 0.5)
        if gold_oil < 0:
            divergences.append({
                'type': 'GOLD_OIL_DIVERGENCE',
                'description': 'Gold and oil moving in opposite directions',
                'severity': 'MEDIUM',
                'value': gold_oil
            })

        return divergences

    def _calculate_risk_sentiment(self, momentum: Dict) -> float:
        """
        Calculate risk sentiment score.

        Returns: -10 (extreme fear) to +10 (extreme greed)
        """
        score = 0.0

        # Equities contribution
        eq_return = momentum.get('equities', {}).get('return_1m', 0)
        score += np.clip(eq_return / 2, -4, 4)  # Max ±4 points

        # Bonds contribution (inverse)
        bond_return = momentum.get('bonds', {}).get('return_1m', 0)
        score -= np.clip(bond_return / 2, -3, 3)  # Max ±3 points (inverse)

        # Commodities contribution
        comm_return = momentum.get('commodities', {}).get('return_1m', 0)
        score += np.clip(comm_return / 4, -2, 2)  # Max ±2 points

        # VIX contribution
        vix_return = momentum.get('volatility', {}).get('return_1m', 0)
        score -= np.clip(vix_return / 3, -3, 3)  # Max ±3 points (inverse)

        return float(np.clip(score, -10, 10))

    def _interpret_regime(self, regime: str, risk_sentiment: float) -> str:
        """Provide interpretation of the regime."""
        interpretations = {
            'RISK_ON': 'Risk assets outperforming, investors favoring growth',
            'RISK_OFF': 'Flight to safety, defensive positioning',
            'FLIGHT_TO_QUALITY': 'Extreme risk aversion, treasuries bid',
            'COMMODITY_DRIVEN': 'Inflation concerns or supply disruptions',
            'ROTATION': 'Sector rotation, mixed market signals',
            'DIVERGENT': 'Low correlation environment, stock-specific opportunities'
        }

        base = interpretations.get(regime, 'Mixed cross-asset signals')

        if risk_sentiment > 5:
            return f"{base}. Sentiment: GREEDY"
        elif risk_sentiment > 2:
            return f"{base}. Sentiment: BULLISH"
        elif risk_sentiment > -2:
            return f"{base}. Sentiment: NEUTRAL"
        elif risk_sentiment > -5:
            return f"{base}. Sentiment: BEARISH"
        else:
            return f"{base}. Sentiment: FEARFUL"


# Module-level function for convenience
_detector = CrossAssetRegimeDetector()


def detect_cross_asset_regime(lookback_days: int = 30) -> Dict:
    """Convenience function for cross-asset regime detection."""
    return _detector.detect_cross_asset_regime(lookback_days)
