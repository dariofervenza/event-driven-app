"""Sends events to one queue"""

from typing import Protocol

from confluent_kafka import KafkaError, Message, Producer

from event_driven.domain.events.base_events import AbstractEvent


class AbstractProducer(Protocol):
    """Abstract class to receive messages from an external queue"""

    def send_event(self, topic: str, event: AbstractEvent):
        """Abstract method contract to send events"""

    def flush(self):
        """Abstract method contract to flush events"""


class KafkaProducer:
    """Kafka producer implementation"""

    def __init__(self, server_url: str):
        self.producer = Producer({"bootstrap.servers": server_url})

    def _delivery_report(self, err: KafkaError | None, msg: Message):
        if err is not None:
            print(f"Delivery failed: {err}")
        else:
            print(f"Event sent to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}")

    def send_event(self, topic: str, event: AbstractEvent):
        """Serialize Pydantic object to JSON and produce to Kafka"""
        json_payload = event.model_dump_json().encode("utf-8")
        try:
            self.producer.produce(
                topic=topic,
                key=event.event_key.encode("utf-8"),
                value=json_payload,
                callback=self._delivery_report,
            )
            self.producer.poll(0)
        except BufferError:
            print("Local queue full, flushing...")
            self.producer.flush()

    def flush(self):
        """Ensure all messages are sent before app shutdown"""
        self.producer.flush()
