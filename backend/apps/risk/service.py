"""
Risk Management Service
Real-time risk monitoring and enforcement
Phase 2: Priority 2 Services
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum

import nats
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import redis
import yaml
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    BREACHED = "BREACHED"


class AlertType(Enum):
    POSITION_SIZE = "POSITION_SIZE"
    EXPOSURE = "EXPOSURE"
    DRAWDOWN = "DRAWDOWN"
    MARGIN = "MARGIN"
    CONCENTRATION = "CONCENTRATION"
    VOLATILITY = "VOLATILITY"
    CORRELATION = "CORRELATION"
    VAR_BREACH = "VAR_BREACH"


@dataclass
class RiskLimit:
    limit_type: str
    max_value: float
    current_value: float = 0.0
    threshold_warning: float = 0.8  # 80% warning
    threshold_critical: float = 0.9  # 90% critical
    breached: bool = False
    last_checked: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RiskAlert:
    alert_id: str
    alert_type: AlertType
    severity: RiskLevel
    message: str
    symbol: Optional[str]
    value: float
    threshold: float
    created_at: datetime
    acknowledged: bool = False


@dataclass
class PortfolioRisk:
    total_exposure: float
    total_positions: int
    max_position_size: float
    current_drawdown: float
    margin_used: float
    margin_available: float
    var_95: float  # Value at Risk at 95% confidence
    var_99: float  # Value at Risk at 99% confidence
    sharpe_ratio: float
    risk_level: RiskLevel
    timestamp: datetime


class RiskManager:
    """Main risk management engine"""

    def __init__(self, config_path: str = '/app/config.yaml'):
        self.config = self._load_config(config_path)
        self.nc = None
        self.redis_client = None

        # Risk limits
        self.risk_limits: Dict[str, RiskLimit] = {}
        self.symbol_limits: Dict[str, Dict[str, float]] = {}

        # Active tracking
        self.active_positions: Dict[str, Dict[str, Any]] = {}
        self.active_orders: Dict[str, Dict[str, Any]] = {}
        self.alerts: List[RiskAlert] = []
        self.blocked_symbols: Set[str] = set()

        # Portfolio metrics
        self.portfolio_risk: Optional[PortfolioRisk] = None
        self.price_cache: Dict[str, float] = {}

        # Historical data for VaR
        self.returns_history: List[float] = []

        # Stats
        self.stats = {
            'orders_checked': 0,
            'orders_approved': 0,
            'orders_rejected': 0,
            'alerts_raised': 0,
            'limits_breached': 0,
            'risk_checks_performed': 0
        }

        self._initialize_limits()

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded config from {config_path}")
                return config
        except Exception as e:
            logger.warning(f"Failed to load config: {e}, using defaults")
            return {
                'nats_url': 'nats://nats:4222',
                'redis_host': 'valkey',
                'redis_port': 6379,
                'check_interval': 1.0,
                'alert_interval': 5.0,
                'health_port': 8103
            }

    def _initialize_limits(self):
        """Initialize risk limits from configuration"""
        # Portfolio-wide limits
        portfolio_limits = self.config.get('portfolio_limits', {})

        self.risk_limits['max_exposure'] = RiskLimit(
            limit_type='max_exposure',
            max_value=portfolio_limits.get('max_exposure', 1000000.0)
        )

        self.risk_limits['max_positions'] = RiskLimit(
            limit_type='max_positions',
            max_value=portfolio_limits.get('max_positions', 100)
        )

        self.risk_limits['max_drawdown'] = RiskLimit(
            limit_type='max_drawdown',
            max_value=portfolio_limits.get('max_drawdown', 0.2)  # 20%
        )

        self.risk_limits['min_margin'] = RiskLimit(
            limit_type='min_margin',
            max_value=portfolio_limits.get('min_margin_ratio', 0.25)  # 25%
        )

        self.risk_limits['max_var_95'] = RiskLimit(
            limit_type='max_var_95',
            max_value=portfolio_limits.get('max_var_95', 50000.0)
        )

        # Symbol-specific limits
        symbol_limits = self.config.get('symbol_limits', {})
        for symbol, limits in symbol_limits.items():
            self.symbol_limits[symbol] = limits

        logger.info(f"Initialized {len(self.risk_limits)} portfolio limits and "
                   f"{len(self.symbol_limits)} symbol-specific limits")

    async def connect_services(self):
        """Connect to NATS and Redis"""
        try:
            # Connect to NATS
            self.nc = await nats.connect(self.config.get('nats_url', 'nats://nats:4222'))
            logger.info(f"Connected to NATS at {self.config.get('nats_url')}")

            # Connect to Redis/Valkey
            self.redis_client = redis.Redis(
                host=self.config.get('redis_host', 'valkey'),
                port=self.config.get('redis_port', 6379),
                db=3,  # Use db 3 for risk
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {self.config.get('redis_host')}")

        except Exception as e:
            logger.error(f"Failed to connect services: {e}")
            raise

    async def subscribe_events(self):
        """Subscribe to risk-relevant events"""

        # Pre-trade risk check
        async def order_check_handler(msg):
            try:
                order_data = json.loads(msg.data.decode())
                result = await self.check_order_risk(order_data)

                # Reply with risk decision
                response = json.dumps({
                    'approved': result['approved'],
                    'reason': result.get('reason', ''),
                    'risk_level': result.get('risk_level', 'UNKNOWN')
                })
                await msg.respond(response.encode())

            except Exception as e:
                logger.error(f"Error checking order risk: {e}")
                await msg.respond(json.dumps({'approved': False, 'reason': str(e)}).encode())

        # Position updates
        async def position_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                await self.update_position(data)
            except Exception as e:
                logger.error(f"Error handling position update: {e}")

        # Fill notifications
        async def fill_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                await self.handle_fill(data)
            except Exception as e:
                logger.error(f"Error handling fill: {e}")

        # Price updates for risk calculations
        async def price_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                symbol = data.get('symbol')
                price = data.get('price') or data.get('last')
                if symbol and price:
                    self.price_cache[symbol] = float(price)
            except Exception as e:
                logger.error(f"Error handling price update: {e}")

        # P&L updates for drawdown monitoring
        async def pnl_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                await self.update_portfolio_metrics(data)
            except Exception as e:
                logger.error(f"Error handling P&L update: {e}")

        await self.nc.subscribe("risk.check.order", cb=order_check_handler)
        await self.nc.subscribe("positions.update", cb=position_handler)
        await self.nc.subscribe("fills.confirmed", cb=fill_handler)
        await self.nc.subscribe("market.tick.*", cb=price_handler)
        await self.nc.subscribe("pnl.update", cb=pnl_handler)

        logger.info("Subscribed to risk management events")

    async def check_order_risk(self, order_data: dict) -> dict:
        """Pre-trade risk check for new orders"""
        self.stats['orders_checked'] += 1

        symbol = order_data.get('symbol')
        quantity = float(order_data.get('quantity', 0))
        price = float(order_data.get('price', 0)) or self.price_cache.get(symbol, 0)
        side = order_data.get('side')

        # Calculate order value
        order_value = quantity * price

        # Check symbol block list
        if symbol in self.blocked_symbols:
            self.stats['orders_rejected'] += 1
            return {
                'approved': False,
                'reason': f'Symbol {symbol} is blocked for trading',
                'risk_level': 'BREACHED'
            }

        # Check symbol-specific limits
        if symbol in self.symbol_limits:
            limits = self.symbol_limits[symbol]

            # Check max position size
            if 'max_position' in limits and quantity > limits['max_position']:
                self.stats['orders_rejected'] += 1
                return {
                    'approved': False,
                    'reason': f'Order size {quantity} exceeds limit {limits["max_position"]}',
                    'risk_level': 'HIGH'
                }

            # Check max value
            if 'max_value' in limits and order_value > limits['max_value']:
                self.stats['orders_rejected'] += 1
                return {
                    'approved': False,
                    'reason': f'Order value ${order_value:.2f} exceeds limit ${limits["max_value"]:.2f}',
                    'risk_level': 'HIGH'
                }

        # Check portfolio-wide limits
        checks = []

        # Check total exposure
        current_exposure = self._calculate_total_exposure()
        new_exposure = current_exposure + order_value
        exposure_limit = self.risk_limits['max_exposure']

        if new_exposure > exposure_limit.max_value:
            checks.append({
                'passed': False,
                'message': f'Would exceed max exposure: ${new_exposure:.2f} > ${exposure_limit.max_value:.2f}'
            })
        elif new_exposure > exposure_limit.max_value * exposure_limit.threshold_warning:
            checks.append({
                'passed': True,
                'message': f'Warning: Approaching max exposure limit',
                'warning': True
            })
        else:
            checks.append({'passed': True})

        # Check position count
        position_count = len(self.active_positions) + 1
        position_limit = self.risk_limits['max_positions']

        if position_count > position_limit.max_value:
            checks.append({
                'passed': False,
                'message': f'Would exceed max positions: {position_count} > {int(position_limit.max_value)}'
            })

        # Check margin requirements
        margin_required = order_value * 0.1  # 10% margin requirement
        margin_available = self._get_available_margin()

        if margin_required > margin_available:
            checks.append({
                'passed': False,
                'message': f'Insufficient margin: Required ${margin_required:.2f}, Available ${margin_available:.2f}'
            })

        # Determine overall result
        failed_checks = [c for c in checks if not c.get('passed', True)]
        warnings = [c for c in checks if c.get('warning', False)]

        if failed_checks:
            self.stats['orders_rejected'] += 1
            return {
                'approved': False,
                'reason': '; '.join([c['message'] for c in failed_checks]),
                'risk_level': 'HIGH'
            }

        self.stats['orders_approved'] += 1

        # Add order to tracking
        order_id = order_data.get('order_id', str(int(time.time() * 1000)))
        self.active_orders[order_id] = {
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'value': order_value,
            'side': side,
            'timestamp': datetime.utcnow()
        }

        # Determine risk level
        if warnings:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'

        return {
            'approved': True,
            'risk_level': risk_level,
            'warnings': [w['message'] for w in warnings] if warnings else None
        }

    async def update_position(self, position_data: dict):
        """Update position tracking"""
        symbol = position_data['symbol']
        quantity = float(position_data.get('quantity', 0))

        if quantity > 0:
            self.active_positions[symbol] = {
                'quantity': quantity,
                'average_price': float(position_data.get('average_price', 0)),
                'current_price': float(position_data.get('current_price', 0)),
                'unrealized_pnl': float(position_data.get('unrealized_pnl', 0)),
                'updated_at': datetime.utcnow()
            }
        else:
            # Position closed
            if symbol in self.active_positions:
                del self.active_positions[symbol]

    async def handle_fill(self, fill_data: dict):
        """Handle fill event for risk tracking"""
        order_id = fill_data.get('order_id')
        if order_id in self.active_orders:
            del self.active_orders[order_id]

        # Update position after fill
        await self.update_position({
            'symbol': fill_data['symbol'],
            'quantity': fill_data.get('filled_quantity', fill_data.get('quantity')),
            'average_price': fill_data['price']
        })

    async def update_portfolio_metrics(self, pnl_data: dict):
        """Update portfolio risk metrics from P&L data"""
        total_pnl = float(pnl_data.get('total_pnl', 0))

        # Track returns for VaR calculation
        if self.returns_history:
            last_pnl = self.returns_history[-1] if self.returns_history else 0
            daily_return = total_pnl - last_pnl
            self.returns_history.append(daily_return)
        else:
            self.returns_history.append(total_pnl)

        # Keep only last 100 days
        if len(self.returns_history) > 100:
            self.returns_history.pop(0)

        # Update drawdown
        max_drawdown = float(pnl_data.get('max_drawdown', 0))
        if max_drawdown > self.risk_limits['max_drawdown'].max_value:
            await self._raise_alert(
                AlertType.DRAWDOWN,
                RiskLevel.CRITICAL,
                f"Maximum drawdown exceeded: {max_drawdown:.1%}",
                value=max_drawdown,
                threshold=self.risk_limits['max_drawdown'].max_value
            )

    def _calculate_total_exposure(self) -> float:
        """Calculate total portfolio exposure"""
        total = 0.0
        for symbol, position in self.active_positions.items():
            price = position.get('current_price', position.get('average_price', 0))
            quantity = position.get('quantity', 0)
            total += abs(price * quantity)
        return total

    def _get_available_margin(self) -> float:
        """Get available margin (simplified calculation)"""
        # In real implementation, would integrate with broker/exchange
        total_equity = 100000.0  # Default equity
        margin_used = self._calculate_total_exposure() * 0.1  # 10% margin
        return max(0, total_equity - margin_used)

    def _calculate_var(self, confidence: float = 0.95) -> float:
        """Calculate Value at Risk"""
        if len(self.returns_history) < 20:
            return 0.0

        sorted_returns = sorted(self.returns_history)
        index = int((1 - confidence) * len(sorted_returns))
        return abs(sorted_returns[index]) if index < len(sorted_returns) else 0.0

    async def _raise_alert(self, alert_type: AlertType, severity: RiskLevel,
                          message: str, symbol: Optional[str] = None,
                          value: float = 0.0, threshold: float = 0.0):
        """Raise a risk alert"""
        alert = RiskAlert(
            alert_id=f"ALERT_{int(time.time() * 1000)}",
            alert_type=alert_type,
            severity=severity,
            message=message,
            symbol=symbol,
            value=value,
            threshold=threshold,
            created_at=datetime.utcnow()
        )

        self.alerts.append(alert)
        self.stats['alerts_raised'] += 1

        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts.pop(0)

        # Publish alert
        await self.nc.publish("risk.alert", json.dumps({
            'alert_id': alert.alert_id,
            'type': alert.alert_type.value,
            'severity': alert.severity.value,
            'message': alert.message,
            'symbol': alert.symbol,
            'value': alert.value,
            'timestamp': alert.created_at.isoformat()
        }).encode())

        logger.warning(f"Risk Alert: {alert.message} (Severity: {alert.severity.value})")

    async def periodic_risk_check(self):
        """Perform periodic comprehensive risk checks"""
        while True:
            try:
                await asyncio.sleep(self.config.get('check_interval', 1.0))

                self.stats['risk_checks_performed'] += 1

                # Calculate current portfolio risk
                exposure = self._calculate_total_exposure()
                position_count = len(self.active_positions)
                var_95 = self._calculate_var(0.95)
                var_99 = self._calculate_var(0.99)
                margin_used = exposure * 0.1
                margin_available = self._get_available_margin()

                # Determine overall risk level
                risk_level = RiskLevel.LOW

                # Check exposure
                exposure_limit = self.risk_limits['max_exposure']
                exposure_ratio = exposure / exposure_limit.max_value if exposure_limit.max_value > 0 else 0

                if exposure_ratio > 1.0:
                    risk_level = RiskLevel.BREACHED
                    exposure_limit.breached = True
                elif exposure_ratio > exposure_limit.threshold_critical:
                    risk_level = RiskLevel.CRITICAL
                elif exposure_ratio > exposure_limit.threshold_warning:
                    risk_level = max(risk_level, RiskLevel.HIGH)

                # Check VaR
                var_limit = self.risk_limits['max_var_95']
                if var_95 > var_limit.max_value:
                    risk_level = max(risk_level, RiskLevel.CRITICAL)
                    await self._raise_alert(
                        AlertType.VAR_BREACH,
                        RiskLevel.CRITICAL,
                        f"VaR(95%) exceeds limit: ${var_95:.2f} > ${var_limit.max_value:.2f}",
                        value=var_95,
                        threshold=var_limit.max_value
                    )

                # Update portfolio risk snapshot
                self.portfolio_risk = PortfolioRisk(
                    total_exposure=exposure,
                    total_positions=position_count,
                    max_position_size=max([p.get('quantity', 0) * p.get('current_price', 0)
                                          for p in self.active_positions.values()]) if self.active_positions else 0,
                    current_drawdown=0.0,  # Would come from P&L service
                    margin_used=margin_used,
                    margin_available=margin_available,
                    var_95=var_95,
                    var_99=var_99,
                    sharpe_ratio=0.0,  # Would come from P&L service
                    risk_level=risk_level,
                    timestamp=datetime.utcnow()
                )

                # Store in Redis
                await self._store_risk_snapshot()

                # Log if risk is elevated
                if risk_level.value in ['HIGH', 'CRITICAL', 'BREACHED']:
                    logger.warning(f"Portfolio Risk Level: {risk_level.value} "
                                 f"(Exposure: ${exposure:.2f}, VaR95: ${var_95:.2f})")

            except Exception as e:
                logger.error(f"Error in periodic risk check: {e}")

    async def _store_risk_snapshot(self):
        """Store risk snapshot in Redis"""
        if not self.portfolio_risk:
            return

        try:
            snapshot_data = {
                'total_exposure': self.portfolio_risk.total_exposure,
                'total_positions': self.portfolio_risk.total_positions,
                'margin_used': self.portfolio_risk.margin_used,
                'margin_available': self.portfolio_risk.margin_available,
                'var_95': self.portfolio_risk.var_95,
                'var_99': self.portfolio_risk.var_99,
                'risk_level': self.portfolio_risk.risk_level.value,
                'timestamp': self.portfolio_risk.timestamp.isoformat()
            }

            self.redis_client.hset('risk:snapshot:current', mapping=snapshot_data)
            self.redis_client.expire('risk:snapshot:current', 3600)  # 1 hour TTL

        except Exception as e:
            logger.error(f"Failed to store risk snapshot: {e}")

    def get_stats(self) -> dict:
        """Get risk management statistics"""
        return {
            **self.stats,
            'active_positions': len(self.active_positions),
            'active_orders': len(self.active_orders),
            'active_alerts': len([a for a in self.alerts if not a.acknowledged]),
            'blocked_symbols': list(self.blocked_symbols),
            'current_risk_level': self.portfolio_risk.risk_level.value if self.portfolio_risk else 'UNKNOWN',
            'portfolio_metrics': {
                'total_exposure': self.portfolio_risk.total_exposure,
                'var_95': self.portfolio_risk.var_95,
                'margin_available': self.portfolio_risk.margin_available
            } if self.portfolio_risk else None
        }

    async def run(self):
        """Run the risk management service"""
        await self.connect_services()
        await self.subscribe_events()

        # Start periodic risk monitoring
        asyncio.create_task(self.periodic_risk_check())

        logger.info("Risk management service started")


# FastAPI app for health and metrics
app = FastAPI(title="Risk Service")
risk_engine = None


@app.on_event("startup")
async def startup_event():
    global risk_engine
    risk_engine = RiskManager()
    await risk_engine.run()


@app.get("/health")
async def health():
    """Health check endpoint"""
    global risk_engine
    if risk_engine and risk_engine.nc and risk_engine.redis_client:
        try:
            risk_engine.redis_client.ping()
            return {"status": "healthy", "service": "risk"}
        except:
            pass
    return JSONResponse(status_code=503, content={"status": "unhealthy"})


@app.get("/stats")
async def stats():
    """Get risk statistics"""
    global risk_engine
    if risk_engine:
        return risk_engine.get_stats()
    return {"error": "Engine not initialized"}


@app.get("/risk/portfolio")
async def get_portfolio_risk():
    """Get current portfolio risk assessment"""
    global risk_engine
    if risk_engine and risk_engine.portfolio_risk:
        pr = risk_engine.portfolio_risk
        return {
            'total_exposure': pr.total_exposure,
            'total_positions': pr.total_positions,
            'margin_used': pr.margin_used,
            'margin_available': pr.margin_available,
            'var_95': pr.var_95,
            'var_99': pr.var_99,
            'risk_level': pr.risk_level.value,
            'timestamp': pr.timestamp.isoformat()
        }
    return {"error": "No risk snapshot available"}


@app.get("/risk/alerts")
async def get_alerts(unacknowledged_only: bool = True):
    """Get risk alerts"""
    global risk_engine
    if risk_engine:
        alerts = risk_engine.alerts
        if unacknowledged_only:
            alerts = [a for a in alerts if not a.acknowledged]

        return [{
            'alert_id': a.alert_id,
            'type': a.alert_type.value,
            'severity': a.severity.value,
            'message': a.message,
            'symbol': a.symbol,
            'value': a.value,
            'threshold': a.threshold,
            'created_at': a.created_at.isoformat(),
            'acknowledged': a.acknowledged
        } for a in alerts]
    return []


@app.post("/risk/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge a risk alert"""
    global risk_engine
    if risk_engine:
        for alert in risk_engine.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return {"status": "acknowledged", "alert_id": alert_id}
    raise HTTPException(status_code=404, detail="Alert not found")


@app.get("/risk/limits")
async def get_risk_limits():
    """Get current risk limits and their status"""
    global risk_engine
    if risk_engine:
        limits = {}
        for name, limit in risk_engine.risk_limits.items():
            utilization = (limit.current_value / limit.max_value * 100) if limit.max_value > 0 else 0
            limits[name] = {
                'max_value': limit.max_value,
                'current_value': limit.current_value,
                'utilization': f"{utilization:.1f}%",
                'breached': limit.breached,
                'warning_threshold': limit.threshold_warning,
                'critical_threshold': limit.threshold_critical
            }
        return limits
    return {}


@app.post("/risk/symbol/{symbol}/block")
async def block_symbol(symbol: str):
    """Block a symbol from trading"""
    global risk_engine
    if risk_engine:
        risk_engine.blocked_symbols.add(symbol)
        return {"status": "blocked", "symbol": symbol}
    raise HTTPException(status_code=503, detail="Risk engine not initialized")


@app.delete("/risk/symbol/{symbol}/block")
async def unblock_symbol(symbol: str):
    """Unblock a symbol from trading"""
    global risk_engine
    if risk_engine:
        risk_engine.blocked_symbols.discard(symbol)
        return {"status": "unblocked", "symbol": symbol}
    raise HTTPException(status_code=503, detail="Risk engine not initialized")


@app.post("/check")
async def check_risk(request: dict):
    """
    Fast risk check endpoint for order submission
    Target: <1.5ms response time
    """
    global risk_engine
    if not risk_engine:
        raise HTTPException(status_code=503, detail="Risk engine not initialized")

    # Extract required fields
    account = request.get("account", "default")
    symbol = request.get("symbol")
    side = request.get("side")
    quantity = request.get("quantity", 0)
    price = request.get("price")

    # Validate required fields
    if not symbol:
        return {
            "approved": False,
            "risk_level": "CRITICAL",
            "reason": "Symbol is required"
        }

    if not side or side not in ["buy", "sell"]:
        return {
            "approved": False,
            "risk_level": "CRITICAL",
            "reason": "Valid side (buy/sell) is required"
        }

    if quantity <= 0:
        return {
            "approved": False,
            "risk_level": "CRITICAL",
            "reason": "Quantity must be positive"
        }

    # Perform risk check using existing function
    result = await risk_engine.check_order_risk({
        "account": account,
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "price": price
    })

    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8103)