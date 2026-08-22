"""sends events to a queue"""

from event_driven.application.handlers.random import periodically_send_random_test_event
from event_driven.infrastructure.messagebus.producer import KafkaProducer
from event_driven.settings import CFG

if __name__ == "__main__":
    queue = CFG.kafka_server.queues[0]
    producer = KafkaProducer(server_url=CFG.kafka_server.server_url)
    WAIT_TIME = 8
    periodically_send_random_test_event(WAIT_TIME, queue.queue_name, producer)
