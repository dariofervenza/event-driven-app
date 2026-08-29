"""Receives kafka events."""

from event_driven.application.handlers.test_handler import test_handler
from event_driven.bootstrap.container import DependencyContainer as DC
from event_driven.settings import CFG

if __name__ == "__main__":
    CONTAINER: DC = DC.get_container_with_queue()
    CONTAINER.current_topic = next(iter(CFG.kafka_server.queues)).queue_name
    CONTAINER.listener_thread.start()
    test_handler(CONTAINER.queue)
