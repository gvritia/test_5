from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status

from app.api_responses import FORBIDDEN, NOT_FOUND, UNAUTHORIZED, VALIDATION_ERROR
from app.dependencies import get_storage, require_admin
from app.models.model_admin_stats import AdminStats
from app.models.model_user import User
from app.models.task_status import TaskStatus
from app.storage import TaskStorage

router = APIRouter(prefix="/admin", tags=["admin"])

ADMIN_STATS_RESPONSES = {**UNAUTHORIZED, **FORBIDDEN}
ADMIN_DELETE_TASK_RESPONSES = {**UNAUTHORIZED, **FORBIDDEN, **NOT_FOUND, **VALIDATION_ERROR}


@router.get("/stats", response_model=AdminStats, responses=ADMIN_STATS_RESPONSES)
def get_stats(
    _: Annotated[User, Depends(require_admin)],
    task_storage: Annotated[TaskStorage, Depends(get_storage)],
) -> AdminStats:
    tasks = task_storage.list()
    by_status = {task_status.value: 0 for task_status in TaskStatus}
    for task in tasks:
        by_status[task.status.value] += 1
    return AdminStats(total_tasks=len(tasks), by_status=by_status)


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ADMIN_DELETE_TASK_RESPONSES,
)
def delete_any_task(
    task_id: Annotated[int, Path(ge=1)],
    _: Annotated[User, Depends(require_admin)],
    task_storage: Annotated[TaskStorage, Depends(get_storage)],
) -> Response:
    if not task_storage.delete(task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task was not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
