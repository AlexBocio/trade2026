"""
Multi-Exchange Market Gateway - Extended Version
Supports multiple exchanges simultaneously
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any
import ccxt.async_support as ccxt
from cryptofeed import FeedHandler
from cryptofeed.callback import BookCallback, TradeCallback
from cryptofeed.defines import BID, ASK, TRADES, L2_BOOK
from cryptofeed.exchanges import (
    Binance, Coinbase, Kraken, Bitfinex, Gemini,
    OKX, Bybit, Huobi, GateIo, KuCoin
)

logger = logging.getLogger(__name__)

class MultiExchangeGateway:
    """Gateway supporting multiple exchanges"""

    # Exchange mappings for CCXT
    CCXT_EXCHANGES = {
        'binance': ccxt.binance,
        'coinbase': ccxt.coinbase,
        'kraken': ccxt.kraken,
        'bitfinex': ccxt.bitfinex,
        'okx': ccxt.okx,
        'bybit': ccxt.bybit,
        'huobi': ccxt.huobi,
        'gateio': ccxt.gateio,
        'kucoin': ccxt.kucoin,
        'gemini': ccxt.gemini,
        'bitstamp': ccxt.bitstamp,
        'bitget': ccxt.bitget,
        'mexc': ccxt.mexc,
        'cryptocom': ccxt.cryptocom,
        'phemex': ccxt.phemex,
    }

    # Exchange mappings for CryptoFeed
    CRYPTOFEED_EXCHANGES = {
        'binance': Binance,
        'coinbase': Coinbase,
        'kraken': Kraken,
        'bitfinex': Bitfinex,
        'okx': OKX,
        'bybit': Bybit,
        'huobi': Huobi,
        'gateio': GateIo,
        'kucoin': KuCoin,
        'gemini': Gemini,
    }

    # Symbol format mappings
    SYMBOL_MAPPINGS = {
        'binance': lambda s: s.replace('/', ''),      # BTC/USDT -> BTCUSDT
        'coinbase': lambda s: s.replace('/', '-'),    # BTC/USDT -> BTC-USDT
        'kraken': lambda s: s.replace('BTC/', 'XBT/'), # BTC/USD -> XBT/USD
        'bitfinex': lambda s: 't' + s.replace('/', ''), # BTC/USDT -> tBTCUSDT
        'okx': lambda s: s.replace('/', '-'),         # BTC/USDT -> BTC-USDT
        'bybit': lambda s: s.replace('/', ''),        # BTC/USDT -> BTCUSDT
    }

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.exchanges = {}
        self.feed_handler = FeedHandler()
        self.active_exchanges = []

    async def initialize_exchanges(self):
        """Initialize all configured exchanges"""

        exchanges_config = self.config.get('exchanges', [])

        for exchange_config in exchanges_config:
            exchange_name = exchange_config['name']
            if not exchange_config.get('enabled', True):
                logger.info(f"Skipping disabled exchange: {exchange_name}")
                continue

            try:
                # Initialize CCXT exchange
                if exchange_name in self.CCXT_EXCHANGES:
                    exchange_class = self.CCXT_EXCHANGES[exchange_name]

                    # Exchange-specific options
                    options = {
                        'enableRateLimit': True,
                        'rateLimit': exchange_config.get('rate_limit', 50),
                    }

                    # Add API credentials if provided
                    if 'api_key' in exchange_config:
                        options['apiKey'] = exchange_config['api_key']
                        options['secret'] = exchange_config.get('api_secret', '')

                    # Special handling for different exchanges
                    if exchange_name == 'binance':
                        options['options'] = {'defaultType': 'spot'}
                    elif exchange_name == 'coinbase':
                        options['required_credentials'] = False
                    elif exchange_name == 'kraken':
                        options['tier'] = exchange_config.get('tier', 'Starter')

                    exchange = exchange_class(options)
                    await exchange.load_markets()

                    self.exchanges[exchange_name] = {
                        'ccxt': exchange,
                        'symbols': exchange_config.get('symbols', []),
                        'config': exchange_config
                    }

                    logger.info(f"Initialized {exchange_name} with {len(exchange_config.get('symbols', []))} symbols")

                    # Setup WebSocket feeds if available
                    if exchange_name in self.CRYPTOFEED_EXCHANGES:
                        self.setup_websocket_feed(exchange_name, exchange_config)

                    self.active_exchanges.append(exchange_name)

                else:
                    logger.warning(f"Exchange {exchange_name} not supported")

            except Exception as e:
                logger.error(f"Failed to initialize {exchange_name}: {e}")

    def setup_websocket_feed(self, exchange_name: str, config: Dict):
        """Setup WebSocket feed for an exchange"""

        if exchange_name not in self.CRYPTOFEED_EXCHANGES:
            return

        exchange_class = self.CRYPTOFEED_EXCHANGES[exchange_name]
        symbols = []

        # Convert symbols to exchange format
        for symbol in config.get('symbols', []):
            if exchange_name in self.SYMBOL_MAPPINGS:
                cf_symbol = self.SYMBOL_MAPPINGS[exchange_name](symbol)
            else:
                cf_symbol = symbol.replace('/', '-')
            symbols.append(cf_symbol)

        # Add feed with callbacks
        self.feed_handler.add_feed(
            exchange_class(
                channels=[L2_BOOK, TRADES],
                symbols=symbols,
                callbacks={
                    L2_BOOK: BookCallback(self.book_callback),
                    TRADES: TradeCallback(self.trade_callback)
                }
            )
        )

        logger.info(f"WebSocket feed configured for {exchange_name}: {symbols}")

    async def book_callback(self, data, receipt_timestamp):
        """Handle order book updates"""
        # Process and publish to NATS with exchange prefix
        exchange_name = data.exchange.lower()
        topic = f"market.tick.{exchange_name}.{data.symbol.replace('-', '')}"
        # ... publish logic

    async def trade_callback(self, data, receipt_timestamp):
        """Handle trade updates"""
        # Process and publish to NATS with exchange prefix
        exchange_name = data.exchange.lower()
        topic = f"market.tick.{exchange_name}.{data.symbol.replace('-', '')}"
        # ... publish logic

    async def fetch_all_exchanges(self):
        """Fetch data from all exchanges concurrently"""

        tasks = []
        for exchange_name, exchange_data in self.exchanges.items():
            task = self.fetch_exchange_data(exchange_name, exchange_data)
            tasks.append(task)

        await asyncio.gather(*tasks)

    async def fetch_exchange_data(self, exchange_name: str, exchange_data: Dict):
        """Fetch data from a single exchange"""

        exchange = exchange_data['ccxt']
        symbols = exchange_data['symbols']

        while True:
            try:
                for symbol in symbols:
                    try:
                        ticker = await exchange.fetch_ticker(symbol)

                        # Publish with exchange prefix
                        normalized_symbol = symbol.replace('/', '')
                        topic = f"market.tick.{exchange_name}.{normalized_symbol}"

                        tick_data = {
                            'exchange': exchange_name,
                            'symbol': symbol,
                            'timestamp': ticker.get('timestamp', int(time.time() * 1000)),
                            'bid': ticker.get('bid', 0.0),
                            'ask': ticker.get('ask', 0.0),
                            'last': ticker.get('last', 0.0),
                            'volume': ticker.get('baseVolume', 0.0)
                        }

                        # Publish to NATS, insert to QuestDB, cache in Valkey
                        await self.publish_tick(topic, tick_data)

                    except Exception as e:
                        logger.error(f"Failed to fetch {symbol} from {exchange_name}: {e}")

                    # Small delay between symbols
                    await asyncio.sleep(0.5)

                # Exchange-specific refresh interval
                interval = exchange_data['config'].get('refresh_interval', 5)
                await asyncio.sleep(interval)

            except Exception as e:
                logger.error(f"Error in {exchange_name} fetch loop: {e}")
                await asyncio.sleep(10)

    async def publish_tick(self, topic: str, tick_data: Dict):
        """Publish tick to NATS, QuestDB, and Valkey"""
        # Implementation would go here
        logger.debug(f"Publishing to {topic}: {tick_data}")

    def get_statistics(self) -> Dict:
        """Get statistics for all exchanges"""

        stats = {
            'active_exchanges': self.active_exchanges,
            'total_exchanges': len(self.exchanges),
            'exchange_details': {}
        }

        for exchange_name, exchange_data in self.exchanges.items():
            stats['exchange_details'][exchange_name] = {
                'symbols': exchange_data['symbols'],
                'connected': exchange_data['ccxt'].has['watchOrderBook'] if 'ccxt' in exchange_data else False
            }

        return stats


# Example configuration for multiple exchanges
MULTI_EXCHANGE_CONFIG = {
    'exchanges': [
        {
            'name': 'binance',
            'enabled': True,
            'symbols': ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'],
            'rate_limit': 50,  # requests per second
            'refresh_interval': 5,
        },
        {
            'name': 'coinbase',
            'enabled': True,
            'symbols': ['BTC/USD', 'ETH/USD', 'SOL/USD'],
            'rate_limit': 10,
            'refresh_interval': 3,
        },
        {
            'name': 'kraken',
            'enabled': True,
            'symbols': ['BTC/USD', 'ETH/USD', 'SOL/USD'],
            'rate_limit': 15,
            'refresh_interval': 5,
            'tier': 'Intermediate',
        },
        {
            'name': 'bybit',
            'enabled': True,
            'symbols': ['BTC/USDT', 'ETH/USDT'],
            'rate_limit': 50,
            'refresh_interval': 2,
        },
        {
            'name': 'okx',
            'enabled': True,
            'symbols': ['BTC/USDT', 'ETH/USDT'],
            'rate_limit': 20,
            'refresh_interval': 3,
        },
        {
            'name': 'gateio',
            'enabled': False,  # Disabled example
            'symbols': ['BTC/USDT', 'ETH/USDT'],
            'rate_limit': 10,
            'refresh_interval': 5,
        },
        {
            'name': 'kucoin',
            'enabled': True,
            'symbols': ['BTC/USDT', 'ETH/USDT'],
            'rate_limit': 30,
            'refresh_interval': 4,
        },
        {
            'name': 'huobi',
            'enabled': True,
            'symbols': ['BTC/USDT', 'ETH/USDT'],
            'rate_limit': 10,
            'refresh_interval': 5,
        },
        {
            'name': 'bitfinex',
            'enabled': True,
            'symbols': ['BTC/USD', 'ETH/USD'],
            'rate_limit': 30,
            'refresh_interval': 3,
        },
        {
            'name': 'gemini',
            'enabled': True,
            'symbols': ['BTC/USD', 'ETH/USD'],
            'rate_limit': 5,
            'refresh_interval': 10,
        }
    ]
}


async def main():
    """Example usage"""

    # Initialize gateway with multiple exchanges
    gateway = MultiExchangeGateway(MULTI_EXCHANGE_CONFIG)

    # Initialize all exchanges
    await gateway.initialize_exchanges()

    # Start WebSocket feeds
    if gateway.feed_handler:
        asyncio.create_task(asyncio.to_thread(gateway.feed_handler.run))

    # Start REST data fetching for all exchanges
    await gateway.fetch_all_exchanges()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())