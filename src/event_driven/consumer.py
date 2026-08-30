"""Receives kafka events."""

from event_driven.bootstrap.container import DependencyContainer as DC
from event_driven.logging import setup_logging
from event_driven.settings import CFG

if __name__ == "__main__":
    LOGGER = setup_logging("consumer")
    LOGGER.info("consumer started")
    CONTAINER: DC = DC.get_container_with_queue()
    CONTAINER.current_topic = next(iter(CFG.kafka_server.queues)).queue_name
    CONTAINER.listener_thread.start()
    CONTAINER.test_handler.handle()
