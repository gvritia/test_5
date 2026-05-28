from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers import admin, health, rooms, tasks, users, websocket_rooms

app = FastAPI(title="Контрольная работа №5", version="1.0.0")


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    _request,
    exc: RequestValidationError,
) -> JSONResponse:
    errors = exc.errors()
    status_code = (
        status.HTTP_400_BAD_REQUEST
        if any(error.get("type") == "json_invalid" for error in errors)
        else status.HTTP_422_UNPROCESSABLE_ENTITY
    )
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({"detail": errors}),
    )


app.include_router(health.router)
app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(rooms.router)
app.include_router(websocket_rooms.router)
