"""
PRISM Configuration Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class PRISMSettings(BaseSettings):
    """PRISM engine configuration."""

    # Service
    HOST: str = "0.0.0.0"
    PORT: int = 8360

    # Order Book
    MAX_ORDER_BOOK_DEPTH: int = 100
    TICK_SIZE: float = 0.01
    MIN_ORDER_SIZE: int = 1
    MAX_ORDER_SIZE: int = 1000000

    # Liquidity
    BASE_LIQUIDITY: float = 1000000.0  # Base market liquidity
    LIQUIDITY_DECAY_RATE: float = 0.1  # How fast liquidity recovers
    IMPACT_COEFFICIENT: float = 0.001  # Price impact per unit volume

    # Price Discovery
    VOLATILITY: float = 0.02  # Daily volatility
    MOMENTUM_FACTOR: float = 0.3  # Momentum influence
    MEAN_REVERSION_RATE: float = 0.1  # Mean reversion speed

    # Execution
    LATENCY_MS: int = 10  # Execution latency
    SLIPPAGE_MODEL: str = "sqrt"  # linear, sqrt, or quadratic

    # Multi-Agent
    NUM_MARKET_MAKERS: int = 5
    NUM_NOISE_TRADERS: int = 20
    NUM_INFORMED_TRADERS: int = 10

    # Integration
    LIBRARY_API_URL: str = "http://localhost:8350"
    QUESTDB_HOST: str = "localhost"
    QUESTDB_PORT: int = 9000

    # Analytics
    CALCULATE_ANALYTICS_EVERY_N_TRADES: int = 100

    class Config:
        env_prefix = "PRISM_"


settings = PRISMSettings()
