# screener_engine.py - Main Screening Engine
# Orchestrates factor calculation, scoring, and ranking

import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from factor_library import calculate_all_factors
from composite_scoring import calculate_composite_score, rank_stocks_by_factors, normalize_factors
from timeframe_strategies import get_strategy, apply_strategy_filters, list_strategies
from universe_manager import UniverseManager

logger = logging.getLogger(__name__)


class ScreenerEngine:
    """
    Main screening engine.

    Orchestrates the entire screening workflow:
    1. Get universe
    2. Calculate factors for all stocks
    3. Apply strategy filters
    4. Score and rank stocks
    """

    def __init__(self, max_workers: int = 10):
        """
        Initialize screener engine.

        Args:
            max_workers: Maximum parallel workers for factor calculation
        """
        self.universe_manager = UniverseManager()
        self.max_workers = max_workers
        logger.info(f"ScreenerEngine initialized with {max_workers} workers")

    def screen_universe(self,
                       universe_name: str = 'sp500',
                       strategy_name: str = 'swing',
                       top_n: int = 50,
                       custom_tickers: Optional[List[str]] = None) -> Dict:
        """
        Screen a universe and return top-ranked stocks.

        Args:
            universe_name: Universe to screen ('sp500', 'nasdaq100', etc.)
            strategy_name: Strategy to use ('swing', 'intraday', 'position', etc.)
            top_n: Number of top stocks to return
            custom_tickers: Optional custom ticker list (overrides universe_name)

        Returns:
            {
                'strategy': Strategy name,
                'universe': Universe name,
                'timestamp': Screening timestamp,
                'total_stocks': Total stocks screened,
                'top_stocks': [
                    {
                        'ticker': Ticker symbol,
                        'rank': Rank (1-indexed),
                        'composite_score': Composite score,
                        'factors': {factor_name: value, ...},
                        'current_price': Current price,
                    },
                    ...
                ]
            }
        """
        logger.info(f"Screening universe={universe_name}, strategy={strategy_name}, top_n={top_n}")

        start_time = datetime.now()

        # Get strategy configuration
        strategy = get_strategy(strategy_name)

        # Get universe tickers
        if custom_tickers:
            tickers = custom_tickers
            universe_name = 'custom'
        else:
            tickers = self.universe_manager.get_universe_tickers(universe_name)

        logger.info(f"Universe contains {len(tickers)} tickers")

        # Calculate factors for all stocks in parallel
        factor_results = self._calculate_factors_parallel(tickers, strategy)

        logger.info(f"Successfully calculated factors for {len(factor_results)} stocks")

        if len(factor_results) == 0:
            return {
                'strategy': strategy_name,
                'universe': universe_name,
                'timestamp': datetime.now().isoformat(),
                'total_stocks': 0,
                'top_stocks': [],
                'error': 'No valid stock data'
            }

        # Convert to DataFrame for scoring
        factor_df = pd.DataFrame.from_dict(factor_results, orient='index')

        # Apply strategy filters
        filtered_tickers = []
        for ticker in factor_df.index:
            stock_data = factor_df.loc[ticker].to_dict()
            if apply_strategy_filters(stock_data, strategy):
                filtered_tickers.append(ticker)

        logger.info(f"{len(filtered_tickers)} stocks passed strategy filters")

        if len(filtered_tickers) == 0:
            return {
                'strategy': strategy_name,
                'universe': universe_name,
                'timestamp': datetime.now().isoformat(),
                'total_stocks': len(factor_results),
                'top_stocks': [],
                'error': 'No stocks passed strategy filters'
            }

        filtered_df = factor_df.loc[filtered_tickers]

        # Rank stocks
        ranked_df = rank_stocks_by_factors(
            filtered_df,
            strategy['factor_weights'],
            top_n=top_n
        )

        # Format results
        top_stocks = []
        for i, (ticker, row) in enumerate(ranked_df.head(top_n).iterrows(), 1):
            stock_result = {
                'ticker': ticker,
                'rank': i,
                'composite_score': float(row['composite_score']),
                'current_price': float(row.get('current_price', 0)),
                'factors': {}
            }

            # Include all factor values
            for factor in strategy['factor_weights'].keys():
                if factor in row:
                    val = row[factor]
                    stock_result['factors'][factor] = float(val) if not pd.isna(val) else None

            top_stocks.append(stock_result)

        elapsed = (datetime.now() - start_time).total_seconds()

        return {
            'strategy': strategy_name,
            'strategy_description': strategy['description'],
            'universe': universe_name,
            'timestamp': datetime.now().isoformat(),
            'total_stocks': len(factor_results),
            'filtered_stocks': len(filtered_tickers),
            'top_stocks': top_stocks,
            'execution_time_seconds': elapsed
        }

    def _calculate_factors_parallel(self,
                                    tickers: List[str],
                                    strategy: Dict) -> Dict[str, Dict]:
        """
        Calculate factors for all tickers in parallel.

        Args:
            tickers: List of tickers
            strategy: Strategy configuration

        Returns:
            Dict mapping ticker -> factor values
        """
        results = {}
        period_days = strategy['data_period_days']

        # Get SPY returns for correlation calculation
        spy_returns = self._get_spy_returns(period_days)

        # Get universe P/E ratios for z-score calculation
        universe_pe_ratios = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_ticker = {
                executor.submit(
                    self._calculate_stock_factors,
                    ticker,
                    period_days,
                    spy_returns
                ): ticker
                for ticker in tickers
            }

            # Collect results
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    factors = future.result()
                    if factors:
                        results[ticker] = factors

                        # Collect P/E ratios
                        if 'pe_zscore' in factors:
                            pe = factors.get('pe_zscore')
                            if not pd.isna(pe):
                                universe_pe_ratios.append(pe)

                except Exception as e:
                    logger.warning(f"Error calculating factors for {ticker}: {e}")

        return results

    def _calculate_stock_factors(self,
                                 ticker: str,
                                 period_days: int,
                                 spy_returns: Optional[pd.Series]) -> Dict:
        """
        Calculate all factors for a single stock.

        Args:
            ticker: Stock ticker
            period_days: Historical data period
            spy_returns: SPY returns for correlation

        Returns:
            Factor values
        """
        try:
            factors = calculate_all_factors(
                ticker,
                period_days=period_days,
                spy_returns=spy_returns
            )

            return factors

        except Exception as e:
            logger.warning(f"Error calculating factors for {ticker}: {e}")
            return {}

    def _get_spy_returns(self, period_days: int) -> pd.Series:
        """
        Get SPY returns for correlation calculation.

        Args:
            period_days: Lookback period

        Returns:
            SPY return series
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days + 30)

            spy = yf.Ticker('SPY')
            hist = spy.history(start=start_date, end=end_date)

            if len(hist) > 0:
                returns = hist['Close'].pct_change().dropna()
                return returns
            else:
                return pd.Series()

        except Exception as e:
            logger.warning(f"Error fetching SPY returns: {e}")
            return pd.Series()

    def get_stock_detail(self,
                        ticker: str,
                        strategy_name: str = 'swing') -> Dict:
        """
        Get detailed factor breakdown for a single stock.

        Args:
            ticker: Stock ticker
            strategy_name: Strategy for scoring

        Returns:
            Detailed stock analysis
        """
        logger.info(f"Getting stock detail for {ticker}, strategy={strategy_name}")

        # Get strategy
        strategy = get_strategy(strategy_name)

        # Calculate factors
        spy_returns = self._get_spy_returns(strategy['data_period_days'])
        factors = self._calculate_stock_factors(ticker, strategy['data_period_days'], spy_returns)

        if not factors:
            return {
                'ticker': ticker,
                'error': 'Unable to calculate factors'
            }

        # Calculate composite score
        factor_df = pd.DataFrame([factors], index=[ticker])
        score_series = calculate_composite_score(factor_df, strategy['factor_weights'])
        composite_score = score_series.iloc[0]

        # Check filters
        passes_filters = apply_strategy_filters(factors, strategy)

        # Normalize factors for percentile ranking
        normalized_df = normalize_factors(factor_df, list(strategy['factor_weights'].keys()), method='percentile')

        return {
            'ticker': ticker,
            'strategy': strategy_name,
            'composite_score': float(composite_score),
            'passes_filters': passes_filters,
            'current_price': factors.get('current_price', None),
            'factors': {
                'raw': {k: float(v) if not pd.isna(v) else None for k, v in factors.items()},
                'percentiles': {
                    k: float(normalized_df[k].iloc[0]) if k in normalized_df else None
                    for k in strategy['factor_weights'].keys()
                }
            },
            'factor_weights': strategy['factor_weights'],
            'timestamp': datetime.now().isoformat()
        }

    def list_available_strategies(self) -> List[Dict]:
        """
        List all available strategies.

        Returns:
            List of strategy metadata
        """
        return list_strategies()

    def list_available_universes(self) -> List[Dict]:
        """
        List all available universes.

        Returns:
            List of universe metadata
        """
        return self.universe_manager.list_available_universes()

    def create_alert(self,
                    ticker: str,
                    strategy_name: str,
                    threshold_score: float) -> Dict:
        """
        Create an alert for a stock based on composite score.

        Args:
            ticker: Stock ticker
            strategy_name: Strategy to use
            threshold_score: Alert if score exceeds this

        Returns:
            Alert configuration
        """
        return {
            'ticker': ticker,
            'strategy': strategy_name,
            'threshold_score': threshold_score,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }

    def backtest_strategy(self,
                         universe_name: str,
                         strategy_name: str,
                         start_date: str,
                         end_date: str,
                         top_n: int = 10,
                         rebalance_frequency: int = 20) -> Dict:
        """
        Backtest a screening strategy.

        Args:
            universe_name: Universe to screen
            strategy_name: Strategy to use
            start_date: Backtest start date (YYYY-MM-DD)
            end_date: Backtest end date (YYYY-MM-DD)
            top_n: Number of stocks to hold
            rebalance_frequency: Days between rebalancing

        Returns:
            Backtest results (simplified for now)
        """
        logger.info(f"Backtesting {strategy_name} on {universe_name} from {start_date} to {end_date}")

        # Placeholder implementation
        # Full backtest would require:
        # 1. Historical factor calculation at each rebalance date
        # 2. Portfolio construction
        # 3. Return calculation
        # 4. Performance metrics

        return {
            'strategy': strategy_name,
            'universe': universe_name,
            'start_date': start_date,
            'end_date': end_date,
            'top_n': top_n,
            'rebalance_frequency': rebalance_frequency,
            'total_return': 0.0,  # Placeholder
            'sharpe_ratio': 0.0,  # Placeholder
            'max_drawdown': 0.0,  # Placeholder
            'note': 'Full backtest implementation pending'
        }
