"""Interfaces to interact with external queues"""

from collections.abc import Sequence
from typing import Protocol

from pydantic import BaseModel

from event_driven.domain.commands import QueueConfig
from event_driven.domain.events import AbstractEvent

type QueuePayload = str | dict | list | BaseModel


class AbstractInitQueues(Protocol):
    """Abstract class to create all app queues"""

    def create_queues(self, queues: list[QueueConfig], server_url: str):
        """Abstract method contract to create topics"""

    def delete_queues(self, topic_names: list[str], server_url: str):
        """Abstract method contract to delete topics"""


class AbstractReceiver(Protocol):
    """Abstract class to receive messages from an external queue"""

    def start_listening(self, event_classes: Sequence[type[AbstractEvent]]):
        """Listens to messages and converts them into pydantic models"""


class AbstractProducer(Protocol):
    """Abstract class to receive messages from an external queue"""

    def send_event(self, topic: str, event: AbstractEvent):
        """Abstract method contract to send events"""

    def flush(self):
        """Abstract method contract to flush events"""


class AbstractInMemoryQueue(Protocol):
    """Abstract class with the contract to use in-memory queues."""

    def put(self, element: QueuePayload) -> None:
        """Sends an element to the in memory queue."""

    def get(self) -> QueuePayload:
        """Extracts one element from the queue."""

    def task_done(self) -> None:
        """Signals that the former queued task is complete."""


class AbstractQueue(Protocol):
    """Abstract class with the contract to use queues (normal or asyncio or others)"""

    def put(self, element: QueuePayload) -> None:
        """Sends an element to the queue."""

    def get(self) -> QueuePayload:
        """Extracts one element from the queue."""
