USER_10 = {"X-User-Id": "10"}
USER_20 = {"X-User-Id": "20"}
ADMIN = {"X-User-Id": "1", "X-User-Role": "admin"}


def create_task(client, headers, title, status="todo"):
    response = client.post(
        "/tasks",
        headers=headers,
        json={
            "title": title,
            "description": None,
            "status": status,
            "priority": 3,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_users_me_returns_current_user(client):
    response = client.get("/users/me", headers=USER_10)

    assert response.status_code == 200
    assert response.json() == {"id": 10, "role": "user"}


def test_missing_user_header_returns_401(client):
    response = client.get("/users/me")

    assert response.status_code == 401


def test_regular_user_gets_403_for_admin_stats(client):
    response = client.get("/admin/stats", headers=USER_10)

    assert response.status_code == 403


def test_admin_gets_stats_for_all_tasks(client):
    create_task(client, USER_10, "First task", status="todo")
    create_task(client, USER_20, "Second task", status="done")
    create_task(client, USER_20, "Third task", status="done")

    response = client.get("/admin/stats", headers=ADMIN)

    assert response.status_code == 200
    assert response.json() == {
        "total_tasks": 3,
        "by_status": {"todo": 1, "in_progress": 0, "done": 2},
    }


def test_regular_user_cannot_delete_foreign_task_through_tasks_router(client):
    foreign_task = create_task(client, USER_20, "Foreign task")

    delete_response = client.delete(f"/tasks/{foreign_task['id']}", headers=USER_10)
    owner_get_response = client.get(f"/tasks/{foreign_task['id']}", headers=USER_20)

    assert delete_response.status_code == 404
    assert owner_get_response.status_code == 200


def test_admin_can_delete_foreign_task(client):
    foreign_task = create_task(client, USER_20, "Foreign task")

    delete_response = client.delete(f"/admin/tasks/{foreign_task['id']}", headers=ADMIN)
    owner_get_response = client.get(f"/tasks/{foreign_task['id']}", headers=USER_20)

    assert delete_response.status_code == 204
    assert owner_get_response.status_code == 404


def test_openapi_groups_routes_by_tags(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert paths["/tasks"]["get"]["tags"] == ["tasks"]
    assert paths["/users/me"]["get"]["tags"] == ["users"]
    assert paths["/admin/stats"]["get"]["tags"] == ["admin"]
