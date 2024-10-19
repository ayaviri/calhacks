import time
import requests
from typing import Any
from pydantic import BaseModel, NonNegativeInt, PositiveInt
from database.schemas import TaskTable
from worker.utils import connect_to_rabbitmq_server, create_db_session_factory, Timer


# TODO: The information necessary for a worker to independently complete a
# portion of the original task
class Subtask(BaseModel):
    model_file_contents: str
    dataset_name: str
    # Represents the ID of the task from which this one is derived, shared by
    # all subtasks of a given task
    task_id: str
    # Represents the order in which this subtask belongs in the collection of
    # subtasks
    task_num: NonNegativeInt
    # Represents the number of subtasks the original task was divided into
    subtask_count: PositiveInt


# The message schema received by this worker, represents a model finetuning task
class TaskSplitMessage(BaseModel):
    # A .keras file
    model_file_contents: str
    # The name of a dataset provided by tensorflow
    dataset_name: str
    task_id: str


# Called when a task is submitted in by the core server in the form of a message.
# Message body is contained in the _body_ parameter as a byte array
def split_task(channel, method, properties, body: bytes):
    with Timer("deserialising message body from json"):
        message = TaskSplitMessage.model_validate_json(str(body))

    # 2) TODO: Split into subtasks according to available workers
    with Timer("splitting into subtasks according to available workers"):
        available_workers = 4
        subtasks = [
            Subtask(
                model_file_contents=message.model_file_contents
                dataset_name=message.dataset_name,
                task_id=message.task_id,
                subtask_count=available_workers
            ) 
            for _ in range(available_workers)
        ]

    # NOTE: Ideally, there is some retry mechanism here since most of the
    # work has already been done in splitting the task
    with Timer("writing subtask count to postgres"):
        with Session.begin() as session:
            TaskTable.set_subtask_count(
                session, message.task_id, subtask_count=available_workers
            )

    with Timer("serialising subtasks into json"):
        serialised_subtasks: list[str] = [s.model_dump_json() for s in subtasks]

    with Timer("publishing each subtask to queue"):
        for message in serialised_subtasks:
            channel.basic_publish(exchange="", routing_key="subtask", body=message)


def main():
    global Session
    rabbitmq_channel = connect_to_rabbitmq_server()
    Session = create_db_session_factory()
    rabbitmq_channel.basic_consume(queue="task_split", on_message_callback=split_task)
    rabbitmq_channel.start_consuming()


main()
