"""Administration of the messagebus server"""

from event_driven.infrastructure.messagebus.create_queues import (
    AbstractInitQueues,
    QueueConfig,
)


def handle_queue_creation(
    queues: list[QueueConfig],
    server_url: str,
    timeout: int,
    initializator: AbstractInitQueues,
):
    """Create all queues handler"""
    initializator.create_queues(queues, server_url, timeout=timeout)


def handle_queue_deletion(names: list[str], server_url: str, timeout: int, initializator: AbstractInitQueues):
    """Delete all topics"""
    initializator.delete_queues(names, server_url, timeout)
