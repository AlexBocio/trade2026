"""
PRISM FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .core.engine import prism_engine
from .core.models import Order, OrderBook, MarketState
from .config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    # Startup
    logger.info("Starting PRISM Engine...")
    await prism_engine.initialize()
    await prism_engine.start()

    # Add default symbols
    prism_engine.add_symbol("AAPL", 150.0)
    prism_engine.add_symbol("MSFT", 300.0)
    prism_engine.add_symbol("GOOGL", 140.0)
    prism_engine.add_symbol("BTCUSDT", 60000.0)
    prism_engine.add_symbol("ETHUSDT", 3000.0)

    logger.info("PRISM Engine started successfully - Full simulation mode")
    logger.info("All components initialized: Order Book, Liquidity, Price Discovery, Execution, Agents, Analytics")

    yield

    # Shutdown
    logger.info("Stopping PRISM Engine...")
    await prism_engine.stop()


app = FastAPI(
    title="PRISM Physics Engine",
    description="Physics-based market simulation and execution engine",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    components = []
    if prism_engine.order_book_sim:
        components.append("order_book")
    if prism_engine.liquidity_model:
        components.append("liquidity")
    if prism_engine.price_discovery:
        components.append("price_discovery")
    if prism_engine.execution_engine:
        components.append("execution")
    if prism_engine.agent_simulator:
        components.append("agents")
    if prism_engine.analytics:
        components.append("analytics")

    mode = "full" if len(components) == 6 else "basic"

    # Check persistence
    persistence_status = "disabled"
    if prism_engine.persistence_enabled:
        persistence_status = "enabled"
        if prism_engine.questdb_client and prism_engine.clickhouse_client:
            persistence_status = "full"  # Both QuestDB and ClickHouse

    return {
        "status": "healthy",
        "service": "prism",
        "version": "1.0.0",
        "running": prism_engine.running,
        "mode": mode,
        "components_implemented": components,
        "num_agents": len(prism_engine.agent_simulator.agents) if prism_engine.agent_simulator else 0,
        "persistence_enabled": prism_engine.persistence_enabled,
        "persistence_status": persistence_status
    }


@app.post("/orders")
async def submit_order(order: Order):
    """Submit an order to PRISM."""
    try:
        order_id = await prism_engine.submit_order(order)
        return {
            "order_id": str(order_id),
            "status": order.status.value,
            "filled_quantity": order.filled_quantity,
            "average_fill_price": order.average_fill_price
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/orderbook/{symbol}")
async def get_order_book(symbol: str):
    """Get order book for symbol."""
    order_book = prism_engine.get_order_book(symbol)
    if not order_book:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    return order_book


@app.get("/market/{symbol}")
async def get_market_state(symbol: str):
    """Get market state for symbol."""
    market_state = prism_engine.get_market_state(symbol)
    if not market_state:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    return market_state


@app.get("/symbols")
async def list_symbols():
    """List all available symbols."""
    return {
        "symbols": list(prism_engine.symbols.keys()),
        "count": len(prism_engine.symbols)
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "PRISM Physics Engine",
        "version": "1.0.0",
        "status": "running",
        "mode": "full" if prism_engine.agent_simulator else "basic",
        "docs": "/docs",
        "health": "/health",
        "implementation_status": {
            "components_1_to_7": "complete",
            "component_8_integration": "pending"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
