"""Listener thread that receives events from Kafka and puts them in the in-memory queue."""

import threading
from collections.abc import Sequence

from event_driven.domain.events import AbstractEvent
from event_driven.domain.ports import AbstractReceiver


class ListenerThread(threading.Thread):
    """Thread that receives events from Kafka and puts them in the in-memory queue."""

    def __init__(
        self,
        receiver: AbstractReceiver,
        event_classes: Sequence[type[AbstractEvent]],
    ) -> None:
        super().__init__(daemon=True)
        self.receiver = receiver
        self.event_classes = event_classes

    def run(self) -> None:
        """Receive events from Kafka and put them in the in-memory queue."""
        self.receiver.start_listening(self.event_classes)
