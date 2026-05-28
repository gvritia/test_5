import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.room_manager import room_manager
from app.storage import storage


@pytest.fixture(autouse=True)
def clean_state():
    storage.clear()
    room_manager.clear()
    yield
    storage.clear()
    room_manager.clear()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
