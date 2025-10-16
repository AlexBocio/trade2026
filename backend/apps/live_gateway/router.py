"""
Order Router - SHADOW/CANARY/LIVE Routing Logic
Phase 11: Live Trading Enablement
"""

import logging
from typing import Dict, Optional
from pydantic import BaseModel

from modes import ModeManager, TradingMode
from ramp_scheduler import RampScheduler
from adapters.venue_health import VenueHealthMonitor
from adapters.idempotency import IdempotencyManager
from adapters import BaseAdapter, OrderResult
from audit_logger import AuditLogger

logger = logging.getLogger(__name__)


class OrderRequest(BaseModel):
    """Incoming order request"""
    tenant: str
    account_id: str
    venue: str
    symbol: str
    side: str
    order_type: str
    qty: float
    price: Optional[float] = None
    client_order_id: str


class RoutingDecision(BaseModel):
    """Routing decision result"""
    execute_live: bool
    actual_qty: float
    reason: str
    shadow_only: bool = False


class OrderRouter:
    """Routes orders based on mode/ramp/health"""

    def __init__(
        self,
        mode_manager: ModeManager,
        ramp_scheduler: RampScheduler,
        health_monitor: VenueHealthMonitor,
        idempotency_manager: IdempotencyManager,
        adapters: Dict[str, BaseAdapter],
        audit_logger: Optional[AuditLogger] = None
    ):
        self.mode_manager = mode_manager
        self.ramp_scheduler = ramp_scheduler
        self.health_monitor = health_monitor
        self.idempotency_manager = idempotency_manager
        self.adapters = adapters
        self.audit_logger = audit_logger

        logger.info("OrderRouter initialized")

    def make_routing_decision(self, order: OrderRequest) -> RoutingDecision:
        """
        Determine if order should execute live

        Steps:
        1. Check venue health (circuit breaker)
        2. Check trading mode
        3. Check ramp capacity
        """

        # 1. Circuit breaker check
        if not self.health_monitor.can_execute(order.venue):
            logger.warning(f"Circuit breaker OPEN for {order.venue} - SHADOW only")
            return RoutingDecision(
                execute_live=False,
                actual_qty=0.0,
                reason="Circuit breaker OPEN",
                shadow_only=True
            )

        # 2. Mode check
        should_execute, mode_qty = self.mode_manager.should_execute_live(order.venue, order.qty)

        if not should_execute:
            return RoutingDecision(
                execute_live=False,
                actual_qty=0.0,
                reason="Mode is SHADOW",
                shadow_only=True
            )

        # 3. Ramp capacity check
        notional = mode_qty * (order.price or 0)
        capacity_ok, capacity_msg = self.ramp_scheduler.check_capacity(notional)

        if not capacity_ok:
            logger.warning(f"Ramp capacity exceeded: {capacity_msg}")
            return RoutingDecision(
                execute_live=False,
                actual_qty=0.0,
                reason=capacity_msg,
                shadow_only=False
            )

        # Approved for live execution
        return RoutingDecision(
            execute_live=True,
            actual_qty=mode_qty,
            reason=f"Mode={self.mode_manager.get_mode(order.venue).mode}, qty={mode_qty}"
        )

    async def route_order(self, order: OrderRequest) -> OrderResult:
        """
        Route order to appropriate adapter

        Returns:
            OrderResult with ext_order_id
        """

        # Check idempotency
        existing = self.idempotency_manager.get_external_id(
            order.tenant,
            order.account_id,
            order.client_order_id
        )

        if existing:
            logger.warning(f"Duplicate order: {order.client_order_id} → {existing}")
            return OrderResult(
                ext_order_id=existing,
                status="DUPLICATE",
                msg="Order already submitted"
            )

        # Make routing decision
        decision = self.make_routing_decision(order)

        logger.info(f"Routing decision: {decision.model_dump()}")

        if not decision.execute_live:
            # SHADOW mode - just log
            logger.info(f"SHADOW: {order.side} {order.qty} {order.symbol} @ {order.price} (reason: {decision.reason})")
            shadow_id = f"SHADOW_{order.client_order_id}"

            # Record idempotency even for shadow
            self.idempotency_manager.check_and_set(
                order.tenant,
                order.account_id,
                order.client_order_id,
                shadow_id
            )

            # Audit log
            if self.audit_logger:
                self.audit_logger.log_order({
                    'tenant': order.tenant,
                    'account_id': order.account_id,
                    'venue': order.venue,
                    'symbol': order.symbol,
                    'side': order.side,
                    'order_type': order.order_type,
                    'qty': order.qty,
                    'price': order.price,
                    'client_order_id': order.client_order_id,
                    'ext_order_id': shadow_id,
                    'status': 'SHADOW',
                    'reason': decision.reason
                })

            return OrderResult(
                ext_order_id=shadow_id,
                status="SHADOW",
                msg=decision.reason
            )

        # LIVE or CANARY execution
        adapter = self.adapters.get(order.venue)
        if not adapter:
            logger.error(f"No adapter for venue: {order.venue}")
            return OrderResult(
                ext_order_id=f"ERROR_{order.client_order_id}",
                status="ERROR",
                msg=f"No adapter for venue {order.venue}"
            )

        try:
            # Submit to venue
            result = await adapter.submit_order(
                account_id=order.account_id,
                symbol=order.symbol,
                side=order.side,
                order_type=order.order_type,
                qty=decision.actual_qty,
                price=order.price,
                client_order_id=order.client_order_id
            )

            # Record idempotency
            duplicate = self.idempotency_manager.check_and_set(
                order.tenant,
                order.account_id,
                order.client_order_id,
                result.ext_order_id
            )

            # Record notional for ramp
            notional = decision.actual_qty * (order.price or 0)
            self.ramp_scheduler.record_notional(notional)

            # Record success for circuit breaker
            self.health_monitor.record_success(order.venue)

            # Audit log success
            if self.audit_logger:
                self.audit_logger.log_order({
                    'tenant': order.tenant,
                    'account_id': order.account_id,
                    'venue': order.venue,
                    'symbol': order.symbol,
                    'side': order.side,
                    'order_type': order.order_type,
                    'qty': decision.actual_qty,
                    'price': order.price,
                    'client_order_id': order.client_order_id,
                    'ext_order_id': result.ext_order_id,
                    'status': result.status,
                    'reason': decision.reason
                })

            logger.info(f"LIVE order submitted: {result.ext_order_id} ({decision.reason})")
            return result

        except Exception as e:
            logger.error(f"Order submission failed: {e}")

            # Record failure for circuit breaker
            self.health_monitor.record_failure(order.venue)

            # Audit log failure
            if self.audit_logger:
                self.audit_logger.log_order({
                    'tenant': order.tenant,
                    'account_id': order.account_id,
                    'venue': order.venue,
                    'symbol': order.symbol,
                    'side': order.side,
                    'order_type': order.order_type,
                    'qty': order.qty,
                    'price': order.price,
                    'client_order_id': order.client_order_id,
                    'ext_order_id': f"ERROR_{order.client_order_id}",
                    'status': 'ERROR',
                    'reason': str(e)
                })

            return OrderResult(
                ext_order_id=f"ERROR_{order.client_order_id}",
                status="ERROR",
                msg=str(e)
            )
