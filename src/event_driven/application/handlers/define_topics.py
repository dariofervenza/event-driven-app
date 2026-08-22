"""Administration of the messagebus server"""

from event_driven.domain.commands import CreateTopicsCommand, DeleteTopicsCommand
from event_driven.domain.ports import (
    AbstractInitQueues,
)


def handle_queue_creation(command: CreateTopicsCommand, initializator: AbstractInitQueues):
    """Create all queues handler"""
    initializator.create_queues(command.queues, command.server_url)


def handle_queue_deletion(command: DeleteTopicsCommand, initializator: AbstractInitQueues):
    """Delete all topics"""
    initializator.delete_queues(command.topic_names, command.server_url)
