"""DTO objects for must complete operations (commands)"""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class QueueConfig(BaseModel):
    """Value object: Configuration for one topic"""

    queue_name: str
    num_partitions: int
    replication_factor: int


class CreateTopicsCommand(BaseModel):
    """Command to start new topics / queues"""

    model_config: ClassVar = ConfigDict(from_attributes=True)

    queues: list[QueueConfig]
    server_url: str


class DeleteTopicsCommand(BaseModel):
    """Command to detele a lsit of topics / queues"""

    model_config: ClassVar = ConfigDict(from_attributes=True)

    topic_names: list[str]
    server_url: str
