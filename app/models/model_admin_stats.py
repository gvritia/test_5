from pydantic import BaseModel, Field


class AdminStats(BaseModel):
    total_tasks: int = Field(..., ge=0)
    by_status: dict[str, int]
