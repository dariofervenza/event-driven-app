"""Entrypoint to create queues"""

from time import sleep

from event_driven.application.handlers.queues import (
    handle_queue_creation,
    handle_queue_deletion,
)
from event_driven.infrastructure.messagebus.create_queues import KafkaInitQueues
from event_driven.settings import CFG

if __name__ == "__main__":
    kafka = CFG.kafka_server
    queues = CFG.kafka_server.queues
    server_url = CFG.kafka_server.server_url
    inititializator = KafkaInitQueues()
    handle_queue_creation(kafka.queues, kafka.server_url, kafka.queue_creation_timeout, inititializator)
    sleep(10)
    handle_queue_deletion(
        [x.queue_name for x in queues],
        kafka.server_url,
        kafka.queue_creation_timeout,
        inititializator,
    )
