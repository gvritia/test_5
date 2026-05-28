from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status

from app.api_responses import BAD_REQUEST, NOT_FOUND, UNAUTHORIZED, VALIDATION_ERROR
from app.dependencies import get_current_user, get_storage
from app.models.model_task_create import TaskCreate
from app.models.model_task_read import TaskRead
from app.models.model_task_status_update import TaskStatusUpdate
from app.models.model_user import User
from app.models.task_status import TaskStatus
from app.storage import TaskStorage

router = APIRouter(prefix="/tasks", tags=["tasks"])

TASK_CREATE_RESPONSES = {**BAD_REQUEST, **UNAUTHORIZED, **VALIDATION_ERROR}
TASK_LIST_RESPONSES = {**UNAUTHORIZED, **VALIDATION_ERROR}
TASK_DETAIL_RESPONSES = {**UNAUTHORIZED, **NOT_FOUND, **VALIDATION_ERROR}
TASK_UPDATE_RESPONSES = {**BAD_REQUEST, **UNAUTHORIZED, **NOT_FOUND, **VALIDATION_ERROR}
TASK_DELETE_RESPONSES = {**UNAUTHORIZED, **NOT_FOUND, **VALIDATION_ERROR}


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    responses=TASK_CREATE_RESPONSES,
)
def create_task(
    payload: TaskCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    task_storage: Annotated[TaskStorage, Depends(get_storage)],
) -> TaskRead:
    return task_storage.create(payload, owner_id=current_user.id)


@router.get("", response_model=list[TaskRead], responses=TASK_LIST_RESPONSES)
def list_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    task_storage: Annotated[TaskStorage, Depends(get_storage)],
    task_status: Annotated[TaskStatus | None, Query(alias="status")] = None,
    min_priority: Annotated[int | None, Query(ge=1, le=5)] = None,
) -> list[TaskRead]:
    return task_storage.list(
        owner_id=current_user.id,
        status=task_status,
        min_priority=min_priority,
    )


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    responses=TASK_DETAIL_RESPONSES,
)
def get_task(
    task_id: Annotated[int, Path(ge=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    task_storage: Annotated[TaskStorage, Depends(get_storage)],
) -> TaskRead:
    task = task_storage.get(task_id)
    if task is None or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task was not found",
        )
    return task


@router.patch(
    "/{task_id}/status",
    response_model=TaskRead,
    responses=TASK_UPDATE_RESPONSES,
)
def update_task_status(
    task_id: Annotated[int, Path(ge=1)],
    payload: TaskStatusUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    task_storage: Annotated[TaskStorage, Depends(get_storage)],
) -> TaskRead:
    task = task_storage.get(task_id)
    if task is None or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task was not found",
        )

    updated_task = task_storage.update_status(task_id, payload.status)
    if updated_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task was not found",
        )
    return updated_task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=TASK_DELETE_RESPONSES,
)
def delete_task(
    task_id: Annotated[int, Path(ge=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    task_storage: Annotated[TaskStorage, Depends(get_storage)],
) -> Response:
    task = task_storage.get(task_id)
    if task is None or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task was not found",
        )

    task_storage.delete(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
