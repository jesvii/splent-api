def test_packages_list(client, monkeypatch):
    packages = [
        {
            "full_name": "fake-owner/splent_feature_demo",
            "owner": "fake-owner",
            "name": "splent_feature_demo",
        }
    ]

    def fake_get_packages(owner=None):
        assert owner == "fake-owner"
        return packages

    monkeypatch.setattr("src.routes.packages.get_packages", fake_get_packages)

    res = client.get("/api/packages?owner=fake-owner")

    assert res.status_code == 200
    assert res.get_json() == packages


def test_get_package_by_name(client, monkeypatch):
    package = {
        "full_name": "fake-owner/splent_feature_demo",
        "owner": "fake-owner",
        "name": "splent_feature_demo",
    }

    def fake_get_package_by_name(name, owner=None):
        assert name == "fake-owner/splent_feature_demo"
        assert owner is None
        return package

    monkeypatch.setattr("src.routes.packages.get_package_by_name", fake_get_package_by_name)

    res = client.get("/api/packages/fake-owner/splent_feature_demo")

    assert res.status_code == 200
    assert res.get_json() == package


def test_get_package_not_found(client, monkeypatch):
    monkeypatch.setattr(
        "src.routes.packages.get_package_by_name",
        lambda name, owner=None: None,
    )

    res = client.get("/api/packages/missing-package")

    assert res.status_code == 404
    assert res.get_json()["error"] == "Package not found"


def test_publish_package_bad_json(client):
    res = client.post(
        "/api/packages",
        data="not-json",
        content_type="application/json",
    )

    assert res.status_code == 400
    assert res.get_json()["error"] == "Request body must be valid JSON"


def test_publish_package_with_owner(client, monkeypatch):
    package = {
        "full_name": "fake-owner/splent_feature_demo",
        "owner": "fake-owner",
        "name": "splent_feature_demo",
    }

    def fake_publish_package(data):
        assert data["owner"] == "fake-owner"
        assert data["name"] == "splent_feature_demo"
        return package

    monkeypatch.setattr("src.routes.packages.publish_package", fake_publish_package)

    res = client.post(
        "/api/packages?owner=fake-owner",
        json={"name": "splent_feature_demo"},
    )

    assert res.status_code == 201
    assert res.get_json() == package


def test_update_package_not_found(client, monkeypatch):
    def fake_update_package(name, data):
        assert name == "missing-package"
        raise FileNotFoundError()

    monkeypatch.setattr("src.routes.packages.update_package", fake_update_package)

    res = client.put(
        "/api/packages/missing-package",
        json={"description": "Updated"},
    )

    assert res.status_code == 404
    assert res.get_json()["error"] == "Package not found"
