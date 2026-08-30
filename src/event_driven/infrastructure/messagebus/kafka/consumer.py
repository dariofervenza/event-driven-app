"""Receives an event"""

import json
import logging
from collections.abc import Sequence
from time import sleep

from confluent_kafka import Consumer, Message
from pydantic import BaseModel, ValidationError

from event_driven.domain.events import AbstractEvent
from event_driven.domain.ports import AbstractQueue

logger = logging.getLogger(__name__)


class KafkaReceiverConfig(BaseModel):
    """Config class for a kafka consumer."""

    server_url: str
    group_id: str
    auto_commit: bool = False
    max_wait_time: int = 300000
    session_timeout: int = 10000
    poll_timeout: float = 1.0
    default_offset: str = "earliest"

    @property
    def consumer_specs(self) -> dict:
        """Transform into a valid kafka consumer input dict."""
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

    def _check_once(self, event_classes: Sequence[type[AbstractEvent]]) -> bool:
        """Tries one time to receive a message. Returns True if an error is produced."""
        msg: Message | None = self.consumer.poll(timeout=self.poll_timeout)
        if msg is None:
            logger.debug("No message, sleeping %s seconds", self.poll_timeout)
            sleep(self.poll_timeout)
            return False
        if err := msg.error():
            if err.code() == 1006:  # KafkaError._PARTITION_EOF
                return False
            logger.error("Consumer error: %s", err)
            return True
        value = msg.value()
        raw_payload = value.decode("utf-8") if value else "{}"
        try:
            _: AbstractEvent = self.process_order(raw_payload, event_classes)
            # we should only commit when the event has been processed
            # hence we need to modify this to follow unit of work pattern
            self.consumer.commit(message=msg, asynchronous=False)
            return False
        except ValidationError as ve:
            logger.exception("Schema validation failed! Bad payload: %s\nError: %s", raw_payload, ve)
            self.consumer.commit(message=msg, asynchronous=False)
            return True

    def start_listening(self, event_classes: Sequence[type[AbstractEvent]]):
        """Start the receiver"""
        logger.info("Listening for Pydantic events...")
        try:
            while True:
                if self._check_once(event_classes):
                    break
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

    def process_order(self, raw_payload: str, event_classes: Sequence[type[AbstractEvent]]) -> AbstractEvent:
        """Detect event class and transform it to a model instance."""
        try:
            event_json = json.loads(raw_payload)
        except json.JSONDecodeError:
            event_json = {}
        event_class = next(
            (x for x in event_classes if event_json.get("event_class_name") == x.__name__),
            AbstractEvent,
        )
        event = event_class.model_validate(event_json)
        if self.queue is not None:
            self.queue.put(event)
        return event
