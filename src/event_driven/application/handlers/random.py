"""Produce or consume test events"""

from random import randint
from time import sleep

from event_driven.domain.events.test_event import TestEvent
from event_driven.infrastructure.messagebus.producer import AbstractProducer

from .send_kafka import send_event

_RANDOM_MAX_USERS = 9999
_RAMDOM_MAX_KEY = 4500
_RANDOM_MAX = 50_000
_RANDOM_MIN_VAL = 1


def send_random_test_event(topic: str, producer: AbstractProducer):
    """Send test event to try out kafka"""
    event = TestEvent(
        user_id="random_user_" + str(randint(_RANDOM_MIN_VAL, _RANDOM_MAX_USERS)),  # NOSONAR
        event_key="random_" + str(randint(_RANDOM_MIN_VAL, _RAMDOM_MAX_KEY)),  # NOSONAR
        value=randint(_RANDOM_MIN_VAL, _RANDOM_MAX),  # NOSONAR
    )
    send_event(topic, event, producer)


def periodically_send_random_test_event(wait_time: int, topic: str, producer: AbstractProducer):
    """Receive test envent to try out kafka"""
    while True:
        try:
            send_random_test_event(topic, producer)
            print(f"Sent message, sleeping {wait_time} seconds")
            sleep(wait_time)
        except KeyboardInterrupt:
            break
