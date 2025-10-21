"""
Messaging module for NATS integration.
"""
from .nats_client import nats_client, LibraryNATSClient
from .events import EventType, Subjects, LibraryEvent
from .publisher import publisher, EventPublisher

__all__ = [
    'nats_client',
    'LibraryNATSClient',
    'EventType',
    'Subjects',
    'LibraryEvent',
    'publisher',
    'EventPublisher',
]
