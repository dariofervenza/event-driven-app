"""Tests for the KafkaInitQueues (confluent-kafka AdminClient wrapper)."""

import logging
from concurrent.futures import Future
from concurrent.futures import TimeoutError as FuturesTimeoutError
from unittest.mock import Mock

import pytest
from confluent_kafka import KafkaError, KafkaException
from confluent_kafka.admin import AdminClient

from event_driven.domain.commands import QueueConfig
from event_driven.infrastructure.messagebus.kafka import KafkaInitQueues


def _client_with(future: Mock) -> tuple:
    """Build a Mock AdminClient whose create/delete return the given future."""
    client = Mock(spec=AdminClient)
    futures = {"q1": future}
    client.create_topics.return_value = futures
    client.delete_topics.return_value = futures
    return client, futures


@pytest.mark.infrastructure
@pytest.mark.unit
def test_create_kafka_topic_maps_config() -> None:
    """KafkaInitQueues.create_kafka_topic maps a QueueConfig to a NewTopic."""
    cfg = QueueConfig(queue_name="q", num_partitions=3, replication_factor=1)
    topic = KafkaInitQueues.create_kafka_topic(cfg)
    assert topic.num_partitions == 3
    assert topic.replication_factor == 1


@pytest.mark.infrastructure
@pytest.mark.unit
def test_create_queues_happy_path(caplog) -> None:
    """KafkaInitQueues.create_queues creates each topic and reports success."""
    caplog.set_level(logging.INFO)
    queues = [QueueConfig(queue_name="q1", num_partitions=3, replication_factor=1)]
    client, _ = _client_with(Mock(spec=Future))
    init = KafkaInitQueues(timeout=5, client=client)
    init.create_queues(queues, "localhost:9092")
    assert "created successfully" in caplog.text


@pytest.mark.infrastructure
@pytest.mark.unit
def test_create_queues_already_exists_warns(caplog) -> None:
    """KafkaInitQueues.create_queues logs a warning on TOPIC_ALREADY_EXISTS."""
    caplog.set_level(logging.WARNING)
    queues = [QueueConfig(queue_name="q1", num_partitions=3, replication_factor=1)]
    err = Mock(spec=KafkaError)
    err.code.return_value = KafkaError.TOPIC_ALREADY_EXISTS
    future = Mock(spec=Future)
    future.result.side_effect = KafkaException(err)
    client, _ = _client_with(future)
    init = KafkaInitQueues(timeout=5, client=client)
    init.create_queues(queues, "localhost:9092")
    assert "already exists" in caplog.text


@pytest.mark.infrastructure
@pytest.mark.unit
def test_create_queues_replication_error_warns(caplog) -> None:
    """KafkaInitQueues.create_queues logs a warning on INVALID_REPLICATION_FACTOR."""
    caplog.set_level(logging.WARNING)
    queues = [QueueConfig(queue_name="q1", num_partitions=3, replication_factor=1)]
    err = Mock(spec=KafkaError)
    err.code.return_value = KafkaError.INVALID_REPLICATION_FACTOR
    future = Mock(spec=Future)
    future.result.side_effect = KafkaException(err)
    client, _ = _client_with(future)
    init = KafkaInitQueues(timeout=5, client=client)
    init.create_queues(queues, "localhost:9092")
    assert "replication" in caplog.text.lower()


@pytest.mark.infrastructure
@pytest.mark.unit
def test_create_queues_timeout_errors(caplog) -> None:
    """KafkaInitQueues.create_queues logs an error on timeout."""
    caplog.set_level(logging.ERROR)
    queues = [QueueConfig(queue_name="q1", num_partitions=3, replication_factor=1)]
    future = Mock(spec=Future)
    future.result.side_effect = FuturesTimeoutError()
    client, _ = _client_with(future)
    init = KafkaInitQueues(timeout=5, client=client)
    init.create_queues(queues, "localhost:9092")
    assert "Timed out" in caplog.text


@pytest.mark.infrastructure
@pytest.mark.unit
def test_create_queues_server_error_errors(caplog) -> None:
    """KafkaInitQueues.create_queues logs an error on a server error."""
    caplog.set_level(logging.ERROR)
    queues = [QueueConfig(queue_name="q1", num_partitions=3, replication_factor=1)]
    err = Mock(spec=KafkaError)
    err.code.return_value = 999
    err.str.return_value = "server said no"
    future = Mock(spec=Future)
    future.result.side_effect = KafkaException(err)
    client, _ = _client_with(future)
    init = KafkaInitQueues(timeout=5, client=client)
    init.create_queues(queues, "localhost:9092")
    assert "Kafka server error" in caplog.text


@pytest.mark.infrastructure
@pytest.mark.unit
def test_delete_queues_happy_path(caplog) -> None:
    """KafkaInitQueues.delete_queues deletes each topic and reports success."""
    caplog.set_level(logging.INFO)
    client, _ = _client_with(Mock(spec=Future))
    init = KafkaInitQueues(timeout=5, client=client)
    init.delete_queues(["q1"], "localhost:9092")
    assert "deleted successfully" in caplog.text


@pytest.mark.infrastructure
@pytest.mark.unit
def test_delete_queues_unknown_topic_warns(caplog) -> None:
    """KafkaInitQueues.delete_queues logs a warning on UNKNOWN_TOPIC_OR_PART."""
    caplog.set_level(logging.WARNING)
    err = Mock(spec=KafkaError)
    err.code.return_value = KafkaError.UNKNOWN_TOPIC_OR_PART
    future = Mock(spec=Future)
    future.result.side_effect = KafkaException(err)
    client, _ = _client_with(future)
    init = KafkaInitQueues(timeout=5, client=client)
    init.delete_queues(["q1"], "localhost:9092")
    assert "does not exist" in caplog.text


@pytest.mark.infrastructure
@pytest.mark.unit
def test_delete_queues_timeout_errors(caplog) -> None:
    """KafkaInitQueues.delete_queues logs an error on timeout."""
    caplog.set_level(logging.ERROR)
    future = Mock(spec=Future)
    future.result.side_effect = FuturesTimeoutError()
    client, _ = _client_with(future)
    init = KafkaInitQueues(timeout=5, client=client)
    init.delete_queues(["q1"], "localhost:9092")
    assert "Timed out" in caplog.text


@pytest.mark.infrastructure
@pytest.mark.unit
def test_delete_queues_server_error_errors(caplog) -> None:
    """KafkaInitQueues.delete_queues logs an error on a server error."""
    caplog.set_level(logging.ERROR)
    err = Mock(spec=KafkaError)
    err.code.return_value = 999
    err.str.return_value = "server said no"
    future = Mock(spec=Future)
    future.result.side_effect = KafkaException(err)
    client, _ = _client_with(future)
    init = KafkaInitQueues(timeout=5, client=client)
    init.delete_queues(["q1"], "localhost:9092")
    assert "Kafka error" in caplog.text
