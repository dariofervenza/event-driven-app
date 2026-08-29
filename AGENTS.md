# AGENTS.md

Python 3.14 Kafka event-driven demo. Managed with `uv` (lockfile: `uv.lock`). No CI or pre-commit hooks.

## Commands

Full check sequence (per README):

```
uv run ruff check --fix
uv run ruff format
uv run ty check .
uv run pylint src/ tests/
uv run pytest
```

- Single test: `uv run pytest tests/test_dummy.py -k <expr>` (pytest config in `pyproject.toml`, `testpaths = ["tests"]`)
- `pytest` always runs with coverage (`addopts` in pyproject): writes `.coverage` and `htmlcov/` (both gitignored)
- Tests are pure unit tests using fake in-memory doubles; they do NOT require Kafka

## Running the app

Requires a local Kafka at `localhost:9092` first: `docker compose up` (apache/kafka).

Config is NOT env-based: it comes from `src/event_driven/settings/config.toml`, loaded at import time into the module-level `CFG` (`AppConfig` instance in `event_driven.settings`). The producer publishes only to `queues[0]`; the consumer subscribes to all queues in the config.

Entry points (run in this order, separate terminals):

```
uv run python -m event_driven.start_queues   # creates topics, sleeps 10s, then DELETES them
uv run python -m event_driven.producer       # infinite loop, Ctrl+C to stop
uv run python -m event_driven.consumer       # infinite loop, Ctrl+C to stop
```

Gotcha: `start_queues` only leaves topics existing for the 10-second window between creation and deletion, so re-run it to keep topics available while producer/consumer run.

## Architecture / wiring

Clean/hexagonal layout under `src/event_driven/` (import name is `event_driven`, not the project name `event-driven`):

- `domain/` — pure: events (`events/`), commands, and ports (abstract interfaces). No Kafka imports.
- `application/handlers/` — orchestration over ports.
- `infrastructure/messagebus/` — confluent-kafka implementations of the ports.

Event deserialization quirk: the consumer matches each message's `event_class_name` field against `AbstractEvent.__subclasses__()` (built in `consumer.py` entry point). A new event class is only deserializable if it's a DIRECT subclass of `AbstractEvent` AND is imported (re-export it in `domain/events/__init__.py`) so it appears in `__subclasses__()`.
