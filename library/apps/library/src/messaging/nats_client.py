"""
NATS client for Library Service.
Handles connection, pub/sub, and request/reply patterns.
"""
import asyncio
import logging
from typing import Optional, Callable, Any
import json
from datetime import datetime
import nats
from nats.aio.client import Client as NATSClient
from nats.errors import TimeoutError, ConnectionClosedError

from ..core.config import settings

logger = logging.getLogger(__name__)


class LibraryNATSClient:
    """NATS client wrapper with retry logic and error handling."""

    def __init__(self):
        self.nc: Optional[NATSClient] = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10

    async def connect(self) -> None:
        """Connect to NATS with retry logic."""
        if not settings.NATS_ENABLED:
            logger.info("NATS is disabled in configuration")
            return

        retry_delay = 1

        for attempt in range(self.max_reconnect_attempts):
            try:
                self.nc = await nats.connect(
                    servers=[settings.NATS_URL],
                    name="library_service",
                    max_reconnect_attempts=60,
                    reconnect_time_wait=2,
                    error_cb=self._error_callback,
                    disconnected_cb=self._disconnected_callback,
                    reconnected_cb=self._reconnected_callback,
                    closed_cb=self._closed_callback,
                )
                self.connected = True
                self.reconnect_attempts = 0
                logger.info(f"Connected to NATS at {settings.NATS_URL}")
                return

            except Exception as e:
                self.reconnect_attempts += 1
                if attempt < self.max_reconnect_attempts - 1:
                    logger.warning(
                        f"NATS connection attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {retry_delay}s..."
                    )
                    await asyncio.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 30)  # Exponential backoff, max 30s
                else:
                    logger.error(f"Failed to connect to NATS after {self.max_reconnect_attempts} attempts")
                    raise

    async def disconnect(self) -> None:
        """Disconnect from NATS."""
        if self.nc:
            await self.nc.close()
            self.connected = False
            logger.info("Disconnected from NATS")

    async def publish(
        self,
        subject: str,
        data: dict,
        headers: Optional[dict] = None
    ) -> None:
        """
        Publish message to NATS subject.

        Args:
            subject: NATS subject (e.g., 'library.entity.registered')
            data: Message payload as dict
            headers: Optional headers
        """
        if not self.connected or not self.nc:
            logger.warning(f"Cannot publish to {subject}: Not connected to NATS")
            return

        try:
            message = json.dumps(data).encode()
            await self.nc.publish(subject, message, headers=headers)
            logger.debug(f"Published to {subject}: {data}")

        except Exception as e:
            logger.error(f"Failed to publish to {subject}: {e}")
            raise

    async def subscribe(
        self,
        subject: str,
        callback: Callable[[dict], None],
        queue: Optional[str] = None
    ) -> int:
        """
        Subscribe to NATS subject.

        Args:
            subject: NATS subject pattern (e.g., 'library.>')
            callback: Async callback function to handle messages
            queue: Optional queue group name for load balancing

        Returns:
            Subscription ID
        """
        if not self.connected or not self.nc:
            raise ConnectionError("Not connected to NATS")

        async def message_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                await callback(data)
            except Exception as e:
                logger.error(f"Error handling message from {msg.subject}: {e}")

        try:
            sid = await self.nc.subscribe(subject, queue=queue, cb=message_handler)
            logger.info(f"Subscribed to {subject}" + (f" (queue: {queue})" if queue else ""))
            return sid

        except Exception as e:
            logger.error(f"Failed to subscribe to {subject}: {e}")
            raise

    async def request(
        self,
        subject: str,
        data: dict,
        timeout: float = 5.0
    ) -> dict:
        """
        Send request and wait for reply (request/reply pattern).

        Args:
            subject: NATS subject (e.g., 'library.swap.validate')
            data: Request payload
            timeout: Timeout in seconds

        Returns:
            Reply data as dict
        """
        if not self.connected or not self.nc:
            raise ConnectionError("Not connected to NATS")

        try:
            message = json.dumps(data).encode()
            response = await self.nc.request(subject, message, timeout=timeout)
            return json.loads(response.data.decode())

        except TimeoutError:
            logger.error(f"Request to {subject} timed out after {timeout}s")
            raise
        except Exception as e:
            logger.error(f"Request to {subject} failed: {e}")
            raise

    async def reply_handler(
        self,
        subject: str,
        handler: Callable[[dict], dict]
    ) -> int:
        """
        Setup reply handler for request/reply pattern.

        Args:
            subject: NATS subject to handle
            handler: Async function that processes request and returns reply

        Returns:
            Subscription ID
        """
        async def message_handler(msg):
            try:
                request_data = json.loads(msg.data.decode())
                reply_data = await handler(request_data)
                reply_message = json.dumps(reply_data).encode()
                await self.nc.publish(msg.reply, reply_message)
            except Exception as e:
                logger.error(f"Error handling request on {subject}: {e}")
                error_reply = {"error": str(e)}
                await self.nc.publish(msg.reply, json.dumps(error_reply).encode())

        sid = await self.nc.subscribe(subject, cb=message_handler)
        logger.info(f"Setup reply handler for {subject}")
        return sid

    # Callback functions
    async def _error_callback(self, e):
        """Handle NATS errors."""
        logger.error(f"NATS error: {e}")

    async def _disconnected_callback(self):
        """Handle disconnection."""
        self.connected = False
        logger.warning("Disconnected from NATS")

    async def _reconnected_callback(self):
        """Handle reconnection."""
        self.connected = True
        logger.info("Reconnected to NATS")

    async def _closed_callback(self):
        """Handle connection close."""
        self.connected = False
        logger.info("NATS connection closed")


# Global NATS client instance
nats_client = LibraryNATSClient()
