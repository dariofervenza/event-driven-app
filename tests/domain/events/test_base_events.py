"""Tests for the domain event base class and the TestEvent example event."""

from datetime import datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from event_driven.domain.events import TestEvent
from event_driven.domain.events.base_events import utc_now


@pytest.mark.domain
@pytest.mark.unit
def test_utc_now_returns_utc_datetime() -> None:
    """utc_now returns a timezone-aware datetime in UTC."""
    now = utc_now()
    assert isinstance(now, datetime)
    assert now.tzinfo is not None


@pytest.mark.domain
@pytest.mark.unit
def test_event_class_name_is_class_name() -> None:
    """AbstractEvent.event_class_name returns the concrete class name."""
    event = TestEvent(user_id="u", event_key="k", value=1)
    assert event.event_class_name == "TestEvent"


@pytest.mark.domain
@pytest.mark.unit
def test_event_default_factory_fields() -> None:
    """event_id/timestamp have factory defaults; user_id/event_key are required."""
    event = TestEvent(user_id="u", event_key="k", value=1)
    assert isinstance(event.event_id, UUID)
    assert isinstance(event.timestamp, datetime)
    assert event.user_id == "u"
    assert event.event_key == "k"


@pytest.mark.domain
@pytest.mark.unit
def test_required_fields_must_be_provided() -> None:
    """Constructing an event without user_id/event_key raises ValidationError."""
    with pytest.raises(ValidationError):
        data = {"value": 1}
        TestEvent.model_validate(data)
