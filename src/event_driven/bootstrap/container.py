"""Dependency injection container."""

from __future__ import annotations

from queue import Queue

from event_driven.domain.events import AbstractEvent
from event_driven.domain.ports import (
    AbstractHandler,
    AbstractInitQueues,
    AbstractInMemoryQueue,
    AbstractListener,
    AbstractProducer,
    AbstractReceiver,
)
from event_driven.infrastructure.messagebus import (
    KafkaInitQueues,
    KafkaProducer,
    KafkaReceiver,
    KafkaReceiverConfig,
    ListenerThread,
    TestHandler,
    ThreadSafeQueue,
)
from event_driven.settings import CFG

__all__ = ["DependencyContainer"]


# pylint: disable=too-many-instance-attributes
class DependencyContainer:
    """Holds all instantiated infrastructure components.

    Uses a class-level singleton pattern to ensure only one container
    exists per process, with optional pre-configured in-memory queue.
    """

    # Class-level singleton instance
    _singleton: DependencyContainer | None = None

    # Class-level default in-memory queue (shared across all singleton instances)
    _default_queue: AbstractInMemoryQueue | None = None

    @classmethod
    def get_container(cls) -> DependencyContainer:
        """Get or create the singleton container (default, no queue)."""
        if cls._singleton is None:
            cls._singleton = cls()
        return cls._singleton

    @classmethod
    def get_container_with_queue(cls) -> DependencyContainer:
        """Get or create the singleton container with a configured in-memory queue."""
        if cls._default_queue is None:
            cls._default_queue = ThreadSafeQueue(Queue(), timeout=CFG.application.get_inmemory_timeout)
        if cls._singleton is None:
            cls._singleton = cls(in_memory_queue=cls._default_queue)
        return cls._singleton

    def __init__(
        self,
        in_memory_queue: AbstractInMemoryQueue | None = None,
    ) -> None:
        self._init_queues: AbstractInitQueues | None = None
        self._producer: AbstractProducer | None = None
        self._receiver: AbstractReceiver | None = None
        self._queue: AbstractInMemoryQueue | None = in_memory_queue
        self._listener_thread: AbstractListener | None = None
        self._test_handler: AbstractHandler | None = None
        self._event_classes: list[type[AbstractEvent]] = []
        self._current_topic: str = ""

    @property
    def init_queues(self) -> AbstractInitQueues:
        """Get the queue initializer (KafkaInitQueues)."""
        if self._init_queues is None:
            self._init_queues = KafkaInitQueues(CFG.kafka_server.init.queue_creation_timeout)
        return self._init_queues

    @property
    def producer(self) -> AbstractProducer:
        """Get the event producer (KafkaProducer)."""
        if self._producer is None:
            self._producer = KafkaProducer(server_url=CFG.kafka_server.server_url)
        return self._producer

    @property
    def receiver(self) -> AbstractReceiver:
        """Get the event receiver (KafkaReceiver) with the in-memory queue."""
        if self._receiver is None:
            topics = [q.queue_name for q in CFG.kafka_server.queues]
            cfg = KafkaReceiverConfig(
                server_url=CFG.kafka_server.server_url,
                **CFG.kafka_server.consume.model_dump(),
            )
            self._receiver = KafkaReceiver(cfg, topics, queue=self._queue)
        return self._receiver

    @property
    def queue(self) -> AbstractInMemoryQueue:
        """Get the in-memory queue (lazy initialization)."""
        if self._queue is None:
            self._queue = ThreadSafeQueue(Queue())
        return self._queue

    @property
    def event_classes(self) -> list[type[AbstractEvent]]:
        """Get all registered event classes."""
        if not self._event_classes:
            self._event_classes = AbstractEvent.__subclasses__()
        return self._event_classes

    @property
    def listener_thread(self) -> AbstractListener:
        """Get the listener thread that moves events from Kafka into the in-memory queue."""
        if self._listener_thread is None:
            self._listener_thread = ListenerThread(
                receiver=self.receiver,
                event_classes=self.event_classes,
            )
        return self._listener_thread

    @property
    def test_handler(self) -> AbstractHandler:
        """Get the test handler that processes events from the in-memory queue."""
        if self._test_handler is None:
            self._test_handler = TestHandler(self.queue)
        return self._test_handler

    @property
    def current_topic(self) -> str:
        """Get the current topic name."""
        return self._current_topic

    @current_topic.setter
    def current_topic(self, topic: str) -> None:
        """Set the current topic name."""
        self._current_topic = topic

    def get_all(self) -> dict:
        """Return all components as a dict for easy access."""
        return {
            "init_queues": self.init_queues,
            "producer": self.producer,
            "receiver": self.receiver,
            "queue": self.queue,
            "event_classes": self.event_classes,
        }
