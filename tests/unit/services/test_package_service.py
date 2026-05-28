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
