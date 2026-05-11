from src.app import create_app


def test_health_ok(client):
    res = client.get("/health")

    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_packages_needs_token_if_token_is_configured():
    app = create_app()
    app.config.update(TESTING=True, SPLENT_API_TOKEN="secret-token")
    client = app.test_client()

    res = client.get("/api/packages")

    assert res.status_code == 401
    assert res.get_json()["error"] == "Unauthorized"


def test_packages_works_with_valid_token(monkeypatch):
    monkeypatch.setattr("src.routes.packages.get_packages", lambda owner=None: [])

    app = create_app()
    app.config.update(TESTING=True, SPLENT_API_TOKEN="secret-token")
    client = app.test_client()

    res = client.get(
        "/api/packages",
        headers={"Authorization": "Bearer secret-token"},
    )

    assert res.status_code == 200
    assert res.get_json() == []


def test_health_works_even_with_token_configured():
    app = create_app()
    app.config.update(TESTING=True, SPLENT_API_TOKEN="secret-token")
    client = app.test_client()

    res = client.get("/health")

    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}
