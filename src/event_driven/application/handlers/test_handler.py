"""Test handler that continuously receives events from the in-memory queue."""

import sys
from queue import Empty

from event_driven.domain.events import AbstractEvent
from event_driven.domain.ports import AbstractInMemoryQueue


def test_handler(queue: AbstractInMemoryQueue) -> None:
    """Continuously receive events from the in-memory queue and print them.

    This function polls the in-memory queue with a timeout, printing received
    events. It blocks briefly when the queue is empty to avoid busy-waiting.
    """
    print("TestHandler started. Waiting for events...")
    try:
        while True:
            try:
                event = queue.get()
                if isinstance(event, AbstractEvent):
                    print(f"Successfully received event: {event.model_dump_json(indent=4)}")
                queue.task_done()
            except Empty:
                continue
    except KeyboardInterrupt:
        print("\nTestHandler shutting down...")
        sys.exit(0)
