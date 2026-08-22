"""Queue implementation to push received elements"""

from queue import Queue

from event_driven.domain.ports import QueuePayload


class ThreadSafeQueue:
    """Queue to transfer data in memory between threads"""

    def __init__(self, q: Queue[QueuePayload]):
        self.q = q

    def put(self, element: QueuePayload):
        """Sends an element to the in memory queue (thread safe)"""
        self.q.put(element)
        print(f"Sent one element to the thread safe queue with type {element.__class__.__name__}")

    def get(self) -> QueuePayload:
        """Extracts one element from the queue (thread safe)"""
        item = self.q.get()
        print("Queue got an element")
        return item

    def task_done(self):
        """Signals that the former queued task is complete."""
        self.q.task_done()

    def join(self):
        """Blocks until all items in the queue have been gotten and processed."""
        self.q.join()
