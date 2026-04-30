import json
import os

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from src.clients.github_client import (
    fetch_org_repos,
    fetch_repo_file,
    fetch_repo_metadata,
)

PACKAGES_FILE = "packages.json"


def load_packages_from_file():
    if not os.path.exists(PACKAGES_FILE):
        return {}

    try:
        with open(PACKAGES_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_packages_to_file(packages):
    try:
        with open(PACKAGES_FILE, "w") as f:
            json.dump(packages, f, indent=2)
    except Exception as e:
        print(f"Error saving packages: {e}")


def _packages_from_registry(owner=None):
    packages = load_packages_from_file()
    values = list(packages.values())
    if owner:
        return [package for package in values if package.get("owner") == owner]
    return values


def _get_package_from_registry(name, owner=None):
    packages = _packages_from_registry(owner=owner)
    for package in packages:
        if name in {
            package.get("name"),
            package.get("full_name"),
            package.get("feature_ref"),
            package.get("repository"),
        }:
            return package

    return None


def extract_contract(pyproject_content):
    data = tomllib.loads(pyproject_content)
    tool = data.get("tool", {})
    splent = tool.get("splent", {})
    contract = splent.get("contract")
    return contract


def normalize_package(repo, contract):
    repository_url = repo.get("html_url")
    full_name = repo.get("full_name")
    owner = (repo.get("owner") or {}).get("login")
    if not owner and isinstance(full_name, str) and "/" in full_name:
        owner = full_name.split("/", 1)[0]
    return {
        "full_name": full_name,
        "html_url": repo.get("html_url"),
        "id": repo.get("id"),
        "name": repo.get("name"),
        "feature_ref": full_name or repo.get("name"),
        "owner": owner,
        "private": repo.get("private"),
        "updated_at": repo.get("updated_at"),
        "repository_url": repository_url,
        "repo_url": repository_url,
        "repository": full_name or repo.get("name"),
        "contract": {
            "description": contract.get("description"),
            "provides": contract.get("provides", {}),
            "requires": contract.get("requires", {}),
        },
    }


def _split_package_ref(package_ref, owner=None):
    ref = package_ref.strip()
    if "@" in ref:
        ref = ref.split("@", 1)[0]

    if "/" in ref:
        ref_owner, repo_name = ref.split("/", 1)
        return ref_owner, repo_name

    return owner, ref


def _packages_from_github(owner=None):
    packages = []

    try:
        repos = fetch_org_repos(org=owner)
    except Exception:
        return packages

    for repo in repos:
        repo_name = repo.get("name")
        if not repo_name:
            continue

        pyproject_content = fetch_repo_file(repo_name, "pyproject.toml", org=owner)
        if not pyproject_content:
            continue

        try:
            contract = extract_contract(pyproject_content)
        except Exception:
            continue

        if not isinstance(contract, dict):
            continue

        packages.append(normalize_package(repo, contract))

    return packages


def get_packages(owner=None):
    packages_by_ref = {}

    for package in _packages_from_github(owner=owner):
        packages_by_ref[_package_key(package)] = package

    for package in _packages_from_registry(owner=owner):
        packages_by_ref[_package_key(package)] = package

    return list(packages_by_ref.values())


def get_package_by_name(name, owner=None):
    package = _get_package_from_registry(name, owner=owner)
    if package:
        return package

    repo_owner, repo_name = _split_package_ref(name, owner=owner)
    if repo_owner:
        repo_metadata = fetch_repo_metadata(repo_name, org=repo_owner)
        if not repo_metadata:
            return None

        pyproject_content = fetch_repo_file(repo_name, "pyproject.toml", org=repo_owner)
        if not pyproject_content:
            return None

        try:
            contract = extract_contract(pyproject_content)
        except Exception:
            return None

        if not isinstance(contract, dict):
            return None

        return normalize_package(repo_metadata, contract)

    for package in _packages_from_github(owner=owner):
        if name in {package.get("name"), package.get("full_name"), package.get("feature_ref")}:
            return package

    return None


def _package_key(data):
    for field in ("feature_ref", "full_name", "name"):
        value = data.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return ""


def _get_contract(data):
    contract = data.get("contract")
    return contract if isinstance(contract, dict) else {}


def _get_description(data):
    contract = _get_contract(data)
    return data.get("description") or contract.get("description")


def _get_provides(data):
    contract = _get_contract(data)
    provides = data.get("provides")
    if provides is None:
        provides = contract.get("provides")
    return provides


def _get_requires(data):
    contract = _get_contract(data)
    requires = data.get("requires")
    if requires is None:
        requires = contract.get("requires")
    return requires


def _get_repository_url(data):
    return data.get("repository_url") or data.get("repo_url") or data.get("html_url")


def _repository_ref(owner, package_ref):
    ref = package_ref
    if "@" in ref:
        ref = ref.split("@", 1)[0]
    if "/" not in ref:
        ref = f"{owner}/{ref}"
    return ref


def _owner_from_data(data):
    owner = data.get("owner")
    if isinstance(owner, str) and owner.strip():
        return owner.strip()

    for field in ("full_name", "feature_ref", "repository"):
        value = data.get(field)
        if isinstance(value, str) and "/" in value:
            return value.split("/", 1)[0].strip()

    raise ValueError("Owner cannot be empty")


def _normalize_package_data(data):
    contract = _get_contract(data)
    description = _get_description(data)
    provides = _get_provides(data)
    requires = _get_requires(data)
    owner = _owner_from_data(data)
    repository_url = _get_repository_url(data)
    full_name = data.get("full_name") or data.get("feature_ref") or data.get("name")
    if isinstance(full_name, str) and "/" not in full_name:
        full_name = f"{owner}/{full_name}"
    feature_ref = data.get("feature_ref") or full_name
    if isinstance(feature_ref, str) and "/" not in feature_ref:
        feature_ref = f"{owner}/{feature_ref}"
    repository = data.get("repository") or _repository_ref(owner, feature_ref)

    package_data = {
        "name": data["name"].strip(),
        "full_name": full_name,
        "feature_ref": feature_ref,
        "owner": owner,
        "repository": repository,
        "repository_url": repository_url,
        "repo_url": repository_url,
        "namespace": data.get("namespace"),
        "description": description,
        "provides": provides,
        "requires": requires,
        "contract": {
            **contract,
            "description": description,
            "provides": provides,
            "requires": requires,
        },
    }

    for field in ("github", "metadata"):
        if field in data:
            package_data[field] = data[field]

    return package_data


def validate_package_data(data, require_name=True):
    required_fields = []

    if require_name:
        required_fields.insert(0, "name")

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
        
    if require_name:
        if not isinstance(data["name"], str) or not data["name"].strip():
            raise ValueError("Package name cannot be empty")

    description = _get_description(data)
    provides = _get_provides(data)
    requires = _get_requires(data)
    repository_url = _get_repository_url(data)
    _owner_from_data(data)

    if not isinstance(description, str) or not description.strip():
        raise ValueError("Description cannot be empty")
    
    if not isinstance(provides, dict):
        raise ValueError("Provides must be an object")
    
    if not isinstance(requires, dict):
        raise ValueError("Requires must be an object")

    if not isinstance(repository_url, str) or not repository_url.strip():
        raise ValueError("Repository URL cannot be empty")
    

def publish_package(data):
    validate_package_data(data)

    package_data = _normalize_package_data(data)
    key = _package_key(package_data)

    packages = load_packages_from_file()
    packages[key] = package_data
    save_packages_to_file(packages)

    return package_data


def update_package(name, data):
    owner, _ = _split_package_ref(name, owner=data.get("owner"))
    existing_package = _get_package_from_registry(name, owner=owner)
    if not existing_package:
        raise FileNotFoundError()

    merged_data = {
        **existing_package,
        **data,
        "name": data.get("name", existing_package.get("name", name)),
        "owner": data.get("owner", existing_package.get("owner", "")),
        "repository_url": data.get(
            "repository_url",
            data.get("repo_url", existing_package.get("repository_url", "")),
        ),
        "description": data.get(
            "description", existing_package.get("description", existing_package["contract"].get("description", ""))
        ),
        "provides": data.get(
            "provides", existing_package.get("provides", existing_package["contract"].get("provides", {}))
        ),
        "requires": data.get(
            "requires", existing_package.get("requires", existing_package["contract"].get("requires", {}))
        ),
    }

    validate_package_data(merged_data)

    updated_data = _normalize_package_data(merged_data)

    old_key = _package_key(existing_package)
    new_key = _package_key(updated_data)
    packages = load_packages_from_file()
    if old_key != new_key:
        packages.pop(old_key, None)
    packages[new_key] = updated_data
    save_packages_to_file(packages)

    return updated_data
