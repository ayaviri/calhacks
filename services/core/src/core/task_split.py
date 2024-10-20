import time
import requests
from typing import Any
from pydantic import BaseModel, NonNegativeInt, PositiveInt

from core.mq import connect_to_rabbitmq_server
from core.database import create_db_session_factory
from core.utils import Timer
from core.schemas import (
    TaskSplitMessage,
    SubtaskMessage,
    TaskTable,
    SubtaskTable,
)


# Called when a task is submitted in by the core server in the form of a message.
# Message body is contained in the _body_ parameter as a byte array
def split_task(channel, method, properties, body: bytes):
    with Timer("deserialising message body from json"):
        message = TaskSplitMessage.model_validate_json(body.decode("utf-8"))

    # 2) TODO: Split into subtasks according to available workers
    with Timer("splitting into subtasks according to available workers"):
        available_workers = 1
        subtasks = [
            SubtaskMessage(
                encoded_model_file_contents=message.encoded_model_file_contents,
                dataset_name=message.dataset_name,
                task_id=message.task_id,
                task_num=index,
                subtask_count=available_workers,
            )
            for index in range(available_workers)
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

    with Timer("batch writing the subtasks to postgres"):
        with Session.begin() as session:
            SubtaskTable.batch_submit(session, serialised_subtasks)


def main():
    global Session

    with Timer("connecting to rabbitmq server"):
        rabbitmq_channel = connect_to_rabbitmq_server()

    with Timer("connecting to postgres"):
        Session = create_db_session_factory()

    with Timer("subscribing to queue and awaiting messages"):
        rabbitmq_channel.basic_consume(
            queue="task_split", on_message_callback=split_task
        )
        rabbitmq_channel.start_consuming()


main()
