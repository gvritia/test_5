from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.api_responses import BAD_REQUEST, FORBIDDEN, UNAUTHORIZED, VALIDATION_ERROR
from app.dependencies import get_current_user
from app.models.model_user import User

router = APIRouter(prefix="/users", tags=["users"])

USER_ME_RESPONSES = {**BAD_REQUEST, **UNAUTHORIZED}
USER_DETAIL_RESPONSES = {**BAD_REQUEST, **UNAUTHORIZED, **FORBIDDEN, **VALIDATION_ERROR}


@router.get("/me", response_model=User, responses=USER_ME_RESPONSES)
def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@router.get("/{user_id}", response_model=User, responses=USER_DETAIL_RESPONSES)
def get_user(
    user_id: Annotated[int, Path(ge=1)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users can only read their own profile",
        )

    if current_user.id == user_id:
        return current_user
    return User(id=user_id, role="user")
