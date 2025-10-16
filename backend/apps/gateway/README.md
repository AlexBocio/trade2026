# Market Data Gateway

## Overview
The gateway service handles all market data ingestion from various exchanges and data providers.

## Responsibilities
- Exchange connectivity (REST + WebSocket)
- Rate limiting and throttling
- Connection management and reconnection logic
- Data normalization to internal format
- Initial validation and filtering
- Publishing to NATS event bus

## Phase 3 Implementation
- [ ] Exchange connector framework
- [ ] WebSocket handlers
- [ ] REST API polling
- [ ] Rate limiter implementation
- [ ] Circuit breaker pattern
- [ ] Data normalization pipeline
- [ ] NATS publisher
- [ ] Health check endpoints
- [ ] Metrics collection

## Technology Stack
- Language: Python 3.11+
- Framework: FastAPI + asyncio
- WebSocket: websockets library
- Serialization: Protobuf/MessagePack
- Monitoring: OpenTelemetry

## Supported Exchanges (Planned)
- Binance
- Coinbase
- Kraken
- Interactive Brokers
- Alpaca

## Data Types
- Order book updates
- Trade executions
- OHLCV candles
- Ticker updates
- Market status

## Configuration
```yaml
exchanges:
  binance:
    api_key: ${BINANCE_API_KEY}
    api_secret: ${BINANCE_API_SECRET}
    rate_limit: 1200/min
    symbols:
      - BTCUSDT
      - ETHUSDT
```

## API Endpoints
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /status/{exchange}` - Exchange connection status
- `POST /subscribe` - Subscribe to symbols
- `DELETE /unsubscribe` - Unsubscribe from symbols

## Event Schema
```protobuf
message MarketData {
  string exchange = 1;
  string symbol = 2;
  int64 timestamp = 3;
  oneof data {
    OrderBook order_book = 4;
    Trade trade = 5;
    Candle candle = 6;
  }
}
```