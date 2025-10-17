#!/usr/bin/env python3
"""
Execution Quality Service - Trade Execution Quality Analysis
Provides TCA (Transaction Cost Analysis) and execution quality metrics
"""

import os
import json
import yaml
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from collections import defaultdict

import uvicorn
import redis.asyncio as redis
import nats
from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Prometheus metrics
executions_analyzed = Counter('execution_quality_analyzed_total', 'Total executions analyzed')
slippage_histogram = Histogram('execution_slippage_bps', 'Execution slippage in basis points', ['venue'])
fill_rate_gauge = Gauge('execution_fill_rate', 'Fill rate by venue', ['venue'])
latency_histogram = Histogram('execution_latency_ms', 'Execution latency', ['venue'])
price_improvement = Counter('execution_price_improvement_total', 'Price improvements', ['type'])

# FastAPI app
app = FastAPI(title="Execution Quality Service", version="1.0.0")


class Execution(BaseModel):
    """Execution model"""
    execution_id: str
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    venue: str
    timestamp: datetime
    arrival_price: Optional[float] = None
    benchmark_price: Optional[float] = None


class ExecutionMetrics(BaseModel):
    """Execution quality metrics"""
    execution_id: str
    slippage_bps: float
    fill_rate: float
    latency_ms: float
    market_impact_bps: float
    price_improvement_bps: float
    implementation_shortfall: float


class VenueStats(BaseModel):
    """Venue statistics"""
    venue: str
    total_executions: int
    avg_slippage_bps: float
    avg_fill_rate: float
    avg_latency_ms: float
    price_improvement_rate: float


class QualityReport(BaseModel):
    """Execution quality report"""
    period_start: datetime
    period_end: datetime
    total_executions: int
    avg_slippage_bps: float
    avg_fill_rate: float
    best_venue: str
    worst_venue: str
    metrics: Dict[str, Any]


class ExecutionQualityService:
    """Execution quality analysis service"""

    def __init__(self):
        self.redis_client = None
        self.nc = None
        self.execution_buffer = []
        self.venue_stats = defaultdict(lambda: {
            'executions': 0,
            'total_slippage': 0,
            'total_fill': 0,
            'total_latency': 0,
            'price_improvements': 0
        })
        self.running = False

    async def start(self):
        """Start the execution quality service"""
        logger.info("Starting Execution Quality service...")

        # Connect to Redis
        self.redis_client = await redis.from_url(
            f"redis://{config['redis_host']}:{config['redis_port']}/{config['redis_db']}"
        )

        # Connect to NATS
        self.nc = await nats.connect(config['nats_url'])

        # Subscribe to execution events
        await self.nc.subscribe("executions.completed", "exec_quality", self.handle_execution)
        await self.nc.subscribe("orders.filled", "exec_quality", self.handle_order_fill)

        # Start background tasks
        self.running = True
        asyncio.create_task(self.analysis_loop())
        asyncio.create_task(self.reporting_loop())
        asyncio.create_task(self.benchmark_calculator())

        logger.info("Execution Quality service started successfully")

    async def stop(self):
        """Stop the execution quality service"""
        self.running = False
        if self.nc:
            await self.nc.close()
        if self.redis_client:
            await self.redis_client.close()

    async def handle_execution(self, msg):
        """Handle execution completed events"""
        try:
            execution_data = json.loads(msg.data.decode())
            execution = Execution(**execution_data)

            # Add to buffer for analysis
            self.execution_buffer.append(execution)

            # Store in Redis
            await self.store_execution(execution)

            executions_analyzed.inc()

        except Exception as e:
            logger.error(f"Error handling execution: {e}")

    async def handle_order_fill(self, msg):
        """Handle order fill events"""
        try:
            fill_data = json.loads(msg.data.decode())

            # Calculate immediate metrics
            metrics = await self.calculate_immediate_metrics(fill_data)

            # Store metrics
            await self.store_metrics(metrics)

        except Exception as e:
            logger.error(f"Error handling order fill: {e}")

    async def store_execution(self, execution: Execution):
        """Store execution data"""
        key = f"execution:{execution.execution_id}"
        await self.redis_client.setex(
            key,
            86400,  # 24 hours
            json.dumps(execution.dict(), default=str)
        )

        # Add to venue list
        venue_key = f"venue:{execution.venue}:executions"
        await self.redis_client.lpush(venue_key, execution.execution_id)
        await self.redis_client.ltrim(venue_key, 0, 999)  # Keep last 1000

    async def store_metrics(self, metrics: Dict[str, Any]):
        """Store execution metrics"""
        if 'execution_id' in metrics:
            key = f"metrics:{metrics['execution_id']}"
            await self.redis_client.setex(
                key,
                86400,  # 24 hours
                json.dumps(metrics, default=str)
            )

    async def calculate_immediate_metrics(self, fill_data: Dict) -> Dict[str, Any]:
        """Calculate immediate execution metrics"""
        metrics = {
            'execution_id': fill_data.get('execution_id'),
            'timestamp': datetime.utcnow().isoformat()
        }

        try:
            # Calculate slippage
            if 'arrival_price' in fill_data and 'execution_price' in fill_data:
                arrival = fill_data['arrival_price']
                execution = fill_data['execution_price']
                slippage_bps = ((execution - arrival) / arrival) * 10000
                metrics['slippage_bps'] = slippage_bps

                venue = fill_data.get('venue', 'unknown')
                slippage_histogram.labels(venue=venue).observe(abs(slippage_bps))

            # Calculate latency
            if 'order_time' in fill_data and 'execution_time' in fill_data:
                order_time = datetime.fromisoformat(fill_data['order_time'])
                exec_time = datetime.fromisoformat(fill_data['execution_time'])
                latency_ms = (exec_time - order_time).total_seconds() * 1000
                metrics['latency_ms'] = latency_ms

                venue = fill_data.get('venue', 'unknown')
                latency_histogram.labels(venue=venue).observe(latency_ms)

            # Calculate fill rate
            if 'ordered_quantity' in fill_data and 'filled_quantity' in fill_data:
                fill_rate = fill_data['filled_quantity'] / fill_data['ordered_quantity']
                metrics['fill_rate'] = fill_rate

        except Exception as e:
            logger.error(f"Error calculating immediate metrics: {e}")

        return metrics

    async def calculate_execution_metrics(self, execution: Execution) -> ExecutionMetrics:
        """Calculate comprehensive execution metrics"""

        # Get benchmark prices
        benchmark = await self.get_benchmark_price(
            execution.symbol,
            execution.timestamp
        )

        # Calculate slippage
        slippage_bps = 0
        if execution.arrival_price:
            slippage_bps = ((execution.price - execution.arrival_price) /
                          execution.arrival_price) * 10000

        # Calculate market impact (simplified)
        market_impact_bps = abs(slippage_bps) * 0.3  # Simplified assumption

        # Calculate price improvement
        price_improvement_bps = 0
        if benchmark:
            if execution.side == "BUY":
                price_improvement_bps = ((benchmark - execution.price) / benchmark) * 10000
            else:
                price_improvement_bps = ((execution.price - benchmark) / benchmark) * 10000

        # Implementation shortfall (simplified)
        implementation_shortfall = abs(slippage_bps) + market_impact_bps

        # Fill rate (assuming full fill for now)
        fill_rate = 1.0

        # Latency (placeholder - would come from order timestamps)
        latency_ms = 50.0

        return ExecutionMetrics(
            execution_id=execution.execution_id,
            slippage_bps=slippage_bps,
            fill_rate=fill_rate,
            latency_ms=latency_ms,
            market_impact_bps=market_impact_bps,
            price_improvement_bps=price_improvement_bps,
            implementation_shortfall=implementation_shortfall
        )

    async def get_benchmark_price(self, symbol: str, timestamp: datetime) -> Optional[float]:
        """Get benchmark price for comparison"""
        # This would fetch VWAP/TWAP from market data
        # For now, return a placeholder
        market_key = f"market:{symbol}:last"
        price = await self.redis_client.get(market_key)
        if price:
            return float(price)
        return None

    async def calculate_vwap(self, symbol: str, start_time: datetime, end_time: datetime) -> float:
        """Calculate VWAP for a period"""
        # Simplified VWAP calculation
        # In production, this would query actual trade data
        return 0.0

    async def calculate_twap(self, symbol: str, start_time: datetime, end_time: datetime) -> float:
        """Calculate TWAP for a period"""
        # Simplified TWAP calculation
        # In production, this would query actual price data
        return 0.0

    async def update_venue_stats(self, venue: str, metrics: ExecutionMetrics):
        """Update venue statistics"""
        stats = self.venue_stats[venue]
        stats['executions'] += 1
        stats['total_slippage'] += abs(metrics.slippage_bps)
        stats['total_fill'] += metrics.fill_rate
        stats['total_latency'] += metrics.latency_ms

        if metrics.price_improvement_bps > 0:
            stats['price_improvements'] += 1

        # Update Prometheus metrics
        fill_rate_gauge.labels(venue=venue).set(
            stats['total_fill'] / stats['executions']
        )

    async def analysis_loop(self):
        """Periodic analysis of executions"""
        while self.running:
            try:
                await asyncio.sleep(config['analysis']['compute_interval'])

                # Process buffered executions
                while self.execution_buffer:
                    execution = self.execution_buffer.pop(0)

                    # Calculate metrics
                    metrics = await self.calculate_execution_metrics(execution)

                    # Update venue stats
                    await self.update_venue_stats(execution.venue, metrics)

                    # Store metrics
                    await self.store_metrics(metrics.dict())

            except Exception as e:
                logger.error(f"Error in analysis loop: {e}")

    async def reporting_loop(self):
        """Generate periodic reports"""
        while self.running:
            try:
                if not config['reporting']['enabled']:
                    await asyncio.sleep(60)
                    continue

                await asyncio.sleep(config['reporting']['generate_interval'])

                # Generate reports
                report = await self.generate_report()

                # Store report
                await self.store_report(report)

                # Send alerts if needed
                await self.check_alerts(report)

            except Exception as e:
                logger.error(f"Error in reporting loop: {e}")

    async def generate_report(self) -> QualityReport:
        """Generate execution quality report"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=config['analysis']['metrics_window'])

        # Calculate aggregates
        total_executions = sum(s['executions'] for s in self.venue_stats.values())

        if total_executions == 0:
            return QualityReport(
                period_start=start_time,
                period_end=end_time,
                total_executions=0,
                avg_slippage_bps=0,
                avg_fill_rate=0,
                best_venue="N/A",
                worst_venue="N/A",
                metrics={}
            )

        total_slippage = sum(s['total_slippage'] for s in self.venue_stats.values())
        total_fill = sum(s['total_fill'] for s in self.venue_stats.values())

        # Find best/worst venues
        venue_scores = {}
        for venue, stats in self.venue_stats.items():
            if stats['executions'] > 0:
                venue_scores[venue] = stats['total_slippage'] / stats['executions']

        best_venue = min(venue_scores, key=venue_scores.get) if venue_scores else "N/A"
        worst_venue = max(venue_scores, key=venue_scores.get) if venue_scores else "N/A"

        return QualityReport(
            period_start=start_time,
            period_end=end_time,
            total_executions=total_executions,
            avg_slippage_bps=total_slippage / total_executions,
            avg_fill_rate=total_fill / total_executions,
            best_venue=best_venue,
            worst_venue=worst_venue,
            metrics={
                'venue_stats': {k: dict(v) for k, v in self.venue_stats.items()}
            }
        )

    async def store_report(self, report: QualityReport):
        """Store quality report"""
        key = f"report:{report.period_end.strftime('%Y%m%d_%H%M%S')}"
        await self.redis_client.setex(
            key,
            config['reporting']['retention_days'] * 86400,
            json.dumps(report.dict(), default=str)
        )

    async def check_alerts(self, report: QualityReport):
        """Check for alert conditions"""
        if not config['alerting']['enabled']:
            return

        alerts = []

        # Check slippage threshold
        if report.avg_slippage_bps > config['alerting']['thresholds']['high_slippage_bps']:
            alerts.append({
                'type': 'high_slippage',
                'value': report.avg_slippage_bps,
                'threshold': config['alerting']['thresholds']['high_slippage_bps']
            })

        # Check fill rate
        if report.avg_fill_rate < config['alerting']['thresholds']['low_fill_rate']:
            alerts.append({
                'type': 'low_fill_rate',
                'value': report.avg_fill_rate,
                'threshold': config['alerting']['thresholds']['low_fill_rate']
            })

        # Send alerts
        for alert in alerts:
            await self.send_alert(alert)

    async def send_alert(self, alert: Dict):
        """Send alert via configured channels"""
        logger.warning(f"Alert: {alert}")

        # Send via NATS
        if 'nats' in config['alerting']['channels']:
            await self.nc.publish(
                "alerts.execution_quality",
                json.dumps(alert).encode()
            )

    async def benchmark_calculator(self):
        """Calculate and store benchmark prices"""
        while self.running:
            try:
                await asyncio.sleep(30)  # Run every 30 seconds

                # This would calculate VWAP/TWAP for active symbols
                # Simplified for now

            except Exception as e:
                logger.error(f"Error in benchmark calculator: {e}")

    def get_venue_statistics(self) -> List[VenueStats]:
        """Get current venue statistics"""
        stats = []

        for venue, data in self.venue_stats.items():
            if data['executions'] > 0:
                stats.append(VenueStats(
                    venue=venue,
                    total_executions=data['executions'],
                    avg_slippage_bps=data['total_slippage'] / data['executions'],
                    avg_fill_rate=data['total_fill'] / data['executions'],
                    avg_latency_ms=data['total_latency'] / data['executions'],
                    price_improvement_rate=data['price_improvements'] / data['executions']
                ))

        return stats


# Service instance
quality_service = ExecutionQualityService()


@app.on_event("startup")
async def startup_event():
    """Start the execution quality service on app startup"""
    await quality_service.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown"""
    await quality_service.stop()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Execution Quality",
        "version": "1.0.0",
        "status": "running",
        "description": "Trade Execution Quality Analysis Service"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    checks = {
        "redis": False,
        "nats": False,
        "service": quality_service.running
    }

    # Check Redis
    try:
        if quality_service.redis_client:
            await quality_service.redis_client.ping()
            checks["redis"] = True
    except:
        pass

    # Check NATS
    if quality_service.nc and quality_service.nc.is_connected:
        checks["nats"] = True

    is_healthy = all(checks.values())

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/venues")
async def get_venue_statistics():
    """Get venue statistics"""
    stats = quality_service.get_venue_statistics()
    return {
        "venues": [s.dict() for s in stats],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/execution/{execution_id}")
async def get_execution_metrics(execution_id: str):
    """Get metrics for a specific execution"""
    key = f"metrics:{execution_id}"
    metrics = await quality_service.redis_client.get(key)

    if not metrics:
        raise HTTPException(status_code=404, detail="Execution metrics not found")

    return json.loads(metrics)


@app.get("/report/latest")
async def get_latest_report():
    """Get the latest execution quality report"""
    # Get the most recent report key
    pattern = "report:*"
    keys = await quality_service.redis_client.keys(pattern)

    if not keys:
        return {"message": "No reports available"}

    # Sort keys to get the latest
    keys.sort(reverse=True)
    latest_key = keys[0]

    report = await quality_service.redis_client.get(latest_key)
    return json.loads(report)


@app.get("/benchmarks/{symbol}")
async def get_benchmarks(symbol: str, window_minutes: int = Query(5)):
    """Get benchmark prices for a symbol"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=window_minutes)

    vwap = await quality_service.calculate_vwap(symbol, start_time, end_time)
    twap = await quality_service.calculate_twap(symbol, start_time, end_time)

    return {
        "symbol": symbol,
        "window_minutes": window_minutes,
        "vwap": vwap,
        "twap": twap,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/analyze")
async def analyze_execution(execution: Execution):
    """Manually analyze an execution"""
    metrics = await quality_service.calculate_execution_metrics(execution)
    return metrics


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


@app.get("/stats")
async def get_stats():
    """Get service statistics"""
    return {
        "buffer_size": len(quality_service.execution_buffer),
        "venues_tracked": len(quality_service.venue_stats),
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8092)