"""DTO objects for must complete operations (commands)"""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class QueueConfig(BaseModel):
    """Value object: Configuration for one topic"""

    queue_name: str = Field(description="The name of the queue / topic.")
    num_partitions: int = Field(description="The number of partitions.")
    replication_factor: int = Field(description="The replication factor.")


class CreateTopicsCommand(BaseModel):
    """Command to start new topics / queues"""

    model_config: ClassVar = ConfigDict(from_attributes=True)

    queues: list[QueueConfig] = Field(description="The queues to create.")
    server_url: str = Field(description="The Kafka server URL.")


class DeleteTopicsCommand(BaseModel):
    """Command to detele a lsit of topics / queues"""

    model_config: ClassVar = ConfigDict(from_attributes=True)

    topic_names: list[str] = Field(description="The topic names to delete.")
    server_url: str = Field(description="The Kafka server URL.")
