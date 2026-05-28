USER_10 = {"X-User-Id": "10"}
USER_20 = {"X-User-Id": "20"}


def task_payload(**overrides):
    payload = {
        "title": "Prepare tests",
        "description": "Write integration tests for main scenarios",
        "status": "todo",
        "priority": 4,
    }
    payload.update(overrides)
    return payload


def create_task(client, headers=None, **overrides):
    response = client.post(
        "/tasks",
        headers=headers or USER_10,
        json=task_payload(**overrides),
    )
    assert response.status_code == 201
    return response.json()


def test_create_task_success(client):
    response = client.post("/tasks", headers=USER_10, json=task_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["owner_id"] == 10
    assert body["title"] == "Prepare tests"


def test_create_task_returns_422_for_short_title(client):
    response = client.post(
        "/tasks",
        headers=USER_10,
        json=task_payload(title="No"),
    )

    assert response.status_code == 422


def test_create_task_returns_400_for_malformed_json(client):
    response = client.post(
        "/tasks",
        headers={**USER_10, "Content-Type": "application/json"},
        content="{",
    )

    assert response.status_code == 400


def test_create_task_returns_401_without_user_header(client):
    response = client.post("/tasks", json=task_payload())

    assert response.status_code == 401


def test_user_sees_only_own_tasks(client):
    first = create_task(client, headers=USER_10, title="User ten task")
    create_task(client, headers=USER_20, title="User twenty task")

    response = client.get("/tasks", headers=USER_10)

    assert response.status_code == 200
    assert response.json() == [first]


def test_filter_tasks_by_status_and_min_priority(client):
    create_task(client, status="todo", priority=5, title="Todo task")
    create_task(client, status="done", priority=2, title="Low done task")
    expected = create_task(client, status="done", priority=4, title="High done task")

    response = client.get(
        "/tasks",
        headers=USER_10,
        params={"status": "done", "min_priority": 3},
    )

    assert response.status_code == 200
    assert response.json() == [expected]


def test_update_task_status_success(client):
    task = create_task(client)

    response = client.patch(
        f"/tasks/{task['id']}/status",
        headers=USER_10,
        json={"status": "done"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_task_detail_returns_404_for_missing_or_foreign_task(client):
    foreign_task = create_task(client, headers=USER_20)

    missing_response = client.get("/tasks/999", headers=USER_10)
    foreign_response = client.get(f"/tasks/{foreign_task['id']}", headers=USER_10)

    assert missing_response.status_code == 404
    assert foreign_response.status_code == 404


def test_delete_task_success(client):
    task = create_task(client)

    delete_response = client.delete(f"/tasks/{task['id']}", headers=USER_10)
    get_response = client.get(f"/tasks/{task['id']}", headers=USER_10)

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
