# universe_manager.py - Stock Universe Management
# Manages different stock universes (S&P500, Russell2000, NASDAQ100, etc.)

import pandas as pd
import requests
from bs4 import BeautifulSoup
import yfinance as yf
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class UniverseManager:
    """
    Manages stock universes for screening.

    Provides access to various predefined universes (S&P 500, Russell 2000, etc.)
    and custom universe creation.
    """

    def __init__(self):
        self._cache = {}
        self._cache_expiry = {}

    def get_universe_tickers(self, universe_name: str) -> List[str]:
        """
        Get tickers for a named universe.

        Args:
            universe_name: Universe identifier
                - 'sp500': S&P 500
                - 'sp400': S&P MidCap 400
                - 'sp600': S&P SmallCap 600
                - 'nasdaq100': NASDAQ 100
                - 'russell2000': Russell 2000
                - 'dow30': Dow Jones 30
                - 'all': All available tickers

        Returns:
            List of ticker symbols
        """
        # Check cache
        if universe_name in self._cache:
            expiry = self._cache_expiry.get(universe_name, datetime.min)
            if datetime.now() < expiry:
                logger.info(f"Using cached universe: {universe_name}")
                return self._cache[universe_name]

        logger.info(f"Fetching universe: {universe_name}")

        # Fetch universe
        if universe_name == 'sp500':
            tickers = self._get_sp500_tickers()
        elif universe_name == 'sp400':
            tickers = self._get_sp400_tickers()
        elif universe_name == 'sp600':
            tickers = self._get_sp600_tickers()
        elif universe_name == 'nasdaq100':
            tickers = self._get_nasdaq100_tickers()
        elif universe_name == 'russell2000':
            tickers = self._get_russell2000_tickers()
        elif universe_name == 'dow30':
            tickers = self._get_dow30_tickers()
        elif universe_name == 'all':
            # Combine major indices
            tickers = list(set(
                self.get_universe_tickers('sp500') +
                self.get_universe_tickers('nasdaq100')
            ))
        else:
            raise ValueError(f"Unknown universe: {universe_name}")

        # Cache for 24 hours
        self._cache[universe_name] = tickers
        self._cache_expiry[universe_name] = datetime.now() + timedelta(hours=24)

        logger.info(f"Universe {universe_name}: {len(tickers)} tickers")
        return tickers

    def _get_sp500_tickers(self) -> List[str]:
        """
        Get S&P 500 tickers from Wikipedia.

        Returns:
            List of S&P 500 tickers
        """
        try:
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            table = soup.find('table', {'id': 'constituents'})
            tickers = []

            for row in table.findAll('tr')[1:]:
                ticker = row.findAll('td')[0].text.strip()
                tickers.append(ticker)

            return tickers

        except Exception as e:
            logger.error(f"Error fetching S&P 500 tickers: {e}")
            # Fallback to a subset
            return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B',
                   'UNH', 'JNJ', 'V', 'WMT', 'XOM', 'JPM', 'MA', 'PG', 'HD', 'CVX',
                   'MRK', 'ABBV', 'KO', 'PEP', 'COST', 'AVGO', 'LLY', 'TMO', 'MCD',
                   'CSCO', 'ACN', 'ABT', 'DHR', 'NKE', 'VZ', 'CRM', 'ADBE', 'TXN',
                   'NFLX', 'DIS', 'WFC', 'PM', 'ORCL', 'BMY', 'UPS', 'NEE', 'QCOM',
                   'RTX', 'HON', 'INTC', 'AMGN', 'IBM']

    def _get_sp400_tickers(self) -> List[str]:
        """
        Get S&P MidCap 400 tickers.

        Returns:
            List of tickers (placeholder)
        """
        # Placeholder - full implementation would fetch from data source
        logger.warning("S&P 400 universe using placeholder data")
        return []

    def _get_sp600_tickers(self) -> List[str]:
        """
        Get S&P SmallCap 600 tickers.

        Returns:
            List of tickers (placeholder)
        """
        # Placeholder
        logger.warning("S&P 600 universe using placeholder data")
        return []

    def _get_nasdaq100_tickers(self) -> List[str]:
        """
        Get NASDAQ 100 tickers.

        Returns:
            List of NASDAQ 100 tickers
        """
        try:
            url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            table = soup.find('table', {'id': 'constituents'})
            tickers = []

            for row in table.findAll('tr')[1:]:
                ticker = row.findAll('td')[1].text.strip()
                tickers.append(ticker)

            return tickers

        except Exception as e:
            logger.error(f"Error fetching NASDAQ 100 tickers: {e}")
            # Fallback
            return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO',
                   'COST', 'NFLX', 'ADBE', 'CSCO', 'PEP', 'INTC', 'CMCSA', 'TXN',
                   'QCOM', 'AMGN', 'HON', 'SBUX', 'INTU', 'AMAT', 'AMD', 'GILD',
                   'ISRG', 'BKNG', 'ADP', 'MDLZ', 'VRTX', 'ADI']

    def _get_russell2000_tickers(self) -> List[str]:
        """
        Get Russell 2000 tickers.

        Returns:
            List of tickers (placeholder)
        """
        # Placeholder - full implementation would use a data provider
        logger.warning("Russell 2000 universe using placeholder data")
        return []

    def _get_dow30_tickers(self) -> List[str]:
        """
        Get Dow Jones 30 tickers.

        Returns:
            List of Dow 30 tickers
        """
        return [
            'AAPL', 'AMGN', 'AXP', 'BA', 'CAT', 'CRM', 'CSCO', 'CVX', 'DIS', 'DOW',
            'GS', 'HD', 'HON', 'IBM', 'INTC', 'JNJ', 'JPM', 'KO', 'MCD', 'MMM',
            'MRK', 'MSFT', 'NKE', 'PG', 'TRV', 'UNH', 'V', 'VZ', 'WBA', 'WMT'
        ]

    def filter_by_criteria(self,
                          tickers: List[str],
                          min_price: Optional[float] = None,
                          max_price: Optional[float] = None,
                          min_volume: Optional[float] = None,
                          min_market_cap: Optional[float] = None,
                          max_market_cap: Optional[float] = None,
                          sectors: Optional[List[str]] = None) -> List[str]:
        """
        Filter tickers by criteria.

        Args:
            tickers: List of tickers to filter
            min_price: Minimum stock price
            max_price: Maximum stock price
            min_volume: Minimum average daily volume
            min_market_cap: Minimum market cap
            max_market_cap: Maximum market cap
            sectors: List of sectors to include

        Returns:
            Filtered list of tickers
        """
        logger.info(f"Filtering {len(tickers)} tickers by criteria")

        filtered = []

        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info

                # Price filter
                current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                if min_price and current_price < min_price:
                    continue
                if max_price and current_price > max_price:
                    continue

                # Volume filter
                avg_volume = info.get('averageVolume', info.get('volume', 0))
                if min_volume and avg_volume < min_volume:
                    continue

                # Market cap filter
                market_cap = info.get('marketCap', 0)
                if min_market_cap and market_cap < min_market_cap:
                    continue
                if max_market_cap and market_cap > max_market_cap:
                    continue

                # Sector filter
                if sectors:
                    stock_sector = info.get('sector', '')
                    if stock_sector not in sectors:
                        continue

                filtered.append(ticker)

            except Exception as e:
                logger.warning(f"Error filtering {ticker}: {e}")
                continue

        logger.info(f"Filtered to {len(filtered)} tickers")
        return filtered

    def create_custom_universe(self, tickers: List[str]) -> List[str]:
        """
        Create a custom universe from a list of tickers.

        Args:
            tickers: List of ticker symbols

        Returns:
            Validated list of tickers
        """
        logger.info(f"Creating custom universe with {len(tickers)} tickers")

        validated = []

        for ticker in tickers:
            try:
                # Validate ticker exists
                stock = yf.Ticker(ticker)
                info = stock.info

                if 'symbol' in info or 'regularMarketPrice' in info:
                    validated.append(ticker)
                else:
                    logger.warning(f"Invalid ticker: {ticker}")

            except Exception as e:
                logger.warning(f"Error validating {ticker}: {e}")

        logger.info(f"Validated {len(validated)} tickers")
        return validated

    def get_universe_by_market_cap(self,
                                   min_cap: float = 0,
                                   max_cap: float = float('inf'),
                                   base_universe: str = 'sp500') -> List[str]:
        """
        Filter universe by market cap tiers.

        Args:
            min_cap: Minimum market cap in billions
            max_cap: Maximum market cap in billions
            base_universe: Base universe to filter

        Returns:
            Filtered tickers
        """
        tickers = self.get_universe_tickers(base_universe)

        return self.filter_by_criteria(
            tickers,
            min_market_cap=min_cap * 1e9,
            max_market_cap=max_cap * 1e9
        )

    def get_mega_caps(self) -> List[str]:
        """Get mega-cap stocks (>$200B market cap)."""
        return self.get_universe_by_market_cap(min_cap=200, base_universe='sp500')

    def get_large_caps(self) -> List[str]:
        """Get large-cap stocks ($10B-$200B market cap)."""
        return self.get_universe_by_market_cap(min_cap=10, max_cap=200, base_universe='sp500')

    def get_mid_caps(self) -> List[str]:
        """Get mid-cap stocks ($2B-$10B market cap)."""
        return self.get_universe_by_market_cap(min_cap=2, max_cap=10, base_universe='sp400')

    def get_small_caps(self) -> List[str]:
        """Get small-cap stocks (<$2B market cap)."""
        return self.get_universe_by_market_cap(max_cap=2, base_universe='sp600')

    def get_universe_info(self, universe_name: str) -> Dict:
        """
        Get information about a universe.

        Args:
            universe_name: Universe identifier

        Returns:
            Universe metadata
        """
        tickers = self.get_universe_tickers(universe_name)

        return {
            'name': universe_name,
            'ticker_count': len(tickers),
            'tickers': tickers[:10],  # Sample
            'last_updated': datetime.now().isoformat()
        }

    def list_available_universes(self) -> List[Dict]:
        """
        List all available universes.

        Returns:
            List of universe metadata
        """
        universes = [
            {'id': 'sp500', 'name': 'S&P 500', 'description': 'Large-cap US stocks'},
            {'id': 'sp400', 'name': 'S&P MidCap 400', 'description': 'Mid-cap US stocks'},
            {'id': 'sp600', 'name': 'S&P SmallCap 600', 'description': 'Small-cap US stocks'},
            {'id': 'nasdaq100', 'name': 'NASDAQ 100', 'description': 'Top 100 NASDAQ stocks'},
            {'id': 'russell2000', 'name': 'Russell 2000', 'description': 'Small-cap index'},
            {'id': 'dow30', 'name': 'Dow Jones 30', 'description': '30 blue-chip stocks'},
            {'id': 'all', 'name': 'All Stocks', 'description': 'Combined universe'},
        ]

        return universes
