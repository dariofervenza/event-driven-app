"""Tests for the KafkaReceiver (confluent-kafka Consumer wrapper)."""

import json
from unittest.mock import Mock

import pytest
from confluent_kafka import Consumer, KafkaError, Message
from pydantic import ValidationError
from tests.fakes import FakeInMemoryQueue

from event_driven.domain.events import AbstractEvent, TestEvent
from event_driven.infrastructure.messagebus.kafka import KafkaReceiver, KafkaReceiverConfig


@pytest.mark.infrastructure
@pytest.mark.unit
def test_consumer_specs() -> None:
    """KafkaReceiverConfig.consumer_specs returns the kafka config dict."""
    cfg = KafkaReceiverConfig(server_url="localhost:9092", group_id="g")
    specs = cfg.consumer_specs
    assert specs["bootstrap.servers"] == "localhost:9092"
    assert specs["group.id"] == "g"
    assert specs["enable.auto.commit"] is False
    assert specs["max.poll.interval.ms"] == 300000
    assert specs["session.timeout.ms"] == 10000


@pytest.mark.infrastructure
@pytest.mark.unit
def test_process_order_validates_and_puts_on_queue() -> None:
    """KafkaReceiver.process_order parses a payload and puts it on the queue."""
    payload = TestEvent(user_id="u", event_key="k", value=5)
    queue = FakeInMemoryQueue()
    receiver = KafkaReceiver(
        KafkaReceiverConfig(server_url="x", group_id="g"),
        topics=[],
        consumer=Mock(spec=Consumer),
        queue=queue,
    )
    event = receiver.process_order(payload.model_dump_json(), [TestEvent])
    assert event is not None
    assert queue.put_elements == [event]


@pytest.mark.infrastructure
@pytest.mark.unit
def test_process_order_unknown_class_falls_back_to_abstract_event() -> None:
    """KafkaReceiver.process_order falls back to AbstractEvent for unknown classes."""
    raw = json.dumps({"event_class_name": "UnknownEvent", "user_id": "u", "event_key": "k"})
    receiver = KafkaReceiver(
        KafkaReceiverConfig(server_url="x", group_id="g"),
        topics=[],
        consumer=Mock(spec=Consumer),
        queue=None,
    )
    event = receiver.process_order(raw, [TestEvent])
    assert isinstance(event, AbstractEvent)


@pytest.mark.infrastructure
@pytest.mark.unit
def test_process_order_raises_on_invalid_payload() -> None:
    """KafkaReceiver.process_order raises ValidationError for an invalid payload."""
    raw = json.dumps({"event_class_name": "TestEvent", "value": "bad"})
    receiver = KafkaReceiver(
        KafkaReceiverConfig(server_url="x", group_id="g"),
        topics=[],
        consumer=Mock(spec=Consumer),
        queue=None,
    )
    with pytest.raises(ValidationError):
        receiver.process_order(raw, [TestEvent])


@pytest.mark.infrastructure
@pytest.mark.unit
def test_check_once_returns_false_when_no_message() -> None:
    """KafkaReceiver._check_once returns False (and sleeps) when poll is empty."""
    consumer = Mock(spec=Consumer)
    consumer.poll.return_value = None
    receiver = KafkaReceiver(
        KafkaReceiverConfig(server_url="x", group_id="g", poll_timeout=0.0),
        topics=[],
        consumer=consumer,
        queue=None,
    )
    assert receiver._check_once([TestEvent]) is False


@pytest.mark.infrastructure
@pytest.mark.unit
def test_check_once_returns_true_on_consumer_error() -> None:
    """KafkaReceiver._check_once returns True on a real consumer error (not _PARTITION_EOF)."""
    err = Mock(spec=KafkaError)
    err.code.return_value = 1007
    msg = Mock(spec=Message)
    msg.error.return_value = err
    consumer = Mock(spec=Consumer)
    consumer.poll.return_value = msg
    receiver = KafkaReceiver(
        KafkaReceiverConfig(server_url="x", group_id="g"),
        topics=[],
        consumer=consumer,
        queue=None,
    )
    assert receiver._check_once([TestEvent]) is True


@pytest.mark.infrastructure
@pytest.mark.unit
def test_check_once_commits_after_processing() -> None:
    """KafkaReceiver._check_once commits after processing a valid event."""
    payload = TestEvent(user_id="u", event_key="k", value=5)
    msg = Mock(spec=Message)
    msg.error.return_value = None
    msg.value.return_value = payload.model_dump_json().encode("utf-8")
    consumer = Mock(spec=Consumer)
    consumer.poll.return_value = msg
    queue = FakeInMemoryQueue()
    receiver = KafkaReceiver(
        KafkaReceiverConfig(server_url="x", group_id="g"),
        topics=[],
        consumer=consumer,
        queue=queue,
    )
    assert receiver._check_once([TestEvent]) is False
    consumer.commit.assert_called_once()


@pytest.mark.infrastructure
@pytest.mark.unit
def test_check_once_returns_true_on_validation_error() -> None:
    """KafkaReceiver._check_once returns True (and commits) on a ValidationError."""
    payload = {"event_class_name": "TestEvent", "value": "bad"}
    msg = Mock(spec=Message)
    msg.error.return_value = None
    msg.value.return_value = json.dumps(payload).encode("utf-8")
    consumer = Mock(spec=Consumer)
    consumer.poll.return_value = msg
    receiver = KafkaReceiver(
        KafkaReceiverConfig(server_url="x", group_id="g"),
        topics=[],
        consumer=consumer,
        queue=None,
    )
    assert receiver._check_once([TestEvent]) is True
    consumer.commit.assert_called_once()


@pytest.mark.infrastructure
@pytest.mark.unit
def test_start_listening_breaks_on_consumer_error() -> None:
    """KafkaReceiver.start_listening stops (and closes) when _check_once errors."""
    err = Mock(spec=KafkaError)
    err.code.return_value = 1007
    msg = Mock(spec=Message)
    msg.error.return_value = err
    consumer = Mock(spec=Consumer)
    consumer.poll.return_value = msg
    receiver = KafkaReceiver(
        KafkaReceiverConfig(server_url="x", group_id="g"),
        topics=[],
        consumer=consumer,
        queue=None,
    )
    receiver.start_listening([TestEvent])
    consumer.close.assert_called_once()
