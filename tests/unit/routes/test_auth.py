from src.app import create_app


def test_auth_check_ok_without_token(client):
    res = client.get("/api/auth/check")

    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_auth_check_requires_token_if_configured():
    app = create_app()
    app.config.update(TESTING=True, SPLENT_API_TOKEN="secret-token")
    client = app.test_client()

    res = client.get("/api/auth/check")

    assert res.status_code == 401
    assert res.get_json()["error"] == "Unauthorized"


def test_auth_check_ok_with_valid_token():
    app = create_app()
    app.config.update(TESTING=True, SPLENT_API_TOKEN="secret-token")
    client = app.test_client()

    res = client.get(
        "/api/auth/check",
        headers={"Authorization": "Bearer secret-token"},
    )

    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}
