import uuid
from sqlalchemy import Column, Integer, String, DateTime, Text, and_, desc
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TaskRow(Base):  # type: ignore
    __tablename__ = "task"

    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TaskTable:
    pass

    @staticmethod
    def write_task(session) -> str:
        task_id = str(uuid.uuid4())
        row = TaskRow(id=task_id)
        session.add(row)
        return task_id
