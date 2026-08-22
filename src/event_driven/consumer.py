"""Receives kafka events"""

from event_driven.application.handlers.receive_kafka import receive_events
from event_driven.domain.events.test_event import TestEvent
from event_driven.infrastructure.messagebus.consumer import (
    KafkaReceiver,
    KafkaReceiverConfig,
)
from event_driven.settings import CFG

if __name__ == "__main__":
    topics = [x.queue_name for x in CFG.kafka_server.queues]
    cfg = KafkaReceiverConfig(
        server_url=CFG.kafka_server.server_url,
        group_id="001",
    )
    receiver = KafkaReceiver(cfg, topics)
    event_classes = [TestEvent]
    receive_events(receiver, event_classes)
