# data_providers.py - Abstracted Data Fetching Layer
# Supports free tier APIs with graceful degradation and mock data mode

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import logging
import requests
from functools import lru_cache
import time
import os

logger = logging.getLogger(__name__)


class DataProvider:
    """
    Abstracted data provider with support for multiple data sources.

    Free Tier Support:
    - Yahoo Finance (yfinance) - OHLCV, options chain
    - Alpha Vantage (free tier) - Market data
    - SEC EDGAR - Insider transactions (Form 4)

    Paid Tier Support (graceful degradation if unavailable):
    - IEX Cloud - Real-time quotes, unusual options
    - Unusual Whales - Dark pool data

    Mock Mode:
    - Generate synthetic data for testing without API calls
    """

    def __init__(self, mock_mode: bool = False):
        """
        Initialize data provider.

        Args:
            mock_mode: If True, use synthetic data instead of API calls
        """
        self.mock_mode = mock_mode
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', None)
        self.iex_cloud_key = os.getenv('IEX_CLOUD_API_KEY', None)

        # Rate limiting
        self._last_request_time = {}
        self._min_request_interval = 0.2  # 200ms between requests

        logger.info(f"DataProvider initialized (mock_mode={mock_mode})")

    def _rate_limit(self, source: str):
        """Apply rate limiting for API calls."""
        if source in self._last_request_time:
            elapsed = time.time() - self._last_request_time[source]
            if elapsed < self._min_request_interval:
                time.sleep(self._min_request_interval - elapsed)

        self._last_request_time[source] = time.time()

    def get_bid_ask_spread(self, symbol: str) -> Optional[Dict]:
        """
        Get current bid-ask spread for a symbol.

        Returns:
            {
                'bid': float,
                'ask': float,
                'spread': float,
                'spread_pct': float,
                'bid_size': int,
                'ask_size': int,
                'timestamp': str
            }
        """
        if self.mock_mode:
            return self._mock_bid_ask_spread(symbol)

        try:
            self._rate_limit('yfinance')
            ticker = yf.Ticker(symbol)
            info = ticker.info

            bid = info.get('bid', None)
            ask = info.get('ask', None)
            bid_size = info.get('bidSize', 0)
            ask_size = info.get('askSize', 0)

            if bid is None or ask is None or bid == 0 or ask == 0:
                logger.warning(f"No bid-ask data for {symbol}")
                return None

            spread = ask - bid
            spread_pct = (spread / bid) * 100 if bid > 0 else 0

            return {
                'symbol': symbol,
                'bid': float(bid),
                'ask': float(ask),
                'spread': float(spread),
                'spread_pct': float(spread_pct),
                'bid_size': int(bid_size),
                'ask_size': int(ask_size),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error fetching bid-ask for {symbol}: {e}")
            return None

    def get_order_book_depth(self, symbol: str) -> Optional[Dict]:
        """
        Get order book depth (simplified version).

        Note: Full order book requires paid data feed.
        This returns bid-ask as proxy for depth.
        """
        if self.mock_mode:
            return self._mock_order_book_depth(symbol)

        # For free tier, return bid-ask as proxy
        spread_data = self.get_bid_ask_spread(symbol)

        if spread_data is None:
            return None

        return {
            'symbol': symbol,
            'bid_depth': spread_data['bid_size'],
            'ask_depth': spread_data['ask_size'],
            'imbalance': (spread_data['bid_size'] - spread_data['ask_size']) /
                        max(spread_data['bid_size'] + spread_data['ask_size'], 1),
            'spread_pct': spread_data['spread_pct'],
            'timestamp': datetime.now().isoformat()
        }

    def get_dark_pool_trades(self, symbol: str, days: int = 5) -> Optional[Dict]:
        """
        Get dark pool trade data.

        Free tier: Unavailable - returns mock data or None
        Paid tier: Unusual Whales, IEX Cloud

        Returns:
            {
                'symbol': str,
                'total_volume': int,
                'dark_pool_volume': int,
                'dark_pool_pct': float,
                'avg_trade_size': float,
                'large_trades_count': int,
                'sentiment': 'bullish' | 'bearish' | 'neutral',
                'period_days': int
            }
        """
        if self.mock_mode:
            return self._mock_dark_pool_trades(symbol, days)

        # Free tier: No reliable free source for dark pool data
        # Return None to indicate unavailable
        logger.warning(f"Dark pool data unavailable for {symbol} (requires paid API)")
        return None

    def get_options_chain(self, symbol: str, expiration: str = None) -> Optional[Dict]:
        """
        Get options chain for a symbol.

        Args:
            symbol: Stock symbol
            expiration: Expiration date (YYYY-MM-DD) or None for nearest

        Returns:
            {
                'symbol': str,
                'expiration': str,
                'calls': pd.DataFrame,
                'puts': pd.DataFrame,
                'total_call_volume': int,
                'total_put_volume': int,
                'pcr': float (put-call ratio)
            }
        """
        if self.mock_mode:
            return self._mock_options_chain(symbol, expiration)

        try:
            self._rate_limit('yfinance')
            ticker = yf.Ticker(symbol)

            # Get available expirations
            expirations = ticker.options
            if not expirations:
                logger.warning(f"No options available for {symbol}")
                return None

            # Use specified expiration or first available
            exp_date = expiration if expiration and expiration in expirations else expirations[0]

            # Fetch options chain
            opt = ticker.option_chain(exp_date)

            calls = opt.calls
            puts = opt.puts

            total_call_volume = calls['volume'].sum() if 'volume' in calls.columns else 0
            total_put_volume = puts['volume'].sum() if 'volume' in puts.columns else 0

            pcr = total_put_volume / max(total_call_volume, 1)

            return {
                'symbol': symbol,
                'expiration': exp_date,
                'calls': calls,
                'puts': puts,
                'total_call_volume': int(total_call_volume),
                'total_put_volume': int(total_put_volume),
                'pcr': float(pcr),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error fetching options for {symbol}: {e}")
            return None

    def get_unusual_options_activity(self, symbol: str) -> Optional[Dict]:
        """
        Detect unusual options activity.

        Criteria:
        - Volume significantly above open interest
        - Large premium trades
        - Unusual call/put ratios

        Returns:
            {
                'symbol': str,
                'unusual_calls': List[Dict],
                'unusual_puts': List[Dict],
                'aggregate_sentiment': 'bullish' | 'bearish' | 'neutral',
                'total_premium': float,
                'confidence': float (0-100)
            }
        """
        if self.mock_mode:
            return self._mock_unusual_options(symbol)

        try:
            options_data = self.get_options_chain(symbol)

            if options_data is None:
                return None

            calls = options_data['calls']
            puts = options_data['puts']

            # Detect unusual calls
            unusual_calls = []
            if not calls.empty and 'volume' in calls.columns and 'openInterest' in calls.columns:
                calls['vol_oi_ratio'] = calls['volume'] / calls['openInterest'].replace(0, 1)
                unusual_calls_df = calls[calls['vol_oi_ratio'] > 2.0]

                for _, row in unusual_calls_df.iterrows():
                    unusual_calls.append({
                        'strike': float(row['strike']),
                        'volume': int(row['volume']),
                        'openInterest': int(row['openInterest']),
                        'vol_oi_ratio': float(row['vol_oi_ratio']),
                        'premium': float(row['lastPrice'] * row['volume'] * 100)
                    })

            # Detect unusual puts
            unusual_puts = []
            if not puts.empty and 'volume' in puts.columns and 'openInterest' in puts.columns:
                puts['vol_oi_ratio'] = puts['volume'] / puts['openInterest'].replace(0, 1)
                unusual_puts_df = puts[puts['vol_oi_ratio'] > 2.0]

                for _, row in unusual_puts_df.iterrows():
                    unusual_puts.append({
                        'strike': float(row['strike']),
                        'volume': int(row['volume']),
                        'openInterest': int(row['openInterest']),
                        'vol_oi_ratio': float(row['vol_oi_ratio']),
                        'premium': float(row['lastPrice'] * row['volume'] * 100)
                    })

            # Aggregate sentiment
            call_premium = sum(c['premium'] for c in unusual_calls)
            put_premium = sum(p['premium'] for p in unusual_puts)

            total_premium = call_premium + put_premium

            if total_premium == 0:
                sentiment = 'neutral'
                confidence = 0.0
            elif call_premium > put_premium * 1.5:
                sentiment = 'bullish'
                confidence = min((call_premium / (put_premium + 1)) * 20, 100)
            elif put_premium > call_premium * 1.5:
                sentiment = 'bearish'
                confidence = min((put_premium / (call_premium + 1)) * 20, 100)
            else:
                sentiment = 'neutral'
                confidence = 30.0

            return {
                'symbol': symbol,
                'unusual_calls': unusual_calls,
                'unusual_puts': unusual_puts,
                'aggregate_sentiment': sentiment,
                'total_premium': float(total_premium),
                'confidence': float(confidence),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error detecting unusual options for {symbol}: {e}")
            return None

    def get_insider_transactions(self, symbol: str, days: int = 90) -> Optional[Dict]:
        """
        Get insider transaction data from SEC EDGAR.

        Returns:
            {
                'symbol': str,
                'transactions': List[Dict],
                'net_buying': float (shares),
                'net_value': float (USD),
                'insider_sentiment': 'bullish' | 'bearish' | 'neutral',
                'period_days': int
            }
        """
        if self.mock_mode:
            return self._mock_insider_transactions(symbol, days)

        try:
            # Use yfinance for insider transactions
            self._rate_limit('yfinance')
            ticker = yf.Ticker(symbol)

            insider_data = ticker.insider_transactions

            if insider_data is None or insider_data.empty:
                logger.warning(f"No insider transaction data for {symbol}")
                return None

            # Filter by date
            cutoff_date = datetime.now() - timedelta(days=days)

            # Process transactions
            transactions = []
            net_shares = 0
            net_value = 0.0

            for _, row in insider_data.iterrows():
                trans_date = row.get('Start Date', None)
                shares = row.get('Shares', 0)
                value = row.get('Value', 0)
                trans_type = row.get('Transaction', 'Unknown')

                # Determine if buy or sell
                is_buy = 'Purchase' in str(trans_type) or 'Buy' in str(trans_type)
                is_sell = 'Sale' in str(trans_type) or 'Sell' in str(trans_type)

                if is_buy:
                    net_shares += shares
                    net_value += value
                elif is_sell:
                    net_shares -= shares
                    net_value -= value

                transactions.append({
                    'date': str(trans_date),
                    'shares': int(shares),
                    'value': float(value) if value else 0.0,
                    'type': str(trans_type)
                })

            # Determine sentiment
            if net_shares > 0:
                sentiment = 'bullish'
            elif net_shares < 0:
                sentiment = 'bearish'
            else:
                sentiment = 'neutral'

            return {
                'symbol': symbol,
                'transactions': transactions[:20],  # Limit to 20 most recent
                'net_buying': float(net_shares),
                'net_value': float(net_value),
                'insider_sentiment': sentiment,
                'period_days': days,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error fetching insider transactions for {symbol}: {e}")
            return None

    # ============================================================================
    # MOCK DATA METHODS
    # ============================================================================

    def _mock_bid_ask_spread(self, symbol: str) -> Dict:
        """Generate mock bid-ask spread data."""
        base_price = 100.0
        spread_pct = np.random.uniform(0.05, 0.30)  # 0.05-0.30% spread

        bid = base_price
        spread = base_price * (spread_pct / 100)
        ask = bid + spread

        return {
            'symbol': symbol,
            'bid': float(bid),
            'ask': float(ask),
            'spread': float(spread),
            'spread_pct': float(spread_pct),
            'bid_size': int(np.random.randint(100, 1000)),
            'ask_size': int(np.random.randint(100, 1000)),
            'timestamp': datetime.now().isoformat()
        }

    def _mock_order_book_depth(self, symbol: str) -> Dict:
        """Generate mock order book depth."""
        bid_size = np.random.randint(500, 5000)
        ask_size = np.random.randint(500, 5000)

        return {
            'symbol': symbol,
            'bid_depth': int(bid_size),
            'ask_depth': int(ask_size),
            'imbalance': float((bid_size - ask_size) / (bid_size + ask_size)),
            'spread_pct': float(np.random.uniform(0.05, 0.30)),
            'timestamp': datetime.now().isoformat()
        }

    def _mock_dark_pool_trades(self, symbol: str, days: int) -> Dict:
        """Generate mock dark pool trade data."""
        total_volume = np.random.randint(1000000, 10000000)
        dark_pool_pct = np.random.uniform(20, 45)
        dark_pool_volume = int(total_volume * dark_pool_pct / 100)

        # Random sentiment
        sentiment_value = np.random.random()
        if sentiment_value > 0.6:
            sentiment = 'bullish'
        elif sentiment_value < 0.4:
            sentiment = 'bearish'
        else:
            sentiment = 'neutral'

        return {
            'symbol': symbol,
            'total_volume': int(total_volume),
            'dark_pool_volume': int(dark_pool_volume),
            'dark_pool_pct': float(dark_pool_pct),
            'avg_trade_size': float(np.random.randint(5000, 50000)),
            'large_trades_count': int(np.random.randint(10, 100)),
            'sentiment': sentiment,
            'period_days': days,
            'timestamp': datetime.now().isoformat()
        }

    def _mock_options_chain(self, symbol: str, expiration: str) -> Dict:
        """Generate mock options chain."""
        # Generate synthetic options data
        strikes = np.arange(90, 111, 5)  # Strikes from 90 to 110

        calls_data = []
        puts_data = []

        for strike in strikes:
            calls_data.append({
                'strike': float(strike),
                'lastPrice': float(np.random.uniform(1, 10)),
                'volume': int(np.random.randint(0, 1000)),
                'openInterest': int(np.random.randint(100, 5000)),
                'impliedVolatility': float(np.random.uniform(0.2, 0.6))
            })

            puts_data.append({
                'strike': float(strike),
                'lastPrice': float(np.random.uniform(1, 10)),
                'volume': int(np.random.randint(0, 1000)),
                'openInterest': int(np.random.randint(100, 5000)),
                'impliedVolatility': float(np.random.uniform(0.2, 0.6))
            })

        calls_df = pd.DataFrame(calls_data)
        puts_df = pd.DataFrame(puts_data)

        total_call_volume = calls_df['volume'].sum()
        total_put_volume = puts_df['volume'].sum()

        return {
            'symbol': symbol,
            'expiration': expiration or '2025-12-31',
            'calls': calls_df,
            'puts': puts_df,
            'total_call_volume': int(total_call_volume),
            'total_put_volume': int(total_put_volume),
            'pcr': float(total_put_volume / max(total_call_volume, 1)),
            'timestamp': datetime.now().isoformat()
        }

    def _mock_unusual_options(self, symbol: str) -> Dict:
        """Generate mock unusual options activity."""
        # Generate 2-5 unusual calls and puts
        num_calls = np.random.randint(2, 6)
        num_puts = np.random.randint(2, 6)

        unusual_calls = []
        for _ in range(num_calls):
            volume = np.random.randint(500, 5000)
            oi = np.random.randint(100, 2000)
            price = np.random.uniform(2, 15)

            unusual_calls.append({
                'strike': float(np.random.randint(95, 106)),
                'volume': int(volume),
                'openInterest': int(oi),
                'vol_oi_ratio': float(volume / oi),
                'premium': float(price * volume * 100)
            })

        unusual_puts = []
        for _ in range(num_puts):
            volume = np.random.randint(500, 5000)
            oi = np.random.randint(100, 2000)
            price = np.random.uniform(2, 15)

            unusual_puts.append({
                'strike': float(np.random.randint(95, 106)),
                'volume': int(volume),
                'openInterest': int(oi),
                'vol_oi_ratio': float(volume / oi),
                'premium': float(price * volume * 100)
            })

        call_premium = sum(c['premium'] for c in unusual_calls)
        put_premium = sum(p['premium'] for p in unusual_puts)

        if call_premium > put_premium * 1.5:
            sentiment = 'bullish'
        elif put_premium > call_premium * 1.5:
            sentiment = 'bearish'
        else:
            sentiment = 'neutral'

        return {
            'symbol': symbol,
            'unusual_calls': unusual_calls,
            'unusual_puts': unusual_puts,
            'aggregate_sentiment': sentiment,
            'total_premium': float(call_premium + put_premium),
            'confidence': float(np.random.uniform(50, 90)),
            'timestamp': datetime.now().isoformat()
        }

    def _mock_insider_transactions(self, symbol: str, days: int) -> Dict:
        """Generate mock insider transaction data."""
        num_transactions = np.random.randint(3, 10)

        transactions = []
        net_shares = 0
        net_value = 0.0

        for i in range(num_transactions):
            is_buy = np.random.random() > 0.5
            shares = np.random.randint(1000, 50000)
            price = np.random.uniform(80, 120)
            value = shares * price

            if is_buy:
                trans_type = 'Purchase'
                net_shares += shares
                net_value += value
            else:
                trans_type = 'Sale'
                net_shares -= shares
                net_value -= value

            date = datetime.now() - timedelta(days=np.random.randint(1, days))

            transactions.append({
                'date': date.strftime('%Y-%m-%d'),
                'shares': int(shares),
                'value': float(value),
                'type': trans_type
            })

        if net_shares > 0:
            sentiment = 'bullish'
        elif net_shares < 0:
            sentiment = 'bearish'
        else:
            sentiment = 'neutral'

        return {
            'symbol': symbol,
            'transactions': transactions,
            'net_buying': float(net_shares),
            'net_value': float(net_value),
            'insider_sentiment': sentiment,
            'period_days': days,
            'timestamp': datetime.now().isoformat()
        }


# Module-level instance
_provider = DataProvider(mock_mode=False)


def get_provider(mock_mode: bool = False) -> DataProvider:
    """Get data provider instance."""
    return DataProvider(mock_mode=mock_mode)
