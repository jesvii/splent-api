try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from src.clients.github_client import fetch_org_repos, fetch_repo_file

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
    repos = fetch_org_repos()
    packages = []

    for repo in repos:
        repo_name = repo.get("name")

        pyproject_content = fetch_repo_file(repo_name, "pyproject.toml")
        if pyproject_content is None:
            continue

        try:
            contract = extract_contract(pyproject_content)
        except Exception:
            continue

        if not contract:
            continue

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