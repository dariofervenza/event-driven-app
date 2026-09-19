"""Read and export app config."""

import tomllib
from pathlib import Path

from pydantic import BaseModel, Field

from event_driven.domain.commands import QueueConfig


class AppConfigApplication(BaseModel):
    """Application-specific configuration."""

    get_inmemory_timeout: float = Field(default=1.0, description="Timeout in seconds for in-memory queue get calls.")
    rating_min_score: int = Field(default=1, description="The minimum rating score a customer can give.")
    rating_max_score: int = Field(default=5, description="The maximum rating score a customer can give.")


class KafkaInitConfig(BaseModel):
    """Config to create / delete topics (init queues)."""

    queue_creation_timeout: int = Field(description="Timeout in seconds for queue creation.")
    create_queues: bool = Field(default=True, description="Whether to create queues on startup.")
    delete_queues: bool = Field(default=True, description="Whether to delete queues on startup.")


class KafkaProducerConfig(BaseModel):
    """Config for the producer."""

    producer_wait_time: int = Field(description="Wait time in seconds between producer sends.")


# pylint: disable=duplicate-code
class KafkaConsumeConfig(BaseModel):
    """Config for the consumer."""

    group_id: str = Field(description="The consumer group id.")
    auto_commit: bool = Field(default=False, description="Whether to auto-commit offsets.")
    max_wait_time: int = Field(default=300000, description="The maximum wait time in milliseconds.")
    session_timeout: int = Field(default=10000, description="The session timeout in milliseconds.")
    poll_timeout: float = Field(default=1.0, description="The poll timeout in seconds.")
    default_offset: str = Field(default="earliest", description="The default offset (earliest or latest).")


class KafkaConfig(BaseModel):
    """Kafka server configuration."""

    server_url: str = Field(description="The Kafka server URL.")
    init: KafkaInitConfig = Field(description="Queue creation / deletion settings.")
    producer: KafkaProducerConfig = Field(description="Producer settings.")
    consume: KafkaConsumeConfig = Field(description="Consumer settings.")
    queues: list[QueueConfig] = Field(description="The queues to create.")


class AppConfig(BaseModel):
    """Application general configuration."""

    kafka_server: KafkaConfig = Field(description="The Kafka server configuration.")
    application: AppConfigApplication = Field(description="The application configuration.")


def read_cfg(config_file: str) -> AppConfig:
    """Read app config and transform it into a model."""
    file = Path(__file__).resolve().parent / config_file
    with file.open("rb") as f:
        cfg = tomllib.load(f)

    return AppConfig.model_validate(cfg)


CFG = read_cfg("config.toml")

__all__ = ["CFG"]
