"""Tests for the KafkaProducer (confluent-kafka Producer wrapper)."""

import json
import logging
from unittest.mock import Mock

import pytest
from confluent_kafka import KafkaError, Message, Producer

from event_driven.domain.events import TestEvent
from event_driven.infrastructure.messagebus.kafka import KafkaProducer


@pytest.mark.infrastructure
@pytest.mark.unit
def test_producer_constructs_real_producer_by_default() -> None:
    """KafkaProducer builds a real confluent Producer when none is injected."""
    kafka_producer = KafkaProducer("localhost:9092")
    assert kafka_producer.producer is not None


@pytest.mark.infrastructure
@pytest.mark.unit
def test_send_event_produces_and_polls() -> None:
    """KafkaProducer.send_event serializes the event and produces to the broker."""
    producer = Mock(spec=Producer)
    kafka_producer = KafkaProducer("localhost:9092", producer=producer)
    event = TestEvent(user_id="u", event_key="k", value=5)
    kafka_producer.send_event("test_queue", event)
    producer.produce.assert_called_once()
    kwargs = producer.produce.call_args.kwargs
    assert kwargs["key"] == b"k"
    assert kwargs["callback"] == kafka_producer._delivery_report
    assert json.loads(kwargs["value"].decode("utf-8"))["value"] == 5


@pytest.mark.infrastructure
@pytest.mark.unit
def test_send_event_flushes_on_buffer_error() -> None:
    """KafkaProducer.send_event flushes on BufferError."""
    producer = Mock(spec=Producer)
    producer.produce.side_effect = BufferError()
    kafka_producer = KafkaProducer("localhost:9092", producer=producer)
    event = TestEvent(user_id="u", event_key="k", value=5)
    kafka_producer.send_event("test_queue", event)
    producer.flush.assert_called_once()


@pytest.mark.infrastructure
@pytest.mark.unit
def test_delivery_report_logs_on_error(caplog) -> None:
    """KafkaProducer._delivery_report logs the delivery error."""
    caplog.set_level(logging.ERROR)
    producer = Mock(spec=Producer)
    kafka_producer = KafkaProducer("localhost:9092", producer=producer)
    msg = Mock(spec=Message)
    kafka_producer._delivery_report(Mock(spec=KafkaError), msg)
    assert "Delivery failed" in caplog.text


@pytest.mark.infrastructure
@pytest.mark.unit
def test_delivery_report_success_logs_offset(caplog) -> None:
    """KafkaProducer._delivery_report logs offset/topic on success (debug)."""
    caplog.set_level(logging.DEBUG)
    producer = Mock(spec=Producer)
    kafka_producer = KafkaProducer("localhost:9092", producer=producer)
    msg = Mock(spec=Message)
    msg.topic.return_value = "test_queue"
    msg.partition.return_value = 2
    msg.offset.return_value = 7
    kafka_producer._delivery_report(None, msg)
    assert "test_queue" in caplog.text


@pytest.mark.infrastructure
@pytest.mark.unit
def test_flush_delegates_to_producer() -> None:
    """KafkaProducer.flush delegates to the underlying producer."""
    producer = Mock(spec=Producer)
    kafka_producer = KafkaProducer("localhost:9092", producer=producer)
    kafka_producer.flush()
    producer.flush.assert_called_once()
