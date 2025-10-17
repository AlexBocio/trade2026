#!/usr/bin/env python3
"""
PTRC Service - Post-Trade, Risk & Compliance
Handles post-trade processing, compliance checks, and regulatory reporting
"""

import os
import json
import yaml
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum

import uvicorn
import redis.asyncio as redis
import nats
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import pandas as pd
import httpx
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Prometheus metrics
trades_processed = Counter('ptrc_trades_processed_total', 'Total trades processed')
compliance_checks = Counter('ptrc_compliance_checks_total', 'Total compliance checks', ['status', 'type'])
regulatory_reports = Counter('ptrc_regulatory_reports_total', 'Total regulatory reports', ['type'])
settlement_status = Gauge('ptrc_settlement_status', 'Settlement status', ['status'])
reconciliation_mismatches = Counter('ptrc_reconciliation_mismatches_total', 'Total reconciliation mismatches')

compliance_latency = Histogram('ptrc_compliance_check_latency_seconds', 'Compliance check latency')
processing_latency = Histogram('ptrc_post_trade_processing_latency_seconds', 'Post-trade processing latency')

# FastAPI app
app = FastAPI(title="PTRC Service", version="1.0.0")


class ComplianceStatus(str, Enum):
    PENDING = "PENDING"
    CHECKING = "CHECKING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    REVIEW = "REVIEW"


class SettlementStatus(str, Enum):
    UNSETTLED = "UNSETTLED"
    PENDING = "PENDING"
    SETTLED = "SETTLED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Trade(BaseModel):
    """Trade model for post-trade processing"""
    trade_id: str
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    venue: str
    execution_time: datetime
    account_id: str
    counterparty: Optional[str] = None
    settlement_date: Optional[datetime] = None


class ComplianceCheck(BaseModel):
    """Compliance check result"""
    trade_id: str
    check_type: str
    status: ComplianceStatus
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RegulatoryReport(BaseModel):
    """Regulatory report"""
    report_id: str
    report_type: str
    period_start: datetime
    period_end: datetime
    trades_count: int
    total_volume: float
    status: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class PTRCService:
    """Post-Trade, Risk & Compliance Service"""

    def __init__(self):
        self.redis_client = None
        self.nc = None
        self.compliance_cache = {}
        self.settlement_queue = []
        self.running = False

    async def start(self):
        """Start the PTRC service"""
        logger.info("Starting PTRC service...")

        # Connect to Redis
        self.redis_client = await redis.from_url(
            f"redis://{config['redis_host']}:{config['redis_port']}/{config['redis_db']}"
        )

        # Connect to NATS
        self.nc = await nats.connect(config['nats_url'])

        # Subscribe to trade events
        await self.nc.subscribe("trades.executed", "ptrc", self.handle_executed_trade)
        await self.nc.subscribe("trades.cancelled", "ptrc", self.handle_cancelled_trade)

        # Start background tasks
        self.running = True
        asyncio.create_task(self.reconciliation_loop())
        asyncio.create_task(self.settlement_monitor())
        asyncio.create_task(self.regulatory_reporting())

        logger.info("PTRC service started successfully")

    async def stop(self):
        """Stop the PTRC service"""
        self.running = False
        if self.nc:
            await self.nc.close()
        if self.redis_client:
            await self.redis_client.close()

    async def handle_executed_trade(self, msg):
        """Handle executed trade for post-trade processing"""
        try:
            trade_data = json.loads(msg.data.decode())
            trade = Trade(**trade_data)

            # Start post-trade processing
            with processing_latency.time():
                await self.process_trade(trade)

            trades_processed.inc()

        except Exception as e:
            logger.error(f"Error processing executed trade: {e}")

    async def handle_cancelled_trade(self, msg):
        """Handle cancelled trade"""
        try:
            trade_data = json.loads(msg.data.decode())
            trade_id = trade_data.get('trade_id')

            # Update settlement status
            await self.update_settlement_status(trade_id, SettlementStatus.CANCELLED)

        except Exception as e:
            logger.error(f"Error handling cancelled trade: {e}")

    async def process_trade(self, trade: Trade):
        """Process trade through post-trade workflow"""

        # 1. Compliance checks
        compliance_result = await self.run_compliance_checks(trade)

        # 2. Risk monitoring
        await self.monitor_risk(trade)

        # 3. Settlement processing
        await self.process_settlement(trade)

        # 4. Audit logging
        await self.audit_log(trade, compliance_result)

        # 5. Send notifications
        await self.send_notifications(trade, compliance_result)

    async def run_compliance_checks(self, trade: Trade) -> ComplianceCheck:
        """Run compliance checks on trade"""
        with compliance_latency.time():

            # Check sanctions
            if config['compliance']['check_sanctions']:
                sanctions_result = await self.check_sanctions(trade)
                if sanctions_result.status == ComplianceStatus.FAILED:
                    compliance_checks.labels(status='failed', type='sanctions').inc()
                    return sanctions_result

            # Check AML
            if config['compliance']['check_aml']:
                aml_result = await self.check_aml(trade)
                if aml_result.status == ComplianceStatus.FAILED:
                    compliance_checks.labels(status='failed', type='aml').inc()
                    return aml_result

            # Check KYC
            if config['compliance']['check_kyc']:
                kyc_result = await self.check_kyc(trade)
                if kyc_result.status == ComplianceStatus.FAILED:
                    compliance_checks.labels(status='failed', type='kyc').inc()
                    return kyc_result

            # All checks passed
            compliance_checks.labels(status='passed', type='all').inc()
            return ComplianceCheck(
                trade_id=trade.trade_id,
                check_type="ALL",
                status=ComplianceStatus.PASSED,
                message="All compliance checks passed"
            )

    async def check_sanctions(self, trade: Trade) -> ComplianceCheck:
        """Check trade against sanctions lists"""
        # Simulate sanctions check
        await asyncio.sleep(0.001)  # 1ms check time

        # Check counterparty against sanctions list
        if trade.counterparty and trade.counterparty in self.get_sanctions_list():
            return ComplianceCheck(
                trade_id=trade.trade_id,
                check_type="SANCTIONS",
                status=ComplianceStatus.FAILED,
                message=f"Counterparty {trade.counterparty} is on sanctions list"
            )

        return ComplianceCheck(
            trade_id=trade.trade_id,
            check_type="SANCTIONS",
            status=ComplianceStatus.PASSED
        )

    async def check_aml(self, trade: Trade) -> ComplianceCheck:
        """Anti-Money Laundering check"""
        # Simulate AML check
        await asyncio.sleep(0.001)

        # Check for suspicious patterns
        if trade.quantity * trade.price > 100000:  # Large transaction
            # Flag for review
            return ComplianceCheck(
                trade_id=trade.trade_id,
                check_type="AML",
                status=ComplianceStatus.REVIEW,
                message="Large transaction flagged for review"
            )

        return ComplianceCheck(
            trade_id=trade.trade_id,
            check_type="AML",
            status=ComplianceStatus.PASSED
        )

    async def check_kyc(self, trade: Trade) -> ComplianceCheck:
        """Know Your Customer check"""
        # Check if account has completed KYC
        kyc_status = await self.redis_client.hget(f"kyc:{trade.account_id}", "status")

        if not kyc_status or kyc_status.decode() != "VERIFIED":
            return ComplianceCheck(
                trade_id=trade.trade_id,
                check_type="KYC",
                status=ComplianceStatus.FAILED,
                message="Account KYC not verified"
            )

        return ComplianceCheck(
            trade_id=trade.trade_id,
            check_type="KYC",
            status=ComplianceStatus.PASSED
        )

    async def monitor_risk(self, trade: Trade):
        """Monitor post-trade risk"""
        # Check position limits
        if config['risk_monitoring']['position_limit_check']:
            await self.check_position_limits(trade)

        # Check exposure limits
        if config['risk_monitoring']['exposure_limit_check']:
            await self.check_exposure_limits(trade)

        # Check concentration
        if config['risk_monitoring']['concentration_check']:
            await self.check_concentration(trade)

    async def check_position_limits(self, trade: Trade):
        """Check if trade violates position limits"""
        # Get current position
        position_key = f"position:{trade.account_id}:{trade.symbol}"
        current_position = await self.redis_client.get(position_key)

        if current_position:
            position = float(current_position)
            # Check against limits (simplified)
            if abs(position) > 100000:
                logger.warning(f"Position limit warning for {trade.account_id} in {trade.symbol}")

    async def check_exposure_limits(self, trade: Trade):
        """Check exposure limits"""
        # Calculate exposure
        exposure = trade.quantity * trade.price

        # Check against account limits
        max_exposure = await self.redis_client.hget(f"limits:{trade.account_id}", "max_exposure")
        if max_exposure and exposure > float(max_exposure):
            logger.warning(f"Exposure limit exceeded for {trade.account_id}")

    async def check_concentration(self, trade: Trade):
        """Check portfolio concentration"""
        # Simplified concentration check
        pass

    async def process_settlement(self, trade: Trade):
        """Process trade settlement"""
        # Calculate settlement date (T+2 by default)
        settlement_days = config['post_trade']['t_plus_settlement_days']
        settlement_date = trade.execution_time + timedelta(days=settlement_days)
        trade.settlement_date = settlement_date

        # Add to settlement queue
        self.settlement_queue.append({
            'trade_id': trade.trade_id,
            'settlement_date': settlement_date,
            'status': SettlementStatus.PENDING
        })

        # Update settlement status
        await self.update_settlement_status(trade.trade_id, SettlementStatus.PENDING)
        settlement_status.labels(status='pending').inc()

    async def update_settlement_status(self, trade_id: str, status: SettlementStatus):
        """Update settlement status in Redis"""
        await self.redis_client.hset(
            f"settlement:{trade_id}",
            mapping={
                'status': status.value,
                'updated_at': datetime.utcnow().isoformat()
            }
        )

    async def audit_log(self, trade: Trade, compliance_result: ComplianceCheck):
        """Create audit log entry"""
        if config['audit']['enabled']:
            audit_entry = {
                'trade_id': trade.trade_id,
                'order_id': trade.order_id,
                'symbol': trade.symbol,
                'quantity': trade.quantity,
                'price': trade.price,
                'venue': trade.venue,
                'account_id': trade.account_id,
                'compliance_status': compliance_result.status.value,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Store in Redis with TTL
            ttl_seconds = config['audit']['retention_days'] * 86400
            await self.redis_client.setex(
                f"audit:{trade.trade_id}",
                ttl_seconds,
                json.dumps(audit_entry)
            )

    async def send_notifications(self, trade: Trade, compliance_result: ComplianceCheck):
        """Send notifications for important events"""
        # Notify on compliance failures
        if compliance_result.status == ComplianceStatus.FAILED:
            await self.nc.publish(
                "alerts.compliance.failed",
                json.dumps({
                    'trade_id': trade.trade_id,
                    'reason': compliance_result.message,
                    'timestamp': datetime.utcnow().isoformat()
                }).encode()
            )

    async def reconciliation_loop(self):
        """Periodic reconciliation"""
        while self.running:
            try:
                interval = config['post_trade']['reconciliation_interval']
                await asyncio.sleep(interval)

                # Perform reconciliation
                await self.reconcile_trades()

            except Exception as e:
                logger.error(f"Error in reconciliation loop: {e}")

    async def reconcile_trades(self):
        """Reconcile trades with external systems"""
        # Get trades to reconcile
        trades = await self.get_pending_reconciliation()

        for trade in trades:
            # Simulate reconciliation
            is_matched = await self.match_with_counterparty(trade)

            if not is_matched:
                reconciliation_mismatches.inc()
                logger.warning(f"Reconciliation mismatch for trade {trade['trade_id']}")

    async def get_pending_reconciliation(self) -> List[Dict]:
        """Get trades pending reconciliation"""
        # Simplified - get from Redis
        return []

    async def match_with_counterparty(self, trade: Dict) -> bool:
        """Match trade with counterparty records"""
        # Simulate matching logic
        return True

    async def settlement_monitor(self):
        """Monitor settlement status"""
        while self.running:
            try:
                interval = config['post_trade']['settlement_check_interval']
                await asyncio.sleep(interval)

                # Check settlement queue
                now = datetime.utcnow()
                for item in self.settlement_queue:
                    if item['status'] == SettlementStatus.PENDING:
                        if item['settlement_date'] <= now:
                            # Process settlement
                            await self.settle_trade(item['trade_id'])

            except Exception as e:
                logger.error(f"Error in settlement monitor: {e}")

    async def settle_trade(self, trade_id: str):
        """Settle a trade"""
        # Update status to settled
        await self.update_settlement_status(trade_id, SettlementStatus.SETTLED)
        settlement_status.labels(status='settled').inc()

        # Remove from queue
        self.settlement_queue = [
            item for item in self.settlement_queue
            if item['trade_id'] != trade_id
        ]

    async def regulatory_reporting(self):
        """Generate regulatory reports"""
        while self.running:
            try:
                if not config['regulatory']['enabled']:
                    await asyncio.sleep(60)
                    continue

                interval = config['regulatory']['report_interval']
                await asyncio.sleep(interval)

                # Generate reports for each type
                for report_type in config['regulatory']['report_types']:
                    await self.generate_report(report_type)

            except Exception as e:
                logger.error(f"Error in regulatory reporting: {e}")

    async def generate_report(self, report_type: str):
        """Generate a regulatory report"""
        logger.info(f"Generating {report_type} report...")

        # Get trades for reporting period
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)

        # Create report
        report = RegulatoryReport(
            report_id=f"{report_type}_{end_time.strftime('%Y%m%d_%H%M%S')}",
            report_type=report_type,
            period_start=start_time,
            period_end=end_time,
            trades_count=0,  # Would get from database
            total_volume=0.0,  # Would calculate
            status="GENERATED"
        )

        # Store report
        await self.redis_client.setex(
            f"report:{report.report_id}",
            config['regulatory']['retention_days'] * 86400,
            json.dumps(report.dict(), default=str)
        )

        regulatory_reports.labels(type=report_type).inc()
        logger.info(f"Generated {report_type} report: {report.report_id}")

    def get_sanctions_list(self) -> List[str]:
        """Get current sanctions list"""
        # In production, this would fetch from a sanctions database
        return ["BLOCKED_ENTITY_1", "BLOCKED_ENTITY_2"]


# Service instance
ptrc_service = PTRCService()


@app.on_event("startup")
async def startup_event():
    """Start the PTRC service on app startup"""
    await ptrc_service.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown"""
    await ptrc_service.stop()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "PTRC",
        "version": "1.0.0",
        "status": "running",
        "description": "Post-Trade, Risk & Compliance Service"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    checks = {
        "redis": False,
        "nats": False,
        "service": ptrc_service.running
    }

    # Check Redis
    try:
        if ptrc_service.redis_client:
            await ptrc_service.redis_client.ping()
            checks["redis"] = True
    except:
        pass

    # Check NATS
    if ptrc_service.nc and ptrc_service.nc.is_connected:
        checks["nats"] = True

    is_healthy = all(checks.values())

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/compliance/check")
async def check_compliance(trade: Trade):
    """Manual compliance check endpoint"""
    result = await ptrc_service.run_compliance_checks(trade)
    return result


@app.get("/settlement/{trade_id}")
async def get_settlement_status(trade_id: str):
    """Get settlement status for a trade"""
    status = await ptrc_service.redis_client.hget(f"settlement:{trade_id}", "status")

    if not status:
        raise HTTPException(status_code=404, detail="Trade not found")

    return {
        "trade_id": trade_id,
        "status": status.decode(),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/reports/{report_type}")
async def get_reports(report_type: str, limit: int = 10):
    """Get recent reports of a specific type"""
    # Get report keys
    pattern = f"report:{report_type}_*"
    keys = await ptrc_service.redis_client.keys(pattern)

    reports = []
    for key in keys[:limit]:
        report_data = await ptrc_service.redis_client.get(key)
        if report_data:
            reports.append(json.loads(report_data))

    return {
        "report_type": report_type,
        "count": len(reports),
        "reports": reports
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


@app.get("/stats")
async def get_stats():
    """Get service statistics"""
    return {
        "trades_processed": trades_processed._value.get(),
        "settlement_queue_size": len(ptrc_service.settlement_queue),
        "compliance_cache_size": len(ptrc_service.compliance_cache),
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8109)