# event-driven-app

# Prerequisites

- Launch Kafka with:

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


- Please never add ignores to bypass linting, type or testing warnings:

- Neither in pyproject.toml nor inline.

- Prefer real issue fix or accept it rather than ignoring it and, hence, burying it.

- Some pylint issues will be acceptable, usually, too many stataments, arguments, access to a protected member (in tests mainly)

- Unacceptable issues/ actions:
    - Magic values (define a _CONSTANT)
    - Redefining a value from outer scope (in pytest you can use request: FixtureRequest)
    - Type errors (avoid casting whenever possible)
    - Ruff problems
    - Removing types to bypass type checker
    - Undefined elements
    - Critical / error pylint elements

## Run always basic checks


```
uv run ruff check --fix
uv run ruff format
uv run ty check .
uv run pylint src/ tests/
uv run pytest
```
