from pydantic import BaseModel

from app.models.task_status import TaskStatus


class TaskStatusUpdate(BaseModel):
    status: TaskStatus
