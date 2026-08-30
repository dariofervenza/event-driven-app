"""Tests for the in-memory ThreadSafeQueue."""

from queue import Empty, Queue

import pytest

from event_driven.infrastructure.messagebus.inmemory import ThreadSafeQueue


@pytest.mark.infrastructure
@pytest.mark.unit
def test_put_get_roundtrip() -> None:
    """ThreadSafeQueue.put then get returns the element."""
    queue = ThreadSafeQueue(Queue())
    queue.put("hello")
    assert queue.get() == "hello"


@pytest.mark.infrastructure
@pytest.mark.unit
def test_task_done_delegates() -> None:
    """ThreadSafeQueue.task_done decrements the underlying queue counter."""
    queue = ThreadSafeQueue(Queue())
    queue.put("hello")
    before = queue.q.unfinished_tasks
    queue.task_done()
    assert queue.q.unfinished_tasks == before - 1


@pytest.mark.infrastructure
@pytest.mark.unit
def test_join_delegates() -> None:
    """ThreadSafeQueue.join delegates to the underlying queue."""
    queue = ThreadSafeQueue(Queue())
    queue.put("hello")
    queue.task_done()
    queue.join()


@pytest.mark.infrastructure
@pytest.mark.unit
def test_get_raises_empty_on_timeout() -> None:
    """ThreadSafeQueue.get raises Empty when the queue is empty (timeout)."""
    queue = ThreadSafeQueue(Queue(), timeout=0.0)
    with pytest.raises(Empty):
        queue.get()
