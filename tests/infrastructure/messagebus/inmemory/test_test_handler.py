"""Tests for the in-memory TestHandler."""

from queue import Empty

import pytest
from tests.fakes import FakeInMemoryQueue

from event_driven.domain.events import TestEvent
from event_driven.infrastructure.messagebus.inmemory import TestHandler


@pytest.mark.infrastructure
@pytest.mark.unit
def test_handle_exits_on_keyboard_interrupt() -> None:
    """TestHandler.handle processes events then exits (SystemExit) on KeyboardInterrupt."""
    event = TestEvent(user_id="u", event_key="k", value=1)
    fake = FakeInMemoryQueue([event, Empty(), KeyboardInterrupt()])
    handler = TestHandler(fake)
    with pytest.raises(SystemExit):
        handler.handle()
    assert fake.task_done_count == 1
