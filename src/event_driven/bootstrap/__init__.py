"""Bootstrap module for dependency injection."""

from event_driven.bootstrap.container import DependencyContainer, ThreadSafeQueue

__all__ = [
    "DependencyContainer",
    "ThreadSafeQueue",
]
