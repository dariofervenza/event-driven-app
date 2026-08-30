"""Shared test doubles (fakes) for the event_driven domain interfaces.

Every fake is a plain class (no mock, no monkeypatch) that structurally conforms
to one of the abstract protocols in ``event_driven.domain.ports``. The concrete
confluent-kafka / stdlib types (Producer, Consumer, Message, AdminClient,
KafkaError, Future) are left to ``unittest.mock`` with a ``spec`` in the
tests, so no broker is ever contacted.
"""

from event_driven.domain.ports import QueuePayload


class FakeEventProducer:
    """Fake AbstractProducer: records send_event/flush; optional raise on send."""

    def __init__(self, send_raises: BaseException | None = None) -> None:
        self.sent: list = []
        self.flushed = 0
        self._send_raises = send_raises

    def send_event(self, topic: str, event) -> None:
        """Record the sent event; raise the configured error (if any)."""
        if self._send_raises is not None:
            raise self._send_raises
        self.sent.append((topic, event))

    def flush(self) -> None:
        """Count a flush call."""
        self.flushed += 1


class FakeInitQueues:
    """Fake AbstractInitQueues: records created/deleted topics per server URL."""

    def __init__(self) -> None:
        self.created: dict = {}
        self.deleted: dict = {}

    def create_queues(self, queues: list, server_url: str) -> None:
        """Record the queues created for the given server URL."""
        self.created[server_url] = queues

    def delete_queues(self, topic_names: list, server_url: str) -> None:
        """Record the topic names deleted for the given server URL."""
        self.deleted[server_url] = topic_names


class FakeEventReceiver:
    """Fake AbstractReceiver: records the event classes it listens to."""

    def __init__(self) -> None:
        self.event_classes: tuple | None = None

    def start_listening(self, event_classes) -> None:
        """Record the event classes the receiver will listen to."""
        self.event_classes = event_classes


class FakeInMemoryQueue:
    """Fake AbstractInMemoryQueue/AbstractQueue: scripted get, recording put."""

    def __init__(self, results: list | None = None) -> None:
        self.put_elements: list = []
        self._results = list(results or [])
        self.task_done_count = 0

    def put(self, element) -> None:
        """Record the element put on the queue."""
        self.put_elements.append(element)

    def get(self) -> QueuePayload:
        """Pop the next scripted result (raising it if it is an exception)."""
        result = self._results.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result

    def task_done(self) -> None:
        """Count a task_done call."""
        self.task_done_count += 1
