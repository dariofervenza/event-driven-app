"""Define app topics"""

from concurrent.futures import TimeoutError as FuturesTimeoutError
from typing import Protocol

from confluent_kafka import KafkaError, KafkaException
from confluent_kafka.admin import AdminClient, NewTopic
from pydantic import BaseModel


class QueueConfig(BaseModel):
    """Configuration for one topic"""

    queue_name: str
    num_partitions: int
    replication_factor: int


class AbstractInitQueues(Protocol):
    """Abstract class to create all app queues"""

    def create_queues(self, queues: list[QueueConfig], server_url: str, timeout: int = 5):
        """Abstract method contract to create topics"""

    def delete_queues(self, topic_names: list[str], server_url: str, timeout: int = 5):
        """Abstract method contract to delete topics"""


class KafkaInitQueues:
    """Create topics in kafka"""

    def create_queues(self, queues: list[QueueConfig], server_url: str, timeout: int = 5):
        """Create all queues in kafka"""
        client = AdminClient({"bootstrap.servers": server_url})
        topics = [self.create_kafka_topic(cfg) for cfg in queues]
        futures = client.create_topics(topics)
        for topic_name, future in futures.items():
            try:
                future.result(timeout=timeout)
                partitions = next(t.num_partitions for t in queues if t.queue_name == topic_name)
                print(f"Topic '{topic_name}' created successfully with {partitions} partitions.")
            except KafkaException as ke:
                err = ke.args[0]
                if err.code() == KafkaError.TOPIC_ALREADY_EXISTS:
                    print(f"Topic '{topic_name}' already exists. Skipping creation.")
                elif err.code() == KafkaError.INVALID_REPLICATION_FACTOR:
                    print("Replication factor is higher than available brokers.")
                else:
                    print(f"Kafka server error [{err.code()}]: {err.str()}")
            except FuturesTimeoutError:
                print(f"Timed out waiting for Kafka to create topic '{topic_name}'.")

    def delete_queues(self, topic_names: list[str], server_url: str, timeout: int = 5):
        """Delete topics from Kafka"""
        client = AdminClient({"bootstrap.servers": server_url})
        futures = client.delete_topics(topic_names)

        for topic_name, future in futures.items():
            try:
                future.result(timeout=timeout)
                print(f"Topic '{topic_name}' deleted successfully.")
            except KafkaException as ke:
                err = ke.args[0]
                if err.code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                    print(f"Topic '{topic_name}' does not exist.")
                else:
                    print(f"Kafka error [{err.code()}]: {err.str()}")
            except FuturesTimeoutError:
                print(f"Timed out waiting to delete '{topic_name}'.")

    def create_kafka_topic(self, cfg: QueueConfig) -> NewTopic:
        """Create on queue in kafka"""
        return NewTopic(
            cfg.queue_name,
            num_partitions=cfg.num_partitions,
            replication_factor=cfg.replication_factor,
        )
