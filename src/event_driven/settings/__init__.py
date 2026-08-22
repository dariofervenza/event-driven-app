"""Read and export app config"""

import tomllib
from pathlib import Path

from pydantic import BaseModel

from event_driven.infrastructure.messagebus.create_queues import QueueConfig


class KafKaConfig(BaseModel):
    """Kafka server validator"""

    server_url: str
    queue_creation_timeout: int
    queues: list[QueueConfig]


class AppConfig(BaseModel):
    """Applicaiton general configuration"""

    kafka_server: KafKaConfig


def read_cfg(config_file: str) -> AppConfig:
    """Read app config and transform it into a model"""
    file = Path(__file__).resolve().parent / config_file
    with file.open("rb") as f:
        cfg = tomllib.load(f)

    return AppConfig.model_validate(cfg)


CFG = read_cfg("config.toml")


__all__ = ["CFG"]
