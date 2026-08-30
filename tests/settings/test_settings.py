"""Tests for the settings module (config loading and the CFG singleton)."""

from event_driven.settings import CFG, AppConfig, read_cfg


def test_read_cfg_returns_app_config() -> None:
    """read_cfg loads settings/config.toml into an AppConfig model."""
    config = read_cfg("config.toml")
    assert isinstance(config, AppConfig)


def test_cfg_fields_match_toml() -> None:
    """CFG exposes the fields defined in settings/config.toml."""
    assert CFG.kafka_server.server_url == "localhost:9092"
    assert CFG.application.get_inmemory_timeout == 1.0
    assert CFG.kafka_server.queues[0].queue_name == "test_queue"
    assert CFG.kafka_server.init.create_queues is True
    assert CFG.kafka_server.init.delete_queues is False
    assert CFG.kafka_server.producer.producer_wait_time == 8
