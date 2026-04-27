try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from src.clients.github_client import (
    create_org_repo,
    create_or_update_repo_file,
    fetch_org_repos,
    fetch_repo_file,
)



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
    repos = fetch_org_repos()  # Obtiene los repositorios de la organización
    packages = []

    # Itera sobre cada repositorio
    for repo in repos:
        repo_name = repo.get("name")

        # Verifica si tenemos acceso al archivo pyproject.toml en ese repositorio
        pyproject_content = fetch_repo_file(repo_name, "pyproject.toml")

        # Si no encontramos el archivo, continuamos con el siguiente repositorio
        if pyproject_content is None:
            continue

        try:
            # Extraemos el contrato del archivo pyproject.toml
            contract = extract_contract(pyproject_content)
        except Exception as e:
            print(f"Error al extraer el contrato del repositorio {repo_name}: {e}")
            continue  # Si hay un error al extraer el contrato, seguimos con el siguiente repositorio

        # Si no se pudo extraer el contrato, continuamos con el siguiente repositorio
        if not contract:
            continue

        # Normalizamos la información y la agregamos a la lista de paquetes
        packages.append(normalize_package(repo, contract))

    return packages


def get_package_by_name(name):
    repos = fetch_org_repos()

    for repo in repos:
        if repo.get("name") != name:
            continue

        pyproject_content = fetch_repo_file(name, "pyproject.toml")
        if pyproject_content is None:
            return None

        try:
            contract = extract_contract(pyproject_content)
        except Exception:
            return None

        if not contract:
            return None

        return normalize_package(repo, contract)

    return None


def validate_package_data(data, require_name=True):
    required_fields = ["description", "provides", "requires"]

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
    
def build_pyproject_content(data):
    provides = data.get("provides", {})
    requires = data.get("requires", {})

    lines = [
        "[tool.splent.contract]",
        f'description = "{data["description"]}"',
        "",
        "[tool.splent.contract.provides]",
    ]
    for key, value in provides.items():
        lines.append(f'{key} = "{value}"')

    lines.extend(
        [
            "",
            "[tool.splent.contract.requires]",
        ]
    )

    for key, value in requires.items():
        lines.append(f'{key} = "{value}"')

    return "\n".join(lines) + "\n"


def publish_package(data):
    validate_package_data(data)

    package_name= data["name"].strip()

    existing_package = get_package_by_name(package_name)
    if existing_package:
        raise ValueError(f"Package with name '{package_name}' already exists")
    
    create_org_repo(
        repo_name=package_name,
        description=data["description"],
        private=data.get("private", False),
    )

    project_content = build_pyproject_content(data)

    create_or_update_repo_file(
        repo_name=package_name,
        path="pyproject.toml",
        content=project_content,
        message="Publish package contract",
    )

    package = get_package_by_name(package_name)

    if package is None:
        return {
            "name": package_name,
            "private": data.get("private", False),
            "contract": {
                "description": data["description"],
                "provides": data["provides"],
                "requires": data["requires"],
            },
        }

    return package


def update_package(name, data):
    existing_package = get_package_by_name(name)
    if existing_package is None:
        raise FileNotFoundError()

    merged_data = {
        "name": name,
        "description": data.get(
            "description",
            existing_package["contract"].get("description", ""),
        ),
        "provides": data.get(
            "provides",
            existing_package["contract"].get("provides", {}),
        ),
        "requires": data.get(
            "requires",
            existing_package["contract"].get("requires", {}),
        ),
    }

    validate_package_data(merged_data)

    pyproject_content = build_pyproject_content(merged_data)

    create_or_update_repo_file(
        repo_name=name,
        path="pyproject.toml",
        content=pyproject_content,
        message="Update package contract",
    )

    updated_package = get_package_by_name(name)

    if updated_package is None:
        return merged_data

    return updated_package
    