# timeframe_strategies.py - Timeframe-Specific Trading Strategies
# Different factor weights and configurations for different holding periods

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


# Intraday/Scalping Strategy (minutes to hours)
# Focus: Short-term momentum, volume, volatility
INTRADAY_STRATEGY = {
    'name': 'Intraday Scalping',
    'timeframe': 'intraday',
    'holding_period': '< 1 day',
    'data_period_days': 20,  # Historical data needed
    'factor_weights': {
        # Technical (90% of score)
        'momentum_20d': 0.15,
        'rsi': 0.10,
        'macd_histogram': 0.15,
        'volume_surge': 0.25,  # Very important for intraday
        'bb_percent_b': 0.10,
        'atr': 0.10,  # Volatility for stop-loss sizing
        'distance_to_support': 0.05,

        # Statistical (10% of score)
        'mean_reversion_zscore': 0.05,
        'liquidity': 0.05,  # Need liquid stocks for intraday
    },
    'filters': {
        'min_liquidity': 10_000_000,  # $10M daily volume minimum
        'min_price': 5.0,
        'max_price': 500.0,
        'min_volume_surge': 1.2,  # 20% above average
    },
    'description': 'Optimized for quick scalps and day trades. Emphasizes volume surges, momentum, and liquidity.'
}


# Swing Trading Strategy (2-10 days)
# Focus: Medium-term momentum, technical patterns, some fundamentals
SWING_STRATEGY = {
    'name': 'Swing Trading',
    'timeframe': 'swing',
    'holding_period': '2-10 days',
    'data_period_days': 60,
    'factor_weights': {
        # Technical (70% of score)
        'momentum_20d': 0.20,
        'rsi': 0.10,
        'macd_crossover': 0.10,
        'macd_histogram': 0.10,
        'bb_percent_b': 0.08,
        'volume_surge': 0.07,
        'distance_to_resistance': 0.05,

        # Fundamental (15% of score)
        'earnings_growth': 0.05,
        'revenue_growth': 0.05,
        'institutional_ownership': 0.05,

        # Statistical (15% of score)
        'sharpe_ratio': 0.05,
        'mean_reversion_zscore': 0.05,
        'liquidity': 0.05,
    },
    'filters': {
        'min_liquidity': 5_000_000,  # $5M daily volume
        'min_price': 3.0,
        'max_price': 1000.0,
    },
    'description': 'Balanced approach for 2-10 day holds. Combines technical momentum with fundamental quality.'
}


# Position Trading Strategy (weeks to months)
# Focus: Fundamentals, long-term trends, valuation
POSITION_STRATEGY = {
    'name': 'Position Trading',
    'timeframe': 'position',
    'holding_period': 'weeks to months',
    'data_period_days': 120,
    'factor_weights': {
        # Technical (40% of score)
        'momentum_60d': 0.15,
        'momentum_20d': 0.10,
        'rsi': 0.05,
        'bb_percent_b': 0.05,
        'distance_to_support': 0.05,

        # Fundamental (45% of score)
        'pe_zscore': 0.10,  # Valuation matters for longer holds
        'earnings_growth': 0.10,
        'revenue_growth': 0.10,
        'profit_margin': 0.08,
        'debt_to_equity': 0.04,
        'institutional_ownership': 0.03,

        # Statistical (15% of score)
        'sharpe_ratio': 0.08,
        'hurst_exponent': 0.04,  # Trending behavior
        'correlation_to_spy': 0.03,
    },
    'filters': {
        'min_liquidity': 2_000_000,  # $2M daily volume
        'min_price': 5.0,
        'max_earnings_growth': None,  # No upper bound on growth
    },
    'description': 'Long-term position trading. Emphasizes fundamentals, valuation, and sustainable growth.'
}


# Momentum Breakout Strategy
# Focus: Strong momentum + volume confirmation
MOMENTUM_BREAKOUT_STRATEGY = {
    'name': 'Momentum Breakout',
    'timeframe': 'swing',
    'holding_period': '3-15 days',
    'data_period_days': 60,
    'factor_weights': {
        # Pure momentum focus
        'momentum_20d': 0.25,
        'momentum_60d': 0.15,
        'macd_histogram': 0.15,
        'volume_surge': 0.20,
        'distance_to_resistance': 0.10,
        'rsi': 0.05,
        'liquidity': 0.05,
        'institutional_ownership': 0.05,
    },
    'filters': {
        'min_momentum_20d': 5.0,  # Minimum 5% gain over 20 days
        'min_volume_surge': 1.5,  # 50% above average
        'min_liquidity': 5_000_000,
    },
    'description': 'Aggressive momentum strategy. Catches strong breakouts with volume confirmation.'
}


# Mean Reversion Strategy
# Focus: Oversold quality stocks
MEAN_REVERSION_STRATEGY = {
    'name': 'Mean Reversion',
    'timeframe': 'swing',
    'holding_period': '5-20 days',
    'data_period_days': 60,
    'factor_weights': {
        # Look for oversold conditions
        'mean_reversion_zscore': 0.25,  # Negative z-score = oversold
        'rsi': 0.15,  # Low RSI
        'bb_percent_b': 0.10,  # Below lower band
        'distance_to_support': 0.10,

        # But still want quality
        'earnings_growth': 0.10,
        'profit_margin': 0.10,
        'institutional_ownership': 0.10,
        'sharpe_ratio': 0.05,
        'liquidity': 0.05,
    },
    'filters': {
        'max_rsi': 35,  # Oversold threshold
        'max_momentum_20d': -2.0,  # Recent pullback
        'min_liquidity': 3_000_000,
    },
    'description': 'Buys quality stocks that have pulled back. Looks for oversold conditions in strong names.'
}


# Growth at Reasonable Price (GARP)
# Focus: Growth + valuation
GARP_STRATEGY = {
    'name': 'Growth at Reasonable Price',
    'timeframe': 'position',
    'holding_period': 'months',
    'data_period_days': 120,
    'factor_weights': {
        # Growth metrics
        'earnings_growth': 0.20,
        'revenue_growth': 0.15,
        'profit_margin': 0.10,

        # Valuation
        'pe_zscore': 0.15,  # Negative = undervalued

        # Momentum
        'momentum_60d': 0.10,
        'momentum_20d': 0.05,

        # Quality
        'debt_to_equity': 0.08,
        'institutional_ownership': 0.07,
        'sharpe_ratio': 0.05,
        'liquidity': 0.05,
    },
    'filters': {
        'min_earnings_growth': 10.0,  # Minimum 10% growth
        'max_pe_zscore': 1.0,  # Not too expensive
        'max_debt_to_equity': 2.0,
    },
    'description': 'Combines growth and value. Seeks growing companies at reasonable valuations.'
}


# High Sharpe Ratio Strategy
# Focus: Risk-adjusted returns
HIGH_SHARPE_STRATEGY = {
    'name': 'High Sharpe Ratio',
    'timeframe': 'position',
    'holding_period': 'months',
    'data_period_days': 120,
    'factor_weights': {
        # Risk-adjusted metrics
        'sharpe_ratio': 0.30,
        'profit_margin': 0.15,
        'institutional_ownership': 0.10,

        # Stability
        'debt_to_equity': 0.10,
        'correlation_to_spy': 0.05,

        # Growth
        'earnings_growth': 0.10,
        'revenue_growth': 0.10,

        # Technical
        'momentum_60d': 0.05,
        'liquidity': 0.05,
    },
    'filters': {
        'min_sharpe_ratio': 1.0,
        'min_profit_margin': 10.0,
        'max_debt_to_equity': 1.5,
    },
    'description': 'Conservative strategy focused on high risk-adjusted returns and quality.'
}


# All available strategies
STRATEGIES = {
    'intraday': INTRADAY_STRATEGY,
    'swing': SWING_STRATEGY,
    'position': POSITION_STRATEGY,
    'momentum_breakout': MOMENTUM_BREAKOUT_STRATEGY,
    'mean_reversion': MEAN_REVERSION_STRATEGY,
    'garp': GARP_STRATEGY,
    'high_sharpe': HIGH_SHARPE_STRATEGY,
}


def get_strategy(strategy_name: str) -> Dict:
    """
    Get strategy configuration by name.

    Args:
        strategy_name: Strategy identifier

    Returns:
        Strategy configuration dict

    Raises:
        ValueError if strategy not found
    """
    if strategy_name not in STRATEGIES:
        available = ', '.join(STRATEGIES.keys())
        raise ValueError(f"Unknown strategy '{strategy_name}'. Available: {available}")

    return STRATEGIES[strategy_name]


def list_strategies() -> List[Dict]:
    """
    List all available strategies with metadata.

    Returns:
        List of strategy summaries
    """
    summaries = []

    for key, strategy in STRATEGIES.items():
        summaries.append({
            'id': key,
            'name': strategy['name'],
            'timeframe': strategy['timeframe'],
            'holding_period': strategy['holding_period'],
            'description': strategy['description']
        })

    return summaries


def apply_strategy_filters(stock_data: Dict,
                          strategy: Dict) -> bool:
    """
    Check if a stock passes strategy filters.

    Args:
        stock_data: Stock data with factors
        strategy: Strategy configuration

    Returns:
        True if stock passes all filters
    """
    filters = strategy.get('filters', {})

    for filter_name, filter_value in filters.items():
        if filter_value is None:
            continue

        # Extract factor name from filter name (e.g., 'min_liquidity' -> 'liquidity')
        if filter_name.startswith('min_'):
            factor_name = filter_name[4:]
            if factor_name in stock_data:
                if stock_data[factor_name] < filter_value:
                    return False

        elif filter_name.startswith('max_'):
            factor_name = filter_name[4:]
            if factor_name in stock_data:
                if stock_data[factor_name] > filter_value:
                    return False

    return True


def get_strategy_factor_names(strategy: Dict) -> List[str]:
    """
    Get list of factor names used in a strategy.

    Args:
        strategy: Strategy configuration

    Returns:
        List of factor names
    """
    return list(strategy['factor_weights'].keys())


def validate_strategy(strategy: Dict) -> bool:
    """
    Validate strategy configuration.

    Args:
        strategy: Strategy to validate

    Returns:
        True if valid

    Raises:
        ValueError if invalid
    """
    required_keys = ['name', 'timeframe', 'holding_period', 'data_period_days', 'factor_weights']

    for key in required_keys:
        if key not in strategy:
            raise ValueError(f"Strategy missing required key: {key}")

    # Check that weights are positive
    for factor, weight in strategy['factor_weights'].items():
        if weight < 0:
            raise ValueError(f"Negative weight for factor {factor}: {weight}")

    logger.info(f"Strategy '{strategy['name']}' validated successfully")
    return True
