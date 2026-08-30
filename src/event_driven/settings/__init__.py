"""Read and export app config."""

import tomllib
from pathlib import Path

from pydantic import BaseModel

from event_driven.domain.commands import QueueConfig


class AppConfigApplication(BaseModel):
    """Application-specific configuration."""

    get_inmemory_timeout: float = 1.0


class KafkaInitConfig(BaseModel):
    """Config to create / delete topics (init queues)."""

    queue_creation_timeout: int
    create_queues: bool = True
    delete_queues: bool = True


class KafkaProducerConfig(BaseModel):
    """Config for the producer."""

    producer_wait_time: int


# pylint: disable=duplicate-code
class KafkaConsumeConfig(BaseModel):
    """Config for the consumer."""

    group_id: str
    auto_commit: bool = False
    max_wait_time: int = 300000
    session_timeout: int = 10000
    poll_timeout: float = 1.0
    default_offset: str = "earliest"


class KafkaConfig(BaseModel):
    """Kafka server configuration."""

    server_url: str
    init: KafkaInitConfig
    producer: KafkaProducerConfig
    consume: KafkaConsumeConfig
    queues: list[QueueConfig]


class AppConfig(BaseModel):
    """Application general configuration."""

    kafka_server: KafkaConfig
    application: AppConfigApplication


def read_cfg(config_file: str) -> AppConfig:
    """Read app config and transform it into a model."""
    file = Path(__file__).resolve().parent / config_file
    with file.open("rb") as f:
        cfg = tomllib.load(f)

    return AppConfig.model_validate(cfg)


CFG = read_cfg("config.toml")

__all__ = ["CFG"]
