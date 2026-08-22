"""Receives an event"""

import json
from collections.abc import Sequence
from time import sleep
from typing import Protocol

from confluent_kafka import Consumer, KafkaError, Message
from pydantic import BaseModel, ValidationError

from event_driven.domain.events.base_events import AbstractEvent


class AbstractReceiver(Protocol):
    """Abstract class to receive messages from an external queue"""

    def start_listening(self, event_classes: Sequence[type[AbstractEvent]]):
        """Listens to messages and converts them into pydantic models"""


class KafkaReceiverConfig(BaseModel):
    """Config class for a kafka consumer"""

    server_url: str
    group_id: str
    auto_commit: bool = False
    max_wait_time: int = 300000
    session_timeout: int = 45000
    poll_timeout: float = 1.0


class KafkaReceiver:
    """Kafka implementation of a consumer"""

    def __init__(
        self,
        kafka_receiver_config: KafkaReceiverConfig,
        topics: list[str],
    ):
        self.poll_timeout = kafka_receiver_config.poll_timeout
        self.consumer = Consumer(
            {
                "bootstrap.servers": kafka_receiver_config.server_url,
                "group.id": kafka_receiver_config.group_id,
                "auto.offset.reset": "earliest",
                "enable.auto.commit": kafka_receiver_config.auto_commit,
                "max.poll.interval.ms": kafka_receiver_config.max_wait_time,
                "session.timeout.ms": kafka_receiver_config.session_timeout,
            }
        )
        self.consumer.subscribe(topics)

    def start_listening(self, event_classes: Sequence[type[AbstractEvent]]):
        """Start the receiver"""
        print("Listening for Pydantic events...")
        try:
            while True:
                msg: Message | None = self.consumer.poll(timeout=self.poll_timeout)
                if msg is None:
                    print(f"No message, sleeping {self.poll_timeout} seconds")
                    sleep(self.poll_timeout)
                    continue
                if err := msg.error():
                    if err.code() == KafkaError._PARTITION_EOF:
                        continue
                    print(f"Consumer error: {err}")
                    break
                value = msg.value()
                raw_payload = value.decode("utf-8") if value else "{}"
                try:
                    _: AbstractEvent = self.process_order(raw_payload, event_classes)
                    # we should only commit when the event has been processed
                    # hence we need to modify this to follow unit of work pattern
                    self.consumer.commit(message=msg, asynchronous=False)
                except ValidationError as ve:
                    print(f"Schema validation failed! Bad payload: {raw_payload}\nError: {ve}")
                    self.consumer.commit(message=msg, asynchronous=False)

        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

    def process_order(self, raw_payload: str, event_classes: Sequence[type[AbstractEvent]]) -> AbstractEvent:
        """Detect event class and transform it to a model instance"""
        event_json = json.loads(raw_payload)
        event_class = next(
            (x for x in event_classes if event_json.get("event_class_name") == x.__name__),
            AbstractEvent,
        )
        event = event_class.model_validate(event_json)
        print(f"Successfully received event: {event.model_dump_json(indent=4)}")
        return event
