from pydantic import BaseModel, Field

from app.models.task_status import TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=80)
    description: str | None = Field(default=None, max_length=500)
    status: TaskStatus
    priority: int = Field(..., ge=1, le=5)
