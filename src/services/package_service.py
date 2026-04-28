import json
import os

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from src.clients.github_client import fetch_org_repos, fetch_repo_file

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


def get_package_by_name_local(name):
    packages = load_packages_from_file()
    return packages.get(name)


def get_packages_local():
    packages = load_packages_from_file()
    return list(packages.values())


def extract_contract(pyproject_content):
    data = tomllib.loads(pyproject_content)
    tool = data.get("tool", {})
    splent = tool.get("splent", {})
    contract = splent.get("contract")
    return contract


def normalize_package(repo, contract):
    return {
        "full_name": repo.get("full_name"),
        "html_url": repo.get("html_url"),
        "id": repo.get("id"),
        "name": repo.get("name"),
        "private": repo.get("private"),
        "updated_at": repo.get("updated_at"),
        "contract": {
            "description": contract.get("description"),
            "provides": contract.get("provides", {}),
            "requires": contract.get("requires", {}),
        },
    }


def get_packages():
    return get_packages_local()


def get_package_by_name(name):
    return get_package_by_name_local(name)


def validate_package_data(data, require_name=True):
    required_fields = ["description", "provides", "requires", "owner", "repository_url"]

    if require_name:
        required_fields.insert(0, "name")

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
        
    if require_name:
        if not isinstance(data["name"], str) or not data["name"].strip():
            raise ValueError("Package name cannot be empty")
        
    if not isinstance(data["description"], str) or not data["description"].strip():
        raise ValueError("Description cannot be empty")
    
    if not isinstance(data["provides"], dict):
        raise ValueError("Provides must be an object")
    
    if not isinstance(data["requires"], dict):
        raise ValueError("Requires must be an object")
    
    if not isinstance(data["owner"], str) or not data["owner"].strip():
        raise ValueError("Owner cannot be empty")
    
    if not isinstance(data["repository_url"], str) or not data["repository_url"].strip():
        raise ValueError("Repository URL cannot be empty")


def publish_package(data):
    validate_package_data(data)

    package_name = data["name"].strip()
    
    if get_package_by_name_local(package_name):
        raise ValueError(f"Package with name '{package_name}' already exists")

    package_data = {
        "name": package_name,
        "owner": data["owner"],
        "repository_url": data["repository_url"],
        "contract": {
            "description": data["description"],
            "provides": data["provides"],
            "requires": data["requires"],
        },
    }
    
    packages = load_packages_from_file()
    packages[package_name] = package_data
    save_packages_to_file(packages)

    return package_data


def update_package(name, data):
    existing_package = get_package_by_name_local(name)
    if not existing_package:
        raise FileNotFoundError()

    merged_data = {
        "name": name,
        "owner": data.get("owner", existing_package.get("owner", "")),
        "repository_url": data.get("repository_url", existing_package.get("repository_url", "")),
        "description": data.get("description", existing_package["contract"].get("description", "")),
        "provides": data.get("provides", existing_package["contract"].get("provides", {})),
        "requires": data.get("requires", existing_package["contract"].get("requires", {})),
    }

    validate_package_data(merged_data)

    updated_data = {
        "name": merged_data["name"],
        "owner": merged_data["owner"],
        "repository_url": merged_data["repository_url"],
        "contract": {
            "description": merged_data["description"],
            "provides": merged_data["provides"],
            "requires": merged_data["requires"],
        },
    }
    
    packages = load_packages_from_file()
    packages[name] = updated_data
    save_packages_to_file(packages)

    return updated_data