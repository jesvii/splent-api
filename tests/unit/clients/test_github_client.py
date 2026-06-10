import base64

from src.clients import github_client


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self.payload = payload or {}

    def json(self):
        return self.payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_build_headers_includes_github_token(app):
    app.config.update(GITHUB_TOKEN="github-token")

    with app.app_context():
        headers = github_client._build_headers()

    assert headers["Authorization"] == "Bearer github-token"
    assert headers["Accept"] == "application/vnd.github+json"


def test_build_headers_can_omit_token(app):
    app.config.update(GITHUB_TOKEN="github-token")

    with app.app_context():
        headers = github_client._build_headers(include_token=False)

    assert "Authorization" not in headers


def test_fetch_org_repos_uses_configured_org(app, monkeypatch):
    app.config.update(GITHUB_ORG="fake-org")
    requested_urls = []

    def fake_get(url):
        requested_urls.append(url)
        return FakeResponse(payload=[{"name": "splent_feature_auth"}])

    monkeypatch.setattr(github_client, "_get", fake_get)

    with app.app_context():
        repos = github_client.fetch_org_repos()

    assert repos == [{"name": "splent_feature_auth"}]
    assert requested_urls == [
        "https://api.github.com/orgs/fake-org/repos?per_page=100"
    ]


def test_fetch_repo_metadata_returns_none_on_404(app, monkeypatch):
    monkeypatch.setattr(github_client, "_get", lambda url: FakeResponse(404))

    with app.app_context():
        metadata = github_client.fetch_repo_metadata("missing")

    assert metadata is None


def test_fetch_repo_file_decodes_base64_content(app, monkeypatch):
    encoded = base64.b64encode(b"[tool.splent.contract]\n").decode("utf-8")
    monkeypatch.setattr(
        github_client,
        "_get",
        lambda url: FakeResponse(
            payload={"content": encoded, "encoding": "base64"}
        ),
    )

    with app.app_context():
        content = github_client.fetch_repo_file("splent_feature_auth", "pyproject.toml")

    assert content == "[tool.splent.contract]\n"


def test_fetch_repo_file_returns_none_on_missing_file(app, monkeypatch):
    monkeypatch.setattr(github_client, "_get", lambda url: FakeResponse(404))

    with app.app_context():
        content = github_client.fetch_repo_file("splent_feature_auth", "pyproject.toml")

    assert content is None


def test_fetch_repo_file_returns_none_for_unexpected_payload(app, monkeypatch):
    monkeypatch.setattr(
        github_client,
        "_get",
        lambda url: FakeResponse(payload={"content": "not-base64", "encoding": "utf-8"}),
    )

    with app.app_context():
        content = github_client.fetch_repo_file("splent_feature_auth", "pyproject.toml")

    assert content is None
