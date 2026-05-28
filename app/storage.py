from threading import Lock

from app.models.model_task_create import TaskCreate
from app.models.model_task_read import TaskRead
from app.models.task_status import TaskStatus


class TaskStorage:
    def __init__(self) -> None:
        self._tasks: dict[int, TaskRead] = {}
        self._next_id = 1
        self._lock = Lock()

    def clear(self) -> None:
        with self._lock:
            self._tasks.clear()
            self._next_id = 1

    def create(self, payload: TaskCreate, owner_id: int) -> TaskRead:
        with self._lock:
            task = TaskRead(id=self._next_id, owner_id=owner_id, **payload.model_dump())
            self._tasks[task.id] = task
            self._next_id += 1
            return task

    def list(
        self,
        *,
        owner_id: int | None = None,
        status: TaskStatus | None = None,
        min_priority: int | None = None,
    ) -> list[TaskRead]:
        with self._lock:
            tasks = list(self._tasks.values())

        if owner_id is not None:
            tasks = [task for task in tasks if task.owner_id == owner_id]
        if status is not None:
            tasks = [task for task in tasks if task.status == status]
        if min_priority is not None:
            tasks = [task for task in tasks if task.priority >= min_priority]
        return tasks

    def get(self, task_id: int) -> TaskRead | None:
        with self._lock:
            return self._tasks.get(task_id)

    def update_status(self, task_id: int, status: TaskStatus) -> TaskRead | None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None

            updated_task = task.model_copy(update={"status": status})
            self._tasks[task_id] = updated_task
            return updated_task

    def delete(self, task_id: int) -> bool:
        with self._lock:
            if task_id not in self._tasks:
                return False

            del self._tasks[task_id]
            return True


storage = TaskStorage()
