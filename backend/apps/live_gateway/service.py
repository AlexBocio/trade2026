"""
Live Trading Gateway - Main Service
Phase 11: Live Trading Enablement
"""

import asyncio
import logging
import os
import yaml
from contextlib import asynccontextmanager
from typing import Dict, Optional

import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import nats
from nats.js import JetStreamContext

from modes import ModeManager, TradingMode
from ramp_scheduler import RampScheduler
from adapters.venue_health import VenueHealthMonitor
from adapters.idempotency import IdempotencyManager
from adapters import MockIBKRAdapter, MockAlpacaAdapter, MockCCXTAdapter, BaseAdapter
from adapters import IBKRAdapter, AlpacaAdapter, CCXTAdapter
from router import OrderRouter, OrderRequest
from audit_logger import AuditLogger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
config: Dict = {}
mode_manager: Optional[ModeManager] = None
ramp_scheduler: Optional[RampScheduler] = None
health_monitor: Optional[VenueHealthMonitor] = None
idempotency_manager: Optional[IdempotencyManager] = None
audit_logger: Optional[AuditLogger] = None
adapters: Dict[str, BaseAdapter] = {}
router: Optional[OrderRouter] = None
nc: Optional[nats.NATS] = None
js: Optional[JetStreamContext] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown"""
    global config, mode_manager, ramp_scheduler, health_monitor, idempotency_manager
    global adapters, router, nc, js, audit_logger

    # Load config
    config_path = os.getenv('CONFIG_PATH', '/app/config.yaml')
    with open(config_path) as f:
        config = yaml.safe_load(f)

    logger.info("Live Trading Gateway starting...")

    # Initialize Redis
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', '6379'))
    redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=False)

    # Initialize managers
    mode_manager = ModeManager(config)
    ramp_scheduler = RampScheduler(config)
    health_monitor = VenueHealthMonitor(config)
    idempotency_manager = IdempotencyManager(redis_client)
    audit_logger = AuditLogger(config)

    # Initialize adapters (use real or mock based on env)
    use_real_adapters = os.getenv('USE_REAL_ADAPTERS', 'false').lower() == 'true'

    if use_real_adapters:
        logger.info("Using REAL broker adapters")
        adapters['IBKR'] = IBKRAdapter(config)
        adapters['ALPACA'] = AlpacaAdapter(config)
        adapters['CCXT'] = CCXTAdapter(config)
    else:
        logger.info("Using MOCK broker adapters")
        adapters['IBKR'] = MockIBKRAdapter(config)
        adapters['ALPACA'] = MockAlpacaAdapter(config)
        adapters['CCXT'] = MockCCXTAdapter(config)

    # Initialize router
    router = OrderRouter(
        mode_manager=mode_manager,
        ramp_scheduler=ramp_scheduler,
        health_monitor=health_monitor,
        idempotency_manager=idempotency_manager,
        adapters=adapters,
        audit_logger=audit_logger
    )

    # Connect to NATS (optional for testing)
    nats_url = os.getenv('NATS_URL', 'nats://localhost:4222')
    try:
        nc = await nats.connect(nats_url, connect_timeout=2, max_reconnect_attempts=1)
        js = nc.jetstream()

        # Subscribe to broker.submit
        await js.subscribe('broker.submit', cb=handle_submit_order)
        logger.info("NATS connected successfully")
    except Exception as e:
        logger.warning(f"NATS connection failed (running without message bus): {e}")
        nc = None
        js = None

    logger.info("Live Trading Gateway ready")

    yield

    # Shutdown
    logger.info("Live Trading Gateway shutting down...")
    if nc:
        await nc.close()


app = FastAPI(lifespan=lifespan)


async def handle_submit_order(msg):
    """Handle broker.submit messages"""
    try:
        import json
        data = json.loads(msg.data.decode())

        order = OrderRequest(**data)
        logger.info(f"Received order: {order.client_order_id}")

        result = await router.route_order(order)
        logger.info(f"Order routed: {result.model_dump()}")

        await msg.ack()

    except Exception as e:
        logger.error(f"Error handling order: {e}")
        await msg.nak()


# Admin endpoints

@app.get('/health')
async def health():
    """Health check"""
    return {
        'status': 'ok',
        'mode': mode_manager.global_mode if mode_manager else 'unknown',
        'circuits': health_monitor.get_status() if health_monitor else {}
    }


class ModeUpdate(BaseModel):
    """Mode update request"""
    mode: str
    venue: Optional[str] = None
    canary_pct: Optional[float] = None
    canary_max_qty: Optional[float] = None


@app.post('/mode')
async def update_mode(req: ModeUpdate):
    """Update trading mode"""
    if not mode_manager:
        raise HTTPException(status_code=500, detail="ModeManager not initialized")

    try:
        new_mode = TradingMode(req.mode)

        if req.venue:
            # Venue-specific mode
            mode_config = {'mode': req.mode}
            if req.canary_pct is not None:
                mode_config['canary_pct'] = req.canary_pct
            if req.canary_max_qty is not None:
                mode_config['canary_max_qty'] = req.canary_max_qty

            mode_manager.update_venue_mode(req.venue, mode_config)

            # Audit log
            if audit_logger:
                audit_logger.log_mode_change({
                    'venue': req.venue,
                    'new_mode': req.mode,
                    'canary_pct': req.canary_pct,
                    'canary_max_qty': req.canary_max_qty
                })

            return {'status': 'ok', 'venue': req.venue, 'mode': req.mode}
        else:
            # Global mode
            mode_manager.update_global_mode(new_mode)

            # Audit log
            if audit_logger:
                audit_logger.log_mode_change({
                    'global': True,
                    'new_mode': req.mode
                })

            return {'status': 'ok', 'global_mode': req.mode}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {e}")


@app.post('/panic')
async def panic():
    """Emergency panic button - force all to SHADOW"""
    if not mode_manager:
        raise HTTPException(status_code=500, detail="ModeManager not initialized")

    mode_manager.panic_mode()

    # Open all circuit breakers
    if health_monitor:
        for venue in health_monitor.circuit_breakers:
            cb = health_monitor.circuit_breakers[venue]
            cb.state = "OPEN"
            cb.consecutive_failures = cb.consecutive_failures_threshold

            # Audit log circuit event
            if audit_logger:
                audit_logger.log_circuit_event({
                    'venue': venue,
                    'event': 'PANIC_OPEN',
                    'state': 'OPEN'
                })

    # Audit log panic
    if audit_logger:
        audit_logger.log_mode_change({
            'global': True,
            'new_mode': 'SHADOW',
            'reason': 'PANIC_BUTTON'
        })

    logger.critical("PANIC BUTTON ACTIVATED - All venues SHADOW, circuits OPEN")
    return {'status': 'PANIC_ACTIVATED', 'global_mode': 'SHADOW'}


@app.get('/ramp')
async def get_ramp_status():
    """Get ramp schedule status"""
    if not ramp_scheduler:
        raise HTTPException(status_code=500, detail="RampScheduler not initialized")

    return {
        'current_pct': ramp_scheduler.get_current_pct(),
        'daily_notional': ramp_scheduler.current_daily_notional,
        'daily_cap': ramp_scheduler.hard_daily_cap
    }


if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', '8200'))
    uvicorn.run(app, host='0.0.0.0', port=port)
