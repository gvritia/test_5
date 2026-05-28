from pydantic import BaseModel, ConfigDict, Field

from app.models.task_status import TaskStatus


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., ge=1)
    title: str = Field(..., min_length=3, max_length=80)
    description: str | None = Field(default=None, max_length=500)
    status: TaskStatus
    priority: int = Field(..., ge=1, le=5)
    owner_id: int = Field(..., ge=1)
