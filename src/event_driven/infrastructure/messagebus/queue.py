"""Queue implementation to push received elements."""

from queue import Queue

from event_driven.domain.ports import AbstractInMemoryQueue, QueuePayload


class ThreadSafeQueue(AbstractInMemoryQueue):
    """Queue to transfer data in memory between threads."""

    def __init__(self, q: Queue[QueuePayload], timeout: float = 1.0) -> None:
        """Initialize the thread-safe queue.

        Args:
            q: The underlying Queue instance.
            timeout: Timeout in seconds for get() calls.
        """
        self.q = q
        self.timeout = timeout

    def put(self, element: QueuePayload) -> None:
        """Sends an element to the in memory queue (thread safe)."""
        self.q.put(element)

    def get(self) -> QueuePayload:
        """Extracts one element from the queue (thread safe)."""
        item = self.q.get(timeout=self.timeout)
        return item

    def task_done(self) -> None:
        """Signals that the former queued task is complete."""
        self.q.task_done()

    def join(self) -> None:
        """Blocks until all items in the queue have been gotten and processed."""
        self.q.join()
