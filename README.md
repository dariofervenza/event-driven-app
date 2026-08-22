# event-driven-app

# Prerequisites

```
docker compose up
```

# Run with

```
uv run python -m event_driven.start_queues

uv run python -m event_driven.producer

uv run python -m event_driven.consumer
```

# Lint, format, style, type checking and tests

```


uv run ruff check --fix
uv run ruff format
uv run ty check .
uv run pylint src/ tests/
uv run pytest


```