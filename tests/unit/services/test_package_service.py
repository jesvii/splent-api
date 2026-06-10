import json

import pytest

from src.services import package_service


@pytest.fixture
def packages_file(tmp_path, monkeypatch):
    path = tmp_path / "packages.json"
    monkeypatch.setattr(package_service, "PACKAGES_FILE", str(path))
    return path


def make_package(**changes):
    package = {
        "full_name": "fake-owner/splent_feature_demo",
        "owner": "fake-owner",
        "name": "splent_feature_demo",
        "repository": "fake-owner/splent_feature_demo",
        "repo_url": "https://github.com/fake-owner/splent_feature_demo",
        "contract": {
            "description": "Demo feature",
            "provides": {},
            "requires": {},
        },
        "metadata": {"source": "splent-cli"},
    }

    package.update(changes)
    return package


def test_split_package_ref_with_version():
    owner, name = package_service._split_package_ref(
        "fake-owner/splent_feature_demo@v1.0.0"
    )

    assert owner == "fake-owner"
    assert name == "splent_feature_demo"


def test_split_package_ref_without_owner():
    owner, name = package_service._split_package_ref(
        "splent_feature_demo",
        owner="fake-owner",
    )

    assert owner == "fake-owner"
    assert name == "splent_feature_demo"


def test_normalize_package_data():
    package = package_service._normalize_package_data(
        {
            "owner": "fake-owner",
            "name": "splent_feature_demo",
            "description": "Demo feature",
            "provides": {},
            "requires": {},
            "repo_url": "https://github.com/fake-owner/splent_feature_demo",
        }
    )

    assert package["full_name"] == "fake-owner/splent_feature_demo"
    assert package["repository"] == "fake-owner/splent_feature_demo"
    assert package["contract"]["description"] == "Demo feature"


def test_publish_package(packages_file):
    package = package_service.publish_package(make_package())

    assert package["full_name"] == "fake-owner/splent_feature_demo"
    assert package["repository"] == "fake-owner/splent_feature_demo"

    saved = json.loads(packages_file.read_text())
    assert saved["fake-owner/splent_feature_demo"] == package


def test_publish_package_without_description(packages_file):
    data = make_package(
        contract={
            "description": "",
            "provides": {},
            "requires": {},
        }
    )

    with pytest.raises(ValueError, match="Description cannot be empty"):
        package_service.publish_package(data)


def test_get_packages_prefers_registry_data(packages_file, monkeypatch):
    registry_package = make_package(
        contract={
            "description": "Registry description",
            "provides": {},
            "requires": {},
        }
    )

    packages_file.write_text(
        json.dumps({"fake-owner/splent_feature_demo": registry_package})
    )

    github_package = {
        **registry_package,
        "contract": {
            "description": "GitHub description",
            "provides": {},
            "requires": {},
        },
    }

    monkeypatch.setattr(
        package_service,
        "_packages_from_github",
        lambda owner=None: [github_package],
    )

    packages = package_service.get_packages()

    assert len(packages) == 1
    assert packages[0]["contract"]["description"] == "Registry description"


def test_extract_contract_reads_splent_contract():
    content = """
[tool.splent.contract]
description = "Authentication feature"

[tool.splent.contract.provides]
routes = ["/login"]

[tool.splent.contract.requires]
features = ["splent_feature_mail"]
"""

    contract = package_service.extract_contract(content)

    assert contract["description"] == "Authentication feature"
    assert contract["provides"]["routes"] == ["/login"]
    assert contract["requires"]["features"] == ["splent_feature_mail"]


def test_packages_from_github_normalizes_repositories(monkeypatch):
    repos = [
        {
            "id": 1,
            "name": "splent_feature_auth",
            "full_name": "fake-owner/splent_feature_auth",
            "html_url": "https://github.com/fake-owner/splent_feature_auth",
            "owner": {"login": "fake-owner"},
            "private": False,
            "updated_at": "2026-06-10T10:00:00Z",
        }
    ]
    pyproject = """
[tool.splent.contract]
description = "Auth feature"

[tool.splent.contract.provides]
routes = ["/login"]

[tool.splent.contract.requires]
features = []
"""

    monkeypatch.setattr(package_service, "fetch_org_repos", lambda org=None: repos)
    monkeypatch.setattr(
        package_service,
        "fetch_repo_file",
        lambda repo_name, path, org=None: pyproject,
    )

    packages = package_service._packages_from_github(owner="fake-owner")

    assert packages == [
        {
            "full_name": "fake-owner/splent_feature_auth",
            "owner": "fake-owner",
            "name": "splent_feature_auth",
            "repository": "fake-owner/splent_feature_auth",
            "repo_url": "https://github.com/fake-owner/splent_feature_auth",
            "contract": {
                "description": "Auth feature",
                "provides": {"routes": ["/login"]},
                "requires": {"features": []},
            },
            "metadata": {
                "github_id": 1,
                "private": False,
                "updated_at": "2026-06-10T10:00:00Z",
                "source": "github",
            },
        }
    ]


def test_packages_from_github_skips_repos_without_contract(monkeypatch):
    repos = [
        {"name": "splent_feature_auth"},
        {"name": "splent_feature_mail"},
        {},
    ]

    def fake_fetch_repo_file(repo_name, path, org=None):
        if repo_name == "splent_feature_auth":
            return ""
        return "[project]\nname = 'without-contract'\n"

    monkeypatch.setattr(package_service, "fetch_org_repos", lambda org=None: repos)
    monkeypatch.setattr(package_service, "fetch_repo_file", fake_fetch_repo_file)

    assert package_service._packages_from_github(owner="fake-owner") == []


def test_packages_from_github_returns_empty_when_github_fails(monkeypatch):
    def fake_fetch_org_repos(org=None):
        raise RuntimeError("rate limit exceeded")

    monkeypatch.setattr(package_service, "fetch_org_repos", fake_fetch_org_repos)

    assert package_service._packages_from_github(owner="fake-owner") == []


def test_get_package_by_name_loads_from_github(monkeypatch):
    repo = {
        "id": 2,
        "name": "splent_feature_auth",
        "full_name": "fake-owner/splent_feature_auth",
        "html_url": "https://github.com/fake-owner/splent_feature_auth",
        "owner": {"login": "fake-owner"},
        "private": False,
        "updated_at": "2026-06-10T10:00:00Z",
    }
    pyproject = """
[tool.splent.contract]
description = "Auth feature"

[tool.splent.contract.provides]
routes = []

[tool.splent.contract.requires]
features = []
"""

    monkeypatch.setattr(package_service, "load_packages_from_file", lambda: {})
    monkeypatch.setattr(package_service, "fetch_repo_metadata", lambda repo_name, org=None: repo)
    monkeypatch.setattr(
        package_service,
        "fetch_repo_file",
        lambda repo_name, path, org=None: pyproject,
    )

    package = package_service.get_package_by_name(
        "fake-owner/splent_feature_auth"
    )

    assert package["full_name"] == "fake-owner/splent_feature_auth"
    assert package["contract"]["description"] == "Auth feature"


def test_get_package_by_name_returns_none_for_missing_github_contract(monkeypatch):
    monkeypatch.setattr(package_service, "load_packages_from_file", lambda: {})
    monkeypatch.setattr(
        package_service,
        "fetch_repo_metadata",
        lambda repo_name, org=None: {"name": repo_name},
    )
    monkeypatch.setattr(
        package_service,
        "fetch_repo_file",
        lambda repo_name, path, org=None: "[project]\nname = 'missing-contract'\n",
    )

    package = package_service.get_package_by_name(
        "fake-owner/splent_feature_missing"
    )

    assert package is None


def test_validate_package_data_rejects_invalid_provides(packages_file):
    data = make_package(
        contract={"description": "Demo", "provides": [], "requires": {}}
    )

    with pytest.raises(ValueError, match="Provides must be an object"):
        package_service.publish_package(data)


def test_validate_package_data_rejects_missing_owner(packages_file):
    data = make_package(
        owner="",
        full_name="splent_feature_demo",
        repository="",
        repo_url="https://example.com/splent_feature_demo",
    )

    with pytest.raises(ValueError, match="Owner cannot be empty"):
        package_service.publish_package(data)


def test_load_packages_uses_default_file_when_configured_file_missing(
    tmp_path,
    monkeypatch,
):
    configured_file = tmp_path / "data" / "packages.json"
    default_file = tmp_path / "packages.json"
    package = make_package()

    default_file.write_text(json.dumps({"fake-owner/splent_feature_demo": package}))

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(package_service, "PACKAGES_FILE", str(configured_file))
    monkeypatch.setattr(package_service, "DEFAULT_PACKAGES_FILE", "packages.json")

    assert package_service.load_packages_from_file() == {
        "fake-owner/splent_feature_demo": package
    }


def test_load_packages_uses_default_file_when_configured_file_is_empty(
    tmp_path,
    monkeypatch,
):
    configured_file = tmp_path / "data" / "packages.json"
    default_file = tmp_path / "packages.json"
    package = make_package()

    configured_file.parent.mkdir()
    configured_file.write_text("{}")
    default_file.write_text(json.dumps({"fake-owner/splent_feature_demo": package}))

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(package_service, "PACKAGES_FILE", str(configured_file))
    monkeypatch.setattr(package_service, "DEFAULT_PACKAGES_FILE", "packages.json")

    assert package_service.load_packages_from_file() == {
        "fake-owner/splent_feature_demo": package
    }


def test_update_package(packages_file):
    package_service.publish_package(make_package())

    updated = package_service.update_package(
        "splent_feature_demo",
        {
            "owner": "fake-owner",
            "description": "Updated demo feature",
            "provides": {"demo": "client"},
        },
    )

    assert updated["contract"]["description"] == "Updated demo feature"
    assert updated["contract"]["provides"] == {"demo": "client"}

    saved = json.loads(packages_file.read_text())
    assert saved["fake-owner/splent_feature_demo"] == updated
