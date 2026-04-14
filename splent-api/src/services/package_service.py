from src.clients.github_client import fetch_org_repos


def normalize_repo(repo):
    return {
        "id": repo.get("id"),
        "name": repo.get("name"),
        "full_name": repo.get("full_name"),
        "description": repo.get("description"),
        "html_url": repo.get("html_url"),
        "private": repo.get("private"),
        "updated_at": repo.get("updated_at"),
        "language": repo.get("language"),
    }


def get_packages():
    repos = fetch_org_repos()
    return [normalize_repo(repo) for repo in repos]