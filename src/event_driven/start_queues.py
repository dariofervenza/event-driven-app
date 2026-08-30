"""Entrypoint to create queues."""

from event_driven.application.handlers import handle_queue_creation, handle_queue_deletion
from event_driven.bootstrap import DependencyContainer as DC
from event_driven.domain.commands import CreateTopicsCommand, DeleteTopicsCommand
from event_driven.logging import setup_logging
from event_driven.settings import CFG

if __name__ == "__main__":
    LOGGER = setup_logging("start_queues")
    LOGGER.info("start_queues started")
    CONTAINER: DC = DC.get_container()
    init_queues = CONTAINER.init_queues

    if CFG.kafka_server.init.create_queues:
        handle_queue_creation(CreateTopicsCommand.model_validate(CFG.kafka_server), init_queues)

    if CFG.kafka_server.init.delete_queues:
        command = DeleteTopicsCommand(
            topic_names=[x.queue_name for x in CFG.kafka_server.queues],
            server_url=CFG.kafka_server.server_url,
        )
        handle_queue_deletion(command, init_queues)
