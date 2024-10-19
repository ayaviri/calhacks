import uuid
from sqlalchemy import Column, Integer, String, DateTime, select
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional
from pydantic import NonNegativeInt

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

    @staticmethod
    def update_task(user_id: UserID, task_id: str, new_state: str):
        with Session.begin() as session:
            task_row: Optional[TaskRow] = (
                session.query(TaskRow)
                .filter(and_(TaskRow.user_id == user_id, TaskRow.task_id == task_id))
                .first()
            )

            if task_row:
                task_row.state = new_state  # type: ignore
                task_row.completed_at = datetime.now()  # type: ignore
            else:
                raise Exception("There is no task with the given ID")
