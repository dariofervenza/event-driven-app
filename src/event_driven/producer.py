"""sends events to a queue."""

from event_driven.application.handlers import periodically_send_random_test_event
from event_driven.bootstrap import DependencyContainer as DC
from event_driven.settings import CFG

if __name__ == "__main__":
    CONTAINER: DC = DC.get_container()
    producer = CONTAINER.producer
    periodically_send_random_test_event(
        CFG.kafka_server.producer_wait_time,
        next(iter(CFG.kafka_server.queues)).queue_name,
        producer,
    )
