"""Receives kafka events."""

from event_driven.application.handlers import receive_events
from event_driven.bootstrap import DependencyContainer as DC
from event_driven.settings import CFG

if __name__ == "__main__":
    CONTAINER: DC = DC.get_container_with_queue()
    receiver = CONTAINER.receiver
    event_classes = CONTAINER.event_classes
    CONTAINER.current_topic = next(iter(CFG.kafka_server.queues)).queue_name
    receive_events(receiver, event_classes)
