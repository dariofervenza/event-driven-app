"""Sends events to one queue"""

from confluent_kafka import KafkaError, Message, Producer

from event_driven.domain.events import AbstractEvent


class KafkaProducer:
    """Kafka producer implementation"""

    def __init__(self, server_url: str, producer: Producer | None = None):
        # maybe it would be better to send the client as a param for testability
        self.producer = producer or Producer({"bootstrap.servers": server_url})

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
            self.flush()

    def flush(self):
        """Ensure all messages are sent before app shutdown"""
        self.producer.flush()
