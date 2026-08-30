"""Define app topics"""

import logging
from concurrent.futures import Future
from concurrent.futures import TimeoutError as FuturesTimeoutError

from confluent_kafka import KafkaError, KafkaException
from confluent_kafka.admin import AdminClient, NewTopic

from event_driven.domain.commands import QueueConfig

logger = logging.getLogger(__name__)


class KafkaInitQueues:
    """Implementation to define topics in kafka"""

    def __init__(self, timeout: int, client: AdminClient | None = None):
        # maybe it would be better to send the client as a param for testability
        self.timeout = timeout
        self.client = client

    @staticmethod
    def _handle_creation_future(queues: list[QueueConfig], topic_name: str, future: Future, timeout: int):
        try:
            future.result(timeout=timeout)
            partitions = next(t.num_partitions for t in queues if t.queue_name == topic_name)
            logger.info("Topic '%s' created successfully with %d partitions.", topic_name, partitions)
        except KafkaException as ke:
            err = ke.args[0]
            if err.code() == KafkaError.TOPIC_ALREADY_EXISTS:
                logger.warning("Topic '%s' already exists. Skipping creation.", topic_name)
            elif err.code() == KafkaError.INVALID_REPLICATION_FACTOR:
                logger.warning("Replication factor is higher than available brokers.")
            else:
                logger.error("Kafka server error [%d]: %s", err.code(), err.str())
        except FuturesTimeoutError:
            logger.error("Timed out waiting for Kafka to create topic '%s'.", topic_name)

    @staticmethod
    def create_kafka_topic(cfg: QueueConfig) -> NewTopic:
        """Create on queue in kafka"""
        return NewTopic(
            cfg.queue_name,
            num_partitions=cfg.num_partitions,
            replication_factor=cfg.replication_factor,
        )

    def create_queues(self, queues: list[QueueConfig], server_url: str):
        """Create all queues in kafka"""
        client = self.client or AdminClient({"bootstrap.servers": server_url})
        topics = [self.create_kafka_topic(cfg) for cfg in queues]
        futures = client.create_topics(topics)
        for topic_name, future in futures.items():
            self._handle_creation_future(queues, topic_name, future, self.timeout)

    @staticmethod
    def _handle_deletion_future(topic_name: str, future: Future, timeout: int):
        try:
            future.result(timeout=timeout)
            logger.info("Topic '%s' deleted successfully.", topic_name)
        except KafkaException as ke:
            err = ke.args[0]
            if err.code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                logger.warning("Topic '%s' does not exist.", topic_name)
            else:
                logger.error("Kafka error [%d]: %s", err.code(), err.str())
        except FuturesTimeoutError:
            logger.exception("Timed out waiting to delete '%s'.", topic_name)

    def delete_queues(self, topic_names: list[str], server_url: str):
        """Delete topics from Kafka"""
        client = self.client or AdminClient({"bootstrap.servers": server_url})
        futures = client.delete_topics(topic_names)
        for topic_name, future in futures.items():
            self._handle_deletion_future(topic_name, future, self.timeout)
