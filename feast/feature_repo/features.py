"""
Feast Feature Definitions for Trading Strategy.

Defines entities and feature views for ML model serving.
"""
from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource, ValueType
from feast.types import Float64, Int64


# ============================================================================
# ENTITIES
# ============================================================================

symbol = Entity(
    name="symbol",
    description="Trading symbol (e.g., BTCUSDT, ETHUSDT)",
    value_type=ValueType.STRING
)


# ============================================================================
# DATA SOURCES
# ============================================================================

# ClickHouse data source for technical indicators
# Note: This will be replaced with actual ClickHouseSource when available
# For now, using FileSource for local testing
technical_indicators_source = FileSource(
    name="technical_indicators_source",
    path="data/features.parquet",
    timestamp_field="timestamp",
)


# ============================================================================
# FEATURE VIEWS
# ============================================================================

technical_indicators_view = FeatureView(
    name="technical_indicators",
    entities=[symbol],
    ttl=timedelta(days=7),
    schema=[
        # Close price
        Field(name="close", dtype=Float64),

        # RSI (Relative Strength Index)
        Field(name="rsi", dtype=Float64),

        # MACD indicators
        Field(name="macd", dtype=Float64),
        Field(name="macd_signal", dtype=Float64),
        Field(name="macd_histogram", dtype=Float64),
        Field(name="macd_crossover", dtype=Float64),

        # Bollinger Bands
        Field(name="bb_upper", dtype=Float64),
        Field(name="bb_middle", dtype=Float64),
        Field(name="bb_lower", dtype=Float64),
        Field(name="bb_bandwidth", dtype=Float64),
        Field(name="bb_percent_b", dtype=Float64),
        Field(name="bb_squeeze", dtype=Float64),
        Field(name="bb_breakout", dtype=Float64),
    ],
    source=technical_indicators_source,
    online=True,
    description="Technical indicators for trading strategy (RSI, MACD, Bollinger Bands)"
)
