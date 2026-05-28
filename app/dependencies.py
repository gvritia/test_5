from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.models.model_user import User
from app.storage import TaskStorage, storage


def get_current_user(
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
    x_user_role: Annotated[str, Header(alias="X-User-Role")] = "user",
) -> User:
    try:
        user_id = int(x_user_id) if x_user_id is not None else 0
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid X-User-Id header is required",
        ) from exc

    if user_id < 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid X-User-Id header is required",
        )

    if x_user_role not in {"user", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-User-Role must be user or admin",
        )

    return User(id=user_id, role=x_user_role)


def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role is required",
        )
    return current_user


def get_storage() -> TaskStorage:
    return storage
