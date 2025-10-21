"""
Event publisher for Library Service.
"""
import logging
from typing import Optional, Dict, Any
from uuid import uuid4
from datetime import datetime

from .nats_client import nats_client
from .events import (
    LibraryEvent, EventType, Subjects,
    EntityRegisteredEvent, DeploymentCompletedEvent
)

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publishes events to NATS."""

    @staticmethod
    async def publish_entity_registered(
        entity_id: str,
        entity_name: str,
        entity_type: str,
        version: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publish entity registered event."""
        event = EntityRegisteredEvent(
            event_id=uuid4(),
            entity_id=entity_id,
            entity_name=entity_name,
            entity_type=entity_type,
            version=version,
            metadata=metadata or {}
        )

        await nats_client.publish(
            Subjects.ENTITY_REGISTERED,
            event.model_dump(mode='json')
        )
        logger.info(f"Published entity.registered: {entity_name}")

    @staticmethod
    async def publish_deployment_completed(
        entity_id: str,
        deployment_id: str,
        environment: str,
        version: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publish deployment completed event."""
        event = DeploymentCompletedEvent(
            event_id=uuid4(),
            entity_id=entity_id,
            deployment_id=deployment_id,
            environment=environment,
            version=version,
            metadata=metadata or {}
        )

        await nats_client.publish(
            Subjects.DEPLOYMENT_COMPLETED,
            event.model_dump(mode='json')
        )
        logger.info(f"Published deployment.completed: {deployment_id}")

    @staticmethod
    async def publish_generic_event(
        event_type: EventType,
        subject: str,
        data: Dict[str, Any],
        entity_id: Optional[str] = None,
        deployment_id: Optional[str] = None
    ) -> None:
        """Publish generic library event."""
        event = LibraryEvent(
            event_id=uuid4(),
            event_type=event_type,
            entity_id=entity_id,
            deployment_id=deployment_id,
            data=data
        )

        await nats_client.publish(subject, event.model_dump(mode='json'))
        logger.info(f"Published {event_type}: {subject}")


# Global publisher instance
publisher = EventPublisher()
