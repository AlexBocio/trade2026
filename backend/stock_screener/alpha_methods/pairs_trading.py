# pairs_trading.py - Pairs Trading Scanner
# Finds cointegrated pairs, calculates spreads, and detects trading opportunities

from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from statsmodels.regression.linear_model import OLS
import logging

from .statistical_tests import StatisticalTests

logger = logging.getLogger(__name__)


class PairsTrading:
    """
    Pairs trading scanner and opportunity detector.

    Features:
    1. Scan universe for cointegrated pairs
    2. Calculate spread and z-score
    3. Detect entry/exit signals
    4. Risk metrics (correlation, beta stability)
    """

    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.stat_tests = StatisticalTests(mock_mode=mock_mode)

    def scan_pairs(self, symbols: List[str], min_correlation: float = 0.7, max_pairs: int = 20) -> List[Dict]:
        """
        Scan universe for cointegrated pairs.

        Args:
            symbols: List of symbols to scan
            min_correlation: Minimum correlation threshold
            max_pairs: Maximum number of pairs to return

        Returns:
            List of pair opportunities, sorted by cointegration strength
        """
        try:
            if self.mock_mode:
                return self._mock_pairs_scan(symbols, max_pairs)

            logger.info(f"Scanning {len(symbols)} symbols for pairs")

            pairs = []

            # Fetch all prices upfront
            prices_cache = {}
            for symbol in symbols:
                prices = self._fetch_prices(symbol, 252)
                if prices is not None and len(prices) >= 100:
                    prices_cache[symbol] = prices

            valid_symbols = list(prices_cache.keys())
            logger.info(f"Found valid price data for {len(valid_symbols)} symbols")

            # Test all pairs
            for i in range(len(valid_symbols)):
                for j in range(i + 1, len(valid_symbols)):
                    symbol1 = valid_symbols[i]
                    symbol2 = valid_symbols[j]

                    # Quick correlation filter
                    corr = self._calculate_correlation(prices_cache[symbol1], prices_cache[symbol2])
                    if corr < min_correlation:
                        continue

                    # Test cointegration
                    coint_result = self.stat_tests.test_cointegration(symbol1, symbol2)

                    if coint_result['is_cointegrated']:
                        # Calculate current spread and z-score
                        spread_data = self._calculate_spread(
                            symbol1, symbol2, coint_result['hedge_ratio']
                        )

                        # Calculate half-life
                        half_life_result = self.stat_tests.calculate_half_life(
                            symbol1, symbol2, coint_result['hedge_ratio']
                        )

                        pair_info = {
                            'symbol1': symbol1,
                            'symbol2': symbol2,
                            'correlation': corr,
                            'hedge_ratio': coint_result['hedge_ratio'],
                            'cointegration_pvalue': coint_result['p_value'],
                            'cointegration_confidence': coint_result['confidence'],
                            'current_zscore': spread_data['current_zscore'],
                            'spread_mean': spread_data['spread_mean'],
                            'spread_std': spread_data['spread_std'],
                            'half_life_days': half_life_result.get('half_life_days'),
                            'is_tradeable': half_life_result.get('is_tradeable', False),
                            'signal': self._determine_signal(spread_data['current_zscore']),
                            'analysis_date': datetime.now().isoformat()
                        }

                        pairs.append(pair_info)

            # Sort by cointegration strength (lowest p-value first)
            pairs.sort(key=lambda x: x['cointegration_pvalue'])

            return pairs[:max_pairs]

        except Exception as e:
            logger.error(f"Error scanning pairs: {e}")
            return []

    def analyze_pair(self, symbol1: str, symbol2: str, lookback_days: int = 252) -> Dict:
        """
        Detailed analysis of a specific pair.

        Args:
            symbol1: First symbol
            symbol2: Second symbol
            lookback_days: Historical data period

        Returns:
            {
                'symbol1': str,
                'symbol2': str,
                'correlation': float,
                'hedge_ratio': float,
                'cointegration': Dict,
                'half_life': Dict,
                'current_zscore': float,
                'signal': str,
                'spread_history': List[Dict],
                'entry_threshold': float,
                'exit_threshold': float
            }
        """
        try:
            if self.mock_mode:
                return self._mock_pair_analysis(symbol1, symbol2)

            # Test cointegration
            coint_result = self.stat_tests.test_cointegration(symbol1, symbol2, lookback_days)

            if not coint_result['is_cointegrated']:
                return {
                    'symbol1': symbol1,
                    'symbol2': symbol2,
                    'error': 'Pair is not cointegrated',
                    'cointegration': coint_result
                }

            # Calculate half-life
            half_life_result = self.stat_tests.calculate_half_life(
                symbol1, symbol2, coint_result['hedge_ratio'], lookback_days
            )

            # Calculate spread data
            spread_data = self._calculate_spread_history(
                symbol1, symbol2, coint_result['hedge_ratio'], lookback_days
            )

            # Determine signal
            current_zscore = spread_data['current_zscore']
            signal = self._determine_signal(current_zscore)

            # Calculate correlation
            prices1 = self._fetch_prices(symbol1, lookback_days)
            prices2 = self._fetch_prices(symbol2, lookback_days)
            correlation = self._calculate_correlation(prices1, prices2)

            return {
                'symbol1': symbol1,
                'symbol2': symbol2,
                'correlation': correlation,
                'hedge_ratio': coint_result['hedge_ratio'],
                'cointegration': coint_result,
                'half_life': half_life_result,
                'current_zscore': current_zscore,
                'spread_mean': spread_data['spread_mean'],
                'spread_std': spread_data['spread_std'],
                'signal': signal,
                'spread_history': spread_data['history'][-30:],  # Last 30 days
                'entry_threshold': 2.0,
                'exit_threshold': 0.5,
                'interpretation': self._generate_interpretation(signal, current_zscore, half_life_result),
                'analysis_date': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error analyzing pair {symbol1}/{symbol2}: {e}")
            return {
                'symbol1': symbol1,
                'symbol2': symbol2,
                'error': str(e)
            }

    def find_opportunities(self, symbols: List[str], min_zscore: float = 1.5) -> List[Dict]:
        """
        Find pairs with current trading opportunities.

        Args:
            symbols: List of symbols to scan
            min_zscore: Minimum z-score threshold for opportunities

        Returns:
            List of tradeable opportunities
        """
        try:
            # Scan for cointegrated pairs
            pairs = self.scan_pairs(symbols, max_pairs=50)

            opportunities = []

            for pair in pairs:
                zscore = abs(pair['current_zscore'])

                if zscore >= min_zscore and pair['is_tradeable']:
                    opportunities.append({
                        'symbol1': pair['symbol1'],
                        'symbol2': pair['symbol2'],
                        'hedge_ratio': pair['hedge_ratio'],
                        'current_zscore': pair['current_zscore'],
                        'signal': pair['signal'],
                        'half_life_days': pair['half_life_days'],
                        'cointegration_confidence': pair['cointegration_confidence'],
                        'expected_reversion_days': pair['half_life_days'] * 2.5 if pair['half_life_days'] else None,
                        'analysis_date': datetime.now().isoformat()
                    })

            # Sort by absolute z-score (most diverged first)
            opportunities.sort(key=lambda x: abs(x['current_zscore']), reverse=True)

            return opportunities

        except Exception as e:
            logger.error(f"Error finding opportunities: {e}")
            return []

    def _fetch_prices(self, symbol: str, lookback_days: int) -> Optional[pd.Series]:
        """Fetch historical closing prices."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days + 20)
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            return hist['Close'] if len(hist) >= 20 else None
        except:
            return None

    def _calculate_correlation(self, prices1: pd.Series, prices2: pd.Series) -> float:
        """Calculate correlation between two price series."""
        try:
            df = pd.concat([prices1, prices2], axis=1).dropna()
            if len(df) < 20:
                return 0.0
            return float(df.iloc[:, 0].corr(df.iloc[:, 1]))
        except:
            return 0.0

    def _calculate_spread(self, symbol1: str, symbol2: str, hedge_ratio: float) -> Dict:
        """Calculate current spread and z-score."""
        try:
            prices1 = self._fetch_prices(symbol1, 252)
            prices2 = self._fetch_prices(symbol2, 252)

            if prices1 is None or prices2 is None:
                return {
                    'current_zscore': 0.0,
                    'spread_mean': 0.0,
                    'spread_std': 1.0
                }

            # Calculate spread
            df = pd.concat([prices1, prices2], axis=1).dropna()
            spread = df.iloc[:, 0] - hedge_ratio * df.iloc[:, 1]

            # Calculate z-score
            spread_mean = spread.mean()
            spread_std = spread.std()
            current_spread = spread.iloc[-1]
            current_zscore = (current_spread - spread_mean) / spread_std if spread_std > 0 else 0.0

            return {
                'current_zscore': float(current_zscore),
                'spread_mean': float(spread_mean),
                'spread_std': float(spread_std),
                'current_spread': float(current_spread)
            }

        except Exception as e:
            logger.error(f"Error calculating spread: {e}")
            return {
                'current_zscore': 0.0,
                'spread_mean': 0.0,
                'spread_std': 1.0
            }

    def _calculate_spread_history(self, symbol1: str, symbol2: str, hedge_ratio: float, lookback_days: int) -> Dict:
        """Calculate spread history with z-scores."""
        try:
            prices1 = self._fetch_prices(symbol1, lookback_days)
            prices2 = self._fetch_prices(symbol2, lookback_days)

            if prices1 is None or prices2 is None:
                return {
                    'current_zscore': 0.0,
                    'spread_mean': 0.0,
                    'spread_std': 1.0,
                    'history': []
                }

            # Calculate spread
            df = pd.concat([prices1, prices2], axis=1).dropna()
            spread = df.iloc[:, 0] - hedge_ratio * df.iloc[:, 1]

            # Calculate rolling z-scores
            spread_mean = spread.mean()
            spread_std = spread.std()

            history = []
            for idx, value in spread.items():
                zscore = (value - spread_mean) / spread_std if spread_std > 0 else 0.0
                history.append({
                    'date': idx.strftime('%Y-%m-%d'),
                    'spread': float(value),
                    'zscore': float(zscore)
                })

            current_zscore = history[-1]['zscore'] if history else 0.0

            return {
                'current_zscore': current_zscore,
                'spread_mean': float(spread_mean),
                'spread_std': float(spread_std),
                'history': history
            }

        except Exception as e:
            logger.error(f"Error calculating spread history: {e}")
            return {
                'current_zscore': 0.0,
                'spread_mean': 0.0,
                'spread_std': 1.0,
                'history': []
            }

    def _determine_signal(self, zscore: float) -> str:
        """
        Determine trading signal based on z-score.

        Z-score > 2.0: Short spread (short symbol1, long symbol2)
        Z-score < -2.0: Long spread (long symbol1, short symbol2)
        -0.5 < Z-score < 0.5: Exit/Close position
        """
        if zscore > 2.0:
            return 'short_spread'
        elif zscore < -2.0:
            return 'long_spread'
        elif -0.5 <= zscore <= 0.5:
            return 'exit'
        else:
            return 'hold'

    def _generate_interpretation(self, signal: str, zscore: float, half_life: Dict) -> str:
        """Generate human-readable interpretation."""
        interpretations = {
            'short_spread': f"Spread is overextended (z={zscore:.2f}). Consider shorting {signal} (short symbol1, long symbol2).",
            'long_spread': f"Spread is underextended (z={zscore:.2f}). Consider going long spread (long symbol1, short symbol2).",
            'exit': f"Spread near equilibrium (z={zscore:.2f}). Consider closing positions.",
            'hold': f"Spread at z={zscore:.2f}. Hold current positions or wait for stronger signal."
        }

        interpretation = interpretations.get(signal, "No clear signal.")

        if half_life.get('is_tradeable'):
            hl = half_life.get('half_life_days', 0)
            interpretation += f" Expected mean reversion in ~{hl*2.5:.0f} days."

        return interpretation

    # Mock methods for testing
    def _mock_pairs_scan(self, symbols: List[str], max_pairs: int) -> List[Dict]:
        """Generate mock pairs scan results."""
        pairs = []
        n_pairs = min(len(symbols) // 2, max_pairs)

        for i in range(n_pairs):
            idx1 = i * 2
            idx2 = i * 2 + 1

            if idx2 >= len(symbols):
                break

            zscore = np.random.uniform(-3, 3)

            pairs.append({
                'symbol1': symbols[idx1],
                'symbol2': symbols[idx2],
                'correlation': np.random.uniform(0.7, 0.95),
                'hedge_ratio': np.random.uniform(0.8, 1.2),
                'cointegration_pvalue': np.random.uniform(0.01, 0.04),
                'cointegration_confidence': '5%',
                'current_zscore': zscore,
                'spread_mean': 0.0,
                'spread_std': 1.0,
                'half_life_days': np.random.uniform(10, 25),
                'is_tradeable': True,
                'signal': self._determine_signal(zscore),
                'analysis_date': datetime.now().isoformat()
            })

        return pairs

    def _mock_pair_analysis(self, symbol1: str, symbol2: str) -> Dict:
        """Generate mock pair analysis."""
        zscore = np.random.uniform(-3, 3)
        half_life = np.random.uniform(10, 25)

        return {
            'symbol1': symbol1,
            'symbol2': symbol2,
            'correlation': np.random.uniform(0.7, 0.95),
            'hedge_ratio': np.random.uniform(0.8, 1.2),
            'cointegration': {
                'is_cointegrated': True,
                'p_value': 0.03,
                'confidence': '5%'
            },
            'half_life': {
                'half_life_days': half_life,
                'is_tradeable': True
            },
            'current_zscore': zscore,
            'spread_mean': 0.0,
            'spread_std': 1.0,
            'signal': self._determine_signal(zscore),
            'spread_history': [],
            'entry_threshold': 2.0,
            'exit_threshold': 0.5,
            'interpretation': self._generate_interpretation(
                self._determine_signal(zscore),
                zscore,
                {'is_tradeable': True, 'half_life_days': half_life}
            ),
            'analysis_date': datetime.now().isoformat()
        }


# Module-level instance
_pairs_trading = PairsTrading()


def scan_pairs(symbols: List[str], min_correlation: float = 0.7, max_pairs: int = 20) -> List[Dict]:
    """Scan universe for cointegrated pairs."""
    return _pairs_trading.scan_pairs(symbols, min_correlation, max_pairs)


def analyze_pair(symbol1: str, symbol2: str, lookback_days: int = 252) -> Dict:
    """Detailed analysis of a specific pair."""
    return _pairs_trading.analyze_pair(symbol1, symbol2, lookback_days)


def find_opportunities(symbols: List[str], min_zscore: float = 1.5) -> List[Dict]:
    """Find pairs with current trading opportunities."""
    return _pairs_trading.find_opportunities(symbols, min_zscore)
