import pika
import os
import time
import uuid
from sqlalchemy import create_engine, Column, Integer, String, DateTime, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from pydantic import NonNegativeInt
from typing import Optional


def connect_to_rabbitmq_server():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))

    return connection.channel()


pg_user = os.environ.get("POSTGRES_USER")
pg_password = os.environ.get("POSTGRES_PASSWORD")
pg_host = os.environ.get("PGHOST")
pg_port = os.environ.get("PGPORT")
pg_db = os.environ.get("POSTGRES_DB")
db_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"


def create_db_session_factory():
    engine = create_engine(db_url)

    return sessionmaker(autocommit=False, autoflush=True, bind=engine)


class Timer:
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        self.startTime = time.time()
        print(f"Started {self.message}")

    def __exit__(self, exc_type, exc_value, traceback):
        self.endTime = time.time()
        print(f"Finished {self.message} in {self.endTime - self.startTime} seconds")

Base = declarative_base()

class TaskRow(Base):
    __tablename__ = "task"

    id = Column(String, primary_key=True, index=True)
    subtask_count = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TaskTable:
    pass

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