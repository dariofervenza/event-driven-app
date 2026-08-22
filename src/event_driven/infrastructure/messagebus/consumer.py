"""Receives an event"""

import json
from collections.abc import Sequence
from time import sleep

from confluent_kafka import Consumer, KafkaError, Message
from pydantic import BaseModel, ValidationError

from event_driven.domain.events import AbstractEvent
from event_driven.domain.ports import AbstractQueue


class KafkaReceiverConfig(BaseModel):
    """Config class for a kafka consumer"""

    server_url: str
    group_id: str
    auto_commit: bool = False
    max_wait_time: int = 300000
    session_timeout: int = 45000
    poll_timeout: float = 1.0
    default_offset: str = "earliest"

    @property
    def consumer_specs(self) -> dict:
        """Transform into a valid kafka consumer input dict"""
        return {
            "bootstrap.servers": self.server_url,
            "group.id": self.group_id,
            "auto.offset.reset": self.default_offset,
            "enable.auto.commit": self.auto_commit,
            "max.poll.interval.ms": self.max_wait_time,
            "session.timeout.ms": self.session_timeout,
        }


class KafkaReceiver:
    """Kafka implementation of a consumer"""

    def __init__(
        self,
        kafka_receiver_config: KafkaReceiverConfig,
        topics: list[str],
        consumer: Consumer | None = None,
        queue: AbstractQueue | None = None,
    ):
        self.poll_timeout = kafka_receiver_config.poll_timeout
        # maybe it would be better to send the client as a param for testability
        self.consumer = consumer or Consumer(kafka_receiver_config.consumer_specs)
        self.consumer.subscribe(topics)
        self.queue = queue

    def _check_once(self, event_classes: Sequence[type[AbstractEvent]]) -> bool | None:
        """Tries one time to receive a message. Returns true if an error is produced"""
        msg: Message | None = self.consumer.poll(timeout=self.poll_timeout)
        if msg is None:
            print(f"No message, sleeping {self.poll_timeout} seconds")
            sleep(self.poll_timeout)
            return
        if err := msg.error():
            if err.code() == KafkaError._PARTITION_EOF:
                return
            print(f"Consumer error: {err}")
            return True
        value = msg.value()
        raw_payload = value.decode("utf-8") if value else "{}"
        try:
            _: AbstractEvent = self.process_order(raw_payload, event_classes)
            # we should only commit when the event has been processed
            # hence we need to modify this to follow unit of work pattern
            self.consumer.commit(message=msg, asynchronous=False)
            return
        except ValidationError as ve:
            print(f"Schema validation failed! Bad payload: {raw_payload}\nError: {ve}")
            self.consumer.commit(message=msg, asynchronous=False)
            return

    def start_listening(self, event_classes: Sequence[type[AbstractEvent]]):
        """Start the receiver"""
        print("Listening for Pydantic events...")
        try:
            while True:
                if self._check_once(event_classes):
                    break
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

    def process_order(self, raw_payload: str, event_classes: Sequence[type[AbstractEvent]]) -> AbstractEvent:
        """Detect event class and transform it to a model instance"""
        try:
            event_json = json.loads(raw_payload)
        except json.JSONDecodeError:
            event_json = {}
        event_class = next(
            (x for x in event_classes if event_json.get("event_class_name") == x.__name__),
            AbstractEvent,
        )
        event = event_class.model_validate(event_json)
        print(f"Successfully received event: {event.model_dump_json(indent=4)}")
        if self.queue is not None:
            self.queue.put(event)
        return event
