"""Receives kafka events"""

from queue import Queue

from event_driven.application.handlers import receive_events
from event_driven.domain.events import AbstractEvent
from event_driven.infrastructure.messagebus import KafkaReceiver, KafkaReceiverConfig, ThreadSafeQueue
from event_driven.settings import CFG

if __name__ == "__main__":
    topics = [x.queue_name for x in CFG.kafka_server.queues]
    cfg = KafkaReceiverConfig(
        server_url=CFG.kafka_server.server_url,
        group_id="001",
    )
    queue = ThreadSafeQueue(Queue())
    receiver = KafkaReceiver(cfg, topics, queue=queue)
    event_classes = AbstractEvent.__subclasses__()
    receive_events(receiver, event_classes)
