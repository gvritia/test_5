def test_health_route(client, monkeypatch):
    monkeypatch.setenv("APP_ENV", "docker")

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "env": "docker"}
