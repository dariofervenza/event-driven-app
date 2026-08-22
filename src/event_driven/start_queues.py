"""Entrypoint to create queues"""

from time import sleep

from event_driven.application.handlers import (
    handle_queue_creation,
    handle_queue_deletion,
)
from event_driven.domain.commands import CreateTopicsCommand, DeleteTopicsCommand
from event_driven.infrastructure.messagebus import KafkaInitQueues
from event_driven.settings import CFG

if __name__ == "__main__":
    kafka = CFG.kafka_server
    inititializator = KafkaInitQueues(kafka.queue_creation_timeout)
    handle_queue_creation(CreateTopicsCommand.model_validate(kafka), inititializator)
    sleep(10)
    command = DeleteTopicsCommand(topic_names=[x.queue_name for x in kafka.queues], server_url=kafka.server_url)
    handle_queue_deletion(
        command,
        inititializator,
    )
