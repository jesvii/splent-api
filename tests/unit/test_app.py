from src.app import create_app


def test_health_ok(client):
    res = client.get("/health")

    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_packages_public_read_without_token_if_token_is_configured(monkeypatch):
    monkeypatch.setattr("src.routes.packages.get_packages", lambda owner=None: [])

    app = create_app()
    app.config.update(TESTING=True, SPLENT_API_TOKEN="secret-token")
    client = app.test_client()

    res = client.get("/api/packages")

    assert res.status_code == 200
    assert res.get_json() == []


def test_package_detail_public_read_without_token_if_token_is_configured(monkeypatch):
    monkeypatch.setattr(
        "src.routes.packages.get_package_by_name",
        lambda name, owner=None: {"name": name},
    )

    app = create_app()
    app.config.update(TESTING=True, SPLENT_API_TOKEN="secret-token")
    client = app.test_client()

    res = client.get("/api/packages/splent_feature_demo")

    assert res.status_code == 200
    assert res.get_json() == {"name": "splent_feature_demo"}


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


def test_publish_package_requires_token_if_token_is_configured():
    app = create_app()
    app.config.update(TESTING=True, SPLENT_API_TOKEN="secret-token")
    client = app.test_client()

    res = client.post("/api/packages", json={"name": "splent_feature_demo"})

    assert res.status_code == 401
    assert res.get_json()["error"] == "Unauthorized"


def test_health_works_even_with_token_configured():
    app = create_app()
    app.config.update(TESTING=True, SPLENT_API_TOKEN="secret-token")
    client = app.test_client()

    res = client.get("/health")

    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}
