import uuid
from sqlalchemy import Column, Integer, String, DateTime, select, Boolean
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional
from pydantic import NonNegativeInt, BaseModel, PositiveInt


#  ____  _____ ___  _   _ _____ ____ _____
# |  _ \| ____/ _ \| | | | ____/ ___|_   _|
# | |_) |  _|| | | | | | |  _| \___ \ | |
# |  _ <| |__| |_| | |_| | |___ ___) || |
# |_| \_\_____\__\_\\___/|_____|____/ |_|
#
#  ____   ____ _   _ _____ __  __    _    ____
# / ___| / ___| | | | ____|  \/  |  / \  / ___|
# \___ \| |   | |_| |  _| | |\/| | / _ \ \___ \
#  ___) | |___|  _  | |___| |  | |/ ___ \ ___) |
# |____/ \____|_| |_|_____|_|  |_/_/   \_\____/
#


class PostResultRequestBody(BaseModel):
    # A base64 encoded string of the binary data contained in a .keras file,
    # representing a finetuned tensorflow model shard
    encoded_model_shard_file_contents: str
    # Represents the order of this subtask result in the
    # collection of subtask results
    task_num: NonNegativeInt
    # Represents the ID of the task from which this subtask was derived
    task_id: str
    # Represents the number of subtasks the original task was divided into
    subtask_count: NonNegativeInt


#  __  __ ___ ____   ____
# |  \/  |_ _/ ___| / ___|
# | |\/| || |\___ \| |
# | |  | || | ___) | |___
# |_|  |_|___|____/ \____|
#


class SubtaskResult(BaseModel):
    encoded_model_shard_file_contents: str
    task_num: NonNegativeInt


#  __  __ _____ ____ ____    _    ____ _____
# |  \/  | ____/ ___/ ___|  / \  / ___| ____|
# | |\/| |  _| \___ \___ \ / _ \| |  _|  _|
# | |  | | |___ ___) |__) / ___ \ |_| | |___
# |_|  |_|_____|____/____/_/   \_\____|_____|
#
#  ____   ____ _   _ _____ __  __    _    ____
# / ___| / ___| | | | ____|  \/  |  / \  / ___|
# \___ \| |   | |_| |  _| | |\/| | / _ \ \___ \
#  ___) | |___|  _  | |___| |  | |/ ___ \ ___) |
# |____/ \____|_| |_|_____|_|  |_/_/   \_\____/
#


# The message schema received by the task splitting worker, represents a
# model finetuning task
class TaskSplitMessage(BaseModel):
    # A base64 encoded string of the binary data contained in a .keras file,
    # representing a tensorflow model
    encoded_model_file_contents: str
    # The name of a dataset provided by tensorflow
    dataset_name: str
    # Represents the ID of the task from which this one is derived, shared by
    # all subtasks of a given task
    task_id: str


# The message schema sent by the task splitting worker to each of the
# finetuning workers. Contains the information necessary to completion a portion
# of the original finetuning task
class SubtaskMessage(BaseModel):
    encoded_model_file_contents: str
    dataset_name: str
    task_id: str
    # Represents the order in which this subtask belongs in the collection of
    # subtasks
    task_num: NonNegativeInt
    # Represents the number of subtasks the original task was divided into
    subtask_count: PositiveInt


# The message schema received by the result aggregation worker,
# represents the collection of results from each worker's subtask (of model finetuning)
class ResultAggregationMessage(BaseModel):
    subtask_results: list[SubtaskResult]


# Represents the aggregated work of each subtask. Schema of the message
# to be sent to the POST /result endpoint
class ResultMessage(BaseModel):
    # The remote URL from which to download the finetuned model
    file_url_model: str


#  ____    _  _____  _    ____    _    ____  _____
# |  _ \  / \|_   _|/ \  | __ )  / \  / ___|| ____|
# | | | |/ _ \ | | / _ \ |  _ \ / _ \ \___ \|  _|
# | |_| / ___ \| |/ ___ \| |_) / ___ \ ___) | |___
# |____/_/   \_\_/_/   \_\____/_/   \_\____/|_____|
#
#  ____   ____ _   _ _____ __  __    _    ____
# / ___| / ___| | | | ____|  \/  |  / \  / ___|
# \___ \| |   | |_| |  _| | |\/| | / _ \ \___ \
#  ___) | |___|  _  | |___| |  | |/ ___ \ ___) |
# |____/ \____|_| |_|_____|_|  |_/_/   \_\____/
#

Base = declarative_base()


class TaskRow(Base):
    __tablename__ = "task"

    id = Column(String, primary_key=True, index=True)
    subtask_count = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SubtaskRow(Base):
    __tablename__ = "subtask"

    id = Column(String, primary_key=True, index=True)
    is_assigned = Column(Boolean)
    message = Column(String)  # JSON formatted string
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TaskTable:
    @staticmethod
    def write_task(session) -> str:
        task_id = str(uuid.uuid4())
        row = TaskRow(id=task_id)
        session.add(row)
        return task_id

    @staticmethod
    def get_task(session, task_id: str) -> Optional[TaskRow]:
        statement = select(TaskRow).where(TaskRow.id == task_id)

        return session.scalars(statement).first()

    @staticmethod
    def set_subtask_count(session, task_id: str, subtask_count: NonNegativeInt):
        task_row: Optional[TaskRow] = TaskTable.get_task(session, task_id)

        if task_row:
            task_row.subtask_count = subtask_count
        else:
            raise Exception("Given task ID does not exist")


class SubtaskTable:
    @staticmethod
    def get_oldest_unassigned_subtask(session) -> Optional[SubtaskRow]:
        statement = (
            select(SubtaskRow)
            .where(not SubtaskRow.is_assigned)
            .order_by(SubtaskRow.created_at)
        )

        return session.scalars(statement).first()

    @staticmethod
    def get_subtask(session, subtask_id: str) -> Optional[SubtaskRow]:
        statement = select(SubtaskRow).where(SubtaskRow.id == subtask_id)

        return session.scalars(statement).first()

    @staticmethod
    def assign(session, subtask_id: str):
        subtask_row: Optional[SubtaskRow] = SubtaskTable.get_subtask(
            session, subtask_id
        )

        if subtask_row:
            subtask_row.is_assigned = True
        else:
            raise Exception("Given subtask ID does not exist")

    @staticmethod
    def batch_submit(session, subtask_messages: list[str]):
        rows = [
            SubtaskRow(id=str(uuid.uuid4()), is_assigned=False, message=m)
            for m in subtask_messages
        ]
        session.add_all(rows)
